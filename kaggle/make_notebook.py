"""Writes the Kaggle notebooks (no outputs, so they are safe to commit).
    python kaggle/make_notebook.py
-> kaggle/tutor_finetune.ipynb        full run: dry run first, then Save & Run All
-> kaggle/tutor_finetune_small.ipynb  short run (~1.5 h) on data/processed/tutor_sft_small, with a time
                                      limit and 4 checkpoints; Save & Run All directly
"""
import json
from pathlib import Path

LLAMA_REF = "2cbe0ec429b849a88664e0f62388fc92a5abd699"  # = LLAMA_CPP_REF in config.env

INSTALL = """# flash-linear-attention: fast Triton kernels for Qwen3.5's Gated DeltaNet layers (else a slow
# PyTorch fallback). If training crashes inside fla/triton: !pip uninstall -y flash-linear-attention fla-core
!pip install -q -U "transformers>=5" peft accelerate safetensors flash-linear-attention
# Kaggle ships torchao 0.10; recent peft refuses to start when an old torchao is installed. Unused here.
!pip uninstall -y -q torchao
!nvidia-smi -L"""

FIND = """import glob, os, subprocess
SCRIPT = glob.glob("/kaggle/input/**/train_tutor.py", recursive=True)[0]
os.environ["DATA_DIR"] = os.path.dirname(SCRIPT)
N_GPU = int(subprocess.check_output("nvidia-smi -L | wc -l", shell=True))
print(SCRIPT, N_GPU, "GPU(s)")"""

SANITY = """import json, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
path = "/kaggle/working/merged"
tok = AutoTokenizer.from_pretrained(path)
dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float32  # fp16 can overflow
model = AutoModelForCausalLM.from_pretrained(path, dtype=dtype).cuda().eval()
val = [json.loads(l) for l in open(os.path.join(os.environ["DATA_DIR"], "val.jsonl"))]
for task in ("prepare", "hint", "error_question", "free", "manipulation"):
    ex = next((r for r in val if r["task"] == task), None)
    if ex is None:  # never stop the notebook here: the GGUF cell comes next
        continue
    prompt = tok.apply_chat_template(ex["messages"][:-1], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    ids = tok(prompt, return_tensors="pt", add_special_tokens=False).to("cuda")
    out = model.generate(**ids, max_new_tokens=500 if task == "prepare" else 120, do_sample=False)
    print(f"===== {task}: {ex['messages'][-2]['content'][:120]}")
    print(tok.decode(out[0, ids["input_ids"].shape[1]:], skip_special_tokens=True))
del model; torch.cuda.empty_cache()"""


def gguf(keep_checkpoints):
    return f"""!git clone -q https://github.com/ggml-org/llama.cpp /kaggle/working/llama.cpp
!cd /kaggle/working/llama.cpp && git checkout -q {LLAMA_REF}
!pip install -q /kaggle/working/llama.cpp/gguf-py sentencepiece
!python /kaggle/working/llama.cpp/convert_hf_to_gguf.py /kaggle/working/merged --outtype q8_0 --outfile /kaggle/working/qwen35-tutor-Q8_0.gguf
# If the converter stops with an error about an MTP head, add --no-mtp to the line above.
!rm -rf /kaggle/working/llama.cpp{'' if keep_checkpoints else ' /kaggle/working/ckpt'}
!ls -lh /kaggle/working /kaggle/working/ckpt 2>/dev/null"""


