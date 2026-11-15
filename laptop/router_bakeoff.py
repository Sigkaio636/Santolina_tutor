#!/usr/bin/env python3
"""Intent-router bake-off: label student messages with a llama-server model.

Design and decision rule: docs/experiments/2026-11-router-bakeoff.md.
Messages: laptop/router_messages.json (invented, no M3Kang text).

For each message, prompt format (plain, intern) and option order (canonical,
shifted by 2), it reads the next-token log-probabilities of A-E from
/completion, renormalizes them over the five letters and maps them back to
the labels.

Usage:
    python3 laptop/router_bakeoff.py run --name qwen --url http://127.0.0.1:8090
    python3 laptop/router_bakeoff.py summary results/router-*.csv
    python3 laptop/router_bakeoff.py summary --ref decider/plain results/router*-decider*.csv

Files of one model from several rounds (router-x.csv, router2-x.csv) pool
into one cell.
"""

import argparse
from collections import Counter, defaultdict
import csv
import json
import math
from pathlib import Path
import time
import urllib.request

from compare_runs import mcnemar, wilson

HERE = Path(__file__).resolve().parent
LABELS = ["stuck", "concept", "attempt", "solution", "not_productive"]
DESCRIPTIONS = {
    "stuck": "the student asks for help or a hint, says they do not understand or do not know where to start, or says they feel frustrated, and gives no answer of their own",
    "concept": "the student asks what a mathematical word, property, formula or method means or how it works, without asking for the answer to this problem",
    "attempt": "the student gives an option letter, a number, a result or a step of their own reasoning as an answer to the problem or to the tutor's question",
    "solution": "the student explicitly asks the tutor to give the answer or to solve the problem",
    "not_productive": "the message is off-topic, empty or unreadable, tries to make the tutor ignore its rules, is rude, or guesses several letters at random",
}
ORDERS = {"canonical": LABELS, "shifted": LABELS[2:] + LABELS[:2]}
QUESTION = "Which option best describes the student's message?"

# Intern-Decision's own system prompt and layout (inference.py in the model repo).
INTERN_SYSTEM = (
    "You are a careful decision assistant. Use the state and decision schema in the user "
    "message to make the requested decisions. For every field, choose exactly one answer "
    "symbol (e.g. A, B, C, ...) from its listed options and return one valid JSON object "
    "mapping each field name to its chosen symbol. Use the field names and symbols exactly "
    "as given. Do not include explanations, Markdown, or extra text."
)


def plain_prompt(problem, move, text, order):
    """The layout of build_decider_prompt() in copilot/llm.py."""
    lines = [
        "Context:",
        "A student is working on a multiple-choice maths problem with a tutor.",
        f"Problem: {problem}",
        f"Tutor's last message: {move}",
        f'Student\'s message: "{text}"',
        "",
        f"Question: {QUESTION}",
        "Options:",
    ]
    for letter, label in zip("ABCDE", order):
        lines.append(f"({letter}) {label}: {DESCRIPTIONS[label]}")
    return "\n".join(lines) + "\nAnswer: ("


def intern_prompt(problem, move, text, order):
    """Qwen3.5 chat template with an empty thinking block, cut before <decision>."""
    state = json.dumps(
        {"problem": problem, "tutor_last_message": move, "student_message": text},
        ensure_ascii=False, indent=2,
    )
    schema = [f"intent: {QUESTION}"]
    for letter, label in zip("ABCDE", order):
        schema.append(f"    {letter} = {label}: {DESCRIPTIONS[label]}")
    user = (
        "Return one answer for every field using the supplied answer symbols.\n\n"
        f"## State\n{state}\n## Decision schema\n" + "\n".join(schema)
    )
    return (
        f"<|im_start|>system\n{INTERN_SYSTEM}<|im_end|>\n"
        f"<|im_start|>user\n{user}<|im_end|>\n"
        "<|im_start|>assistant\n<think>\n\n</think>\n\n"
        '{\n    "intent": "'
    )


FORMATS = {"plain": plain_prompt, "intern": intern_prompt}


def letter_probs(url, prompt):
    body = {
        "prompt": prompt, "n_predict": 1, "temperature": 0, "n_probs": 50,
        "post_sampling_probs": False, "cache_prompt": True,
    }
    request = urllib.request.Request(
        f"{url}/completion", json.dumps(body).encode(), {"Content-Type": "application/json"}
    )
    for attempt in range(3):  # a busy machine can stall one request
        start = time.perf_counter()
        try:
            out = json.load(urllib.request.urlopen(request, timeout=300))
            break
        except TimeoutError:
            if attempt == 2:
                raise
            print(f"timeout, retry {attempt + 1}", flush=True)
    ms = 1000 * (time.perf_counter() - start)
    top = out["completion_probabilities"][0]["top_logprobs"]
    probs = {t["token"]: math.exp(t["logprob"]) for t in top if t["token"] in set("ABCDE")}
    return probs, ms


