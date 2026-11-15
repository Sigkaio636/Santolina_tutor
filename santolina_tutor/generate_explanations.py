"""Generate tutoring data (hints, step-by-step solutions) for M3Kang problems with Helmcode models.

    uv run python -m santolina_tutor.generate_explanations --n 10
    uv run python -m santolina_tutor.generate_explanations --n 10 --models qwen3.6,glm5.3-flash

Input: data/interim/m3kang/problems.jsonl plus images (from santolina_tutor.dataset).
Each problem is sent to each model with its image (the options A-E are only in the image)
and the official answer letter. The model returns one JSON object per problem.

Output, in data/processed/explanations/ (git-ignored; M3Kang is research-use only):
    sample.jsonl              the (id, language) pairs that were sampled, in order
    raw/<model>.jsonl         one structured record per problem (see SCHEMA_HINT)
    sft/<model>.jsonl         chat-format examples for fine-tuning a small text-only model

Re-running resumes: problems already in raw/<model>.jsonl are skipped.
The API key comes from HELMCODE_API_KEY, or is asked for in the terminal.
"""

import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from getpass import getpass
import json
import os
from pathlib import Path
import random
import re
import time

from loguru import logger
import typer

from santolina_tutor.config import INTERIM_DATA_DIR, PROCESSED_DATA_DIR

app = typer.Typer()

BASE_URL = "https://api.helmcode.com/v1"
PLAN_MODELS = ["glm5.3-flash", "qwen3.6", "gemma4", "deepseek-v4-flash"]
LANG_NAMES = {"eng": "English", "cat": "Catalan", "esp": "Spanish", "fra": "French"}

SCHEMA_HINT = """{
  "options": {"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."},
  "needs_figure": true or false,
  "figure_description": "what the figure shows, in words, or empty string",
  "topic": "short topic, e.g. counting, geometry, logic, arithmetic",
  "key_idea": "one sentence: the insight that unlocks the problem",
  "hints": ["hint 1 (gentle nudge)", "hint 2 (more concrete)", "hint 3 (almost the method)"],
  "solution_steps": ["step 1", "step 2", "..."],
  "final_answer": "one letter A-E",
  "answer_justification": "one or two sentences on why that option is right",
  "common_mistakes": ["a typical wrong path and which wrong option it leads to"],
  "agrees_with_key": true or false
}"""

SYSTEM_PROMPT = f"""You are an expert, patient math teacher preparing material for students of the
Kangaroo (Cangur) math competition. You receive a problem (text and an image that contains the
answer options A-E and sometimes a figure) and the official correct answer.

Write material a student can learn from:
- Hints go from gentle to concrete and NEVER reveal the answer or the final number.
- Solution steps explain the reasoning as you would to a student, one idea per step,
  with every calculation shown. Do not skip steps.
- Reach the official answer by honest reasoning. If after careful work you believe the
  official answer is wrong, set "agrees_with_key" to false and explain why in the steps.
- Transcribe the options exactly as in the image. If an option is a picture, describe it.
- Write everything in {{language}}.

Reply with ONE JSON object and nothing else, following this shape:
{SCHEMA_HINT}"""

TUTOR_SYSTEM = (
    "You are a patient math tutor. Explain step by step, show every calculation, "
    "and answer with the letter of the correct option at the end."
)
HINT_REQUEST = {
    "eng": "Can you give me a hint, without telling me the answer?",
    "cat": "Em pots donar una pista, sense dir-me la resposta?",
    "esp": "¿Me das una pista, sin decirme la respuesta?",
}
MORE_HINT_REQUEST = {
    "eng": "I'm still stuck. Can you give me another hint?",
    "cat": "Encara estic encallat. Em pots donar una altra pista?",
    "esp": "Sigo atascado. ¿Me das otra pista?",
}
ANSWER_WORD = {"eng": "Answer", "cat": "Resposta", "esp": "Respuesta"}


def get_client(timeout: float = 150):
    from openai import OpenAI

    key = os.environ.get("HELMCODE_API_KEY") or getpass("Helmcode API key: ").strip()
    if not key:
        raise typer.BadParameter("no API key")
    # max_retries=1: call_model already retries once; slow calls should fail fast, not stack.
    return OpenAI(base_url=BASE_URL, api_key=key, timeout=timeout, max_retries=1)