FULL = [
    ("markdown", """# Santolina tutor: LoRA fine-tune of Qwen3.5-0.8B

Before running:
1. On the laptop: `uv run python laptop/build_tutor_sft.py`, then upload `data/processed/tutor_sft/`
   as a **Private** Kaggle dataset (M3Kang is research-only: never make it, or the model, public).
2. Notebook settings: **Accelerator GPU T4 x2**, **Internet on**, add that dataset as input.
3. Run the cells up to the **dry run** interactively (about 5 min). It checks memory and prints an
   upper bound for the full training time.
4. Then **Save Version → Save & Run All (Commit)**: the run continues with the browser closed (max 12 h)
   and `/kaggle/working/` is kept as the version's output
   (`adapter/`, `merged/`, `qwen35-tutor-Q8_0.gguf`).

Knobs (env vars, set in the CONFIG cell): `EPOCHS` (2), `LR` (2e-4), `LORA_R` (32),
`BATCH`/`GRAD_ACCUM` (4/4), `MAX_MINUTES` (time limit: stop, then merge and save as usual).
If the dry run runs out of memory: `BATCH=2 GRAD_ACCUM=8`. If the loss turns NaN on T4: `FP16=0`."""),
    ("code", INSTALL),
    ("code", """# CONFIG
import os
os.environ.update({"EPOCHS": "2", "LR": "2e-4", "LORA_R": "32", "BATCH": "4", "GRAD_ACCUM": "4"})"""),
    ("code", FIND),
    ("markdown", "## Dry run: 3 steps on the longest examples (memory check + ETA)"),
    ("code", """!DRY_RUN=1 torchrun --nproc_per_node {N_GPU} {SCRIPT}"""),
    ("markdown", "## Full training"),
    ("code", """!torchrun --nproc_per_node {N_GPU} {SCRIPT}"""),
    ("markdown", "## Sanity check: a few replies on validation problems (outputs stay in Kaggle)"),
    ("code", SANITY),
    ("markdown", "## Convert to GGUF Q8_0 for the board (llama.cpp at the commit pinned in config.env)"),
    ("code", gguf(keep_checkpoints=False)),
]

SMALL = [
    ("markdown", """# Santolina tutor: SHORT LoRA fine-tune of Qwen3.5-0.8B (~1.5 h)

Data: `data/processed/tutor_sft_small/` (built with `laptop/build_tutor_sft.py --allow-unjudged --lean
--sample 0.2 --out data/processed/tutor_sft_small`), uploaded as its own **Private** Kaggle dataset.
Attach ONLY that dataset, so the notebook finds the right `train_tutor.py`.

Settings: **GPU T4 x2**, **Internet on**. Then directly **Save Version → Save & Run All (Commit)**.

- `MAX_MINUTES=70`: training stops cleanly after 70 min from its start whatever happens, then the
  script merges and saves, so the run ends normally and Kaggle keeps the output.
- `EVALS=4`: 4 evals, each saving a LoRA checkpoint in `ckpt/` (kept in the output). The best one by
  validation loss is merged into `merged/` and converted to `qwen35-tutor-Q8_0.gguf`."""),
    ("code", INSTALL),
    ("code", """# CONFIG
import os
os.environ.update({"EPOCHS": "1", "LR": "2e-4", "LORA_R": "32", "BATCH": "4", "GRAD_ACCUM": "2",
                   "MAX_MINUTES": "70", "EVALS": "4", "FINAL_EVAL_ROWS": "0"})"""),
    ("code", FIND),
    ("markdown", "## Training (stops by itself after MAX_MINUTES)"),
    ("code", """!torchrun --nproc_per_node {N_GPU} {SCRIPT}"""),
    ("markdown", "## Sanity check: a few replies on validation problems (outputs stay in Kaggle)"),
    ("code", SANITY),
    ("markdown", "## Convert to GGUF Q8_0 for the board (llama.cpp at the commit pinned in config.env)"),
    ("code", gguf(keep_checkpoints=True)),
]


def write(cells, name):
    nb = {
        "cells": [
            {"cell_type": t, "metadata": {}, "source": src.splitlines(keepends=True),
             **({"execution_count": None, "outputs": []} if t == "code" else {})}
            for t, src in cells
        ],
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                     "language_info": {"name": "python"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    out = Path(__file__).with_name(name)
    out.write_text(json.dumps(nb, indent=1))
    print("wrote", out)


write(FULL, "tutor_finetune.ipynb")
write(SMALL, "tutor_finetune_small.ipynb")
