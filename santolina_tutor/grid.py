"""Laptop grid: which way of asking the board's model beats the letter prior.

Runs the same GGUF and llama.cpp commit as the board, so the answers match;
only the speed differs. Board time is simulated from token counts with the
board's measured speeds (11 tokens/s read, 5.5 tokens/s written).

    uv run --offline python -m santolina_tutor.grid --config letter --name letter-08b
    uv run --offline python -m santolina_tutor.grid --config cot --port 8081 --cap 220

Rows go to data/grid/<name>.jsonl (git-ignored: they carry M3Kang ids and labels).
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import random
import re

from copilot.client import post
from copilot.llm import SYSTEM, format_problem
from copilot.prior import best
from copilot.program_head import (
    ASK_LETTER,
    code_from_reply,
    judge,
    letter_turn,
    matches,
    program_turn,
    translate,
)

LETTERS = "ABCDE"
READ_TPS, WRITE_TPS, LIMIT = 11.0, 5.5, 55.0
COT_SYSTEM = ("Solve the math problem. Write only the key calculations, one short line each. "
              "Finish with 'Answer:' and the letter of the correct option.")
NUMBER = re.compile(r"-?\d+(?:[.,]\d+)?(?:/\d+)?")


def subset(path, size, seed, language="eng"):
    with open(path, encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle]
    rows = [r for r in rows if r["language"] == language and r.get("options")]
    rows.sort(key=lambda r: r["id"])
    random.Random(seed).shuffle(rows)
    return rows[:size]


def letter_probs(choice):
    """Probabilities of A to E from the first token's top logprobs, renormalized."""
    top = choice["logprobs"]["content"][0]["top_logprobs"]
    logp = {t["token"].strip(): t["logprob"] for t in top if t["token"].strip() in LETTERS and t["token"].strip()}
    floor = min(logp.values(), default=-20.0) - 2.0
    weights = {letter: math.exp(logp.get(letter, floor)) for letter in LETTERS}
    total = sum(weights.values())
    return {letter: round(w / total, 4) for letter, w in weights.items()}


def ask_letter(base, messages):
    response = post(base + "/v1/chat/completions", {
        "messages": messages, "grammar": "root ::= [A-E]", "max_tokens": 1, "temperature": 0,
        "seed": 42, "cache_prompt": True, "logprobs": True, "top_logprobs": 20,
        "chat_template_kwargs": {"enable_thinking": False}}, timeout=600)
    choice = response["choices"][0]
    return choice["message"]["content"].strip(), letter_probs(choice), response.get("timings", {})


def last_option_value(text, options):
    """The letter of the last number in the text that equals exactly one option."""
    for found in reversed(NUMBER.findall(text.replace("−", "-"))):
        hits = matches(found.replace(",", "."), options)
        if len(hits) == 1:
            return hits[0]
    return None


