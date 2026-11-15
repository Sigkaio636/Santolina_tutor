"""Catalan to English with Softcatalà's NMT model (CTranslate2), before the program solver.

The math models write much better programs from English: on the practice set, Qwen2.5-Math
went from 14 to 26 of 50 Catalan problems with this step. The model is softcatala/
translate-cat-eng (MIT, 71 MB, int8). It needs the ctranslate2 and sentencepiece packages,
installed offline from wheels (docs/how-to/try-qwen-math-nmt.md). Without them, or without
the model folder, translate_problem() returns the problem unchanged.
"""
import json
import os
import re
import sys

from .config import CONFIG

MODEL_DIR = os.path.expanduser(CONFIG.get("NMT_MODEL_DIR", "~/models/softcatala-cat-eng"))
# folder with the ctranslate2, sentencepiece, numpy and pyyaml wheels extracted (no pip needed);
# added to sys.path so that a plain `python3 predict.py` finds them
SITE = os.path.expanduser(CONFIG.get("NMT_SITE", "~/nmt-site"))
THREADS = int(CONFIG.get("NMT_THREADS", "4"))
# symbols missing from the NMT vocabulary come out as unknown pieces: write them in ASCII or words
ASCII = {"−": "-", "–": "-", "×": " x ", "÷": " / ", "·": " * ", "²": "^2", "³": "^3", "√": "sqrt",
         "≤": " at most ", "≥": " at least ", "≠": " is not ", "…": "..."}
WORDS = {"=": " equals ", "^": " to the power ", "<": " less than ", ">": " greater than "}
HAS_WORD = re.compile(r"[A-Za-zÀ-ÿ]")
_state = {}


def _load():
    """The translator, the tokenizer and the vocabulary's characters; None if unavailable."""
    if "model" not in _state:
        if os.path.isdir(SITE) and SITE not in sys.path:
            sys.path.insert(0, SITE)
        try:
            import ctranslate2
            import sentencepiece
            with open(os.path.join(MODEL_DIR, "shared_vocabulary.json")) as f:
                vocab = set("".join(json.load(f)))
            _state["model"] = (
                ctranslate2.Translator(MODEL_DIR, device="cpu", inter_threads=1, intra_threads=THREADS),
                sentencepiece.SentencePieceProcessor(model_file=os.path.join(MODEL_DIR, "sp_m.model")),
                vocab)
        except (ImportError, OSError, RuntimeError, ValueError):
            _state["model"] = None
    return _state["model"]


def available():
    return _load() is not None


def translate(texts):
    """English for each Catalan text, in one batch."""
    translator, sp, vocab = _load()
    texts = ["".join(ASCII.get(c, c) for c in t) for t in texts]
    out = translator.translate_batch([sp.encode(t, out_type=str) for t in texts], beam_size=1)
    result = []
    for text, o in zip(texts, out):
        # SentencePiece writes an unknown piece as " ⁇ "; take one space on each side with it
        english = re.sub(r" ?⁇ ?", "<unk>", sp.decode(o[0]["tokens"]))
        unknown = [c for c in text if not c.isspace() and c not in vocab]
        if english.count("<unk>") == len(unknown):
            for c in unknown:  # the symbols keep their order through the translation
                english = english.replace("<unk>", c, 1)
        else:
            english = english.replace("<unk>", "?")
            for c, w in WORDS.items():
                english = english.replace(c, w)
        result.append(english)
    return result


def translate_problem(problem):
    """The problem with its statement, and any option with words, in English."""
    if problem.get("language") != "cat" or not available():
        return problem
    m = re.match(r"\s*(\d+\.\s*)(.*)", problem["text"], re.DOTALL)  # keep the "12. " prefix as is
    prefix, body = (m.group(1), m.group(2)) if m else ("", problem["text"])
    options = problem.get("options") or {}
    worded = [k for k, v in sorted(options.items()) if HAS_WORD.search(str(v))]
    english = translate([body] + [str(options[k]) for k in worded])
    return {**problem, "text": prefix + english[0],
            "options": {**options, **dict(zip(worded, english[1:]))}}
