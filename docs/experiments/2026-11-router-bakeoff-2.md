# Intent router bake-off, round 2: decider-0.8b as candidate

Status: **pre-registered on 2026-11-14, before any run.** Results are added
below the line "Results" after the runs.

## Why a second round

In [round 1](2026-11-router-bakeoff.md), decider-0.8b was registered only as
a reference, because its model card says English only. It reached 84 % in its
own `plain` format, outside the rule. A finding seen after the fact needs a
new test: this round registers decider-0.8b as the candidate, on messages
written after round 1 and never used to tune anything.

## What changes from round 1

- **New data:** `laptop/router_messages_r2.json`, 150 messages (30 per label,
  10 per language per label) and 5 new invented problems. They are written to
  look more like chat input than round 1: mostly lowercase, no accents, some
  typos ("nose", "q hago") and chat abbreviations ("idk", "pls", "xd"). They
  are still short. 24 are marked as boundary cases (frustration, "I tried but
  nothing works" with no content, property questions, a single letter,
  several letters, manipulation, asking for the answer after answering). No
  message repeats a round-1 message word for word, but many are paraphrases
  of round-1 forms, so this is not a fully independent sample. No M3Kang
  text. One author (Claude) wrote messages and labels again, which stays a
  limitation. See [how the messages were made](2026-11-router-messages-method.md).
- **Models:** decider-0.8b (candidate) and Qwen3.5-0.8B (reference, already on
  the board). Intern-Decision-0.8B was rejected in round 1 and is not rerun.
- **Same everything else:** the five labels and their descriptions, the
  `plain` and `intern` formats, the two option orders, the readout and the
  script (`laptop/router_bakeoff.py`). Nothing was changed after seeing the
  round-1 results, except the new `--messages` option to point the script at
  this file.

## Decision rule

The candidate cell is **decider-0.8b with the `plain` format and the
canonical option order**, fixed now. Adopt decider-0.8b as the router to try
on the board only if all four hold:

1. Accuracy **≥ 70 %**, and the lower end of its 95 % Wilson interval
   **≥ 60 %**.
2. Recall **≥ 60 % on every label**.
3. Accuracy **≥ 60 % on the Catalan messages** (50 messages), because the
   model card says English only.
4. It beats Qwen3.5-0.8B in Qwen's best format of this round by **at least
   10 pp**, with an exact McNemar test p < 0.05.

Otherwise keep Qwen3.5-0.8B behind the rules of
[TUTOR_RESPONSE_TYPES.md](../TUTOR_RESPONSE_TYPES.md#si-esto-alimenta-un-decisor),
and plan a LoRA or distillation run.

Passing this rule does not settle deployment. A second model on the board
costs about 0.8 GB at Q8_0 (about 0.5 GB at Q4_0), and RAM, latency and
quantization on the UNO Q are a separate test.

**Power.** With 150 messages, a 10 pp gap reaches p < 0.05 only if the two
models disagree on few messages. Condition 1 is the one that carries most of
the weight.

## Results

Run on 2026-11-14 on the laptop CPU, after the rule above was written.
Reproduce with:

```bash
python3 laptop/router_bakeoff.py run --name <model> --messages laptop/router_messages_r2.json --out results/router2-<model>.csv
python3 laptop/router_bakeoff.py summary results/router2-decider.csv results/router2-qwen.csv
```

Accuracy with the canonical option order, 150 messages, 95 % Wilson
interval. The majority-label floor is 20 %.

| Model | Format | Accuracy | Shifted order | Both orders averaged | Label changes between orders |
|---|---|---|---|---|---|
| decider-0.8b | plain | **78.7 %** [71.4–84.5] | 82.0 % | 81.3 % | 24 |
| decider-0.8b | intern | 63.3 % [55.4–70.6] | 50.7 % | 56.7 % | 32 |
| Qwen3.5-0.8B | intern | **36.7 %** [29.4–44.6] | 32.7 % | 37.3 % | 60 |
| Qwen3.5-0.8B | plain | 20.0 % [14.4–27.1] | 26.7 % | 20.0 % | 125 |

As in round 1, Qwen3.5 with `plain` answers A for every message.

Recall per label, canonical order:

| Model / format | stuck | concept | attempt | solution | not_productive |
|---|---|---|---|---|---|
| decider / plain | 83 % | 100 % | 100 % | **37 %** | 73 % |
| Qwen3.5 / intern | 60 % | 23 % | 100 % | 0 % | 0 % |

By language, decider / plain: Catalan 37/50, English 45/50, Spanish 36/50.
On "solution" messages it is right on 7 of 10 in English but only 2 of 10 in
Catalan and 2 of 10 in Spanish. Its errors on that label go to "attempt" (10)
and "stuck" (8). All 4 "several letters" messages and 1 of 3 manipulation
messages were labelled "attempt".

## Decision

For decider-0.8b, `plain`, canonical order:

1. **Passes:** 78.7 %, Wilson lower end 71.4 %.
2. **Fails:** recall on "solution" is 36.7 % (11/30).
3. **Passes:** Catalan 74 % (37/50).
4. **Passes:** +42 pp over Qwen3.5 / `intern`, McNemar 0 vs 63 discordant
   messages, p < 0.001.

**decider-0.8b is not adopted as the router.** By the rule, the router stays
on Qwen3.5-0.8B behind the rules of TUTOR_RESPONSE_TYPES.md, and a LoRA or
distillation run is the next step.

The team later adopted decider-0.8b behind rules, departing from this
outcome; see the [conclusion](2026-11-router-0.8b-conclusion.md).

## What this suggests (not part of the rule)

- decider-0.8b replicated most of its round-1 result on new messages (84 % →
  79 %). Its weak point is asking for the solution in Catalan and Spanish,
  which matches its English-only model card.
- The two labels that failed are the ones TUTOR_RESPONSE_TYPES.md already
  sends to rules first: keyword rules for asking for the solution, and
  pattern rules for several letters. A router that only has to separate
  stuck, concept, attempt and off-topic, behind those rules, would be a
  different test with its own pre-registered rule.
- A LoRA on Catalan and Spanish "solution" messages, starting from
  decider-0.8b rather than from Qwen3.5, is the other route.

Limitations as in round 1: one author for messages and labels, many
round-2 messages are paraphrases of round-1 forms, n = 150, laptop only.
