"""Head B: the model writes a short Python solve(), the board runs it and matches an option.

Standard library only, like the rest of copilot/. The same functions run in three
places, so they can't drift apart: on the board, in the laptop verifier
(santolina_tutor/finetune/programs.py) and in the Kaggle evaluation.

    letter, info = answer(problem)   # letter is None when head B can't answer

Head B answers only when the program runs and its value matches exactly one option.
Otherwise the caller falls back to the one-letter answer (copilot/llm.py).
SOLVER=program (copilot/pipeline.py) uses the zero-shot prompt and solve_board() below.
"""
import ast
from fractions import Fraction
import json
import os
import re
import subprocess
import sys
import tempfile

LETTERS = "ABCDE"

# Kept short and stable: llama-server caches the start of the prompt.
SYSTEM = ("Write a short Python function solve() that computes the answer to the problem. "
          "Use only the standard library. Return the answer's value, not a letter.")

RUNNER = """
import json
from fractions import Fraction
r = solve()
if isinstance(r, Fraction):
    r = f"{r.numerator}/{r.denominator}"
elif isinstance(r, bool) or not isinstance(r, (int, float, str)):
    r = str(r)
print(json.dumps(r))
"""


def format_problem(problem):
    lines = [problem["text"].strip()]
    lines += [f"{k}) {v}" for k, v in sorted((problem.get("options") or {}).items())]
    return "\n".join(lines)


def build_messages(problem, example=None):
    """The chat for one problem. example = (similar problem, its program): one solved turn first."""
    messages = [{"role": "system", "content": SYSTEM}]
    if example is not None:
        similar, program = example
        messages += [{"role": "user", "content": format_problem(similar)},
                     {"role": "assistant", "content": program.strip()}]
    return messages + [{"role": "user", "content": format_problem(problem)}]


# Zero-shot prompt for a model that was not fine-tuned (SOLVER=program). Untuned models
# otherwise write equations as code and spend their budget on comments. The system prompt
# and the two made-up examples (not from M3Kang or the practice set) never change, so the
# server reads them once, at warm-up, and keeps them in its prompt cache.
ZERO_SHOT_SYSTEM = ("Write a Python function solve() that computes the answer to the problem. "
                    "Prefer brute force with loops over clever algebra. No comments, no explanation, "
                    "at most 12 lines. Use only the standard library. Return the answer's value, "
                    "not a letter. Reply with only the code in one ```python block.")
SHOTS = [
    (("How many two-digit numbers have digits that add up to 9?\n"
     "A) 7\nB) 8\nC) 9\nD) 10\nE) 11"),
     "```python\ndef solve():\n    return sum(1 for n in range(10, 100) if n // 10 + n % 10 == 9)\n```"),
    (("A father is three times as old as his son. In 10 years he will be twice as old as his son. "
     "How old is the son now?\nA) 5\nB) 8\nC) 10\nD) 12\nE) 15"),
     ("```python\ndef solve():\n    for son in range(1, 100):\n        father = 3 * son\n"
     "        if father + 10 == 2 * (son + 10):\n            return son\n```")),
]
ASK_LETTER = "Which option is correct? Reply with the letter."
NO_THINKING = {"enable_thinking": False}  # 2B models think by default and never reach the code
_FENCE = re.compile(r"^\s*```[a-zA-Z]*\n")


def zero_shot_messages(problem):
    """System prompt, the two worked examples, then the problem."""
    messages = [{"role": "system", "content": ZERO_SHOT_SYSTEM}]
    for question, program in SHOTS:
        messages += [{"role": "user", "content": question}, {"role": "assistant", "content": program}]
    return messages + [{"role": "user", "content": format_problem(problem)}]


def code_from_reply(text):
    """The program in a reply: drop an opening fence and anything after a closing one."""
    return _FENCE.sub("", text, count=1).split("```")[0].strip()


def extract_program(text):
    """The code from a model reply, without Markdown fences if the model added them."""
    fenced = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return (fenced.group(1) if fenced else text).strip()


def _limits(seconds):
    def apply():
        import resource  # Linux only, like the board
        resource.setrlimit(resource.RLIMIT_CPU, (seconds, seconds))
        resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))  # 1 GB
    return apply


