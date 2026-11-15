"""Head B on a Kaggle GPU: LoRA on Qwen3.5 0.8B to write a short solve() program.

Runs as a Kaggle script kernel (see santolina_tutor/finetune/kaggle_run.py).
Reads programs/train.jsonl, programs/val.jsonl and programs/program_head.py from
the attached private dataset. program_head.py is copilot/program_head.py, so the
prompt, the sandbox and the option matching are exactly the board's.

Before training and after every epoch, the model writes one program per validation
problem (greedy, like the board); each program runs in the sandbox and is matched to
the options. Written to /kaggle/working:

    metrics.json                coverage, precision, accuracy, tokens: zero-shot and per epoch
    val_programs.jsonl          each generated program and its result (last epoch)
    val_programs_epoch<n>.jsonl the same after epoch n
    adapter/epoch<n>/, merged/  the LoRA adapter of every epoch; last epoch merged (bf16) for GGUF

With rag_k = 1 (kaggle_run push --set rag_k=1), every prompt first shows one similar
solved training problem and its program (copilot/program_head.build_messages example).
Neighbours come from bge-small-en-v1.5 embeddings computed here, as on the board:
the query gets the bge prefix, stored problems don't, text cut at 1400 characters.
Training examples never see themselves. Their example is drawn once (fixed seed):
none_share get no example, weak_share a bad one (a far neighbour or a random program
of another topic), the rest the nearest fitting one, where a twin (same problem at
another level: cosine >= twin_cos and twin_options equal option values) is allowed
for about twin_share of all examples only. Validation retrieves from train only.
Extra outputs: neighbours.json (ids and cosines, no text), and metrics split into
twin and non-twin cases plus a no-model baseline that runs the example's program.
"""
import os
import socket

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import subprocess
import sys

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
import glob
import json
import math
import os
import random
import re
import shutil
import time

from peft import LoraConfig, get_peft_model, get_peft_model_state_dict, set_peft_model_state_dict
import torch
from transformers import (
    AutoConfig,
    AutoModel,
    AutoModelForCausalLM,
    AutoModelForImageTextToText,
    AutoProcessor,
    AutoTokenizer,
)

if not torch.cuda.is_available():
    sys.exit("No GPU in this kernel: verify the Kaggle account by phone (kaggle.com/settings) "
             "and push with --accelerator NvidiaTeslaT4.")

CFG = {"base": "Qwen/Qwen3.5-0.8B",
       "revision": "2fc06364715b967f1860aea9cf38778875588b17",  # base of bartowski/Qwen_Qwen3.5-0.8B-GGUF
       # gguf: convert the best epoch with llama.cpp at the board's commit and quantize it, so only
       # one small file needs downloading; the merged weights are then deleted from the output
       "skip_before": False, "gguf": "", "gguf_quants": ["Q4_K_M", "Q4_0", "Q3_K_M"], "llama_cpp": "2cbe0ec429b849a88664e0f62388fc92a5abd699",
"epochs": 3, "lr": 2e-4, "batch": 4, "accum": 4, "warmup": 0.05, "rank": 32, "alpha": 64,
       "dropout": 0.05, "max_len": 1024, "max_new_tokens": 160, "seed": 42,
       "rag_k": 0, "none_share": 0.10, "weak_share": 0.25, "twin_share": 0.05,
       "twin_cos": 0.90, "twin_options": 4, "example_max_tokens": 150}
CFG_OVERRIDES = {}  # set by kaggle_run push --set
CFG.update(CFG_OVERRIDES)
BASE, REVISION = CFG["base"], CFG["revision"]
EMBED = "BAAI/bge-small-en-v1.5"
EMBED_REVISION = "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"
EMBED_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "  # config.env
EMBED_MAX_CHARS = 1400  # copilot/embed.py
OUT = "/kaggle/working"
random.seed(CFG["seed"])
torch.manual_seed(CFG["seed"])
device = "cuda"
print("GPU:", torch.cuda.get_device_name(0), "| config:", CFG, flush=True)


