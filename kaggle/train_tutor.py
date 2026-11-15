"""LoRA fine-tune of Qwen3.5-0.8B as the local tutor. Runs on a Kaggle GPU (T4 x2 / P100) or locally.

Data: train.jsonl / val.jsonl from laptop/build_tutor_sft.py (each row: messages, task, weight).
Loss: cross-entropy on the LAST assistant message only, averaged per example (so short hints
count as much as long solutions), multiplied by the row's weight. The rest of the conversation
(system prompt with problem + key, earlier turns) is context only.

    python train_tutor.py                          # one GPU
    torchrun --nproc_per_node 2 train_tutor.py     # Kaggle T4 x2
Env overrides: DATA_DIR, OUT_DIR, MODEL_ID, EPOCHS, LR, LORA_R, MAX_LEN, BATCH, GRAD_ACCUM,
               MAX_STEPS (smoke tests), LIMIT (use only N train rows), FP16=0 (disable AMP on T4),
               MAX_MINUTES (stop training cleanly after N minutes from start, then merge and save
               as usual, so a Kaggle commit still ends normally and keeps its output),
               EVALS (evals + checkpoints per run), FINAL_EVAL_ROWS (0 = every val row).
Output: OUT_DIR/merged  (full HF model, LoRA merged in, ready for convert_hf_to_gguf.py)
"""
import json
import math
import os
import random
import time
from collections import defaultdict
from glob import glob

import torch
import torch.distributed as dist
import torch.nn.functional as F
from peft import LoraConfig, get_peft_model, set_peft_model_state_dict
from safetensors.torch import load_file
from torch.utils.checkpoint import checkpoint
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainerCallback, TrainingArguments

START = time.time()


def env(name, default, cast=str):
    return cast(os.environ.get(name, default))


def find_data_dir():
    if "DATA_DIR" in os.environ:
        return os.environ["DATA_DIR"]
    hits = glob("/kaggle/input/**/train.jsonl", recursive=True)  # any attached Kaggle dataset
    return os.path.dirname(hits[0]) if hits else "data/processed/tutor_sft"


MODEL_ID = env("MODEL_ID", "Qwen/Qwen3.5-0.8B")
DATA_DIR = find_data_dir()
OUT_DIR = env("OUT_DIR", "/kaggle/working" if os.path.isdir("/kaggle/working") else "models/tutor")
MAX_LEN = env("MAX_LEN", 3072, int)  # longest example is ~2.3k tokens
EPOCHS = env("EPOCHS", 2, float)
LR = env("LR", 2e-4, float)
LORA_R = env("LORA_R", 32, int)
BATCH = env("BATCH", 4, int)
GRAD_ACCUM = env("GRAD_ACCUM", 4, int)
MAX_STEPS = env("MAX_STEPS", -1, int)
LIMIT = env("LIMIT", 0, int)
EVAL_ROWS = env("EVAL_ROWS", 400, int)  # val rows used for the evals during training
FINAL_EVAL_ROWS = env("FINAL_EVAL_ROWS", 0, int)  # val rows for the per-task loss at the end (0 = all)
EVALS = env("EVALS", 2, int)  # evals (each one saves a checkpoint) spread over the run
MAX_MINUTES = env("MAX_MINUTES", 0, float)  # 0 = no time limit
DRY_RUN = env("DRY_RUN", "0") == "1"  # 3 steps on the longest examples: checks memory, prints an ETA
DRY_STEPS = 3
SEED = 42
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

tok = AutoTokenizer.from_pretrained(MODEL_ID)
END = "<|im_end|>"  # Qwen chat turn terminator; the model must learn to stop here
assert tok.convert_tokens_to_ids(END) != tok.unk_token_id, "tokenizer has no <|im_end|>"


def encode(row):
    """Prompt rendered exactly as llama.cpp renders it on the board (--jinja --reasoning off)."""
    msgs = row["messages"]
    prompt = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    p = tok(prompt, add_special_tokens=False)["input_ids"]
    c = tok(msgs[-1]["content"] + END, add_special_tokens=False)["input_ids"]
    if len(p) + len(c) > MAX_LEN:
        return None
    return {"input_ids": p + c, "labels": [-100] * len(p) + c, "weight": float(row["weight"]), "task": row["task"]}


def load(name, limit=0):
    rows = [json.loads(line) for line in open(os.path.join(DATA_DIR, f"{name}.jsonl"), encoding="utf-8")]
    if limit:
        rows = random.Random(SEED).sample(rows, min(limit, len(rows)))
    enc = [e for e in map(encode, rows) if e]
    print(f"{name}: {len(enc)} examples, {sum(len(e['input_ids']) for e in enc):,} tokens "
          f"({len(rows) - len(enc)} dropped as longer than {MAX_LEN} tokens)")
    return enc