def load_rows(path: Path) -> list[dict]:
    """Read JSONL; skip a line cut off by a crash mid-write, so a resume never fails on it."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                logger.warning(f"{path.name}: skipping unreadable line {i} (interrupted write)")
    return rows


def sample_problems(rows, n, languages, seed, text_only):
    """Deterministic sample: one translation per problem id, spread over levels."""
    pool = [r for r in rows if r["language"] in languages and (r["text_only"] or not text_only)]
    rng = random.Random(seed)
    rng.shuffle(pool)
    by_level: dict[int, list] = {}
    for r in pool:
        by_level.setdefault(r["level"], []).append(r)
    picked, ids = [], set()
    while len(picked) < n and any(by_level.values()):
        for level in sorted(by_level):
            bucket = by_level[level]
            while bucket and bucket[-1]["id"] in ids:
                bucket.pop()
            if bucket and len(picked) < n:
                r = bucket.pop()
                picked.append(r)
                ids.add(r["id"])
    return picked


def parse_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("no JSON object in reply")
    return json.loads(text[start : end + 1])


def call_model(client, model, row, image_dir, reasoning_effort, max_tokens=16000):
    language = LANG_NAMES.get(row["language"], row["language"])
    image_b64 = base64.b64encode((image_dir / row["image"]).read_bytes()).decode()
    user = (
        f"Problem (level {row['level']}):\n{row['text']}\n\n"
        f"Official correct answer: {row['label']}\n"
        "The answer options A-E are in the image."
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.replace("{language}", language)},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            ],
        },
    ]
    last_error = None
    for attempt in range(3):
        start = time.time()
        content = ""
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                reasoning_effort=reasoning_effort,
            )
            choice = resp.choices[0]
            content = choice.message.content or ""
            usage = resp.usage.model_dump() if resp.usage else {}
            if not content.strip():
                raise ValueError(f"empty reply (finish_reason={choice.finish_reason})")
            data = parse_json(content)
            return data, round(time.time() - start, 1), usage, None
        except Exception as e:  # noqa: BLE001 - keep going, record the error
            snippet = content.strip().replace("\n", " ")[:120]
            last_error = f"{type(e).__name__}: {e}"[:200] + (f" | reply starts: {snippet!r}" if snippet else "")
            logger.warning(f"{model} {row['id']}/{row['language']} attempt {attempt + 1}: {last_error}")
            # The API appears to cache identical requests, so an identical retry returns the
            # same broken reply. Change the request: ask again for strict JSON.
            messages = messages[:2] + [
                {"role": "user", "content": (
                    f"(Retry {attempt + 1}) Your previous reply was not one valid JSON object. "
                    "Reply again with ONLY the JSON object described in the instructions, "
                    "no text before or after it, keeping it concise.")},
            ]
    return None, None, {}, last_error


def check(data: dict, label: str) -> dict:
    hints = data.get("hints") or []
    options = data.get("options") or {}
    return {
        "answer_matches_label": str(data.get("final_answer", "")).strip().upper()[:1] == label,
        "has_5_options": sorted(options) == list("ABCDE"),
        "n_hints": len(hints),
        "n_steps": len(data.get("solution_steps") or []),
        "agrees_with_key": data.get("agrees_with_key"),
    }


def problem_prompt(row, data) -> str:
    """The question as the small, text-only model will see it on the board.
    The contest number ("6. A rectangular mosaic...") is removed: a student's question has none."""
    parts = [re.sub(r"^\s*\d+\s*[.)]\s*", "", row["text"].strip())]
    if data.get("needs_figure") and data.get("figure_description"):
        parts.append(f"[Figure: {data['figure_description']}]")
    options = data.get("options") or {}
    parts.append("\n".join(f"{k}) {options[k]}" for k in "ABCDE" if k in options))
    return "\n\n".join(p for p in parts if p)