def run_program(source, seconds=2):
    """Run solve() in a separate, isolated Python process. Returns (value, error)."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "prog.py")
        with open(path, "w") as f:
            f.write(source + "\n" + RUNNER)
        try:
            run = subprocess.run([sys.executable, "-I", path], cwd=d, capture_output=True,
                                 text=True, timeout=seconds + 1, env={},
                                 preexec_fn=_limits(seconds), check=False)
        except subprocess.TimeoutExpired:
            return None, "timeout"
    if run.returncode != 0:
        return None, (run.stderr.strip().splitlines() or ["killed"])[-1][:200]
    try:
        return json.loads(run.stdout.strip().splitlines()[-1]), None
    except (json.JSONDecodeError, IndexError):
        return None, "no output"


def as_number(x):
    """A number from a result or an option ('1/2', '2.5', '2,5', '12 cm', '−3'), else None."""
    if isinstance(x, bool):
        return None
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, float):
        return Fraction(x).limit_denominator(10**9)
    s = str(x).strip().replace("−", "-").replace("–", "-").replace(" ", "")
    s = re.sub(r"[a-zA-Z%°²³€$]+$", "", s)
    if re.fullmatch(r"-?\d+,\d+", s):  # decimal comma (cat, esp)
        s = s.replace(",", ".")
    try:
        return Fraction(s)
    except (ValueError, ZeroDivisionError):
        return None


def _text_key(x):
    return re.sub(r"\s+", "", str(x)).lower().replace("×", "x")


def matches(value, options):
    """The letters whose option equals the program's value."""
    v = as_number(value)
    hits = []
    for letter, text in options.items():
        o = as_number(text)
        if v is not None and o is not None:
            if abs(v - o) <= Fraction(1, 10**6) * max(1, abs(o)):
                hits.append(letter)
        elif _text_key(value) == _text_key(text):
            hits.append(letter)
    return sorted(hits)


def is_constant(source):
    """True if solve() only returns a literal: a value worked out by hand, not computed."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "solve":
            body = [n for n in node.body if not isinstance(n, ast.Expr)]
            return (len(body) == 1 and isinstance(body[0], ast.Return)
                    and isinstance(body[0].value, (ast.Constant, ast.UnaryOp)))
    return False


def judge(source, options, seconds=2):
    """Run a program and match it: {"letter", "value", "error", "hits"}; letter only if unique."""
    value, error = run_program(source, seconds)
    hits = matches(value, options) if error is None else []
    return {"letter": hits[0] if len(hits) == 1 else None, "value": value, "error": error,
            "hits": hits}


def _base(url):
    """http://host:port from a server URL such as http://host:port/v1/chat/completions."""
    return url.split("/v1/")[0].rstrip("/")


_SENTINEL = "\u0000REPLY\u0000"
_suffix_cache = {}


def _follow_suffix(base):
    """The chat-template text that closes the model's reply and asks for the letter."""
    if base not in _suffix_cache:
        from .client import post
        prompt = post(base + "/apply-template", {
            "messages": [{"role": "user", "content": "x"}, {"role": "assistant", "content": _SENTINEL},
                         {"role": "user", "content": ASK_LETTER}],
            "chat_template_kwargs": NO_THINKING}, timeout=30)["prompt"]
        _suffix_cache[base] = prompt.split(_SENTINEL, 1)[1]
    return _suffix_cache[base]


def program_messages(problem, prompt="zero_shot"):
    """zero_shot: an untuned model with the two examples; tuned: the fine-tuned model's
    training prompt (build_messages, short system prompt, no example)."""
    return build_messages(problem) if prompt == "tuned" else zero_shot_messages(problem)