def dry_run_subset(data, world):
    """The longest examples, enough for DRY_STEPS optimizer steps: worst case for memory and speed."""
    n = BATCH * GRAD_ACCUM * world * DRY_STEPS
    return sorted(data, key=lambda e: -len(e["input_ids"]))[:n]


def collate(batch):
    n = max(len(b["input_ids"]) for b in batch)
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.convert_tokens_to_ids(END)
    return {
        "input_ids": torch.tensor([b["input_ids"] + [pad] * (n - len(b["input_ids"])) for b in batch]),
        "attention_mask": torch.tensor([[1] * len(b["input_ids"]) + [0] * (n - len(b["input_ids"])) for b in batch]),
        "labels": torch.tensor([b["labels"] + [-100] * (n - len(b["labels"])) for b in batch]),
        "weight": torch.tensor([b["weight"] for b in batch]),
    }


def chunk_ce(hidden, head, targets):
    return F.cross_entropy(head(hidden).float(), targets, reduction="none")


class WeightedLM(torch.nn.Module):
    """Wraps the PEFT model so the whole loss runs inside forward(): DDP (torchrun) then syncs
    gradients normally. The LM head runs only on target positions, in checkpointed chunks: full
    logits for 4 x 3k tokens x 248k vocab would not fit in 16 GB."""

    def __init__(self, peft_model):
        super().__init__()
        self.peft = peft_model

    def forward(self, input_ids, attention_mask, labels, weight):
        base = self.peft.get_base_model()
        hidden = base.get_decoder()(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        head = base.get_output_embeddings()
        labels, hidden = labels[:, 1:], hidden[:, :-1]
        mask = labels != -100
        h, t = hidden[mask], labels[mask]
        row = mask.nonzero()[:, 0]  # which example each target token belongs to
        losses = torch.cat([checkpoint(chunk_ce, h[i:i + 512], head, t[i:i + 512], use_reentrant=False)
                            for i in range(0, len(t), 512)])
        per_ex = torch.zeros(labels.shape[0], device=losses.device).index_add_(0, row, losses)
        per_ex = per_ex / mask.sum(1).clamp(min=1)
        return {"loss": (per_ex * weight.to(per_ex.device)).mean(), "per_example": per_ex}


class AdapterTrainer(Trainer):
    def _save(self, output_dir=None, state_dict=None):
        """Checkpoints hold the LoRA adapter only (a few MB), not the whole model."""
        output_dir = output_dir or self.args.output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.accelerator.unwrap_model(self.model).peft.save_pretrained(output_dir)


class Deadline(TrainerCallback):
    """Stop after MAX_MINUTES: evaluate and save one last checkpoint, then the script merges and
    converts as after a full run. With torchrun, every process must stop at the same step, so the
    decision is shared (all_reduce max) instead of each process reading its own clock."""

    def on_step_end(self, args, state, control, **kwargs):
        over = torch.tensor([float(time.time() - START > MAX_MINUTES * 60)],
                            device="cuda" if torch.cuda.is_available() else "cpu")
        if dist.is_available() and dist.is_initialized():
            dist.all_reduce(over, op=dist.ReduceOp.MAX)
        if over.item():
            if state.is_world_process_zero:
                print(f"MAX_MINUTES={MAX_MINUTES:g} reached at step {state.global_step}: stopping, then merging.")
            control.should_training_stop = True
            control.should_evaluate = True
            control.should_save = True
        return control


@torch.no_grad()
def per_task_loss(wrapped, data, batch=8):
    """Unweighted val loss per task: the number to compare across runs."""
    wrapped.eval()
    device = next(wrapped.parameters()).device
    total, count = defaultdict(float), defaultdict(int)
    for i in range(0, len(data), batch):
        chunk = data[i:i + batch]
        per_ex = wrapped(**{k: v.to(device) for k, v in collate(chunk).items()})["per_example"]
        for ex, loss in zip(chunk, per_ex.tolist()):
            total[ex["task"]] += loss
            count[ex["task"]] += 1
    return {t: round(total[t] / count[t], 4) for t in sorted(total)}


def main():
    torch.manual_seed(SEED)
    train, val = load("train", LIMIT), load("val", LIMIT // 10 if LIMIT else 0)
    cuda = torch.cuda.is_available()
    bf16 = cuda and torch.cuda.is_bf16_supported()
    fp16 = cuda and not bf16 and env("FP16", "1") == "1"  # T4/P100: fp32 weights + fp16 autocast
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.bfloat16 if bf16 else torch.float32)
    model.config.use_cache = False
    print(type(model).__name__)

    # LoRA on every linear layer of the language model (attention, Gated DeltaNet, MLP);
    # the LM head and embeddings stay frozen.
    lora = LoraConfig(r=LORA_R, lora_alpha=2 * LORA_R, lora_dropout=0.05, task_type="CAUSAL_LM",
                      target_modules="all-linear")
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()
    wrapped = WeightedLM(model)

    world = int(os.environ.get("WORLD_SIZE", 1))
    steps_per_epoch = math.ceil(len(train) / (BATCH * GRAD_ACCUM * world))
    if DRY_RUN:
        full_tokens, full_steps = sum(len(e["input_ids"]) for e in train), math.ceil(steps_per_epoch * EPOCHS)
        train, val = dry_run_subset(train, world), val[:BATCH]
        dry_tokens = sum(len(e["input_ids"]) for e in train)
    total_steps = MAX_STEPS if MAX_STEPS > 0 else math.ceil(steps_per_epoch * EPOCHS)
    eval_every = max(5 if MAX_STEPS < 0 else 1, total_steps // max(EVALS, 1))
    every = "no" if DRY_RUN else "steps"
    args = TrainingArguments(
        output_dir=os.path.join(OUT_DIR, "ckpt"),
        num_train_epochs=EPOCHS,
        max_steps=DRY_STEPS if DRY_RUN else MAX_STEPS,
        per_device_train_batch_size=BATCH,
        per_device_eval_batch_size=BATCH,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LR,
        lr_scheduler_type="cosine",
        warmup_steps=max(1, steps_per_epoch // 20),
        weight_decay=0.0,
        max_grad_norm=1.0,
        bf16=bf16,
        fp16=fp16,
        eval_strategy=every,
        eval_steps=eval_every,
        save_strategy=every,
        save_steps=eval_every,
        save_total_limit=3,
        metric_for_best_model="eval_loss",  # tracks state.best_model_checkpoint; loaded by hand below
        prediction_loss_only=True,
        remove_unused_columns=False,
        dataloader_num_workers=2,
        ddp_find_unused_parameters=False,
        logging_steps=10,
        report_to="none",
        seed=SEED,
    )
    # A fixed sample is enough to pick the best checkpoint; every eval on all val rows costs ~4%.
    eval_rows = random.Random(SEED).sample(val, min(EVAL_ROWS, len(val))) if EVAL_ROWS else val
    trainer = AdapterTrainer(model=wrapped, args=args, train_dataset=train, eval_dataset=eval_rows, data_collator=collate,
                             callbacks=[Deadline()] if MAX_MINUTES > 0 and not DRY_RUN else None)
    result = trainer.train()

    if DRY_RUN:
        if trainer.is_world_process_zero():
            sec = result.metrics["train_runtime"]
            peak = torch.cuda.max_memory_allocated() / 2**30 if cuda else 0
            # Upper bound: the dry run used the longest examples; time scales ~linearly with tokens.
            eta = sec / dry_tokens * full_tokens * EPOCHS / 3600
            print(f"DRY RUN OK: peak GPU memory {peak:.1f} GiB per GPU, {sec:.0f} s for {DRY_STEPS} steps. "
                  f"Full run: {full_steps} steps, roughly {eta:.1f} h at most (EPOCHS={EPOCHS:g}).")
        return

    if trainer.is_world_process_zero():
        best = trainer.state.best_model_checkpoint
        if best:  # the checkpoint with the lowest weighted val loss, not just the last one
            print("loading best checkpoint", best)
            set_peft_model_state_dict(model, load_file(os.path.join(best, "adapter_model.safetensors")))
        final_rows = random.Random(SEED).sample(val, min(FINAL_EVAL_ROWS, len(val))) if FINAL_EVAL_ROWS else val
        with torch.autocast("cuda", dtype=torch.float16, enabled=fp16):
            print("val loss per task:", json.dumps(per_task_loss(wrapped, final_rows)))
        model.save_pretrained(os.path.join(OUT_DIR, "adapter"))
        merged = model.merge_and_unload()
        merged.config.use_cache = True
        out = os.path.join(OUT_DIR, "merged")
        merged.to(torch.bfloat16).save_pretrained(out)
        tok.save_pretrained(out)
        print("saved", out)


if __name__ == "__main__":
    main()
