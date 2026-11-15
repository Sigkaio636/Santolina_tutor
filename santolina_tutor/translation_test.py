"""How badly does machine translation corrupt Kangaroo problems? (Catalan/Spanish -> English)

    uv run python -m santolina_tutor.translation_test --n 200
    uv run python -m santolina_tutor.translation_test --n 200 --solve   # + meaning check via API

M3Kang is a parallel corpus: the same problem exists in official English, Catalan and Spanish.
We machine-translate the official Catalan/Spanish text and compare it with the official English.

Candidates (each one optional; missing models are skipped):
    softcatala-ca   softcatala/opennmt-cat-eng (CTranslate2)
    opus-ca         Helsinki-NLP/opus-mt-ca-en (CTranslate2 conversion by gaudi)
    opus-es         Helsinki-NLP/opus-mt-es-en (CTranslate2 conversion by gaudi)
    roa-ca/roa-es   Helsinki-NLP/opus-mt-roa-en, one model for Romance languages -> English
    mul-ca/mul-es   Helsinki-NLP/opus-mt-mul-en, one model for ~100 languages -> English
    qwen-ca/qwen-es the board's Qwen3.5 0.8B Q8_0 through a local llama-server (--qwen-url)
Baselines for search: the untranslated Catalan / Spanish text.

Measures, per candidate:
    1. critical errors: numbers, units and condition words (at least, exactly, consecutive, ...)
       that differ from the official English
    2. search: does the bge-small English index (all official English problems) return the
       right problem first / in the top 5 when queried with the translation?
    3. chrF and BLEU against the official English
    4. seconds per problem on this machine (4 threads, to approach the board)
    5. (--solve) does glm5.3-flash still reach the official key from the translated text?

Outputs in data/processed/translation_test/ (git-ignored: M3Kang-derived text). The printed
summary has aggregates only.
"""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import random
import re
import time
import urllib.request

from loguru import logger
import typer

from santolina_tutor.config import EXTERNAL_DATA_DIR, INTERIM_DATA_DIR, PROCESSED_DATA_DIR

app = typer.Typer()

TRANSLATORS = EXTERNAL_DATA_DIR / "translators"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "  # as in config.env
MAX_CHARS = 1400  # as copilot/embed.py
LANG_NAME = {"cat": "Catalan", "esp": "Spanish"}

# ---------------------------------------------------------------- normalisation and checks
NUMBER_WORDS = {
    # "one" is left out: as a pronoun or article ("one of them", "one/a square") it floods the
    # check with false alarms; digits and the other number words still catch real changes.
    "zero": 0, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100, "thousand": 1000,
    "half": 0.5, "double": 2, "twice": 2, "dozen": 12,
}
# Each category: the condition a word encodes. A difference between official English and the
# translation means the translation may state a different problem.
CONDITIONS = {
    "at_least": r"\bat least\b|\bno (?:fewer|less) than\b|\bminimum\b",
    "at_most": r"\bat most\b|\bno more than\b|\bmaximum\b|\bnot more than\b",
    "exactly": r"\bexactly\b",
    "more_than": r"\b(?:more|greater|larger|bigger|higher|older|longer|taller) than\b",
    "less_than": r"\b(?:less|fewer|smaller|lower|younger|shorter) than\b",
    "consecutive": r"\bconsecutive\b|\bin a row\b|\bsuccessive\b",
    "each_every": r"\beach\b|\bevery\b",
    "different": r"\bdifferent\b|\bdistinct\b",
    "only": r"\bonly\b",
    "negation": r"\bnot\b|n't\b|\bnever\b|\bnone\b|\bneither\b|\bnor\b|\bno\b",
    "same_equal": r"\bsame\b|\bequal\b",
}
UNITS = {
    "cm": r"\bcm\b|\bcentimet(?:er|re)s?\b",
    "m": r"\bm\b|\bmet(?:er|re)s?\b",
    "km": r"\bkm\b|\bkilomet(?:er|re)s?\b",
    "mm": r"\bmm\b|\bmillimet(?:er|re)s?\b",
    "kg": r"\bkg\b|\bkilo(?:gram)?s?\b",
    "g": r"\bgrams?\b",
    "l": r"\blit(?:er|re)s?\b",
    "h": r"\bhours?\b|\bh\b",
    "min": r"\bmin(?:ute)?s?\b",
    "s": r"\bseconds?\b",
    "money": r"€|\beuros?\b|\bcents?\b|\$|\bdollars?\b",
    "percent": r"%|\bper ?cent\b",
    "degree": r"°|\bdegrees?\b",
    "area": r"cm\^?2|cm²|m²|\bsquare\b",
}


