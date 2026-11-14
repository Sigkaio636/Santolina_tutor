# Report template

Use this structure. Keep the prose tight; findings are the deliverable. Write in the
user's language (section titles may be translated).

```
# Critique: <what the chart is, in 5–10 words>

**Input**: <file / code / image>, idiom: <bar | line | ...>, data: <keys and values with
types, n items, k categories>.
**Assumed purpose**: <explanatory | analysis | exploratory>; reader: <...>; task(s):
<the question(s) the chart must answer>. <State what the user did not specify.>

## Verdict
<One paragraph. Value delivered vs. value possible with this data and task. Whether a
visualization is warranted at all. The one change that would recover the most value.>

## Value scorecard (V = T + I + E + C)
| Component | Score | Why |
|---|---|---|
| T · Time | n/3 | <which low-level tasks are immediate / work / impossible> |
| I · Insight | n/3 | <what is revealed beyond a table; what is hidden> |
| E · Essence | n/3 | <five-second takeaway vs intended message> |
| C · Confidence | n/3 | <source, n, normalization, missing data, honesty> |

Expressive: <yes/no, why> · Effective: <yes/partly/no, why> · Appropriate: <yes/no, why>

## Findings

### Critical (misleads or blocks the main task)
- **[RULE-ID]** <finding>. Evidence: <what in the chart/spec>. Consequence: <what the
  reader gets wrong or cannot do>. Fix: <concrete change>.

### Major (slows the task, hides insight, loses readers)
- ...

### Minor
- ...

## Deterministic check log
<Bullet list of script findings and measurements used (axis domains, counts of
categories/hues/legend entries, CVD simulation result, contrast ratios, lie factor).
Mark any deterministic finding you dismissed and why (which exception applied).>

## What to preserve
<2–5 bullets: choices a redesign must keep.>

## Redesign
- Idiom: ...
- Encodings: <attribute → mark + channel>, ordering, scales (zero / range / shared)
- Color plan: <purpose of color; palette type; accent; CVD check>
- Text plan: <title with takeaway, axis titles with units, direct labels, annotations
  with context, source/n>
- Interaction (if any): <default state, overview → filter → details, linked views>
- <Code, if the input was code and the user asked for a fixed version.>
```

Conventions:

- Rule IDs come from `rules-catalog.md` (PUR/EXP/EFF/SCL/COL/TXT/CLT/CMP/IDM/INT/DAT/ACC)
  and `papers.md` (TRUNC/TEXT/MEANBAR). Cite the most specific one; add a second ID when
  two rules bite.
- Never list a finding without evidence you can point at. Never repeat a finding at two
  severities.
- Severity means impact on value for the stated purpose, not how many rules are broken.
- If the chart is good, the Findings section is short and the Verdict says so plainly;
  do not manufacture Minor findings to look thorough.
- Do not write about aesthetics. If a style choice costs legibility, salience, trust or
  accessibility, name that cost and the rule.
