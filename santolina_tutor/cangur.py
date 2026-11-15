"""Past Cangur papers (cangur.org) as extra solved problems for the retrieval index.

The papers are the Catalan source of M3Kang, with the five options as text.
Everything here reads and writes under data/cangur/, which is git-ignored:
the problems are copyrighted, like M3Kang, and must not enter Git.

    uv run --offline python -m santolina_tutor.cangur parse    # PDFs -> questions.jsonl
    uv run --offline python -m santolina_tutor.cangur match    # link to M3Kang, attach answers

parse splits each PDF into blocks (one exam model each) of numbered questions.
match finds the M3Kang problem behind each question (same Catalan text), which
gives the block its year and level, and picks the answer-key row of that year
that agrees best with the M3Kang labels of the matched questions.
"""
import argparse
from collections import Counter, defaultdict
import csv
import io
import json
from pathlib import Path
import re
import subprocess
import unicodedata

ROOT = Path("data/cangur")
RAW = ROOT / "raw"
LETTERS = "ABCDE"
QUESTION = re.compile(r"^\s{0,6}(\d{1,2})\s*[.)]\s+(?=\S)")
OPTION = re.compile(r"(?:^|(?<=\s))([A-E])\)\s*")
NOISE = re.compile(r"^\s*(Q[üu]estions de \d+ punts.*|.*Cangur SCM.*|\d+|.*Societat Catalana de Matem.*"
                   r"|.*Model de la prova.*|P[àa]gina \d+.*)\s*$", re.IGNORECASE)


def words(text):
    """Lower-case words without accents, for matching the same text across sources."""
    text = unicodedata.normalize("NFKD", text.replace("ı", "i").replace("l·l", "ll"))
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    return re.findall(r"[a-z0-9]+", text)


def squash(text):
    """An option without spaces or case, to compare the same value from two sources."""
    return re.sub(r"\s+", "", str(text)).lower().replace("²", "2")


def pdf_text(path):
    done = subprocess.run(["pdftotext", str(path), "-"], capture_output=True, text=True, check=False)
    return done.stdout


def split_options(chunk):
    """(question text, {letter: option}) from one question's lines; options may be missing."""
    marks = [(m.group(1), m.start(), m.end()) for m in OPTION.finditer(chunk)]
    best = None
    for i, (letter, _start, _end) in enumerate(marks):  # the last A) that B) to E) follow in order
        if letter != "A":
            continue
        run, want = [marks[i]], 1
        for mark in marks[i + 1:]:
            if want < 5 and mark[0] == LETTERS[want]:
                run.append(mark)
                want += 1
        if want == 5:
            best = run
    if best is None:
        return " ".join(chunk.split()), {}
    options = {}
    for j, (letter, _start, end) in enumerate(best):
        stop = best[j + 1][1] if j + 1 < 5 else len(chunk)
        options[letter] = " ".join(chunk[end:stop].split())
    return " ".join(chunk[:best[0][1]].split()), options


def parse_text(text):
    """Blocks of questions. A block ends when the numbering starts again at 1."""
    blocks, current, number, lines = [], [], 0, []

    def close():
        if number:
            body, options = split_options("\n".join(lines))
            current.append({"n": number, "text": body, "options": options})

    for line in unicodedata.normalize("NFC", text).replace("\f", "\n").split("\n"):
        if NOISE.match(line):
            continue
        found = QUESTION.match(line)
        value = int(found.group(1)) if found else 0
        if found and (value == number + 1 or (value == 1 and number >= 10)):
            close()
            if value == 1 and current:
                blocks.append(current)
                current = []
            number, lines = value, [line[found.end():]]
        elif number:
            lines.append(line)
    close()
    if current:
        blocks.append(current)
    return [b for b in blocks if len(b) >= 10]


def parse():
    out = ROOT / "questions.jsonl"
    files = sorted(p for p in RAW.iterdir() if p.suffix.lower() == ".pdf")
    total = 0
    with open(out, "w", encoding="utf-8") as handle:
        for path in files:
            for index, block in enumerate(parse_text(pdf_text(path))):
                for question in block:
                    question.update(file=path.name, block=index)
                    handle.write(json.dumps(question, ensure_ascii=False) + "\n")
                total += len(block)
    print(f"{len(files)} PDFs, {total} questions -> {out}")


