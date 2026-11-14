# Design document template ("ficha de diseño")

File `<out_dir>/<slug>_design.md`, written in the user's language (headings may be
translated). Rule IDs cite `encoding-essentials.md` (same ids as vis-value-critique).
Every stage ends with **Rejected alternatives** and **Validation**; a validation states
the threat, the method, whether the user confirmed it, and what remains unverified.

```
# Design: <takeaway-style title>

| Decision record | <id> v<n> · new | reused <id> | supersedes <id> · status declared/candidate |
| Library / host  | <library> (<version>; project.yaml) · <host> |
| Data            | <file(s)>, <n> rows, signature <…>, period <…> |
| Outputs         | <slug>.py, <slug>.png/.html/.vl.json, app.py (if any) |
| Language        | dialogue <xx>, code en |

## 1. Domain problem characterization
- Reader: <profile> — <two lines: literacy, time, device, prior knowledge>; modifiers <…>
- Mode: explanatory | analysis | exploration
- Question(s), in the reader's words: <…>
- Medium and constraints: <…>
- Rejected readings of the problem: <the other candidate questions and why not>
- Validation (threat: wrong problem): <restatement confirmed by the user on <date> | assumed>.
  Not done: observing/interviewing real readers; adoption.

## 2. Data and task abstraction
| attribute | type | role | levels/range | notes (parsing, missing, grain) |
- Derived data: <name = formula>, filters, normalisation (denominator), time grain
- Tasks: why <goal/search/query>; low-level <ranked list>; temporal <…>; Shneiderman <…>
- Rejected abstractions: <e.g. per-event granularity, monthly bins, totals instead of rates>
- Validation (threat: wrong abstraction): <each term of the question → attribute/derived; tasks sufficient; confirmed | assumed | FAILED: missing attribute <…>>

## 3. Visual encoding and interaction
- Idiom: <catalog id and name>
| attribute | mark + channel | rank (Mackinlay) | expressiveness check |
- Ordering, scales, baselines, facets: <…> (CMP-01, EXP-08, SCL-02/08)
- Color plan: purpose <…>, palette <…>, CVD second cue <…> (COL-01/02/04/05)
- Text plan: title "<rendered takeaway>", subtitle <period, units, definition>, axis titles, direct labels, annotations <…>, source/n (TXT-01/02/04/05/08)
- Composition (only if several views): type <juxtapose|superimpose|small-multiples|overview-detail|…>, relation <multiform|…>;
  | view | idiom | role |  and  | link from → to | highlight/filter/navigation | selection name |
  shared scales and colors <…>; space per view <…> (CMP-09/10/11/12/13, SCL-08)
- Interaction plan: <none | intents>; default state answers the main task (INT-02); every selection changes another view, one highlight color (INT-09/10/11)
- Rejected idioms: | idiom | reason | rule |
- Validation (threat: wrong idiom):
  a. Rule checklist: <rule → pass/fail → evidence>
  b. Task-time table: <task → immediate / work / impossible>
  c. Render inspected: <png>, grayscale <…>, deuteranopia <…>
  d. Critique (optional): <verdict, findings applied>
  e. Reader acceptance: <accepted | changed <…> | assumed>

## 4. Algorithm
- Library <name version>, host <…>, pipeline load → derive → build_chart → save
- Rows in <n>, rows after derivation <n>, run time <s>, limits <…>
- Rejected alternatives: <libraries/hosts and why>
- Validation (threat: wrong algorithm): run_check.py summary <exit, outputs, inspector findings, blocking fixed>; render matches stage 3 <yes/no>

## 5. Decision record
```yaml
<the record as saved>
```

## 6. Assumptions and open points
<mandatory in autonomous mode: question id → assumed answer → reason; otherwise "none">
```
