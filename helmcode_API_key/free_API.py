import os
from getpass import getpass

from openai import OpenAI

BASE_URL = "https://api.helmcode.com/v1"

# Models from https://helmcode.com/docs/models
PLAN_MODELS = ["glm5.3-flash", "qwen3.6", "gemma4", "deepseek-v4-flash"]
ADDON_MODELS = ["glm5.3"]  # flagship, paid per-key add-on, not covered by a plan
FRONTIER_MODELS = [  # paid from prepaid credit
    "claude-fable-5",
    "claude-opus-5",
    "claude-sonnet-5",
    "claude-haiku-4-5",
    "gpt-5.6-sol",
    "gpt-5.6-terra",
    "gpt-5.6-luna",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
]
MODELS = PLAN_MODELS + ADDON_MODELS + FRONTIER_MODELS


def ask_api_key() -> str:
    # Use HELMCODE_API_KEY if set, otherwise prompt (input is hidden).
    key = os.environ.get("HELMCODE_API_KEY") or getpass("Helmcode API key: ").strip()
    if not key:
        raise SystemExit("No API key provided.")
    return key


def ask_model() -> str:
    print("\nAvailable models:")
    for i, m in enumerate(MODELS, 1):
        tag = (
            "" if m in PLAN_MODELS
            else "  (add-on)" if m in ADDON_MODELS
            else "  (frontier, prepaid credit)"
        )
        print(f"  {i:2d}. {m}{tag}")
    while True:
        choice = input(f"Choose model [1-{len(MODELS)}] or type an ID (default gemma4): ").strip()
        if not choice:
            return "qwen3.6"
        if choice.isdigit() and 1 <= int(choice) <= len(MODELS):
            return MODELS[int(choice) - 1]
        if not choice.isdigit():
            return choice
        print("Invalid number.")


def main() -> None:
    client = OpenAI(base_url=BASE_URL, api_key=ask_api_key())
    model = ask_model()
    print(f"\nUsing {model}. Empty line or Ctrl-D to quit.\n")
    messages = []
    while True:
        try:
            prompt = input("you> ").strip()
        except EOFError:
            break
        if not prompt:
            break
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(model=model, messages=messages)
        answer = resp.choices[0].message.content
        messages.append({"role": "assistant", "content": answer})
        print(f"\n{model}> {answer}\n")


if __name__ == "__main__":
    main()