def strip_enumerator(text: str) -> str:
    return re.sub(r"^\s*\d+\s*[.)]\s*", "", text.strip())


def numbers(text: str) -> Counter:
    """Numbers as written in English-style text. '1,5' stays '1,5' so a Catalan decimal comma
    copied into English is caught; '1,500' (English thousands) becomes 1500."""
    t = text.lower()
    out = Counter()
    for m in re.finditer(r"\d{1,3}(?:,\d{3})+(?!\d)|\d+(?:[.,]\d+)?", t):
        s = m.group()
        if re.fullmatch(r"\d{1,3}(?:,\d{3})+", s):
            s = s.replace(",", "")
        out[s] += 1
    for w, v in NUMBER_WORDS.items():
        k = len(re.findall(rf"\b{w}\b", t))
        if k:
            out[str(v) if not isinstance(v, float) else "0.5"] += k
    return out


def presence(text: str, table: dict) -> set:
    t = text.lower()
    return {k for k, rx in table.items() if re.search(rx, t)}


def critical_errors(reference: str, hypothesis: str) -> dict:
    ref_n, hyp_n = numbers(reference), numbers(hypothesis)
    return {
        "numbers_missing": sorted((ref_n - hyp_n).elements()),
        "numbers_extra": sorted((hyp_n - ref_n).elements()),
        "decimal_comma": bool(re.search(r"\d,\d(?!\d\d)", hypothesis)),
        "units_diff": sorted(presence(reference, UNITS) ^ presence(hypothesis, UNITS)),
        "conditions_diff": sorted(presence(reference, CONDITIONS) ^ presence(hypothesis, CONDITIONS)),
    }


# ---------------------------------------------------------------- translators
def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?:;])\s+|\n+", text.strip())
    return [p for p in parts if p.strip()]


class CT2Translator:
    """CTranslate2 model, sentence by sentence, int8 on 4 CPU threads (closest to the board)."""

    def __init__(self, folder: Path, kind: str):
        import ctranslate2

        self.kind = kind
        self.model = ctranslate2.Translator(str(folder), device="cpu", compute_type="int8",
                                            intra_threads=4)
        if kind == "onmt":  # Softcatalà: one SentencePiece model, OpenNMT tokenizer
            import pyonmttok

            sp = next(folder.glob("*.model"))
            self.tok = pyonmttok.Tokenizer(mode="none", sp_model_path=str(sp))
        else:  # Marian (Opus-MT): source/target SentencePiece models, </s> appended
            import sentencepiece as spm

            self.src = spm.SentencePieceProcessor(model_file=str(folder / "source.spm"))
            self.tgt = spm.SentencePieceProcessor(model_file=str(folder / "target.spm"))

    def __call__(self, text: str) -> str:
        sents = split_sentences(text)
        if self.kind == "onmt":
            batch = [self.tok.tokenize(s)[0] for s in sents]
        else:
            batch = [self.src.encode(s, out_type=str) + ["</s>"] for s in sents]
        results = self.model.translate_batch(batch, beam_size=2, max_decoding_length=256)
        out = []
        for r in results:
            toks = r.hypotheses[0]
            out.append(self.tok.detokenize(toks) if self.kind == "onmt" else self.tgt.decode(toks))
        return " ".join(out)


