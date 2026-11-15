"""The baseline copilot: one problem in, one letter out.

This is the file to change first. predict.py and eval.py both call solve(),
so whatever you build here is exactly what the official run measures.
"""
import socket
import time
import urllib.error

from .config import CONFIG
from .llm import URL, answer_letter
from .prior import best
from .program_head import solve_board, warm_up

TIME_LIMIT = float(CONFIG["TIME_LIMIT_SECONDS"])
FALLBACK = CONFIG["FALLBACK_ANSWER"]
MARGIN = 3.0  # seconds kept free for Python and for writing the answer
# "prior": answer from where the right option tends to sit, no model call (copilot/prior.py).
# "letter": the baseline, one forced letter from the model, with the prior as its fallback.
# "program": the model writes solve(), Python runs it and matches an option; if that fails,
#   the model gives a letter in the same conversation (copilot/program_head.py).
SOLVER = CONFIG.get("SOLVER", "prior")
READ_TPS = float(CONFIG.get("READ_TPS", "4.86"))  # board reading speed of the model, tokens/s
# "zero_shot" for an untuned model (two worked examples), "tuned" for a model fine-tuned on
# santolina_tutor/finetune/program_data.py (short system prompt, no example)
PROGRAM_PROMPT = CONFIG.get("PROGRAM_PROMPT", "zero_shot")
# "nmt": translate Catalan problems to English first, inside the clock (copilot/nmt.py)
TRANSLATE = CONFIG.get("TRANSLATE", "")
_warm = {"done": False, "error": ""}


def solve(problem, index=None, k=0, exclude_id=None, image_b64=None, llm_url=URL,
          time_limit=TIME_LIMIT):
    """Return {"answer", "seconds", "status", ...} for one problem.

    index and k turn on retrieval: the k most similar solved problems are
    added to the prompt as examples. Each example costs reading time.
    image_b64 and llm_url send the problem image to a vision server.
    """
    if SOLVER == "program" and not _warm["done"]:
        # read the fixed prompt prefix once, before the first problem's clock starts
        _warm["done"] = True
        try:
            if TRANSLATE == "nmt":  # load the NMT model before the clock too
                from .nmt import available
                available()
            warm_up(llm_url, prompt=PROGRAM_PROMPT)
        except Exception as error:  # noqa: BLE001 - a failed warm-up only makes the first problem slower
            _warm["error"] = f"{type(error).__name__}: {error}"
    start = time.perf_counter()
    result = {"answer": FALLBACK, "status": "ok", "prompt_tokens": 0, "retrieved": "", "examples": []}
    try:
        result["answer"] = best(problem)
    except (ArithmeticError, AttributeError, KeyError, TypeError, ValueError) as error:
        # a malformed problem must still get a letter
        result["status"] = f"prior error: {error}"
    if SOLVER == "prior" and image_b64 is None:
        result["seconds"] = round(time.perf_counter() - start, 2)
        return result
    try:
        examples = []
        if index is not None and k > 0:
            hits = index.search(problem, k=k, exclude_id=exclude_id)
            examples = [p for _score, p in hits]
            result["examples"] = hits
            result["retrieved"] = ";".join(f"{p['id']}:{s:.2f}" for s, p in hits)
        remaining = time_limit - (time.perf_counter() - start) - MARGIN
        if SOLVER == "program" and image_b64 is None:
            if TRANSLATE == "nmt":
                from .nmt import translate_problem
                problem = translate_problem(problem)
            letter, info = solve_board(problem, llm_url, start + time_limit - MARGIN,
                                       seed=int(CONFIG["SEED"]), read_tps=READ_TPS,
                                       prompt=PROGRAM_PROMPT)
            if letter is not None and (len(letter) != 1 or letter not in "ABCDE"):
                raise ValueError(f"the model replied {letter!r}, not one letter A-E")
            # no letter: no time was left for it, so the prior's letter stays
            result.update(answer=letter or result["answer"], how=info["how"], value=info["value"],
                          prompt_tokens=info["timings"].get("prompt_n", 0))
            result["seconds"] = round(time.perf_counter() - start, 2)
            return result
        letter, timings = answer_letter(problem, examples, timeout=max(remaining, 1.0),
                                        image_b64=image_b64, url=llm_url)
        if len(letter) != 1 or letter not in "ABCDE":
            raise ValueError(f"the model replied {letter!r}, not one letter A-E")
        result["answer"] = letter
        result["prompt_tokens"] = timings.get("prompt_n", 0)
    except Exception as error:  # noqa: BLE001 - any failure must still give a letter
        # A dropped connection, a bad JSON body, a reply without "choices",
        # an HTTP 500: whatever goes wrong, this problem gets FALLBACK and the
        # run goes on to the next one.
        result["answer"] = FALLBACK
        if isinstance(error, urllib.error.HTTPError):
            error.close()  # an HTTP error still holds the open response
        if isinstance(getattr(error, "reason", None), BaseException):
            error = error.reason  # urllib wraps the real cause in URLError
        if isinstance(error, (socket.timeout, TimeoutError)):
            result["status"] = "timeout"
        else:
            result["status"] = f"error: {type(error).__name__}: {error}".replace("\n", " ")
    result["seconds"] = round(time.perf_counter() - start, 2)
    return result