def to_sft(row, data, model) -> list[dict]:
    """Training examples per problem: a full solution, then one example per hint.
    Hint k is a conversation where hints 1..k-1 were already given and the student asks again;
    the last assistant turn (hint k) is the target."""
    lang = row["language"]
    question = problem_prompt(row, data)
    steps = "\n".join(f"{i}. {s}" for i, s in enumerate(data["solution_steps"], 1))
    solution = (
        f"{data.get('key_idea', '')}\n\n{steps}\n\n"
        f"{data.get('answer_justification', '')}\n\n"
        f"{ANSWER_WORD.get(lang, 'Answer')}: {row['label']}"
        + (f" ({data['options'][row['label']]})" if row["label"] in (data.get("options") or {}) else "")
    ).strip()
    meta = {"id": row["id"], "language": lang, "level": row["level"], "teacher": model}
    examples = [
        {
            "task": "solution",
            **meta,
            "messages": [
                {"role": "system", "content": TUTOR_SYSTEM},
                {"role": "user", "content": question},
                {"role": "assistant", "content": solution},
            ],
        }
    ]
    messages = [
        {"role": "system", "content": TUTOR_SYSTEM},
        {"role": "user", "content": f"{question}\n\n{HINT_REQUEST.get(lang, HINT_REQUEST['eng'])}"},
    ]
    hints = [h.strip() for h in data.get("hints") or [] if isinstance(h, str) and h.strip()]
    for level, hint in enumerate(hints, 1):
        if level > 1:
            messages.append({"role": "user", "content": MORE_HINT_REQUEST.get(lang, MORE_HINT_REQUEST["eng"])})
        messages.append({"role": "assistant", "content": hint})
        examples.append({"task": "hint", "hint_level": level, **meta, "messages": list(messages)})
    return examples