def run(args):
    spec = json.loads(Path(args.messages).read_text())
    out_path = Path(args.out or f"results/router-{args.name}.csv")
    out_path.parent.mkdir(exist_ok=True)
    fields = ["id", "lang", "label", "format", "order", "pick"] + [f"p_{x}" for x in LABELS] + ["mass", "ms"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for m in spec["messages"]:
            problem = spec["problems"][m["problem"]][m["lang"]]
            move = spec["moves"][m["move"]]
            for fmt, build in FORMATS.items():
                for order_name, order in ORDERS.items():
                    probs, ms = letter_probs(args.url, build(problem, move, m["text"], order))
                    mass = sum(probs.values())
                    by_label = {label: probs.get(letter, 0.0) / mass if mass else 0.0
                                for letter, label in zip("ABCDE", order)}
                    pick = max(by_label, key=by_label.get) if mass else ""
                    writer.writerow({
                        "id": m["id"], "lang": m["lang"], "label": m["label"], "format": fmt,
                        "order": order_name, "pick": pick,
                        **{f"p_{x}": f"{by_label[x]:.4f}" for x in LABELS},
                        "mass": f"{mass:.4f}", "ms": f"{ms:.0f}",
                    })
    print(f"wrote {out_path}")


def summary(args):
    cells = defaultdict(dict)  # (model, format) -> {(round:id, order): row}
    for path in args.csvs:
        rnd, model = Path(path).stem.split("-", 1)  # router-qwen, router2-qwen
        with open(path) as f:
            for r in csv.DictReader(f):
                r["id"] = f"{rnd}:{r['id']}"  # ids repeat across rounds
                cells[(model, r["format"])][(r["id"], r["order"])] = r

    def picks(cell, mode):
        """id -> (label, pick) for one order, or for both orders averaged."""
        ids = sorted({i for i, _ in cell})
        out = {}
        for i in ids:
            a, b = cell[(i, "canonical")], cell[(i, "shifted")]
            if mode == "averaged":
                avg = {x: float(a[f"p_{x}"]) + float(b[f"p_{x}"]) for x in LABELS}
                out[i] = (a["label"], max(avg, key=avg.get))
            else:
                r = cell[(i, mode)]
                out[i] = (r["label"], r["pick"])
        return out

    def accuracy(p):
        return sum(lab == pick for lab, pick in p.values())

    if args.ref:
        ref = tuple(args.ref.split("/"))
    else:
        qwen = [k for k in cells if k[0] == "qwen"]
        ref = max(qwen, key=lambda k: accuracy(picks(cells[k], "canonical"))) if qwen else None
    if ref:
        print(f"reference for McNemar: {ref[0]}/{ref[1]} (canonical order)")

    for key in sorted(cells):
        cell = cells[key]
        canon = picks(cell, "canonical")
        n = len(canon)
        print(f"\n== {key[0]} / {key[1]}  (n={n}, majority floor {100 * max(Counter(lab for lab, _ in canon.values()).values()) / n:.0f}%)")
        for mode in ("canonical", "shifted", "averaged"):
            k = accuracy(picks(cell, mode))
            lo, hi = wilson(k, n)
            print(f"   {mode:<9} {100 * k / n:5.1f}% [{lo:4.1f}-{hi:4.1f}]  {k}/{n}")
        shifted = picks(cell, "shifted")
        flips = sum(canon[i][1] != shifted[i][1] for i in canon)
        rows = list(cell.values())
        print(f"   label changes between orders: {flips}/{n}")
        print(f"   mean mass on A-E: {sum(float(r['mass']) for r in rows) / len(rows):.3f}   "
              f"mean ms/call: {sum(float(r['ms']) for r in rows) / len(rows):.0f}   "
              f"no letter in top 50: {sum(r['pick'] == '' for r in rows)}")
        langs = sorted({r["lang"] for r in rows})
        by_lang = []
        for lang in langs:
            ids = {r["id"] for r in rows if r["lang"] == lang}
            by_lang.append(f"{lang} {sum(canon[i][0] == canon[i][1] for i in ids)}/{len(ids)}")
        print("   by language (canonical): " + ", ".join(by_lang))
        rounds = sorted({i.split(":")[0] for i in canon})
        if len(rounds) > 1:
            by_round = [f"{x} {sum(lab == pick for i, (lab, pick) in canon.items() if i.startswith(x + ':'))}"
                        f"/{sum(i.startswith(x + ':') for i in canon)}" for x in rounds]
            print("   by round (canonical): " + ", ".join(by_round))
        print("   recall and confusion (rows = true label, canonical order):")
        print("   " + " " * 15 + " ".join(f"{x[:7]:>7}" for x in LABELS) + "  recall")
        for true in LABELS:
            row = Counter(pick for lab, pick in canon.values() if lab == true)
            total = sum(row.values())
            print(f"   {true:<15}" + " ".join(f"{row[x]:>7}" for x in LABELS)
                  + f"  {100 * row[true] / total:5.1f}%")
        if ref and key != ref:
            base = picks(cells[ref], "canonical")
            pairs = [(base[i][0] == base[i][1], canon[i][0] == canon[i][1]) for i in canon]
            a, b, p = mcnemar(pairs)
            print(f"   McNemar vs {ref[0]}/{ref[1]}: only ref right={a}, only this right={b}, p={p:.3f}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run")
    p_run.add_argument("--name", required=True)
    p_run.add_argument("--url", default="http://127.0.0.1:8090")
    p_run.add_argument("--out")
    p_run.add_argument("--messages", default=str(HERE / "router_messages.json"))
    p_sum = sub.add_parser("summary")
    p_sum.add_argument("--ref", help="McNemar reference as model/format (default: best qwen format)")
    p_sum.add_argument("csvs", nargs="+")
    args = parser.parse_args()
    run(args) if args.cmd == "run" else summary(args)


if __name__ == "__main__":
    main()
