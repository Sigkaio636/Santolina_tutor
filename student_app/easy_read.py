"""Easy read: the problem text one sentence per line, with the question last.

It's a code transform with no model, so it's instant and it can't change the maths: every
word and number of the input is in the output. Only the place of the question changes.
"""

# A dot after one of these doesn't end a sentence ("p. ex.", "e.g.", "3 cm. de llarg").
ABBREVIATIONS = {
    "ex", "e.g", "i.e", "etc", "cm", "mm", "km", "kg", "min", "fig", "núm", "num", "nº",
    "pàg", "pág", "aprox", "approx", "vs", "sr", "sra", "dr", "dra", "art", "tel", "no",
}  # fmt: skip
OPEN, CLOSE = "([{", ")]}"
QUOTES = {"“": "”", "«": "»"}


def _dot_ends_sentence(text: str, i: int, line_start: int) -> bool:
    start = i
    while start > line_start and not text[start - 1].isspace() and text[start - 1] not in OPEN:
        start -= 1
    word = text[start:i].lower()
    # A capital alone is an initial ("A. Riba"). A small letter alone can be a unit that
    # ends the sentence ("5 m. Which…"): the check on the next word decides.
    if word in ABBREVIATIONS or (len(word) == 1 and text[start].isupper()):
        return False
    if word.isdigit() and not text[line_start:start].strip():  # "1. First step"
        return False
    rest = text[i + 1 :].lstrip()
    return not (rest and rest[0].islower())  # "…and so on. then" is not a new sentence


def sentences(text: str) -> list | None:
    """The sentences of `text` in order, or None when brackets or quotes don't balance."""
    out, start, depth, quote, line_start = [], 0, 0, None, 0
    i = 0
    while i < len(text):
        ch = text[i]
        inside = depth > 0 or quote is not None
        if ch == "\n" and not inside:
            out.append(text[start:i])
            start = line_start = i + 1
        elif quote is not None:
            if ch == quote:
                quote = None
        elif ch == '"' or ch in QUOTES:
            quote = QUOTES.get(ch, '"')
        elif ch in OPEN:
            depth += 1
        elif ch in CLOSE:
            depth -= 1
            if depth < 0:
                return None
        elif ch in ".?!" and not inside:
            end = i
            while end + 1 < len(text) and text[end + 1] in ".?!":
                end += 1
            ellipsis = end > i and set(text[i : end + 1]) == {"."}
            at_gap = end + 1 == len(text) or text[end + 1].isspace()
            if at_gap and not ellipsis and (ch != "." or _dot_ends_sentence(text, i, line_start)):
                out.append(text[start : end + 1])
                start = end + 1
            i = end
        i += 1
    if depth or quote is not None:
        return None
    out.append(text[start:])
    return [s.strip() for s in out if s.strip()]


def easy_read(text: str) -> str:
    """`text` with one sentence per line and the last question at the end, after a blank line.

    Returns the text unchanged when it's a single sentence or it can't be split safely.
    """
    parts = sentences(text or "")
    if not parts or len(parts) < 2:
        return text
    questions = [k for k, s in enumerate(parts) if s.endswith("?")]
    if not questions:
        return "\n".join(parts)
    question = parts.pop(questions[-1])
    return "\n".join(parts) + "\n\n" + question