def key_rows(files):
    """Every run of 18 to 30 answer letters in the answer files: spreadsheet rows and columns, text lines."""
    rows = []

    def add(name, cells):
        letters = [c.strip() for c in cells if c.strip()]
        answers = [c for c in letters if c in set(LETTERS)]
        if 18 <= len(answers) <= 30 and len(answers) >= 0.8 * len(letters):
            rows.append({"file": name, "key": "".join(answers)})

    for path in files:
        suffix = path.suffix.lower()
        if suffix == ".xls":
            text = subprocess.run(["xls2csv", str(path)], capture_output=True, text=True, check=False).stdout
            grid = list(csv.reader(io.StringIO(text)))
            for line in grid:
                add(path.name, line)
            for column in range(max((len(line) for line in grid), default=0)):
                cells = [line[column] if column < len(line) else "" for line in grid]
                # a column holds one key per sheet block: cut it where the answers stop
                run = []
                for cell in cells + [""]:
                    if cell.strip() in set(LETTERS):
                        run.append(cell)
                    elif run:
                        add(path.name, run)
                        run = []
        elif suffix == ".pdf":
            for line in pdf_text(path).split("\n"):
                add(path.name, re.findall(r"\S+", line))
    return rows


def load_m3kang(paths=("claude_workspace/m3kang_ocr/train.jsonl", "claude_workspace/m3kang_ocr/val.jsonl")):
    problems = []
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            problems += [json.loads(line) for line in handle]
    cat = [p for p in problems if p["language"] == "cat"]
    for problem in cat:
        problem["words"] = set(words(re.sub(r"^\s*\d+\.\s*", "", problem["text"])))
    return cat


def match(threshold=0.6):
    cat = load_m3kang()
    by_word = defaultdict(list)
    for i, problem in enumerate(cat):
        for word in problem["words"]:
            by_word[word].append(i)
    with open(ROOT / "questions.jsonl", encoding="utf-8") as handle:
        questions = [json.loads(line) for line in handle]
    for question in questions:
        mine = set(words(question["text"]))
        votes = Counter(i for word in mine for i in by_word.get(word, ()))
        best, score = None, 0.0
        for i, shared in votes.most_common(20):
            jaccard = shared / max(1, len(mine | cat[i]["words"]))
            if jaccard > score:
                best, score = cat[i], jaccard
        if best is not None and score >= threshold:
            question.update(m3kang=best["id"], sim=round(score, 2))
    blocks = defaultdict(list)
    for question in questions:
        blocks[(question["file"], question["block"])].append(question)
    by_id = {p["id"]: p for p in cat}
    report, report_keys = [], []
    for (file, index), block in sorted(blocks.items()):
        hits = [by_id[q["m3kang"]] for q in block if "m3kang" in q]
        year = Counter(p["year"] for p in hits).most_common(1)
        level = Counter(p["level"] for p in hits).most_common(1)
        for question in block:
            question.update(year=year[0][0] if year else None, level=level[0][0] if level else None)
        report.append((file, index, len(block), len(hits), year[0][0] if year else None,
                       level[0][0] if level else None, sum(bool(q["options"]) for q in block)))
    keys = key_rows(sorted(p for p in RAW.rglob("*") if p.is_file()))
    labelled = 0
    for (file, index), block in sorted(blocks.items()):
        known = []  # (question, the M3Kang answer as an option value, or as a letter at the same level)
        for q in block:
            source = by_id.get(q.get("m3kang"))
            if source is None:
                continue
            value = (source.get("options") or {}).get(source["label"])
            if value and q["options"]:
                known.append((q, "value", squash(value)))
            elif source["level"] == q["level"]:
                known.append((q, "letter", source["label"]))
        size = max(q["n"] for q in block)
        best, agreement = None, 0
        for row in keys:
            if len(row["key"]) != size:
                continue
            same = 0
            for q, how, want in known:
                letter = row["key"][q["n"] - 1]
                same += (squash(q["options"].get(letter, "")) == want) if how == "value" else (letter == want)
            if same > agreement:
                best, agreement = row, same
        ok = best is not None and len(known) >= 6 and agreement >= 0.8 * len(known)
        for question in block:
            if ok:
                question.update(label=best["key"][question["n"] - 1], key_file=best["file"])
        labelled += ok
        report_keys.append((file, index, len(known), agreement, best["file"] if ok else "-"))
    with open(ROOT / "matched.jsonl", "w", encoding="utf-8") as handle:
        handle.writelines(json.dumps(q, ensure_ascii=False) + "\n" for q in questions)
    print("file | block | questions | in M3Kang | year | level | with options")
    for row in report:
        print(" | ".join(str(x) for x in row))
    print("file | block | matched | agree with key | key file")
    for row in report_keys:
        print(" | ".join(str(x) for x in row))
    print(f"{len(keys)} key rows, {labelled} of {len(blocks)} blocks labelled")
    seen = {q["m3kang"] for q in questions if "m3kang" in q}
    print(f"{len(questions)} questions, {sum('m3kang' in q for q in questions)} matched, "
          f"{len(seen)} of {len(cat)} M3Kang problems found")

