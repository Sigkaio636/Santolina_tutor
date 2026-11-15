"""Ask the small language model for one letter, A to E."""
from .config import CONFIG
from .client import get, post

URL = f"http://127.0.0.1:{CONFIG['LLM_PORT']}/v1/chat/completions"
# "decider": plain-text prompt for Mapika/decider-* models, sent to /completion
PROMPT = CONFIG.get("LLM_PROMPT", "chat")

# Keep the system prompt stable: llama-server caches the start of the prompt,
# so text that never changes is only read once.
SYSTEM = ("You solve multiple-choice math competition problems for school students. "
          "Read the problem and the options, then reply with the letter of the correct option.")


def format_problem(problem, sees_image=False):
    lines = [problem["text"].strip()]
    options = problem.get("options") or {}
    for letter in "ABCDE":
        if letter in options:
            lines.append(f"{letter}) {options[letter]}")
    if not options:
        lines.append("(The options are in the picture.)" if sees_image else
                     "(The options are in a picture that you can't see. Pick the most likely letter.)")
    return "\n".join(lines)


def build_messages(problem, examples=(), image_b64=None):
    """image_b64 is a PNG as base64 text. Only a server started with --mmproj can see it."""
    messages = [{"role": "system", "content": SYSTEM}]
    for ex in examples:  # solved problems retrieved with RAG, if any
        messages.append({"role": "user", "content": format_problem(ex) + "\nAnswer:"})
        messages.append({"role": "assistant", "content": ex["label"]})
    text = format_problem(problem, sees_image=bool(image_b64)) + "\nAnswer:"
    if image_b64:
        content = [{"type": "image_url", "image_url": {"url": "data:image/png;base64," + image_b64}},
                   {"type": "text", "text": text}]
    else:
        content = text
    messages.append({"role": "user", "content": content})
    return messages


def build_decider_prompt(problem, sees_image=False):
    """The 'plain' layout of Mapika/decider: the letter is read right after 'Answer: ('.

    Options missing from the text are 'figure X' when the model sees the image, as in
    decider's own Raven training data, and 'option X' when it does not.
    """
    options = problem.get("options") or {}
    filler = "figure" if sees_image else "option"
    lines = ["Context:\n" + problem["text"].strip(), "",
             "Question: Which option is the correct answer?", "Options:"]
    for letter in "ABCDE":
        lines.append(f"({letter}) {options.get(letter, filler + ' ' + letter)}")
    return "\n".join(lines) + "\nAnswer: ("


_markers = {}


def media_marker(url):
    """The server's media placeholder. Recent llama-server builds pick a random one and
    publish it in /props; older ones use mtmd's default."""
    base = url.split("/v1/")[0].split("/completion")[0]
    if base not in _markers:
        _markers[base] = get(base + "/props").get("media_marker", "<__media__>")
    return _markers[base]


def answer_letter(problem, examples=(), timeout=60, image_b64=None, url=URL):
    """Return (letter, timings). The grammar makes any other output impossible."""
    if PROMPT == "decider":  # no RAG examples in this layout
        text = build_decider_prompt(problem, sees_image=bool(image_b64))
        # decider puts the image before the prompt (decider/vision/model.py)
        prompt = ({"prompt_string": media_marker(url) + text, "multimodal_data": [image_b64]}
                  if image_b64 else text)
        response = post(url.replace("/v1/chat/completions", "/completion"), {
            "prompt": prompt,
            "grammar": "root ::= [A-E]",
            "n_predict": 1,
            "temperature": 0,
            "seed": int(CONFIG["SEED"]),
            "cache_prompt": True,
        }, timeout=timeout)
        return response["content"].strip(), response.get("timings", {})
    response = post(url, {
        "messages": build_messages(problem, examples, image_b64),
        "grammar": "root ::= [A-E]",
        "max_tokens": 1,
        "temperature": 0,
        "seed": int(CONFIG["SEED"]),
        "cache_prompt": True,
    }, timeout=timeout)
    letter = response["choices"][0]["message"]["content"].strip()
    return letter, response.get("timings", {})