class LlamaTranslator:
    """The board's small LLM, asked to translate (no extra model on the board)."""

    def __init__(self, url: str, source_lang: str):
        self.url = url.rstrip("/") + "/v1/chat/completions"
        self.system = (
            f"Translate the user's {LANG_NAME[source_lang]} math problem into English. "
            "Keep every number, unit, name and condition exactly. Output only the translation."
        )

    def __call__(self, text: str) -> str:
        body = {
            "messages": [{"role": "system", "content": self.system}, {"role": "user", "content": text}],
            "temperature": 0, "seed": 42, "max_tokens": 600, "cache_prompt": True,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        req = urllib.request.Request(self.url, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as r:
            content = json.loads(r.read())["choices"][0]["message"]["content"] or ""
        return re.sub(r"<think>.*?</think>", "", content, flags=re.S).strip()


def server_alive(url: str) -> bool:
    try:
        with urllib.request.urlopen(url.rstrip("/") + "/health", timeout=3) as r:
            return r.status == 200
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------- search
class EnglishIndex:
    """bge-small-en-v1.5 over every official English problem text (ONNX via fastembed; the
    board runs the same weights as GGUF, so scores differ slightly, rankings barely)."""

    def __init__(self, texts: dict[str, str]):
        import numpy as np
        from fastembed import TextEmbedding

        self.np = np
        self.model = TextEmbedding("BAAI/bge-small-en-v1.5")
        self.ids = list(texts)
        self.mat = self._embed([texts[i][:MAX_CHARS] for i in self.ids])

    def _embed(self, texts):
        v = self.np.array(list(self.model.embed(texts)))
        return v / self.np.linalg.norm(v, axis=1, keepdims=True)

    def ranks(self, queries: list[str], targets: list[str]) -> list[int]:
        q = self._embed([(QUERY_PREFIX + t)[:MAX_CHARS] for t in queries])
        scores = q @ self.mat.T
        out = []
        for row, target in zip(scores, targets):
            order = self.np.argsort(-row)
            out.append(int(self.np.where(self.np.array(self.ids)[order] == target)[0][0]) + 1)
        return out


# ---------------------------------------------------------------- meaning check (API)
def solve_all(variants: dict[str, dict[str, str]], problems: dict[str, dict], image_dir: Path,
              workers: int) -> dict[str, dict[str, str]]:
    """glm5.3-flash answers each problem from a given text + the English image (options)."""
    import base64

    from santolina_tutor.generate_explanations import get_client

    client = get_client(timeout=150)

    def one(name, pid, text):
        p = problems[pid]
        img = base64.b64encode((image_dir / p["image"]).read_bytes()).decode()
        msgs = [
            {"role": "system", "content": "Solve the multiple-choice math problem. The options A-E "
             "are in the image. Reply with JSON only: {\"answer\": \"<letter>\"}."},
            {"role": "user", "content": [
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}}]},
        ]
        for attempt in range(2):
            try:
                r = client.chat.completions.create(model="glm5.3-flash", messages=msgs,
                                                   max_tokens=6000, reasoning_effort="medium")
                m = re.search(r'"answer"\s*:\s*"([A-E])"', r.choices[0].message.content or "")
                if m:
                    return name, pid, m.group(1)
            except Exception as e:  # noqa: BLE001
                logger.warning(f"solve {name} {pid}: {e}")
            msgs = msgs[:2] + [{"role": "user", "content": f"(retry {attempt + 1}) JSON only."}]
        return name, pid, ""

    jobs = [(n, pid, t) for n, texts in variants.items() for pid, t in texts.items()]
    answers: dict[str, dict[str, str]] = {n: {} for n in variants}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for i, (name, pid, letter) in enumerate(pool.map(lambda j: one(*j), jobs), 1):
            answers[name][pid] = letter
            if i % 50 == 0:
                logger.info(f"solve {i}/{len(jobs)}")
    return answers