PAPER = re.compile(r"^Cangur (EP5|EP6|P5|P6|E[1-4]|B[12]|N[1-4]) (\d{4})\s*(Solucion\w*)?\s*(\w*)\.?\s*$")
LEVEL = {"P5": 0, "EP5": 0, "P6": 1, "EP6": 1, "E1": 2, "E2": 3, "E3": 4, "E4": 5, "B1": 6, "B2": 7,
         "N1": 4, "N2": 5, "N3": 6, "N4": 7}
PAREN_OPTION = re.compile(r"\(([A-E])\)\s*")


def paren_options(chunk):
    """(text, options) for the compendium layout: (A) ... (B) ... (E) ..."""
    marks = [m for m in PAREN_OPTION.finditer(chunk)]
    start = next((i for i in range(len(marks) - 4)
                  if "".join(m.group(1) for m in marks[i:i + 5]) == LETTERS), None)
    if start is None:
        return " ".join(chunk.split()), {}
    run = marks[start:start + 5]
    options = {}
    for j, mark in enumerate(run):
        stop = run[j + 1].start() if j < 4 else len(chunk)
        options[mark.group(1)] = " ".join(chunk[mark.end():stop].split())
    return " ".join(chunk[:run[0].start()].split()), options


def read_volume(text, papers):
    """Add one volume's papers to `papers`: {(year, code): {"questions": [...], "key": "ABC..."}}."""
    state = {"paper": None, "mode": None, "number": 0, "lines": []}

    def close():
        if state["paper"] is not None and state["mode"] == "questions" and state["number"]:
            body, options = paren_options("\n".join(state["lines"]))
            state["paper"]["questions"].append({"n": state["number"], "text": body, "options": options})

    for line in text.replace("\f", "\n").split("\n"):
        head = PAPER.match(line.strip())
        if head:
            close()
            code, year, solutions, extra = head.groups()
            key = (int(year), code)
            state.update(number=0, lines=[])
            if not solutions:
                paper = papers.setdefault(key, {"questions": [], "key": ""})
                state.update(paper=paper, mode="questions" if not paper["questions"] else None)
            else:
                paper = papers.get(key)
                usable = paper is not None and not paper["key"] and not extra
                state.update(paper=paper, mode="key" if usable else None)
            continue
        if state["mode"] == "questions":
            bare = re.fullmatch(r"\s*(\d{1,2})\.?\s*", line)
            if bare and int(bare.group(1)) == state["number"] + 1:
                close()
                state.update(number=state["number"] + 1, lines=[])
            elif state["number"]:
                state["lines"].append(line)
        elif state["mode"] == "key" and line.strip() in set(LETTERS):
            state["paper"]["key"] += line.strip()
    close()


