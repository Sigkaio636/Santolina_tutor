# Tutor response policy (proposal)

!!! note "Proposal, mostly not built"
    This page is a design record. It proposes the rules that choose one of
    the [tutor response types](../reference/tutor-response-types.md) for each
    student message. The student app builds only a small part of it: the
    intent router's labels, a fixed redirect, a clue ladder and the solution
    button. The table
    [What is built](../reference/tutor-response-types.md#what-is-built) says
    which part.

The policy answers one question: when a student writes to the chat of the
student app, which type of reply comes next? The reasons for each rule are in
[Why the tutor answers this way](tutor-response-types-evidence.md).

## What decides the type

| Variable | Effect | Source |
|---|---|---|
| Does the message help the lesson? | No: T9 | Baker et al. 2004; Aleven et al. |
| Does the student give an attempt? | Yes: T6. No: T0, then the ladder | Bridge (Step A: infer the type of error) |
| Number of failed helps so far | One step up each time; T7 after 2 or 3 failures | Wood & Wood 1999 (about three hints of growing explicitness, then show the step); socratic-tutor rules |
| Prior knowledge | Beginner: T4a or T5 earlier. Advanced: T1, T4b, T4c | Expertise reversal effect (Kalyuga) |
| Age or level | Primary school (grades 2 to 5): teach before letting the student fail | Sinha & Kapur 2021: the benefit of productive failure reverses in those grades |
| Explicit request for the solution | T7, then T8 | Socratic-tutor rules ("just tell me") |
| Direct question about a concept | T5a, with no ladder | Socratic-tutor rules |
| Explicit help just given | T8 | Socratic-tutor rules |

The same rules as a tree:

```
student message
 ├─ does not help the lesson ──────────────────► T9 → T0 (not a failed help)
 ├─ asks for the solution ─────────────────────► T7 → T8
 ├─ asks about a concept ──────────────────────► T5a → T8
 ├─ gives a wrong attempt ─────────────────────► T6 (question → point → correct → T8)
 └─ stuck, with no attempt
      T0 → T1 → T4 → T5 → T7 → T8
      (beginner or primary school: T4a or T5 earlier; stuck because of size: T4c)
```

## Labels for the intent router

The policy does not ask a model to choose among the eight types. A small
model cannot do that well: even trained people agree little on fine-grained
teacher moves (see
[Why a small router needs few labels](tutor-response-types-evidence.md#why-a-small-router-needs-few-labels)).
The model labels only the student's message. The rules then choose the reply.

This draft first proposed five Spanish labels. The
[intent router](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md)
adopted them in English, and the student app maps them to its own names
(`student_app/router.py`):

| Draft label | Router label (decider-2b) | App label | Proposed type |
|---|---|---|---|
| PRODUCTIVA_ATASCO | `stuck` | `STUCK` | The next step of the ladder (T0, T1, T4, T5, T7) |
| PRODUCTIVA_CONCEPTO | `concept` | `CONCEPT` | T5a |
| INTENTO | `attempt` | `ATTEMPT` | T6 |
| PIDE_SOLUCIÓN | `solution` | `SOLUTION` | T7 (only when the keyword rule agrees) |
| NO_PRODUCTIVA | `not_productive` | `OTHER` | T9 |

Who decides each type, in this proposal and today:

| Type | Proposed | Today |
|---|---|---|
| T8 | A fixed rule: follows T4a, T5, T7 and the direct correction of T6 | Only after the solution button shows "The right answer is X" |
| T6 | A rule: an option letter, a number or a reasoning in the message | decider-2b (`attempt`); the keyword rule when the router does not answer. A message that names an option gets a fixed "use the answer button" text first. |
| T9b, T9c, T9d | Rules | Rules for an empty message and for several letters; decider-2b (`not_productive`) for the rest |
| T7 on request | A keyword rule | The keyword rule must agree with the label. It misses some Spanish forms ("dímelo", "solución" alone). |
| The step of the ladder (T0, T1, T4, T5, T7) | The count of failed helps and the student's level | Not built: every label except `OTHER` gets the same tutor model call |

What is left for the model is small: tell T9a (off topic) from a productive
question, and T5a (a question about a concept) from being stuck in general.

How the router was chosen and measured: the
[conclusion of the 0.8B comparison](../experiments/2026-11-router-0.8b-conclusion.md)
and [how to use decider-2b as the intent router](../how-to/use-decider-2b-router.md).

## Open decision: the order of the ladder

Three orders exist today.

| Source | Order |
|---|---|
| This policy | T0 question → T1 heuristic → T4 similar problem → T5 knowledge → T7 solution |
| The student app's clue buttons (`Tutor.clue`) | Clue 1: the tutor model is asked how to start. Clue 2: the tutor model again, plus a similar, easier problem from the index. Clue 3 and on: the tutor model is asked for the next step. The solution button, after one attempt. |
| The skill `m3kang-copilot` (*Teaching features*) | Similar, easier solved problem → topic of the neighbours → one-sentence model hint → solution only on request |

The app and the skill put the example (T4) before the generic hint (T1), the
opposite of this policy.

- **For the example first.** T4 comes from the index, with no text
  generation: cheap on the board, and it cannot invent facts. For beginners,
  an example first is what Kalyuga and Ringenberg & VanLehn suggest.
- **For this policy's order.** For stronger students the example adds
  nothing and takes away the useful effort. T0 and T1 can also be fixed
  texts that need no model.

A middle option is to choose the order by the student's level. The team has
not decided.
