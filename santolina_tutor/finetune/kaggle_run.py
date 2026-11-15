"""Run a fine-tuning job on Kaggle: private dataset up, script kernel, results down.

Needs the Kaggle CLI token in ~/.kaggle/access_token (never in the repo).

    uv run python -m santolina_tutor.finetune.kaggle_run upload --data data/finetune/letters
    uv run python -m santolina_tutor.finetune.kaggle_run push --script letters
    uv run python -m santolina_tutor.finetune.kaggle_run status --script letters
    uv run python -m santolina_tutor.finetune.kaggle_run output --script letters --out data/kaggle_out/letters

--name gives a script its own kernel (santolina-<name>), so two runs don't overwrite
each other; --set key=value (value as JSON) overrides one CFG entry of the script:

    ... push --script programs --name programs-rag --set rag_k=1

The dataset is derived from M3Kang (research use only). The Kaggle CLI creates
datasets private unless told otherwise, and this script never asks for public.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KAGGLE = ["uvx", "--python", "3.12", "--from", "kaggle", "--with", "six", "kaggle"]
DATASET_SLUG = "santolina-m3kang-finetune"
OVERRIDES_LINE = re.compile(r"^CFG_OVERRIDES = \{\}.*$", re.MULTILINE)
STAGING = os.path.join("data", "kaggle_staging")  # under data/, so Git ignores it


def kaggle(*args, check=True):
    print("$ kaggle", " ".join(args), file=sys.stderr)
    run = subprocess.run(KAGGLE + list(args), capture_output=True, text=True, check=False)
    out = (run.stdout + run.stderr).strip()
    if out:
        print(out, file=sys.stderr)
    if check and run.returncode != 0:
        sys.exit(f"kaggle failed with exit {run.returncode}")
    return run.returncode, out


def username():
    _, out = kaggle("config", "view")
    for line in out.splitlines():
        if line.strip().startswith("- username:"):
            return line.split(":", 1)[1].strip()
    sys.exit("no Kaggle username in `kaggle config view`")


def upload(args):
    user = username()
    stage = os.path.join(STAGING, "dataset")
    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(stage)
    for root, dirs, files in os.walk(args.data):  # keep sub-folders, e.g. letters/train.jsonl
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in files:
            src = os.path.join(root, name)
            dst = os.path.join(stage, os.path.relpath(src, os.path.dirname(args.data.rstrip("/"))))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
    meta = {"title": "Santolina M3Kang finetune (private)",  # Kaggle allows 6-50 characters
            "id": f"{user}/{DATASET_SLUG}", "licenses": [{"name": "other"}]}
    with open(os.path.join(stage, "dataset-metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)
    code, out = kaggle("datasets", "status", f"{user}/{DATASET_SLUG}", check=False)
    if code == 0 and "ready" in out.lower():
        kaggle("datasets", "version", "-p", stage, "-m", args.message, "--dir-mode", "zip")
    else:  # `datasets create` is private by default; never pass -u/--public here
        kaggle("datasets", "create", "-p", stage, "--dir-mode", "zip")


def kernel_name(args):
    return args.name or args.script


def push(args):
    user = username()
    stage = os.path.join(STAGING, f"kernel-{kernel_name(args)}")
    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(stage)
    code_file = f"train_{args.script}.py"
    with open(os.path.join(HERE, "kaggle", code_file)) as f:
        code = f.read()
    if args.set:
        overrides = {}
        for item in args.set:
            key, _, value = item.partition("=")
            overrides[key] = json.loads(value)
        if not OVERRIDES_LINE.search(code):
            sys.exit(f"{code_file} has no 'CFG_OVERRIDES = {{}}' line for --set")
        # repr, not json.dumps: the line is Python source, where JSON's true/null are not defined
        code = OVERRIDES_LINE.sub(lambda _: f"CFG_OVERRIDES = {overrides!r}", code, count=1)
    with open(os.path.join(stage, code_file), "w") as f:
        f.write(code)
    name = kernel_name(args)
    meta = {"id": f"{user}/santolina-{name}", "title": f"santolina-{name}",
            "code_file": code_file, "language": "python", "kernel_type": "script",
            "is_private": True, "enable_gpu": True, "enable_internet": True,
            "machine_shape": "NvidiaTeslaT4",
            "dataset_sources": [f"{user}/{DATASET_SLUG}"], "competition_sources": [],
            "kernel_sources": [f"{user}/santolina-{k}" for k in args.source]}
    with open(os.path.join(stage, "kernel-metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)
    kaggle("kernels", "push", "-p", stage, "--accelerator", "NvidiaTeslaT4")


def status(args):
    kaggle("kernels", "status", f"{username()}/santolina-{kernel_name(args)}")


def output(args):
    os.makedirs(args.out, exist_ok=True)
    extra = ["--file-pattern", args.pattern] if args.pattern else []
    kaggle("kernels", "output", f"{username()}/santolina-{kernel_name(args)}", "-p", args.out, *extra)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("upload", help="create or update the private dataset")
    p.add_argument("--data", required=True, help="folder to upload, e.g. data/finetune/letters")
    p.add_argument("--message", default="update")
    p.set_defaults(fn=upload)
    for name, fn in (("push", push), ("status", status), ("output", output)):
        p = sub.add_parser(name)
        p.add_argument("--script", required=True, help="letters -> kaggle/train_letters.py")
        p.add_argument("--name", default="", help="kernel santolina-<name> (default: the script)")
        if name == "push":
            p.add_argument("--set", action="append", default=[], metavar="KEY=JSON",
                           help="override one CFG entry, e.g. rag_k=1")
            p.add_argument("--source", action="append", default=[], metavar="NAME",
                           help="attach the output of kernel santolina-<NAME> as input")
        if name == "output":
            p.add_argument("--out", required=True, help="local folder under data/ (Git-ignored), e.g. data/kaggle_out/letters")
            p.add_argument("--pattern", default="", help="regex of files to fetch, e.g. 'metrics|val_probs'")
        p.set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
