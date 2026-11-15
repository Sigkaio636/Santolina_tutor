# How to time a 2B model on the board

This guide measures how fast Qwen3.5 2B reads and writes on the Arduino UNO Q, and how much RAM it takes. We need those numbers to decide whether a 2B model can answer a problem inside the 60-second limit. The guide changes nothing in the copilot: the 2B model runs by hand on a spare port, and the default services come back at the end.

The test takes about 15 minutes, most of it the download.

## Before you start

- The board is set up to [step 7 of the board guide](../BOARD_SETUP.md#step-7-run-both-models-as-services).
- The board has internet access for the download, and 1.5 GB of free disk space. Check with `df -h ~`.

## 1. Download the model

On the board:

```bash
cd ~/models
wget --continue https://huggingface.co/bartowski/Qwen_Qwen3.5-2B-GGUF/resolve/7d26695454df6de5fbcce2e58681e62dae06ce43/Qwen_Qwen3.5-2B-Q4_K_M.gguf
sha256sum --check <<'EOF'
57a1085840f497d764a7fc5d346922dbde961efb54cc792ea81d694fd846a1d8  Qwen_Qwen3.5-2B-Q4_K_M.gguf
EOF
```

You should see `Qwen_Qwen3.5-2B-Q4_K_M.gguf: OK`. The file is 1.4 GB. If the download breaks, run the same `wget` again.

## 2. Stop the default language model

The final copilot would run the 2B model in place of the 0.8B model, so time it alone:

```bash
sudo systemctl stop math-llm
free -m
```

Write down the `available` column of the `Mem:` line.

## 3. Start the 2B model by hand (terminal 1)

Same options as the service, on port 8090:

```bash
~/llama.cpp/build/bin/llama-server \
  -m ~/models/Qwen_Qwen3.5-2B-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8090 \
  --threads 4 --ctx-size 4096 \
  --parallel 1 --cache-ram 0 --ctx-checkpoints 2 \
  --jinja --reasoning off --reasoning-budget 0
```

Leave it running. It is ready when it prints `server is listening`.

## 4. Measure (terminal 2)

Open a second terminal on the board. Check the server and the RAM:

```bash
curl -s http://127.0.0.1:8090/health
free -m
```

You should see `{"status":"ok"}`. Write down `available` again: the difference from step 2 is what the model takes.

### 4.1 Reading: one forced letter

```bash
curl -s http://127.0.0.1:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "system", "content": "You solve multiple-choice math competition problems for school students. Read the problem and the options, then reply with the letter of the correct option."}, {"role": "user", "content": "7. A baker fills trays with 12 rolls each. On Monday she bakes 9 full trays and sells 85 rolls. On Tuesday she bakes 6 more trays and sells 70 rolls. How many rolls are left at the end of Tuesday?\nA) 15\nB) 20\nC) 25\nD) 30\nE) 35\nAnswer:"}], "grammar": "root ::= [A-E]", "max_tokens": 1, "temperature": 0, "seed": 42}' \
  | jq '{answer: .choices[0].message.content, timings: (.timings | {prompt_n, prompt_per_second, prompt_ms})}'
```

The right answer is C. `prompt_per_second` is the reading speed.

### 4.2 Writing: a short program

```bash
time curl -s http://127.0.0.1:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "system", "content": "Write a short Python function solve() that computes the answer to the problem. Use only the standard library. Return the answer'"'"'s value, not a letter."}, {"role": "user", "content": "12. How many whole numbers from 1 to 200 are divisible by 3 but not by 5?\nA) 40\nB) 53\nC) 54\nD) 60\nE) 66"}], "max_tokens": 120, "temperature": 0, "seed": 42}' \
  | jq '{text: .choices[0].message.content, timings: (.timings | {prompt_n, prompt_per_second, predicted_n, predicted_per_second})}'
```

`predicted_per_second` is the writing speed. `time` prints the whole request's duration on the line `real`. A correct program returns 53.

### 4.3 Writing: worked steps

```bash
time curl -s http://127.0.0.1:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "system", "content": "Solve the math problem. Write only the key calculations, one short line each. Finish with Answer: and the letter of the correct option."}, {"role": "user", "content": "7. A baker fills trays with 12 rolls each. On Monday she bakes 9 full trays and sells 85 rolls. On Tuesday she bakes 6 more trays and sells 70 rolls. How many rolls are left at the end of Tuesday?\nA) 15\nB) 20\nC) 25\nD) 30\nE) 35"}], "max_tokens": 150, "temperature": 0, "seed": 42}' \
  | jq '{text: .choices[0].message.content, timings: (.timings | {prompt_n, prompt_per_second, predicted_n, predicted_per_second})}'
```

Run each request twice. The second run of the same request reads fewer tokens, because the server keeps the start of the prompt: report the first run.

## 5. Report

Send these numbers:

| What | Where it comes from |
| --- | --- |
| RAM the model takes, in MB | `available` in step 2 minus `available` in step 4 |
| Reading speed | `prompt_per_second` in 4.1 |
| Writing speed | `predicted_per_second` in 4.2 and 4.3 |
| Whole-request time | `real` in 4.2 and 4.3 |
| The three answers | The letter in 4.1, the program in 4.2, the steps in 4.3 |

How to read them. A practice problem with its options and instruction is about 110 tokens, and a useful answer is 60 to 150 written tokens. The copilot keeps 5 seconds of margin, so the model fits when:

```text
110 / reading speed + written tokens / writing speed <= 55 seconds
```

| Reading | Writing | Verdict |
| --- | --- | --- |
| 5 tokens/s or more | 2.5 tokens/s or more | Fits with about 80 written tokens: enough for a short program |
| 4 tokens/s | 2 tokens/s | Fits with about 55 written tokens: only short programs |
| Under 3 tokens/s | Under 1.5 tokens/s | Only the one-letter answer fits |

For comparison, the 0.8B model reads about 11 tokens per second and writes about 6.

## 6. Go back to the default

Stop the 2B server with `Ctrl+C` in terminal 1. Then:

```bash
sudo systemctl start math-llm
curl -s http://127.0.0.1:8081/health
```

You should see `{"status":"ok"}`. Leave the 2B file in `~/models`: if the model is adopted, `config.env` will point at it.

## Optional: the same test with Noema-2B

[Noema-2B](https://huggingface.co/NoemaAI-labs/Noema-2B) is Qwen3.5 2B trained further on maths and short programs (Apache-2.0). It has the same size, so the speeds should match; the answers may differ. Download it and repeat steps 3 to 5 with its file name:

```bash
cd ~/models
wget --continue https://huggingface.co/NoemaAI-labs/Noema-2B-GGUF/resolve/66d96b1efe4fec42eda0bdea42563fb3ec728c73/Noema-2B-Q4_K_M.gguf
sha256sum --check <<'EOF'
e39e79c60f0411304ec6813ca3a07ba7dcd1c9fd3312202ad9de7a1b455cb762  Noema-2B-Q4_K_M.gguf
EOF
```

## If you work with Claude on the board

Give it this request:

> Read docs/how-to/time-2b-model-on-board.md and follow steps 1 to 6 on the board. Use the unoq-board skill to connect. Don't change config.env or any code. Report the table of step 5, and confirm that math-llm is running again at the end.
