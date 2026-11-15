# Intent router

**Question:** which small model best labels a student's chat message with the kind of help it needs?

**The labels:** `stuck`, `concept`, `attempt`, `solution` and `not_productive`. They come from the response types in [Tutor response types](../../TUTOR_RESPONSE_TYPES.md) (in Spanish). Rules then turn each label into a reply type.

**Where it lives:** `student_app/router.py`. **Today `classify` is a keyword rule.** The tutor works without a router model. To plug a model in, replace `classify`. The model alone can never unlock the solution: a `solution` label counts only when the keywords agree. The comparison script is `laptop/router_bakeoff.py`.

## How we tested

- **Messages:** 250 student messages that we invented, in Catalan, Spanish and English, with no M3Kang text. [How we made the messages](../2026-11-router-messages-method.md) shows how to check them and how to run a round again.
- **Readout:** the next-token probability of the letters A to E, one letter per label. Two prompt formats and two option orders.
- **Runtime:** llama.cpp `2cbe0ec` on the laptop CPU. Each round wrote its decision rule before the run.
- **Floor:** the majority label is right on 20 % of the messages.

## Reports

| Date | Report | Compared | Messages | Best result | Verdict |
| --- | --- | --- | --- | --- | --- |
| 2026-11-14 | [Round 1](../2026-11-router-bakeoff.md) | Qwen3.5 0.8B, Intern-Decision-0.8B, decider-0.8b | 100 | decider-0.8b `plain`: 84 % | Rule says no: recall on `solution` too low (60 %) |
| 2026-11-14 | [Round 2](../2026-11-router-bakeoff-2.md) | Qwen3.5 0.8B, decider-0.8b | 150 new | decider-0.8b: 78.7 % | Rule says no: recall on `solution` 37 % |
| 2026-11-14 | [Conclusion for 0.8B](../2026-11-router-0.8b-conclusion.md) | Rounds 1 and 2 | 250 | — | The team overrode the rule: decider-0.8b, with two keyword rules in front of it |
| 2026-11-15 | [Round 3: decider-2b](../2026-11-router-bakeoff-3.md) | decider-2b Q4_K_M against decider-0.8b | 250 | **87.6 %** against 80.8 %, p = 0.009 | Passes all four conditions. decider-2b replaces decider-0.8b. |

## Current decision

- **decider-2b Q4_K_M,** with the `plain` prompt format and the canonical option order, **is the router to try on the board.** To set it up, see [Use decider-2b as router](../../how-to/use-decider-2b-router.md).
- **Its gain is almost all on `solution` messages.** On the messages that do not go to the keyword rules, decider-2b and decider-0.8b are equal.
- **Not on the board yet.** The student app still uses the keyword rule. RAM and time on the board's CPU are not measured.

## Open

- One author (Claude) wrote all the messages and labels. No real student message was used.
- The `plain` prompt follows decider's own format, which favours it.
- The [conclusion page](../2026-11-router-0.8b-conclusion.md#next-steps) lists a test of the keyword rules on the round messages as a next step.

## History

[Message classifier prompt](../../TOOL_CALLER_PROMPT.md) is the first draft of the classifier prompt. Nobody tested it, and the rounds above replaced it. We keep it as a record.