def find(name):
    # Kaggle keeps the programs/ folder when the dataset has several folders, and
    # unpacks it at the dataset root when it is the only one.
    hits = (glob.glob(f"/kaggle/input/**/programs/{name}", recursive=True)
            or glob.glob(f"/kaggle/input/**/{name}", recursive=True))
    assert len(hits) == 1, f"expected one {name} under /kaggle/input, found {hits}"
    return hits[0]


def read(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


sys.path.insert(0, os.path.dirname(find("program_head.py")))
import program_head

train_rows, val_rows = read(find("train.jsonl")), read(find("val.jsonl"))
print(f"train {len(train_rows)} programs, val {len(val_rows)} problems", flush=True)

tok = AutoTokenizer.from_pretrained(BASE, revision=REVISION)
END = "<|im_end|>"  # end of an assistant turn in Qwen's chat template


def prompt(messages):
    # The board runs llama-server --jinja --reasoning off: the model's own template, no thinking.
    return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True,
                                   enable_thinking=False)


def problem_text(r):
    return r["messages"][-1]["content"]  # format_problem(r), what copilot/rag.py embeds


@torch.no_grad()
def embed(texts, query):
    etok = AutoTokenizer.from_pretrained(EMBED, revision=EMBED_REVISION)
    emodel = AutoModel.from_pretrained(EMBED, revision=EMBED_REVISION).to(device).eval()
    prefix = EMBED_QUERY_PREFIX if query else ""
    vectors = []
    for i in range(0, len(texts), 64):
        enc = etok([(prefix + t)[:EMBED_MAX_CHARS] for t in texts[i:i + 64]], padding=True,
                   truncation=True, max_length=512, return_tensors="pt").to(device)
        cls = emodel(**enc).last_hidden_state[:, 0].float()  # bge: CLS pooling, unit length
        vectors.append(torch.nn.functional.normalize(cls, dim=-1))
    del emodel
    return torch.cat(vectors)


def shared_options(a, b):
    return sum(1 for v in a["options"].values() if program_head.matches(v, b["options"]))


def attach_examples():
    """Pick each row's example and rewrite its messages; returns the neighbour log (no text)."""
    rng = random.Random(CFG["seed"])
    docs = embed([problem_text(r) for r in train_rows], query=False)
    sims = {"train": (embed([problem_text(r) for r in train_rows], query=True) @ docs.T).tolist(),
            "val": (embed([problem_text(r) for r in val_rows], query=True) @ docs.T).tolist()}
    ex_tokens = [len(tok(problem_text(r) + r["program"], add_special_tokens=False)["input_ids"])
                 for r in train_rows]
    fits = [n <= CFG["example_max_tokens"] for n in ex_tokens]

    def twin(r, j, cos):
        return cos >= CFG["twin_cos"] and shared_options(r, train_rows[j]) >= CFG["twin_options"]

    def ranked(r, row_sims):
        order = sorted(range(len(train_rows)), key=lambda j: -row_sims[j])
        return [j for j in order if train_rows[j]["id"] != r["id"]]  # never itself

    plans = []
    for r, row_sims in zip(train_rows, sims["train"]):
        order = ranked(r, row_sims)
        twins = [j for j in order[:5] if twin(r, j, row_sims[j])]
        plans.append((order, twins))
    with_twin = sum(1 for _, twins in plans if twins)
    p_twin = min(1.0, CFG["twin_share"] * len(train_rows) / with_twin) if with_twin else 0.0
    print(f"train problems with a twin in train: {with_twin}; twin used with p={p_twin:.2f}",
          flush=True)

    log = {"train": [], "val": []}
    frozen = list(train_rows)  # indices into the original order
    for r, row_sims, (order, twins) in zip(frozen, sims["train"], plans):
        u, j, role = rng.random(), None, "none"
        if u < CFG["none_share"]:
            pass
        elif u < CFG["none_share"] + CFG["weak_share"]:
            role = "weak"
            if rng.random() < 0.5:
                pool = [k for k in order[9:30] if fits[k] and k not in twins]
            else:
                pool = [k for k in order if fits[k] and train_rows[k]["topic"] != r["topic"]]
            j = rng.choice(pool) if pool else None
        else:
            role = "near"
            if twins and rng.random() < p_twin:
                j = next((k for k in twins if fits[k]), None)
            if j is None:
                j = next((k for k in order if fits[k] and k not in twins), None)
        log["train"].append({"id": r["id"], "role": role,
                             "example": frozen[j]["id"] if j is not None else None,
                             "cos": round(row_sims[j], 4) if j is not None else None,
                             "twin": j in twins if j is not None else False})
        r["example"] = j
    for r, row_sims in zip(val_rows, sims["val"]):
        order = ranked(r, row_sims)
        j = next((k for k in order if fits[k]), None)
        r["example"], r["twin"] = j, twin(r, j, row_sims[j])
        r["example_program"] = frozen[j]["program"]
        log["val"].append({"id": r["id"], "example": frozen[j]["id"],
                           "cos": round(row_sims[j], 4), "twin": r["twin"],
                           "top5": [(frozen[k]["id"], round(row_sims[k], 4)) for k in order[:5]]})
    for r in train_rows + val_rows:
        j = r.pop("example")
        if j is not None:
            r["messages"] = program_head.build_messages(r, (frozen[j], frozen[j]["program"]))
    print(f"train roles {dict(collections.Counter(x['role'] for x in log['train']))}, "
          f"twin examples {sum(x['twin'] for x in log['train'])}; "
          f"val twin cases {sum(r['twin'] for r in val_rows)}/{len(val_rows)}", flush=True)
    with open(f"{OUT}/neighbours.json", "w") as f:
        json.dump(log, f)


