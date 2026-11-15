#!/usr/bin/env python3
"""Time the figure path on the board: the 0.8B vision server writes a program from the image.

For each problem with a figure (text_only false), it sends the problem image with the
two-example program prompt (copilot/program_head.py), runs the program and matches it
to the options. It prints the wall time of each problem and the tokens read and written.
Standard library only, like the rest of the board code.

    python3 board/time_vision.py --input data/demo/train.jsonl --images data/demo/images --limit 6

Start the vision server first (docs/BOARD_SETUP.md, "Let the model see the image"),
with --image-max-tokens 128. Output has problem IDs and numbers only, no problem text.
"""
import argparse
import base64
import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from copilot.client import post
from copilot.program_head import NO_THINKING, code_from_reply, judge, zero_shot_messages


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default="data/demo/train.jsonl")
    ap.add_argument("--images", default="data/demo/images", help="<id>_<language>.png files")
    ap.add_argument("--url", default="http://127.0.0.1:8083/v1/chat/completions")
    ap.add_argument("--limit", type=int, default=6)
    ap.add_argument("--max-tokens", type=int, default=90)
    args = ap.parse_args()

    with open(args.input) as f:
        rows = [json.loads(line) for line in f if line.strip()]
    rows = [r for r in rows if r.get("text_only") is False][:args.limit]
    # the fixed prefix (system prompt and examples) is read once, before the clock, as in predict.py
    post(args.url, {"messages": zero_shot_messages({"text": "What is 1 + 1?", "options": {}}),
                    "max_tokens": 1, "cache_prompt": True, "chat_template_kwargs": NO_THINKING},
         timeout=300)
    seconds, right = [], 0
    for r in rows:
        with open(os.path.join(args.images, f"{r['id']}_{r['language']}.png"), "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        start = time.perf_counter()
        messages = zero_shot_messages(r)
        messages[-1] = {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}},
            {"type": "text", "text": messages[-1]["content"]}]}
        response = post(args.url, {"messages": messages, "max_tokens": args.max_tokens, "temperature": 0,
                                   "seed": 42, "cache_prompt": True, "chat_template_kwargs": NO_THINKING},
                        timeout=300)
        result = judge(code_from_reply(response["choices"][0]["message"].get("content") or ""),
                       r.get("options") or {})
        seconds.append(time.perf_counter() - start)
        right += result["letter"] == r.get("label")
        t = response.get("timings", {})
        print(f"{r['id']} {r['language']}: {seconds[-1]:.1f} s | read {t.get('prompt_n')} tokens in "
              f"{t.get('prompt_ms', 0) / 1000:.1f} s | wrote {t.get('predicted_n')} in "
              f"{t.get('predicted_ms', 0) / 1000:.1f} s | answer {result['letter']} (truth {r.get('label')})",
              flush=True)
    print(f"\n{len(seconds)} problems: mean {statistics.mean(seconds):.1f} s, worst {max(seconds):.1f} s, "
          f"over 57 s: {sum(s > 57 for s in seconds)}, program right: {right}")


if __name__ == "__main__":
    main()
