"""Head A on a Kaggle GPU: LoRA on Qwen3.5 0.8B for the one-letter A-E answer.

Runs as a Kaggle script kernel (see santolina_tutor/finetune/kaggle_run.py).
Reads train.jsonl/val.jsonl from the attached private dataset, measures the
untrained model, trains, measures again, and writes to /kaggle/working:

    metrics.json       accuracy before/after, by language and level, letter counts
    val_probs.csv      the five letter probabilities for every validation row
    adapter/           the LoRA adapter (small)
    merged/            base + adapter merged, bf16, ready for convert_hf_to_gguf.py

The loss is cross-entropy over the five letter tokens at the answer position,
which is the decision the board makes with the grammar root ::= [A-E].
"""
import os
import socket

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import subprocess
import sys

# Kaggle gives a GPU and internet only to phone-verified accounts, and otherwise runs the
# script on CPU, offline, without saying so. Stop at once with the reason.
try:
    socket.create_connection(("huggingface.co", 443), timeout=10).close()
except OSError:
    sys.exit("No internet in this kernel: verify the Kaggle account by phone "
             "(kaggle.com/settings), then push again with enable_internet.")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U",
                "transformers>=4.57", "peft>=0.17", "accelerate"], check=True)
# Kaggle's image ships an old torchao that new peft rejects; we don't use it.
subprocess.run([sys.executable, "-m", "pip", "uninstall", "-q", "-y", "torchao"], check=False)

import collections
import csv
import glob
import json
import math
import random
import time

from peft import LoraConfig, get_peft_model
import torch
from transformers import AutoModelForImageTextToText, AutoProcessor, AutoTokenizer

BASE = "Qwen/Qwen3.5-0.8B"
REVISION = "2fc06364715b967f1860aea9cf38778875588b17"  # the base of bartowski/Qwen_Qwen3.5-0.8B-GGUF
LETTERS = "ABCDE"
CFG = {"epochs": 2, "lr": 1e-4, "batch": 4, "accum": 4, "warmup": 0.05, "rank": 32, "alpha": 64,
       "dropout": 0.05, "max_len": 768, "seed": 42}
OUT = "/kaggle/working"

if not torch.cuda.is_available():
    sys.exit("No GPU in this kernel: verify the Kaggle account by phone (kaggle.com/settings) "
             "and push with --accelerator NvidiaTeslaT4.")
random.seed(CFG["seed"])
torch.manual_seed(CFG["seed"])
device = "cuda"
print("GPU:", torch.cuda.get_device_name(0), "| config:", CFG, flush=True)


def find(name):
    hits = glob.glob(f"/kaggle/input/**/letters/{name}", recursive=True)
    assert len(hits) == 1, f"expected one {name} under /kaggle/input, found {hits}"
    return hits[0]


def read(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


train_rows, val_rows = read(find("train.jsonl")), read(find("val.jsonl"))
print(f"train {len(train_rows)} rows, val {len(val_rows)} rows", flush=True)

tok = AutoTokenizer.from_pretrained(BASE, revision=REVISION)
tok.padding_side = "left"  # the answer position is then always the last one
letter_ids = []
for letter in LETTERS:
    ids = tok.encode(letter, add_special_tokens=False)
    assert len(ids) == 1, f"{letter} is not one token: {ids}"
    letter_ids.append(ids[0])


def prompt(messages):
    # The board runs llama-server --jinja --reasoning off: the model's own template, no thinking.
    return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True,
                                   enable_thinking=False)


print("Example prompt:\n" + prompt(train_rows[0]["messages"]) + "<answer>" + train_rows[0]["label"],
      flush=True)

model = AutoModelForImageTextToText.from_pretrained(BASE, revision=REVISION, torch_dtype=torch.float16)
# Frozen base in fp16 to fit the T4's 15 GB; peft keeps the LoRA weights in fp32.
model.to(device)


def letter_logits(batch_rows):
    texts = [prompt(r["messages"]) for r in batch_rows]
    enc = tok(texts, return_tensors="pt", padding=True, truncation=True, max_length=CFG["max_len"])
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.autocast("cuda", dtype=torch.float16):
        out = model(**enc, logits_to_keep=1)
    return out.logits[:, -1, :].float()[:, letter_ids]