if CFG["rag_k"]:
    assert CFG["rag_k"] == 1, "only k=1 fits the board's time budget"
    attach_examples()

print("Example target:\n" + prompt(train_rows[0]["messages"])[-400:] + train_rows[0]["program"],
      flush=True)

# Qwen3.5 0.8B is a vision-language checkpoint; Noema-2B is text only (Qwen3_5ForCausalLM)
TEXT_ONLY = any(a.endswith("ForCausalLM") for a in AutoConfig.from_pretrained(BASE, revision=REVISION).architectures)
Model = AutoModelForCausalLM if TEXT_ONLY else AutoModelForImageTextToText
model = Model.from_pretrained(BASE, revision=REVISION, torch_dtype=torch.float16)
# Frozen base in fp16 to fit the T4's 15 GB; peft keeps the LoRA weights in fp32.
model.to(device)


@torch.no_grad()
def evaluate(tag):
    model.eval()
    tok.padding_side = "left"
    results = []
    for i in range(0, len(val_rows), 16):
        batch = val_rows[i:i + 16]
        enc = tok([prompt(r["messages"]) for r in batch], return_tensors="pt", padding=True,
                  add_special_tokens=False).to(device)
        with torch.autocast("cuda", dtype=torch.float16):
            # Stop at the end of the assistant turn, as llama-server does on the board.
            out = model.generate(**enc, max_new_tokens=CFG["max_new_tokens"], do_sample=False,
                                 eos_token_id=[tok.convert_tokens_to_ids(END), tok.eos_token_id],
                                 pad_token_id=tok.pad_token_id or tok.eos_token_id)
        for r, seq in zip(batch, out[:, enc["input_ids"].shape[1]:]):
            text = tok.decode(seq, skip_special_tokens=False).split(END)[0]
            n_tokens = len(tok(text, add_special_tokens=False)["input_ids"]) + 1
            program = program_head.extract_program(text)
            j = program_head.judge(program, r["options"])
            status = ("correct" if j["letter"] == r["label"] else "wrong" if j["letter"]
                      else "error" if j["error"] else "no_match" if not j["hits"] else "ambiguous")
            results.append({"id": r["id"], "level": r["level"], "label": r["label"], "status": status,
                            "letter": j["letter"], "value": j["value"], "error": j["error"],
                            "tokens": n_tokens, "program": program, "twin": r.get("twin"),
                            "copy": same_program(program, r.get("example_program"))})
    model.train()
    return report(tag, results), results