# ---------------------------------------------------------------- main
@app.command()
def main(
    n: int = typer.Option(200, help="number of problems (each has eng, cat and esp)"),
    seed: int = 42,
    qwen_url: str = typer.Option("http://127.0.0.1:8091", help="llama-server with Qwen 0.8B"),
    solve: bool = typer.Option(False, help="also check meaning with glm5.3-flash (API calls)"),
    solve_workers: int = 4,
    llm_workers: int = typer.Option(4, help="parallel requests to the local llama-server"),
    systems: str = typer.Option("", help="comma-separated candidates to run (default: all found)"),
    no_qwen: bool = typer.Option(False, help="skip the local LLM even if its server is up"),
    input_dir: Path = INTERIM_DATA_DIR / "m3kang",
    output_dir: Path = PROCESSED_DATA_DIR / "translation_test",
):
    import sacrebleu

    rows = [json.loads(line) for line in open(input_dir / "problems.jsonl", encoding="utf-8")]
    by_id: dict[str, dict[str, dict]] = {}
    for r in rows:
        if r["language"] in ("eng", "cat", "esp"):
            by_id.setdefault(r["id"], {})[r["language"]] = r
    full = sorted(i for i, v in by_id.items() if len(v) == 3)
    # Stratified by level: round-robin over shuffled per-level lists.
    rng = random.Random(seed)
    levels: dict[int, list] = {}
    for i in full:
        levels.setdefault(by_id[i]["eng"]["level"], []).append(i)
    for v in levels.values():
        rng.shuffle(v)
    sample = []
    while len(sample) < n and any(levels.values()):
        for lv in sorted(levels):
            if levels[lv] and len(sample) < n:
                sample.append(levels[lv].pop())
    logger.info(f"{len(sample)} problems with eng+cat+esp, levels {Counter(by_id[i]['eng']['level'] for i in sample)}")

    ref = {i: strip_enumerator(by_id[i]["eng"]["text"]) for i in sample}
    src = {lang: {i: strip_enumerator(by_id[i][lang]["text"]) for i in sample} for lang in ("cat", "esp")}

    candidates: dict[str, tuple[str, object]] = {}
    for name, folder, kind, lang in [
        ("softcatala-ca", "opennmt-cat-eng", "onmt", "cat"),
        ("opus-ca", "opus-mt-ca-en-ctranslate2", "marian", "cat"),
        ("opus-es", "opus-mt-es-en-ctranslate2", "marian", "esp"),
        # multilingual: one model for both source languages
        ("roa-ca", "opus-mt-roa-en-ctranslate2", "marian", "cat"),
        ("roa-es", "opus-mt-roa-en-ctranslate2", "marian", "esp"),
        ("mul-ca", "opus-mt-mul-en-ctranslate2", "marian", "cat"),
        ("mul-es", "opus-mt-mul-en-ctranslate2", "marian", "esp"),
    ]:
        if (TRANSLATORS / folder / "model.bin").exists():
            candidates[name] = (lang, CT2Translator(TRANSLATORS / folder, kind))
        else:
            logger.warning(f"skip {name}: {TRANSLATORS / folder} not found")
    if not no_qwen and server_alive(qwen_url):
        candidates["qwen-ca"] = ("cat", LlamaTranslator(qwen_url, "cat"))
        candidates["qwen-es"] = ("esp", LlamaTranslator(qwen_url, "esp"))
    else:
        logger.warning(f"skip qwen: disabled or no llama-server at {qwen_url}")
    if systems:
        keep = {s_.strip() for s_ in systems.split(",")}
        candidates = {k: v for k, v in candidates.items() if k in keep}
    logger.info(f"candidates: {', '.join(candidates)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    cache_path = output_dir / "translations.jsonl"
    cache = {}
    if cache_path.exists():
        for line in open(cache_path, encoding="utf-8"):
            c = json.loads(line)
            cache[(c["system"], c["id"])] = c
    hyps: dict[str, dict[str, str]] = {}
    secs: dict[str, list[float]] = {}
    with open(cache_path, "a", encoding="utf-8") as f:
        for name, (lang, translate) in candidates.items():
            hyps[name], secs[name] = {}, []
            todo = []
            for i in sample:
                if (name, i) in cache:
                    hyps[name][i] = cache[(name, i)]["translation"]
                    secs[name].append(cache[(name, i)]["seconds"])
                else:
                    todo.append(i)

            def timed(i, translate=translate, lang=lang):
                t0 = time.time()
                return i, translate(src[lang][i]), time.time() - t0

            # The LLM server runs several slots in parallel; CTranslate2 already uses 4 threads.
            # Parallel slots make each call slower, so laptop seconds are for comparison only.
            workers = llm_workers if isinstance(translate, LlamaTranslator) else 1
            with ThreadPoolExecutor(max_workers=workers) as pool:
                for k, (i, out, dt) in enumerate(pool.map(timed, todo), 1):
                    hyps[name][i] = out
                    secs[name].append(dt)
                    c = {"system": name, "id": i, "translation": out, "seconds": round(dt, 3)}
                    f.write(json.dumps(c, ensure_ascii=False) + "\n")
                    f.flush()
                    if k % 50 == 0:
                        logger.info(f"{name}: {k}/{len(todo)} ({sum(secs[name][-k:]) / k:.2f} s/call)")

    # Search: index = every official English problem (the realistic search space).
    all_eng = {i: strip_enumerator(v["eng"]["text"]) for i, v in by_id.items() if "eng" in v}
    index = EnglishIndex(all_eng)
    systems = {f"raw-{lang}": (lang, src[lang]) for lang in ("cat", "esp")}
    systems.update({name: (lang, hyps[name]) for name, (lang, _) in candidates.items()})

    answers = {}
    if solve:
        variants = {"official-eng": ref, **{n_: hyps[n_] for n_ in candidates}}
        answers = solve_all(variants, {i: by_id[i]["eng"] for i in sample}, input_dir, solve_workers)

    summary, per_problem = {}, []
    for name, (lang, texts) in systems.items():
        ids = list(texts)
        ranks = index.ranks([texts[i] for i in ids], ids)
        s = {
            "source": lang,
            "n": len(ids),
            "search_top1_pct": round(100 * sum(r == 1 for r in ranks) / len(ranks), 1),
            "search_top5_pct": round(100 * sum(r <= 5 for r in ranks) / len(ranks), 1),
        }
        if not name.startswith("raw-"):
            errs = {i: critical_errors(ref[i], texts[i]) for i in ids}
            num_bad = sum(bool(e["numbers_missing"] or e["numbers_extra"]) for e in errs.values())
            unit_bad = sum(bool(e["units_diff"]) for e in errs.values())
            cond_bad = sum(bool(e["conditions_diff"]) for e in errs.values())
            dec_bad = sum(e["decimal_comma"] for e in errs.values())
            any_bad = sum(bool(e["numbers_missing"] or e["numbers_extra"] or e["units_diff"]
                               or e["decimal_comma"]) for e in errs.values())
            cond_counts = Counter(c for e in errs.values() for c in e["conditions_diff"])
            s.update({
                "numbers_wrong_pct": round(100 * num_bad / len(ids), 1),
                "decimal_comma_pct": round(100 * dec_bad / len(ids), 1),
                "units_wrong_pct": round(100 * unit_bad / len(ids), 1),
                "conditions_differ_pct": round(100 * cond_bad / len(ids), 1),
                "conditions_by_type": dict(cond_counts.most_common()),
                "clean_numbers_units_pct": round(100 * (len(ids) - any_bad) / len(ids), 1),
                "chrF": round(sacrebleu.corpus_chrf([texts[i] for i in ids], [[ref[i] for i in ids]]).score, 1),
                "BLEU": round(sacrebleu.corpus_bleu([texts[i] for i in ids], [[ref[i] for i in ids]]).score, 1),
                "seconds_per_problem": round(sum(secs[name]) / len(secs[name]), 2),
            })
            for i, r in zip(ids, ranks):
                per_problem.append({"system": name, "id": i, "rank": r, **errs[i],
                                    "solved": answers.get(name, {}).get(i)})
        if answers.get(name):
            key = {i: by_id[i]["eng"]["label"] for i in ids}
            s["solved_pct"] = round(100 * sum(answers[name][i] == key[i] for i in ids) / len(ids), 1)
        summary[name] = s
    if answers.get("official-eng"):
        summary["official-eng"] = {"solved_pct": round(100 * sum(
            answers["official-eng"][i] == by_id[i]["eng"]["label"] for i in sample) / len(sample), 1)}

    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    with open(output_dir / "per_problem.jsonl", "w", encoding="utf-8") as f:
        for p in per_problem:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(json.dumps(summary, indent=2))
    logger.success(f"Wrote {output_dir}/summary.json, per_problem.jsonl, translations.jsonl")


if __name__ == "__main__":
    app()
