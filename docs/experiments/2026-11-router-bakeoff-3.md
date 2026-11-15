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

Run on 2026-11-15 on the laptop CPU, after the rule above was written.
Reproduce with:

```bash
python3 laptop/router_bakeoff.py run --name decider2b-q4 --out results/router-decider2b-q4.csv
python3 laptop/router_bakeoff.py run --name decider2b-q4 --messages laptop/router_messages_r2.json --out results/router2-decider2b-q4.csv
# the same two runs with --name decider2b-q8 and the Q8_0 server
python3 laptop/router_bakeoff.py summary --ref decider/plain results/router{,2}-decider.csv results/router{,2}-decider2b-q4.csv results/router{,2}-decider2b-q8.csv
```

The SHA256 of both files matches the hash on the Hub:

| File | SHA256 |
|---|---|
| `decider-2b-v12-Q4_K_M.gguf` | `e6d3a7534a3abc3a723f8263dc694b86f533214a5bf761474113c66d44018340` |
| `decider-2b-v12-Q8_0.gguf` | `b89b9bed14dc889075de93136e9a9e3cd859c26b008bfb4bb0211ca0d7357c27` |

Accuracy with the canonical option order, 250 messages, 95 % Wilson
interval. The majority-label floor is 20 %.

| Model | Format | Accuracy | Shifted order | Label changes between orders | Catalan (80) | McNemar against decider-0.8b |
|---|---|---|---|---|---|---|
| decider-0.8b Q8_0 | plain | 80.8 % [75.5–85.2] | 84.0 % | 34 | 59 | Reference |
| **decider-2b Q4_K_M** | **plain** | **87.6 %** [82.9–91.1] | 88.0 % | 12 | 65 | 28 vs 11, p = 0.009 |
| decider-2b Q4_K_M | intern | 85.2 % [80.3–89.1] | 84.4 % | 31 | 63 | 25 vs 14, p = 0.108 |
| decider-2b Q8_0 | plain | 87.6 % [82.9–91.1] | 87.2 % | 10 | 64 | 32 vs 15, p = 0.019 |
| decider-2b Q8_0 | intern | 88.4 % [83.8–91.8] | 88.4 % | 14 | 67 | 28 vs 9, p = 0.003 |

In the McNemar column, the first number counts messages that only
decider-2b gets right and the second counts messages that only decider-0.8b
gets right.

Recall per label, `plain` format, canonical order:

| Model | stuck | concept | attempt | solution | not_productive |
|---|---|---|---|---|---|
| decider-0.8b Q8_0 | 84 % | 100 % | 100 % | 46 % | 74 % |
| decider-2b Q4_K_M | 96 % | 94 % | 96 % | **80 %** | 72 % |
| decider-2b Q8_0 | 96 % | 86 % | 94 % | 88 % | 74 % |

By round, decider-2b Q4_K_M is right on 93 of 100 (round 1) and 126 of 150
(round 2). decider-0.8b is right on 84 and 118.

**Time per call.** The laptop load changed during the runs, because other
people's jobs used the CPU. We measured time in two ways:

- As registered: decider-0.8b again on the round-1 messages, after the
  decider-2b runs. `plain` mean 1,465 ms, against 3,208 ms for decider-2b
  Q4_K_M (2.2 times). The labels of this rerun are identical to round 1 on
  all 100 messages.
- Paired, added after the runs because the load changed: both servers at
  the same time, one `plain` canonical call per message for each model, in
  alternating order, on the 100 round-1 messages. Median 967 ms for
  decider-0.8b and 1,553 ms for decider-2b Q4_K_M (1.5 times).

Secondary results (not part of the rule):

| | decider-0.8b | decider-2b Q4_K_M | decider-2b Q8_0 |
|---|---|---|---|
| "solution", Catalan | 4/16 | 11/16 | 12/16 |
| "solution", Spanish | 5/17 | 14/17 | 15/17 |
| "solution", English | 14/17 | 15/17 | 17/17 |
| Several letters (7), labelled "attempt" | 6 | 7 | 6 |
| Messages that do not go to rules (193) | 178 | 179 | 175 |

Q4_K_M and Q8_0 give the same label on 236 of the 250 messages. "Messages
that do not go to rules" excludes the "solution" label and the
several-letter messages, which the two rules of the conclusion handle.

## Decision

For decider-2b Q4_K_M, `plain`, canonical order:

1. **Passes:** +6.8 pp (87.6 % against 80.8 %), McNemar 28 vs 11, p = 0.009.
2. **Passes:** the largest recall loss is 6 pp (concept, 100 % to 94 %).
3. **Passes:** Catalan 65 of 80, against 59.
4. **Passes:** 2.2 times as registered, 1.5 times in the paired measurement.

**By the rule, decider-2b Q4_K_M replaces decider-0.8b as the router to try
on the board.** The board test (RAM, time on the A53 CPU) is still open.

## What this suggests (not part of the rule)

- Almost all of the gain is on "solution" messages in Catalan and Spanish.
  On the messages that do not go to rules, decider-2b and decider-0.8b are
  equal (179 and 178 of 193). With the keyword rule in front, decider-2b
  adds little. Without it, decider-2b covers most of what the rule would
  catch.
- So the practical choice is between two set-ups: decider-0.8b with a
  keyword rule that is not yet written or tested, or decider-2b with or
  without that rule, at about 0.5 GB more RAM and 1.5 to 2.2 times the time
  per call on the laptop.
- No model separates several-letter messages from attempts. That rule stays
  necessary.
- Q8_0 is no better than Q4_K_M in the `plain` format (219 of 250 for both),
  so the smaller file costs nothing here.

Limitations as in rounds 1 and 2: one author for messages and labels, the
messages were not new to the team, n = 250, laptop only.
