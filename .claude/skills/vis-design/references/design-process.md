# The four-stage design process (Munzner's nested model)

Visualization design is a cascade of four levels. Each level takes the output of the one
above as its requirements, and a mistake at one level makes every level below it wrong
no matter how well it is executed. The skill walks the levels in order and validates each
one before moving on, because validation methods differ per level.

| Stage | Question | Output | Threat ("wrong …") | How to validate |
|---|---|---|---|---|
| 1 Domain problem characterization | Who needs what, from which data, in which situation? | reader profile, mode, the domain question in the reader's words, medium, constraints | wrong problem: the reader does not have this question, or has it with other words | restate it to the reader and have it confirmed; observe or interview target users; adoption measured only after deployment |
| 2 Data and task abstraction | Which generic data (types, keys, values, derived data) and which generic tasks (why/how/what) capture the domain question? | attribute table, derived data with formulas, task list in Brehmer–Munzner / Amar / Shneiderman / Aigner vocabulary, data-shape signature | wrong abstraction: the tasks or the derived data do not answer the domain question (e.g. the needed attribute is missing) | justify the mapping question → task → data; stop if an attribute the question needs does not exist |
| 3 Visual encoding and interaction design | Which idiom, marks, channels, order, scales, color, text and interaction make those tasks fast and honest for that reader? | the solution block of the decision record; rejected alternatives with the rule that rejects them | wrong idiom: a perceptual or cognitive principle is violated, or the idiom does not scale to the data | rule checklist (encoding-essentials / sibling rules), task-time table (immediate / work / impossible), render inspected in grayscale and CVD simulation, optional vis-value-critique |
| 4 Algorithm design | Which library, data pipeline and layout implement that encoding fast enough and reproducibly? | runnable code, exported artifacts, run log | wrong algorithm: the code does not render the specified encoding, is too slow, or drops data | execute headless; compare the rendered chart with stage 3; measure runtime and rows; inspectors |

Two consequences for the workflow:

- **Downstream validation cannot fix upstream errors.** A beautiful, fast chart of the
  wrong abstraction is worthless; the questionnaire therefore confirms stage 1 before
  stage 2 is opened, and so on. Validation of stage k is asked in the same call that opens
  stage k+1, so it costs no extra round trip.
- **Each level has its own vocabulary.** Stage 1 speaks the reader's language (Spanish or
  English, domain terms). Stages 2–4 speak the abstract vocabulary in `profiles/vocab.yaml`
  (English ids), which is what makes a decision reusable across domains: two problems from
  different fields with the same abstraction get the same solution.

## The visualization pipeline that stage 4 implements

raw data → data transformations (clean, parse dates, derive, aggregate, normalise) → data
table (cases × attributes) → visual mapping (marks and channels from stage 3) → visual
structure (axes, grids, legends, labels) → view (size, scales, clipping) → interaction (if
any) at any step. The generated code mirrors this: `load()`, `derive()`, `build_chart()`,
`save()`.

## Why decisions are reusable

A decision record stores stages 1–3 for one (archetype, mode, profile, data-shape
signature). When a new problem has the same abstraction and reader, the same solution is
the right default: the domain changed, the design problem did not. The record carries the
rejected alternatives and the rules behind them so the design document can state them
without re-deriving them.

Sources: Munzner, "A Nested Model for Visualization Design and Validation" (InfoVis
2009) and *Visualization Analysis and Design* (2014); Card, Mackinlay & Shneiderman 1999
(pipeline); Brehmer & Munzner 2013 (task typology).
