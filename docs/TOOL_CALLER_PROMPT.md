# Prompt for the student-message classifier

!!! warning "Superseded (note added on 2026-11-15)"
    This page is an old draft. Nobody tested this prompt. The
    [intent router](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md)
    that the student app uses is in `student_app/router.py`. It uses a
    different model, decider-2b, and a different prompt. The router labels
    chat messages. The student app uses the label to choose how to
    answer: with the
    [tutor model](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md)
    or with a fixed reply. For why the team chose decider-2b, see the
    [conclusion of the 0.8B comparison](experiments/2026-11-router-0.8b-conclusion.md)
    and [round 3](experiments/2026-11-router-bakeoff-3.md). To set it up, see
    [How to install and use decider-2b as the intent router](how-to/use-decider-2b-router.md).
    Two parts of the draft still match the code: the five labels (`STUCK`,
    `CONCEPT`, `ATTEMPT`, `SOLUTION`, `OTHER`) and the rule that the model
    alone never unlocks the solution. The rest of the text below is a record
    of the draft only.

This document gives the prompt that sorts each student message into one label.
The copilot uses the label to choose a response type from
[the tutor response types](reference/tutor-response-types.md). This version fixes the five
critical faults of the first version.

**Status:** draft. We did not test this prompt on a model. All examples are
made up. This document contains no M3Kang problem text.

## Summary

- **Model:** the default chat model (Qwen3.5-0.8B), through
  `/v1/chat/completions`. Do not use decider-0.8b. Its training teaches it to
  solve problems, not to follow instructions.
- **Output:** one of five words. A grammar forces the output.
- **Safety:** the model alone cannot make the tutor give the solution. A
  keyword rule must agree.
- **Input:** the code cleans and cuts all external text before it goes into
  the prompt.

## Labels and the response that each label starts

| Label | Meaning | Tutor response |
|---|---|---|
| `STUCK` | The student asks for help or a hint, does not understand, does not know how to start, or is frustrated. The student gives no answer. | T0 (diagnostic question) or T1 (general hint) |
| `CONCEPT` | The student asks what a word, property, formula or method means, or how it works. | T5a (concept) |
| `ATTEMPT` | The student gives an answer, a number, a result or a step of their reasoning. | T6 (correction), or continue with T0c |
| `SOLUTION` | The student explicitly asks for the final answer, or asks the tutor to solve the problem. | T7 (solution), only if the rule agrees |
| `OTHER` | The message is off-topic, empty or unreadable. | T9 (redirect) |

## Prompt

### System message

```text
You classify one message that a student sends to a maths tutor while working on a multiple-choice maths problem.

Reply with exactly one label:
STUCK    - The student asks for help or a hint, says they do not understand or do not know how to start, or says they are frustrated. They give no answer of their own.
CONCEPT  - The student asks what a mathematical word, property, formula or method means, or how it works.
ATTEMPT  - The student gives an answer, a number, a result or a step of their own reasoning.
SOLUTION - The student explicitly tells the tutor to give the final answer or to solve the problem.
OTHER    - The message is off-topic, empty or unreadable.

If the message fits both STUCK and SOLUTION, reply SOLUTION only if the student explicitly asks for the answer.
If the message fits ATTEMPT and another label, reply ATTEMPT.
```

### User message

```text
Problem statement: <problem>{problem_stem}</problem>
Tutor's last message: <tutor>{last_tutor_move}</tutor>
Student's message: <student>{student_message}</student>
Label:
```

### Request parameters

```json
{
  "grammar": "root ::= \"STUCK\" | \"CONCEPT\" | \"ATTEMPT\" | \"SOLUTION\" | \"OTHER\"",
  "max_tokens": 6,
  "temperature": 0,
  "cache_prompt": true
}
```

## Code before and after the model

```python
import re

OPTION_LINE = re.compile(r"^\s*\(?[A-E][\)\.:]\s.*$", re.M)
SOLUTION_RULE = re.compile(
    r"(dime|dame|digues|dona'?m|tell me|give me).{0,20}(respuesta|resposta|soluci|answer)"
    r"|resu[eé]lve|resol|solve it|just the answer",
    re.I)
LABELS = {"STUCK", "CONCEPT", "ATTEMPT", "SOLUTION", "OTHER"}


def clean(text, limit):
    """Remove text that looks like prompt structure, and cut the text."""
    text = re.sub(r"</?\w+>", " ", text or "")              # no fake tags
    text = re.sub(r"(?i)\b(label|answer|options?)\s*:", " ", text)
    text = re.sub(r"\s+", " ", text).strip()                # no newlines
    return text[:limit] or "(none)"


def problem_stem(problem_text):
    """Return the statement without its options (A)-(E)."""
    return clean(OPTION_LINE.sub("", problem_text), 400)


def route(label, student_message):
    """The model alone never sends the solution."""
    if label not in LABELS:                                 # error or timeout
        return "STUCK"
    if label == "SOLUTION" and not SOLUTION_RULE.search(student_message or ""):
        return "STUCK"
    return label
```

Before the code puts each text into the prompt, it applies these functions:

| Field | Function | Limit |
|---|---|---|
| `{problem_stem}` | `problem_stem(problem_text)` | 400 characters |
| `{last_tutor_move}` | `clean(last_tutor_move, 300)` | 300 characters |
| `{student_message}` | `clean(student_message, 300)` | 300 characters |

On the first turn, the tutor has no last message, so `clean` returns `(none)`.

## Faults that this version fixes

| Fault in the first version | Fix |
|---|---|
| The problem text had its own options (A)–(E), and the labels were also A–E. The model could return the answer of the problem. | The labels are words. The prompt contains only the problem statement, without the options. |
| The model copied the letter that the student wrote ("is it D?" gave D). | The labels are not letters or digits. |
| decider-0.8b learned from a fixed `Question:` line, so it probably ignores the instruction in that line. | The prompt uses the chat format with the default model, which follows instructions. |
| D (give the solution) was the most dangerous label. D is also the most frequent M3Kang answer. | `SOLUTION` needs the rule to agree. On doubt or on an error, the label is `STUCK`. |
| The student could put `Answer: (D` into the message. | The code cleans and cuts all external text and puts it between tags. |

## Decisions

- **The model does not detect attempts to break the rules or rude messages.**
  Rules detect them before the model runs. A 0.8B model is not a reliable
  defense.
- **Several letters in one message ("not A and not B") count as `ATTEMPT`.**
  One message is not sufficient to tell a random guess from an elimination of
  options. Elimination is a valid strategy (T1g).
- **The code cuts the problem statement to 400 characters.** This length is
  sufficient to decide whether a number is an attempt. It also decreases the
  prompt processing time on the UNO Q.
- **The `SOLUTION` rule is narrow on purpose.** An error toward `STUCK` gives
  a diagnostic question. An error toward `SOLUTION` gives away the answer.

## Open items

- **Short replies such as "ok" or "thanks":** they get the label `OTHER`, so
  the tutor redirects a student who did nothing wrong.
- **Questions about the problem statement** ("does the start square count?"):
  no label fits them.
- **Two types of `ATTEMPT`:** the label does not separate an answer to the
  problem from an answer to a tutor sub-question. These two cases need
  different responses.
- **Measurement:** we need a set of about 150 made-up messages, balanced by
  label and by language. Compare the model with a keyword-only classifier.
  The number that decides adoption is the rate of false `SOLUTION` labels.