@torch.no_grad()
def evaluate(tag):
    model.eval()
    probs = []
    for i in range(0, len(val_rows), 16):
        probs.append(torch.softmax(letter_logits(val_rows[i:i + 16]), -1).cpu())
    probs = torch.cat(probs)
    pred = [LETTERS[j] for j in probs.argmax(-1).tolist()]
    right = [p == r["label"] for p, r in zip(pred, val_rows)]

    def acc(key):
        groups = collections.defaultdict(list)
        for ok, r in zip(right, val_rows):
            groups[r[key]].append(ok)
        return {str(k): {"acc": round(sum(v) / len(v), 4), "n": len(v)} for k, v in sorted(groups.items())}

    m = {"acc": round(sum(right) / len(right), 4), "n": len(right),
         "by_language": acc("language"), "by_level": acc("level"),
         "pred_letters": dict(sorted(collections.Counter(pred).items())),
         "true_letters": dict(sorted(collections.Counter(r["label"] for r in val_rows).items())),
         "mean_top_prob": round(probs.max(-1).values.mean().item(), 4)}
    print(f"[{tag}] acc {m['acc']:.3f} ({sum(right)}/{len(right)}) | by language "
          f"{ {k: v['acc'] for k, v in m['by_language'].items()} } | predicted {m['pred_letters']}",
          flush=True)
    model.train()
    return m, probs, pred


before, _, _ = evaluate("zero-shot")

# LoRA on every linear layer of the text model (attention, DeltaNet and MLP); the vision tower stays frozen.
leaf_names = sorted({name.split(".")[-1] for name, mod in model.named_modules()
                     if isinstance(mod, torch.nn.Linear) and "language_model" in name})
print("LoRA targets:", leaf_names, flush=True)
lora = LoraConfig(r=CFG["rank"], lora_alpha=CFG["alpha"], lora_dropout=CFG["dropout"],
                  target_modules=rf".*language_model.*\.({'|'.join(leaf_names)})$")
model.config.use_cache = False
model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
model.enable_input_require_grads()
model = get_peft_model(model, lora)
model.print_trainable_parameters()

params = [p for p in model.parameters() if p.requires_grad]
optim = torch.optim.AdamW(params, lr=CFG["lr"], weight_decay=0.0)
steps = math.ceil(len(train_rows) / (CFG["batch"] * CFG["accum"])) * CFG["epochs"]
warm = int(steps * CFG["warmup"])
sched = torch.optim.lr_scheduler.LambdaLR(optim, lambda s: min(1.0, (s + 1) / max(1, warm)) *
                                          0.5 * (1 + math.cos(math.pi * min(1.0, s / steps))))
scaler = torch.amp.GradScaler("cuda")
target_of = {letter: i for i, letter in enumerate(LETTERS)}

model.train()
step, start, history = 0, time.time(), []
for epoch in range(CFG["epochs"]):
    random.shuffle(train_rows)
    running = []
    for i in range(0, len(train_rows), CFG["batch"]):
        batch = train_rows[i:i + CFG["batch"]]
        target = torch.tensor([target_of[r["label"]] for r in batch], device=device)
        loss = torch.nn.functional.cross_entropy(letter_logits(batch), target) / CFG["accum"]
        scaler.scale(loss).backward()
        running.append(loss.item() * CFG["accum"])
        if (i // CFG["batch"] + 1) % CFG["accum"] == 0:
            scaler.unscale_(optim)
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            scaler.step(optim)
            scaler.update()
            optim.zero_grad(set_to_none=True)
            sched.step()
            step += 1
            if step % 50 == 0:
                avg = sum(running[-100:]) / len(running[-100:])
                print(f"epoch {epoch + 1} step {step}/{steps} loss {avg:.4f} "
                      f"({time.time() - start:.0f} s)", flush=True)
    m, _, _ = evaluate(f"epoch {epoch + 1}")
    history.append({"epoch": epoch + 1, **m})

after, probs, pred = evaluate("final")
with open(f"{OUT}/metrics.json", "w") as f:
    json.dump({"base": BASE, "revision": REVISION, "config": CFG, "before": before, "after": after,
               "history": history, "train_seconds": round(time.time() - start)}, f, indent=2)
with open(f"{OUT}/val_probs.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "language", "level", "label", "pred"] + [f"p_{x}" for x in LETTERS])
    for r, p, row in zip(val_rows, pred, probs.tolist()):
        w.writerow([r["id"], r["language"], r["level"], r["label"], p] + [round(x, 5) for x in row])

model.save_pretrained(f"{OUT}/adapter")
merged = model.merge_and_unload().to(torch.bfloat16)
merged.save_pretrained(f"{OUT}/merged", safe_serialization=True)
AutoProcessor.from_pretrained(BASE, revision=REVISION).save_pretrained(f"{OUT}/merged")
tok.save_pretrained(f"{OUT}/merged")
print(f"done: zero-shot {before['acc']:.3f} -> fine-tuned {after['acc']:.3f}", flush=True)
