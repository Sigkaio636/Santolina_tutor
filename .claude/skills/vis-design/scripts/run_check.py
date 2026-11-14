#!/usr/bin/env python3
"""Stage-4 validation: run a generated chart script headless and report what it produced.

    python3 run_check.py chart.py --library altair|matplotlib|plotly --out-dir OUT [--data DATA]
                        [--streamlit app.py] [--timeout 120] [--no-inspectors]

Steps: preflight imports → run the script with --out-dir (and --data) → list outputs with
sizes → run the sibling vis-value-critique inspectors when installed (rule findings with
severity) → run inspect_image.py on the first PNG → Streamlit AppTest smoke test when
asked. Prints JSON; `ok` is false when the script fails or a critical deterministic finding
blocks acceptance (EXP-01/02/03/08/11, COL-02/05).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from find_sibling import find as find_sibling  # noqa: E402

BLOCKING = {"EXP-01", "EXP-02", "EXP-03", "EXP-08", "EXP-11", "COL-02", "COL-05", "EXP-05", "EXP-06", "EXP-09"}


def parse_json_tail(text: str):
    """The inspectors exec the chart script, whose prints precede the JSON report."""
    for i, line in enumerate(text.splitlines()):
        if line.startswith("{"):
            try:
                return json.loads("\n".join(text.splitlines()[i:]))
            except json.JSONDecodeError:
                continue
    raise json.JSONDecodeError("no JSON object found", text, 0)


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def run(cmd: list[str], timeout: int, cwd: str | None = None) -> dict:
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return {"cmd": " ".join(cmd), "returncode": p.returncode, "stdout": p.stdout,
                "stderr": p.stderr[-4000:], "seconds": round(time.time() - t0, 2)}
    except subprocess.TimeoutExpired:
        return {"cmd": " ".join(cmd), "returncode": -1, "stdout": "", "stderr": f"timeout after {timeout}s",
                "seconds": timeout}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script")
    ap.add_argument("--library", required=True, choices=["altair", "matplotlib", "plotly"])
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--data")
    ap.add_argument("--streamlit")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--no-inspectors", action="store_true")
    args = ap.parse_args()

    out = {"script": os.path.abspath(args.script), "library": args.library, "ok": True, "steps": [],
           "outputs": [], "findings": [], "blocking": [], "warnings": []}
    need = {"altair": ["altair", "pandas"], "matplotlib": ["matplotlib", "pandas"], "plotly": ["plotly", "pandas"]}[args.library]
    missing = [m for m in need if not module_available(m)]
    renderers = {"altair": "vl_convert", "plotly": "kaleido", "matplotlib": None}[args.library]
    out["environment"] = {"missing_modules": missing,
                          "png_renderer": (module_available(renderers) if renderers else True),
                          "streamlit": module_available("streamlit")}
    if missing:
        out["ok"] = False
        out["reason"] = f"missing modules: {missing}"
        print(json.dumps(out, indent=2))
        return
    args.out_dir = os.path.abspath(args.out_dir)
    if args.data:
        args.data = os.path.abspath(args.data)
    os.makedirs(args.out_dir, exist_ok=True)
    cmd = [sys.executable, args.script, "--out-dir", args.out_dir]
    if args.data:
        cmd += ["--data", args.data]
    env_before = set(os.listdir(args.out_dir))
    res = run(cmd, args.timeout, cwd=os.path.dirname(os.path.abspath(args.script)))
    res["step"] = "run script"
    out["steps"].append(dict(res, stdout=res["stdout"][-4000:]))
    if res["returncode"] != 0:
        out["ok"] = False
        out["reason"] = "script failed"
    for f in sorted(set(os.listdir(args.out_dir)) - env_before | {f for f in os.listdir(args.out_dir)}):
        p = os.path.join(args.out_dir, f)
        if os.path.isfile(p):
            out["outputs"].append({"file": p, "bytes": os.path.getsize(p)})
    # prefer the files this script wrote (same stem as the script), newest first, so a shared
    # output folder with several charts does not make the inspector read another chart's spec
    stem = os.path.splitext(os.path.basename(args.script))[0]

    def prefer(files):
        def key(f):
            base = os.path.basename(f)
            exact = os.path.splitext(base)[0] == stem or base.startswith(stem + ".")
            return (not exact, not base.startswith(stem), -os.path.getmtime(f))
        return sorted(files, key=key)

    pngs = prefer([o["file"] for o in out["outputs"] if o["file"].lower().endswith(".png")])
    if not pngs:
        out["warnings"].append("no PNG produced: render the HTML in a browser and screenshot it for stage-3 validation")
    sib = None if args.no_inspectors else find_sibling()
    out["sibling"] = sib or "absent"
    if sib and res["returncode"] == 0:
        insp = {"altair": "inspect_vegalite.py", "matplotlib": "inspect_matplotlib.py", "plotly": "inspect_plotly.py"}[args.library]
        target = args.script
        # the inspectors understand .py for matplotlib/plotly; for altair prefer a saved spec
        if args.library == "altair":
            specs = prefer([o["file"] for o in out["outputs"] if o["file"].endswith(".vl.json")])
            htmls = prefer([o["file"] for o in out["outputs"] if o["file"].endswith(".html")])
            target = (specs or htmls or [args.script])[0]
        icmd = [sys.executable, os.path.join(sib, "scripts", insp), target]
        if args.library == "matplotlib":
            icmd += ["--out-dir", os.path.join(args.out_dir, "inspect")]
        ires = run(icmd, args.timeout)
        ires["step"] = f"sibling {insp}"
        out["steps"].append({k: v for k, v in ires.items() if k != "stdout"})
        try:
            rep = parse_json_tail(ires["stdout"])
            out["findings"] = [{"rule": f["rule"], "severity": f["severity"], "message": f["message"],
                                "evidence": f.get("evidence", ""), "kind": f.get("kind")} for f in rep.get("findings", [])]
            out["blocking"] = [f for f in out["findings"] if f["rule"] in BLOCKING and f["severity"] == "crit" and f.get("kind") == "DET"]
            out["inspector_warnings"] = rep.get("warnings", [])
            if any("No figures" in w or "raised" in w or "No Altair chart" in w or "No plotly Figure" in w
                   for w in out["inspector_warnings"]):
                out["warnings"].append("the inspector could not execute the chart script (it runs it with cwd = "
                                       "the script folder and its own argv): its empty findings are NOT a clean bill; "
                                       "make DATA_PATH script-relative or absolute")
                out["inspector_ran_script"] = False
            else:
                out["inspector_ran_script"] = True
            if out["blocking"]:
                out["ok"] = False
                out["reason"] = "blocking deterministic findings"
        except (json.JSONDecodeError, KeyError):
            out["warnings"].append("could not parse inspector output")
        if pngs:
            icmd = [sys.executable, os.path.join(sib, "scripts", "inspect_image.py"), pngs[0], "--out-dir", os.path.join(args.out_dir, "inspect")]
            ires = run(icmd, args.timeout)
            try:
                rep = parse_json_tail(ires["stdout"])
                out["image_artifacts"] = rep.get("artifacts", [])
                out["image_findings"] = [{"rule": f["rule"], "severity": f["severity"], "message": f["message"]} for f in rep.get("findings", [])]
            except json.JSONDecodeError:
                out["warnings"].append("inspect_image failed")
    if args.streamlit:
        if module_available("streamlit"):
            code = ("from streamlit.testing.v1 import AppTest\n"
                    f"at = AppTest.from_file({args.streamlit!r}, default_timeout=60).run()\n"
                    "import json; print(json.dumps({'exceptions': [str(e) for e in at.exception], 'n_elements': len(at.main)}))")
            sres = run([sys.executable, "-c", code], args.timeout, cwd=os.path.dirname(os.path.abspath(args.streamlit)))
            sres["step"] = "streamlit AppTest"
            out["steps"].append(sres)
            try:
                st = json.loads(sres["stdout"].strip().splitlines()[-1])
                out["streamlit"] = st
                if st.get("exceptions"):
                    out["ok"] = False
                    out["reason"] = "streamlit app raised"
            except (json.JSONDecodeError, IndexError):
                out["warnings"].append("streamlit AppTest produced no result")
        else:
            out["warnings"].append("streamlit not installed: app not smoke-tested")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
