"""Convert a merged fine-tuned model from another kernel's output to GGUF and quantize it.

Runs as a Kaggle script kernel (santolina_tutor/finetune/kaggle_run.py push --script convert
--source <kernel>). It finds merged/ under /kaggle/input, converts it with llama.cpp at the
board's commit (--model-name keeps the SHA256 independent of folder names, --no-mtp because
the merged model has no MTP head) and writes one GGUF per quantization with its SHA256.
"""
import glob
import os
import subprocess
import sys

CFG = {"name": "noema-2b-programs", "quants": ["Q4_K_M", "Q4_0", "Q3_K_M"],
       "llama_cpp": "2cbe0ec429b849a88664e0f62388fc92a5abd699"}
CFG_OVERRIDES = {}  # set by kaggle_run push --set
CFG.update(CFG_OVERRIDES)
OUT = "/kaggle/working"


def sh(cmd, cwd=None):
    print("$", cmd, flush=True)
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)


merged = [os.path.dirname(p) for p in glob.glob("/kaggle/input/**/merged/config.json", recursive=True)]
assert len(merged) == 1, f"expected one merged/ under /kaggle/input, found {merged}"
src = "/kaggle/temp/llama.cpp"
sh(f"git clone -q https://github.com/ggml-org/llama.cpp {src}")
sh(f"git checkout -q {CFG['llama_cpp']}", cwd=src)
sh(f"{sys.executable} -m pip install -q --no-deps {src}/gguf-py sentencepiece")
f16 = f"/kaggle/temp/{CFG['name']}-f16.gguf"
sh(f"{sys.executable} {src}/convert_hf_to_gguf.py {merged[0]} --outtype f16 "
   f"--model-name {CFG['name']} --outfile {f16} --no-mtp")
sh("cmake -B build -DGGML_CUDA=OFF -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF > /dev/null", cwd=src)
sh("cmake --build build --target llama-quantize -j4 > /dev/null", cwd=src)
for quant in CFG["quants"]:
    final = f"{OUT}/{CFG['name']}-{quant}.gguf"
    sh(f"{src}/build/bin/llama-quantize {f16} {final} {quant} > /dev/null")
    sh(f"sha256sum {final} > {final}.sha256 && cat {final}.sha256")
os.remove(f16)
