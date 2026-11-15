# Intent router bake-off, round 3: decider-2b against decider-0.8b

Status: **pre-registered on 2026-11-14, before any run.** We add the results
below the line "Results" after the runs.

## Question

The team adopted decider-0.8b as the tutor's intent router, behind two
rules (see the [conclusion](2026-11-router-0.8b-conclusion.md)). It is weak
on two kinds of message: "solution" messages in Catalan and Spanish, and
messages with several option letters. Does the bigger decider-2b, from the
same family, label the student's message better? And can the board hold it?

## Candidate

`Mapika/decider-2b-GGUF`, revision `0df001b`, Apache-2.0, version v12 of
2026-10-20, base model Qwen3.5-2B-Base. The model card says English only.
Its prompt layout is `plain`, the same as decider-0.8b, so the script builds
the same prompts. We use the official GGUF files and do not convert
anything:

| File | Size | Role |
|---|---|---|
| `decider-2b-v12-Q4_K_M.gguf` | 1.27 GB | Candidate: the only file that fits on the board |
| `decider-2b-v12-Q8_0.gguf` | 2.0 GB | Quality ceiling, laptop only |

The board has about 2.5 GB free next to its two model servers
([BOARD_SETUP.md](../BOARD_SETUP.md)). Q4_K_M and its cache fit in that
space. Q8_0 does not fit next to App Lab.

## Data

The 250 messages of rounds 1 and 2: `laptop/router_messages.json` (100) and
`laptop/router_messages_r2.json` (150), 80 of them in Catalan. Nothing was
tuned on decider-2b, so both sets are new to it. The decider-0.8b results on
the same messages already exist from rounds 1 and 2, on the same llama.cpp
build `2cbe0ec`. We compare the two models message by message.

Limitations:

- The `plain` layout and the label descriptions follow decider's own prompt
  format. This favours both models of the family equally, not one of them.
- One author (Claude) wrote all messages and labels.
- The team already saw these messages, and many round-2 messages paraphrase
  round-1 forms. No real student message is in the set.

## Design

As in rounds 1 and 2: the same five labels and descriptions, the `plain` and
`intern` formats, the two option orders, the A–E readout and the script
`laptop/router_bakeoff.py`. The only change to the script is in `summary`:
it pools the two rounds of one model into one cell of 250 messages, and it
takes the McNemar reference as an option (`--ref`).

**Candidate cell:** decider-2b Q4_K_M, `plain` format, canonical order.

**Reference cell:** decider-0.8b Q8_0, `plain` format, canonical order. This
is the adopted router. On the 250 messages it is right on 202 (80.8 %), and
on 59 of the 80 Catalan messages.

## Decision rule

Replace decider-0.8b with decider-2b Q4_K_M only if all four hold, on the
250 pooled messages:

1. Accuracy is **at least 5 pp higher** than decider-0.8b, with an exact
   McNemar test p < 0.05.
2. **No label loses more than 10 pp** of recall against decider-0.8b.
3. Accuracy on the **Catalan messages is not lower** than decider-0.8b's.
4. Laptop time per call is **at most 3 times** decider-0.8b's. This is only a
   proxy. The board's A53 CPU is a separate test. Another model server runs
   on the laptop during this round, so we time decider-0.8b again on the
   round-1 messages under the same load, and compare with that time.

Otherwise keep decider-0.8b.

Reported but not part of the rule:

- recall on "solution" in Catalan and Spanish, and the several-letter
  messages
- accuracy on the four labels that do not go to rules
- how often Q8_0 and Q4_K_M give the same label
- label changes between the two option orders
- accuracy per round.

**Power.** decider-0.8b is wrong on 48 of the 250 messages. A 5 pp gain is a
net 13 messages. It reaches p < 0.05 only if decider-2b breaks few of the
messages that decider-0.8b gets right. A null result does not show that the
models are equal.

## Results