def program_turn(url, problem, n_predict, seed=42, t_max_ms=0, timeout=600, prompt="zero_shot"):
    """Ask for a program. Returns (rendered prompt, reply, timings).

    The chat endpoint makes the server save cache checkpoints at message boundaries, so
    the next problem goes back to the end of the fixed prefix. A raw /completion request
    saves none there, and a hybrid model (Qwen3.5, Noema) then reads the whole prompt again.
    No stop string: the model closes its fence and ends, so the reply text is exactly
    what the server holds in its cache, and letter_turn() can continue it.
    """
    from .client import post
    base = _base(url)
    messages = program_messages(problem, prompt)
    body = {"messages": messages, "max_tokens": n_predict, "temperature": 0, "seed": seed,
            "cache_prompt": True, "chat_template_kwargs": NO_THINKING}
    if t_max_ms:
        body["t_max_predict_ms"] = int(t_max_ms)
    response = post(base + "/v1/chat/completions", body, timeout=timeout)
    prompt = post(base + "/apply-template", {"messages": messages, "chat_template_kwargs": NO_THINKING},
                  timeout=30)["prompt"]
    return prompt, response["choices"][0]["message"].get("content") or "", response.get("timings", {})


def letter_turn(url, prompt, raw, seed=42, timeout=600):
    """One letter, asked right after the program: only the question is new to the cache.

    A raw continuation of the program request. Through the chat endpoint the template
    drops the reply's empty think block from the history, so the cache would not match.
    """
    from .client import post
    base = _base(url)
    response = post(base + "/completion", {
        "prompt": prompt + raw + _follow_suffix(base), "n_predict": 1, "temperature": 0,
        "seed": seed, "cache_prompt": True, "grammar": "root ::= [A-E]"}, timeout=timeout)
    return response.get("content", "").strip(), response.get("timings", {})


def warm_up(url, timeout=180, prompt="zero_shot"):
    """Read the fixed prefix once, before the first problem, so no problem pays for it."""
    program_turn(url, {"text": "What is 1 + 1?", "options": {}}, n_predict=1, timeout=timeout,
                 prompt=prompt)


def solve_board(problem, url, deadline, seed=42, read_tps=4.86, max_tokens=160, run_seconds=2,
                prompt="zero_shot"):
    """SOLVER=program: write solve(), run it, match an option; else ask for the letter.

    deadline is a time.perf_counter() value. Returns (letter or None, info); None means
    the caller keeps its own fallback. The program may write until the deadline minus one
    second for running it: correct programs need 40 to 80 tokens, and every token counts.
    The follow-up letter (about 25 tokens of reading) is asked only if time is left.
    """
    import time

    def left():
        return deadline - time.perf_counter()

    # reading time of the new part only: the prefix is in the cache after warm_up()
    fresh = len(format_problem(problem)) / 3.5 + 25  # about 3.5 characters per token
    letter_cost = 30 / read_tps + 1.0
    write_ms = (left() - fresh / read_tps - 1.0) * 1000
    info = {"program": "", "value": None, "error": None, "how": "none", "timings": {}}
    if write_ms > 3000:
        rendered, raw, info["timings"] = program_turn(url, problem, max_tokens, seed, write_ms,
                                                      max(left(), 1.0), prompt)
        info["program"] = code_from_reply(raw)
        result = judge(info["program"], problem.get("options") or {},
                       max(1, min(run_seconds, int(left()))))
        info.update(value=result["value"], error=result["error"])
        if result["letter"]:
            info["how"] = "program"
            return result["letter"], info
    else:  # no time to write: ask for the letter right after the problem
        rendered, raw, _ = program_turn(url, problem, 1, seed, 0, max(left(), 1.0), prompt)
    if left() < letter_cost:
        return None, info
    letter, _ = letter_turn(url, rendered, raw, seed, max(left(), 1.0))
    info["how"] = "letter"
    return letter, info


def answer(problem, timeout=40, max_tokens=160, seconds=2, example=None):
    """On the board: ask the model for a program, run it, return (letter or None, info)."""
    from .client import post
    from .config import CONFIG
    url = f"http://127.0.0.1:{CONFIG['LLM_PORT']}/v1/chat/completions"
    response = post(url, {"messages": build_messages(problem, example), "max_tokens": max_tokens,
                          "temperature": 0, "seed": int(CONFIG["SEED"]), "cache_prompt": True},
                    timeout=timeout)
    program = extract_program(response["choices"][0]["message"]["content"])
    result = judge(program, problem.get("options") or {}, seconds)
    return result["letter"], {**result, "program": program, "timings": response.get("timings", {})}