def run_one(problem, config, base, cap, read_tps=READ_TPS, write_tps=WRITE_TPS, program_prompt="zero_shot",
            translate_cat=False, extra_seconds=0.0):
    user = format_problem(problem) + "\nAnswer:"
    row = {"id": problem["id"], "language": problem["language"], "level": problem["level"],
           "label": problem["label"], "config": config,
           "text_only": problem.get("text_only")}
    if config == "letter":
        letter, probs, timings = ask_letter(base, [{"role": "system", "content": SYSTEM},
                                                   {"role": "user", "content": user}])
        row.update(answer=letter, probs=probs, prompt_n=timings.get("prompt_n", 0), predicted_n=1,
                   board_seconds=round(timings.get("prompt_n", 0) / READ_TPS + 1, 1))
        return row
    if config == "program":  # exactly the board's SOLVER=program requests (copilot/program_head.py)
        # the system prompt and examples are cached after warm-up, so only the problem's own
        # tokens cost reading time. Board deadline: 57 s; 1 s kept for running the program.
        spent = extra_seconds  # board seconds before the program request (e.g. a translation)
        if translate_cat and problem["language"] == "cat":
            n_text = len(post(base + "/tokenize", {"content": problem["text"]}, timeout=60)["tokens"])
            english, t = translate(base, problem["text"], int(n_text * 1.5) + 10)
            spent = (n_text + 15) / read_tps + t.get("predicted_n", 0) / write_tps
            problem = {**problem, "text": english}
            row.update(translation_written=t.get("predicted_n", 0))
        tokens = len(post(base + "/tokenize", {"content": format_problem(problem)}, timeout=60)["tokens"]) + 25
        budget = int(min(cap, max(0.0, LIMIT + 2 - spent - tokens / read_tps - 1) * write_tps))
        prompt, raw, timings = program_turn(base, problem, max(budget, 1), prompt=program_prompt)
        program = code_from_reply(raw)
        result = judge(program, problem.get("options") or {})
        used = spent + tokens / read_tps + timings.get("predicted_n", 0) / write_tps + 0.5
        if not result["letter"]:  # the board asks the letter only if 30 tokens of reading still fit
            follow, second = letter_turn(base, prompt, raw)
            fits = used + 30 / read_tps + 1.0 <= LIMIT + 2
            row.update(follow_letter=follow if fits else "", follow_prompt_n=second.get("prompt_n", 0),
                       follow_fits=fits, prior=best(problem))
        row.update(answer=result["letter"] or "", value=str(result["value"])[:60], error=result["error"],
                   program=program, budget=budget, prompt_n=tokens, predicted_n=timings.get("predicted_n", 0),
                   board_seconds=round(used + 0.5, 1))
        return row
    # cot / think: write some work inside the time budget, then one forced letter
    system = COT_SYSTEM if config == "cot" else SYSTEM
    question = format_problem(problem)
    messages = [{"role": "system", "content": system}, {"role": "user", "content": question}]
    tokens = len(post(base + "/tokenize", {"content": system + question}, timeout=60)["tokens"]) + 25
    budget = int(min(cap, max(0.0, LIMIT - 4 - tokens / read_tps) * write_tps))
    text, reasoning, first = "", "", {}
    if budget >= 20:
        response = post(base + "/v1/chat/completions", {
            "messages": messages, "max_tokens": budget, "temperature": 0, "seed": 42,
            "cache_prompt": True}, timeout=600)
        message = response["choices"][0]["message"]
        text, reasoning = message.get("content") or "", message.get("reasoning_content") or ""
        first = response.get("timings", {})
    work = text or reasoning
    follow = messages + ([{"role": "assistant", "content": work}] if work else []) + \
        [{"role": "user", "content": ASK_LETTER}]
    letter, probs, second = ask_letter(base, follow)
    # the board has one slot, so the second call only reads the short follow-up question
    seconds = (tokens + 20) / read_tps + first.get("predicted_n", 0) / write_tps + 1
    row.update(answer=letter, probs=probs, text=text, reasoning=reasoning, budget=budget,
               value_letter=last_option_value(reasoning + "\n" + text, problem["options"]),
               prompt_n=first.get("prompt_n", 0) + second.get("prompt_n", 0),
               predicted_n=first.get("predicted_n", 0), board_seconds=round(seconds, 1))
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--config", choices=["letter", "cot", "think", "program"], required=True)
    parser.add_argument("--name")
    parser.add_argument("--input", default="claude_workspace/m3kang_ocr/train.jsonl")
    parser.add_argument("--language", default="eng")
    parser.add_argument("--size", type=int, default=300)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--cap", type=int, default=220, help="most tokens of written work")
    parser.add_argument("--prompt", default="zero_shot", choices=["zero_shot", "tuned"],
                        help="program: the untuned prompt with examples, or the fine-tuned one")
    parser.add_argument("--translate", action="store_true",
                        help="program: translate Catalan statements to English first, inside the time budget")
    parser.add_argument("--extra-seconds", type=float, default=0.0,
                        help="program: board seconds spent before the program request, e.g. NMT translation")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--read-tps", type=float, default=READ_TPS, help="board tokens/s read")
    parser.add_argument("--write-tps", type=float, default=WRITE_TPS, help="board tokens/s written")
    args = parser.parse_args()
    base = f"http://127.0.0.1:{args.port}"
    problems = subset(args.input, args.size, args.seed, args.language)
    out = Path("data/grid") / f"{args.name or args.config}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(args.workers) as pool:
        rows = list(pool.map(lambda p: run_one(p, args.config, base, args.cap, args.read_tps, args.write_tps, args.prompt,
                                                      args.translate, args.extra_seconds), problems))
    with open(out, "w", encoding="utf-8") as handle:
        handle.writelines(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    n = len(rows)
    correct = sum(r["answer"] == r["label"] for r in rows)
    times = sorted(r["board_seconds"] for r in rows)
    print(f"{out}: {correct}/{n} = {correct / n:.3f}  board s: median {times[n // 2]}, "
          f"p90 {times[int(n * 0.9)]}, max {times[-1]}")
    print("  answers:", {x: sum(r["answer"] == x for r in rows) for x in LETTERS},
          "none:", sum(not r["answer"] for r in rows))
    if rows and rows[0]["config"] == "program":
        ran = [r for r in rows if not r["error"]]
        hit = [r for r in rows if r["answer"]]
        print(f"  programs ran: {len(ran)}/{n}, matched an option: {len(hit)}, "
              f"correct: {sum(r['answer'] == r['label'] for r in hit)}, wrong: "
              f"{sum(r['answer'] != r['label'] for r in hit)}, unanswered: {n - len(hit)}")
        follow = [r for r in rows if r.get("follow_letter")]
        if follow:
            fixed = sum((r["answer"] or r.get("follow_letter") or r.get("prior")) == r["label"] for r in rows)
            print(f"  letter asked in time: {len(follow)}, prior used: "
                  f"{sum(not r['answer'] and not r.get('follow_letter') for r in rows)}")
            print(f"  follow-up letter: {sum(r['follow_letter'] == r['label'] for r in follow)}/{len(follow)} "
                  f"right; program then follow-up: {fixed}/{n}; follow-up tokens read, median "
                  f"{sorted(r['follow_prompt_n'] for r in follow)[len(follow) // 2]}")
        print("  errors:", dict(sorted(Counter((r["error"] or "")[:30] for r in rows if r["error"]).items())))
    if rows and "value_letter" in rows[0]:
        hit = [r for r in rows if r["value_letter"]]
        print(f"  last matching value: {sum(r['value_letter'] == r['label'] for r in hit)}/{len(hit)} answered")


if __name__ == "__main__":
    main()