def same_program(a, b):
    return b is not None and "".join(a.split()) == "".join(b.split())


def summarize(results):
    n = len(results)
    count = collections.Counter(r["status"] for r in results)
    answered = count["correct"] + count["wrong"]
    tokens = sorted(r["tokens"] for r in results)
    m = {"n": n, "correct": count["correct"], "status": dict(count),
         "coverage": round(answered / n, 4) if n else None,
         "precision": round(count["correct"] / answered, 4) if answered else None,
         "accuracy": round(count["correct"] / n, 4) if n else None,
         "median_tokens": tokens[n // 2] if n else None, "max_tokens": tokens[-1] if n else None}
    if any(r["copy"] for r in results):
        copies = [r for r in results if r["copy"]]
        m["copies"] = {"n": len(copies), "correct": sum(r["status"] == "correct" for r in copies)}
    return m


def report(tag, results):
    m = summarize(results)
    print(f"[{tag}] correct {m['correct']}/{m['n']} | coverage {m['coverage']} | precision "
          f"{m['precision']} | {m['status']} | median {m['median_tokens']} tokens", flush=True)
    if CFG["rag_k"]:
        m["twin"] = summarize([r for r in results if r["twin"]])
        m["non_twin"] = summarize([r for r in results if not r["twin"]])
        print(f"[{tag}] twin {m['twin']['correct']}/{m['twin']['n']} | non-twin "
              f"{m['non_twin']['correct']}/{m['non_twin']['n']} (precision "
              f"{m['non_twin']['precision']}) | copies {m.get('copies')}", flush=True)
    return m


def copy_baseline():
    """No model: run the retrieved example's program against the validation options."""
    results = []
    for r in val_rows:
        j = program_head.judge(r["example_program"], r["options"])
        status = ("correct" if j["letter"] == r["label"] else "wrong" if j["letter"]
                  else "error" if j["error"] else "no_match" if not j["hits"] else "ambiguous")
        results.append({"status": status, "tokens": 0, "twin": r["twin"], "copy": True})
    return report("copy example program", results)


baseline = copy_baseline() if CFG["rag_k"] else None


# skip_before: the untuned score is already known from an earlier run, so save the time
before = {"correct": -1, "accuracy": None, "precision": None} if CFG["skip_before"] else evaluate("zero-shot")[0]


def encode(r):
    p = tok(prompt(r["messages"]), add_special_tokens=False)["input_ids"]
    t = tok(r["program"].strip() + END + "\n", add_special_tokens=False)["input_ids"]
    ids = (p + t)[: CFG["max_len"]]
    return ids, ([-100] * len(p) + t)[: CFG["max_len"]]  # loss on the program only


def collate(batch_rows):
    pairs = [encode(r) for r in batch_rows]
    width = max(len(ids) for ids, _ in pairs)
    pad = tok.pad_token_id or tok.eos_token_id
    ids = torch.tensor([x + [pad] * (width - len(x)) for x, _ in pairs], device=device)
    labels = torch.tensor([y + [-100] * (width - len(y)) for _, y in pairs], device=device)
    mask = torch.tensor([[1] * len(x) + [0] * (width - len(x)) for x, _ in pairs], device=device)
    return ids, mask, labels


# every Linear inside the decoder layers; never the vision tower or the output head
DECODER = re.compile(r"^(?!.*visual).*\blayers\.\d+\.")
leaf_names = sorted({name.split(".")[-1] for name, mod in model.named_modules()
                     if isinstance(mod, torch.nn.Linear) and DECODER.match(name)})
print("LoRA targets:", leaf_names, flush=True)
lora = LoraConfig(r=CFG["rank"], lora_alpha=CFG["alpha"], lora_dropout=CFG["dropout"],
                  target_modules=rf"^(?!.*visual).*\blayers\.\d+\..*\.({'|'.join(leaf_names)})$")
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

model.train()
tok.padding_side = "right"
step, start, history = 0, time.time(), []
best = {"correct": before["correct"], "epoch": 0, "state": None}
for epoch in range(CFG["epochs"]):
    random.shuffle(train_rows)
    running = []
    for i in range(0, len(train_rows), CFG["batch"]):
        ids, mask, labels = collate(train_rows[i:i + CFG["batch"]])
        with torch.autocast("cuda", dtype=torch.float16):
            loss = model(input_ids=ids, attention_mask=mask, labels=labels).loss / CFG["accum"]
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
            if step % 10 == 0:
                print(f"epoch {epoch + 1} step {step}/{steps} loss "
                      f"{sum(running[-40:]) / len(running[-40:]):.4f} ({time.time() - start:.0f} s)",
                      flush=True)
    m, results = evaluate(f"epoch {epoch + 1}")
    history.append({"epoch": epoch + 1, **m})
    with open(f"{OUT}/val_programs_epoch{epoch + 1}.jsonl", "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in results)
    model.save_pretrained(f"{OUT}/adapter/epoch{epoch + 1}")
    if m["correct"] > best["correct"] or best["state"] is None:
        best = {"correct": m["correct"], "epoch": epoch + 1,
                "state": {k: v.detach().clone() for k, v in get_peft_model_state_dict(model).items()}}

after = next(h for h in history if h["epoch"] == best["epoch"])  # the epoch that is merged
print(f"best epoch {best['epoch']}: correct {best['correct']}", flush=True)
set_peft_model_state_dict(model, best["state"])
with open(f"{OUT}/metrics.json", "w") as f:
    json.dump({"base": BASE, "revision": REVISION, "config": CFG, "before": before, "after": after,
               "best_epoch": best["epoch"],
               "history": history, "copy_baseline": baseline,
               "train_seconds": round(time.time() - start)}, f, indent=2)
with open(f"{OUT}/val_programs.jsonl", "w") as f:
    f.writelines(json.dumps(r) + "\n" for r in results)

merged = model.merge_and_unload().to(torch.bfloat16)
merged.save_pretrained(f"{OUT}/merged", safe_serialization=True)
if not TEXT_ONLY:
    AutoProcessor.from_pretrained(BASE, revision=REVISION).save_pretrained(f"{OUT}/merged")
tok.save_pretrained(f"{OUT}/merged")
print(f"done: correct {before['accuracy']} -> {after['accuracy']:.3f} of val; "
      f"precision {before['precision']} -> {after['precision']}", flush=True)


if CFG["gguf"]:
    # GGUF at the board's llama.cpp commit; --model-name keeps the file's metadata (and its
    # SHA256) independent of the folder name. Kaggle's torch is kept: only gguf-py is added.
    def sh(cmd, cwd=None):
        print("$", cmd, flush=True)
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)

    del merged, model
    torch.cuda.empty_cache()
    src = "/kaggle/temp/llama.cpp"
    sh(f"git clone -q https://github.com/ggml-org/llama.cpp {src}")
    sh(f"git checkout -q {CFG['llama_cpp']}", cwd=src)
    sh(f"{sys.executable} -m pip install -q --no-deps {src}/gguf-py sentencepiece")
    f16 = f"/kaggle/temp/{CFG['gguf']}-f16.gguf"
    sh(f"{sys.executable} {src}/convert_hf_to_gguf.py {OUT}/merged --outtype f16 "
       f"--model-name {CFG['gguf']} --outfile {f16} --no-mtp")  # the merged model has no MTP head
    sh("cmake -B build -DGGML_CUDA=OFF -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF > /dev/null", cwd=src)
    sh("cmake --build build --target llama-quantize -j4 > /dev/null", cwd=src)
    # Q4_K_M is the one timed on the board; Q4_0 has repacked ARM kernels and Q3_K_M is
    # smaller, so both may write faster on the A53. Their accuracy is measured on the laptop.
    for quant in CFG["gguf_quants"]:
        final = f"{OUT}/{CFG['gguf']}-{quant}.gguf"
        sh(f"{src}/build/bin/llama-quantize {f16} {final} {quant} > /dev/null")
        sh(f"sha256sum {final} > {final}.sha256 && cat {final}.sha256")
    shutil.rmtree(f"{OUT}/merged")  # 4 GB that nobody needs to download
    os.remove(f16)