def compendium(paths=("Cangur2", "Cangur", "Cangur3")):
    """Parse the Compendium Cangur volumes (toomates.net, CC BY-NC) into one row per question."""
    papers = {}
    for name in paths:
        text = (ROOT / "toomates" / f"{name}.txt").read_text(encoding="utf-8")
        read_volume(unicodedata.normalize("NFC", text), papers)
    rows, report = [], []
    for (year, code), paper in sorted(papers.items()):
        count = len(paper["questions"])
        good = count >= 10 and len(paper["key"]) == count
        report.append(f"{year} {code}: {count} questions, {len(paper['key'])} answers, "
                      f"{sum(bool(q['options']) for q in paper['questions'])} with options"
                      + ("" if good else "  <-- skipped"))
        if not good:
            continue
        for question in paper["questions"]:
            rows.append({"id": f"cangur-{year}-{code}-{question['n']}", "language": "cat", "year": year,
                         "level": LEVEL[code], "text": question["text"], "options": question["options"],
                         "label": paper["key"][question["n"] - 1]})
    with open(ROOT / "compendium.jsonl", "w", encoding="utf-8") as handle:
        handle.writelines(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    print("\n".join(report))
    print(f"{len(rows)} questions with answers -> {ROOT / 'compendium.jsonl'}")


TRANSLATE_SYSTEM = (
    "You translate Catalan math competition problems. Translate the problem text and each option "
    "faithfully and plainly. Keep every number, unit, formula and name exactly. Options that are only "
    "numbers or formulas stay unchanged. Do not solve the problem and do not add anything.")
TRANSLATE_SCHEMA = {
    "type": "object", "required": ["items"], "additionalProperties": False,
    "properties": {"items": {"type": "array", "items": {
        "type": "object", "required": ["id", "text", "options"], "additionalProperties": False,
        "properties": {"id": {"type": "string"}, "text": {"type": "string"},
                       "options": {"type": "array", "items": {"type": "string"}}}}}}}
LANGUAGE_NAME = {"eng": "English", "esp": "Spanish"}


def translate(language, model="haiku", batch=12, workers=4, limit=None):
    """Translate the compendium rows to `language` with headless Claude; safe to stop and rerun."""
    from concurrent.futures import ThreadPoolExecutor

    from santolina_tutor.claude_cli import claude_json

    with open(ROOT / "compendium.jsonl", encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle]
    out = ROOT / f"compendium_{language}.jsonl"
    done = set()
    if out.exists():
        with open(out, encoding="utf-8") as handle:
            done = {json.loads(line)["id"] for line in handle}
    todo = [row for row in rows if row["id"] not in done][:limit]
    chunks = [todo[i:i + batch] for i in range(0, len(todo), batch)]

    def work(chunk):
        payload = [{"id": row["id"], "text": row["text"],
                    "options": [row["options"].get(letter, "") for letter in LETTERS] if row["options"] else []}
                   for row in chunk]
        prompt = (f"Translate these problems from Catalan to {LANGUAGE_NAME[language]}. Return one item per "
                  f"problem, same id, options in the same order.\n" + json.dumps(payload, ensure_ascii=False))
        try:
            reply, _ms = claude_json(prompt, TRANSLATE_SYSTEM, TRANSLATE_SCHEMA, model)
        except (RuntimeError, subprocess.TimeoutExpired, ValueError) as error:
            return [], str(error)[:120]
        by_id = {row["id"]: row for row in chunk}
        result = []
        for item in reply["items"]:
            source = by_id.get(item["id"])
            if source is None or len(item["options"]) not in (0, 5):
                continue
            options = dict(zip(LETTERS, item["options"])) if source["options"] else {}
            result.append({**source, "language": language, "text": item["text"], "options": options})
        return result, None

    written = 0
    with ThreadPoolExecutor(workers) as pool, open(out, "a", encoding="utf-8") as handle:
        for result, error in pool.map(work, chunks):
            if error:
                print("  failed batch:", error, flush=True)
            handle.writelines(json.dumps(row, ensure_ascii=False) + "\n" for row in result)
            handle.flush()
            written += len(result)
    print(f"{language}: {written} translated now, {len(done) + written} of {len(rows)} in {out}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("command", choices=["parse", "match", "compendium", "translate"])
    parser.add_argument("--language", choices=sorted(LANGUAGE_NAME), default="eng")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.command == "translate":
        translate(args.language, limit=args.limit)
    else:
        {"parse": parse, "match": match, "compendium": compendium}[args.command]()


if __name__ == "__main__":
    main()