@app.command()
def main(
    n: int = typer.Option(10, help="number of problems to sample"),
    models: str = typer.Option(
        ",".join(PLAN_MODELS),
        help="comma-separated model IDs; order = preference for combined.jsonl",
    ),
    languages: str = typer.Option("eng,cat", help="M3Kang language codes to sample from"),
    seed: int = 42,
    text_only: bool = typer.Option(True, help="only problems marked text_only in M3Kang"),
    reasoning_effort: str = typer.Option("medium", help="low, medium, high or max"),
    workers: int = typer.Option(16, help="parallel API calls"),
    timeout: float = typer.Option(150, help="seconds before one API call is abandoned"),
    max_tokens: int = typer.Option(8000, help="cap on completion tokens per call"),
    tiebreak: str = typer.Option(
        "", help="model called only when the --models disagree on the key (e.g. qwen3.6)"
    ),
    build_only: bool = typer.Option(
        False, help="no API calls: rebuild sft/*.jsonl and combined.jsonl from the saved raw files"
    ),
    input_dir: Path = INTERIM_DATA_DIR / "m3kang",
    output_dir: Path = PROCESSED_DATA_DIR / "explanations",
):
    rows = load_rows(input_dir / "problems.jsonl")
    model_list = [m.strip() for m in models.split(",") if m.strip()]
    if build_only:
        # Every problem of the chosen languages that has a saved row, in dataset order. All
        # saved models vote (incl. a tie-break model); only --models write training text.
        (output_dir / "sft").mkdir(parents=True, exist_ok=True)
        voters = sorted(p.stem for p in (output_dir / "raw").glob("*.jsonl"))
        raw = read_raw(output_dir, voters)
        have = {(r["id"], r["language"]) for recs in raw.values() for r in recs}
        langs = set(languages.split(","))
        sample = [r for r in rows if r["language"] in langs and (r["id"], r["language"]) in have]
        logger.info(f"build only: {len(sample)} problems with saved rows; voters: {', '.join(voters)}")
        build_sft(sample, raw, model_list, output_dir)
        return
    sample = sample_problems(rows, n, set(languages.split(",")), seed, text_only)
    (output_dir / "raw").mkdir(parents=True, exist_ok=True)
    (output_dir / "sft").mkdir(parents=True, exist_ok=True)
    with open(output_dir / "sample.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps({k: r[k] for k in ("id", "language", "level", "label")}) + "\n" for r in sample)
    logger.info(f"Sampled {len(sample)} problems; models: {', '.join(model_list)}")

    client = get_client(timeout)
    run_calls(client, model_list, sample, input_dir, output_dir, reasoning_effort, max_tokens, workers)

    vote_models = list(model_list)
    if tiebreak:
        # A third opinion only where the first models split on the key: the vote stays a strict
        # majority, at a fraction of the cost of always calling three models.
        raw = read_raw(output_dir, model_list)
        disputed = [r for r in sample if split_vote(raw, (r["id"], r["language"]))]
        logger.info(f"{len(disputed)} problems need the tie-break model {tiebreak}")
        run_calls(client, [tiebreak], disputed, input_dir, output_dir, reasoning_effort, max_tokens, workers)
        vote_models.append(tiebreak)

    # Rewrite the raw files in sample order (they were appended as calls finished).
    order = {(r["id"], r["language"]): i for i, r in enumerate(sample)}
    raw = read_raw(output_dir, vote_models)
    for model, keep in raw.items():
        keep.sort(key=lambda r: order.get((r["id"], r["language"]), 10**9))
        # Write a temporary file and swap it in: a crash here can't truncate the results.
        path = output_dir / "raw" / f"{model}.jsonl"
        tmp = path.with_suffix(".jsonl.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in keep)
        os.replace(tmp, path)
    # The tie-break model votes but never writes training text.
    build_sft(sample, raw, model_list, output_dir)
    logger.success(f"Done. Output in {output_dir}")


def read_raw(output_dir: Path, models: list[str]) -> dict[str, list]:
    """Latest successful record per (model, problem); failed attempts are dropped."""
    raw = {}
    for model in models:
        path = output_dir / "raw" / f"{model}.jsonl"
        latest = {}
        for r in load_rows(path) if path.exists() else []:
            if r.get("output"):
                latest[(r["id"], r["language"])] = r
        raw[model] = list(latest.values())
    return raw


def split_vote(raw: dict[str, list], key: tuple) -> bool:
    votes = [
        bool((r.get("checks") or {}).get("answer_matches_label"))
        for records in raw.values()
        for r in records
        if (r["id"], r["language"]) == key
    ]
    return len(set(votes)) > 1 or len(votes) < len(raw)


def run_calls(client, models, sample, input_dir, output_dir, reasoning_effort, max_tokens, workers):
    """Call every model on every sample problem not done yet; append each result as it lands,
    so an interrupted run loses at most the calls in flight."""
    jobs = []
    for model in models:
        path = output_dir / "raw" / f"{model}.jsonl"
        done = {(r["id"], r["language"]) for r in load_rows(path) if r.get("output")} if path.exists() else set()
        jobs += [(model, r) for r in sample if (r["id"], r["language"]) not in done]
    logger.info(f"{len(jobs)} calls to make with {workers} workers")
    if not jobs:
        return
    start, finished = time.time(), 0
    files = {m: open(output_dir / "raw" / f"{m}.jsonl", "a", encoding="utf-8") for m in models}  # noqa: SIM115 - closed in finally
    pool = ThreadPoolExecutor(max_workers=workers)
    try:
        futures = {
            pool.submit(call_model, client, m, r, input_dir, reasoning_effort, max_tokens): (m, r)
            for m, r in jobs
        }
        if True:  # keeps the loop body's indentation
            for fut in as_completed(futures):
                model, row = futures[fut]
                data, seconds, usage, error = fut.result()
                record = {
                    "id": row["id"],
                    "language": row["language"],
                    "level": row["level"],
                    "label": row["label"],
                    "teacher": model,
                    "reasoning_effort": reasoning_effort,
                    "seconds": seconds,
                    "usage": usage,
                    "error": error,
                    "checks": check(data, row["label"]) if data else None,
                    "output": data,
                }
                files[model].write(json.dumps(record, ensure_ascii=False) + "\n")
                files[model].flush()
                finished += 1
                ok = record["checks"] and record["checks"]["answer_matches_label"]
                rate = finished / (time.time() - start)
                eta = (len(jobs) - finished) / rate / 60 if rate else 0
                logger.info(
                    f"[{finished}/{len(jobs)} ~{eta:.0f} min left] {model:18} "
                    f"{row['id']}/{row['language']}: {'ok' if ok else 'CHECK'} {seconds}s"
                )
        pool.shutdown()
    except KeyboardInterrupt:
        # Ctrl-C: drop the queued calls and leave now. Without this, the pool finishes every
        # queued call first (it looks frozen). Saved results are flushed; rerun to continue.
        for f in files.values():
            f.close()
        logger.warning(f"Interrupted after {finished}/{len(jobs)} calls; results so far are saved. "
                       "Rerun the same command to continue.")
        pool.shutdown(wait=False, cancel_futures=True)
        os._exit(130)  # in-flight HTTP calls would otherwise hold the process for minutes
    finally:
        for f in files.values():
            if not f.closed:
                f.close()


# Text a student-facing tutor must not learn. Thinking aloud: self-corrections inside the
# solution ("... wait, let me verify"). Plain "actually" is ordinary English ("which parts would
# you actually see?"), so only its self-correcting forms count. Key mentions: the tutor on the
# board never has the official answer, so it must not learn to cite one.
THINKING_ALOUD = re.compile(
    r"\bwait\b(?!\s+(?:for|until|\d))|\blet me\b|\bhmm+\b|\boops\b|\bon second thought\b"
    r"|\.\.\.\s*actually\b|(?:^|[.!?;:—-]\s*)actually,|\bbut actually\b"
    r"|\bI (?:made a mistake|was wrong|need to re)",
    re.IGNORECASE,
)
MENTIONS_KEY = re.compile(r"\bofficial(?:ly)?\b|\banswer key\b|\bgiven answer\b|\bmatches the key\b",
                          re.IGNORECASE)


def leaks(output: dict) -> str:
    """Name of the problem in the student-facing text, or '' if it is clean."""
    fields = [output.get("key_idea"), output.get("answer_justification"),
              *(output.get("solution_steps") or []), *(output.get("hints") or [])]
    text = " ".join(str(f) for f in fields if f)
    if MENTIONS_KEY.search(text):
        return "mentions the official answer"
    if THINKING_ALOUD.search(text):
        return "thinks aloud"
    return ""


def clean(record) -> bool:
    c = record.get("checks") or {}
    return bool(
        record.get("output")
        and c.get("answer_matches_label")
        and c.get("has_5_options")
        and c.get("agrees_with_key") is not False
        and record["output"].get("solution_steps")
        and not leaks(record["output"])
    )


def build_sft(sample, raw, model_list, output_dir):
    """Write sft/<model>.jsonl and sft/combined.jsonl.

    A problem is trusted only if a strict majority of the teachers that answered reached the
    official key on their own reasoning. This drops problems whose key or text is wrong: a
    teacher that forces the key there teaches the small model to rationalize.
    combined.jsonl takes, per trusted problem, the first clean teacher in --models order.
    """
    by_key: dict[tuple, dict] = {}
    for model, records in raw.items():
        for r in records:
            by_key.setdefault((r["id"], r["language"]), {})[model] = r
    # Problems whose key the models disputed. Saved before the rows that missed the key were
    # deleted from raw/, so the vote can no longer be recomputed for them: never trust them.
    disputed_path = output_dir / "disputed_keys.jsonl"
    disputed = set()
    if disputed_path.exists():
        disputed = {(d["id"], d["language"]) for d in load_rows(disputed_path)}
    trusted, report = set(), []
    for key, recs in by_key.items():
        answered = [r for r in recs.values() if r.get("output")]
        votes = sum(1 for r in answered if (r.get("checks") or {}).get("answer_matches_label"))
        ok = bool(answered) and votes * 2 > len(answered) and key not in disputed
        if ok:
            trusted.add(key)
        else:
            report.append(f"{key[0]}/{key[1]} ({votes}/{len(answered)} teachers reach the key)")
    if report:
        logger.warning("Excluded from SFT, teachers dispute the key: " + "; ".join(report))

    sample_by_key = {(r["id"], r["language"]): r for r in sample}
    combined = []
    for model in model_list:
        with open(output_dir / "sft" / f"{model}.jsonl", "w", encoding="utf-8") as f:
            for r in raw[model]:
                key = (r["id"], r["language"])
                if key in trusted and key in sample_by_key and clean(r):
                    f.writelines(json.dumps(ex, ensure_ascii=False) + "\n" for ex in to_sft(sample_by_key[key], r["output"], model))
    for row in sample:
        key = (row["id"], row["language"])
        if key not in trusted:
            continue
        for model in model_list:
            r = by_key[key].get(model)
            if r and clean(r):
                combined += to_sft(row, r["output"], model)
                break
    with open(output_dir / "sft" / "combined.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps(ex, ensure_ascii=False) + "\n" for ex in combined)
    logger.info(f"combined.jsonl: {len(combined)} examples from {len(trusted)} trusted problems")


if __name__ == "__main__":
    app()
