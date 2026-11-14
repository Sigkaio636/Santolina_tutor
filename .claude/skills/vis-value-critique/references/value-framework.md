# The value framework

Sources: Stasko, "Value-driven evaluation of visualizations" (EuroVis 2014 capstone,
BELIV 2014); Munzner, *Visualization Analysis and Design* (2014); Amar, Eagan & Stasko
2005 (low-level analytic tasks); Shneiderman 1996 (mantra and task taxonomy); Yi, Kang,
Stasko & Jacko 2007 (interaction intents); van Wijk 2005 (value model); Anscombe 1973 and
Matejka & Fitzmaurice 2017 (same statistics, different graphs); Card, Mackinlay &
Shneiderman 1999 (expressiveness/effectiveness); Nielsen 1993 (response times).

## 1. Purpose comes first

Munzner: "Computer-based visualization systems provide visual representations of
datasets designed to help people carry out tasks more effectively." Every word is a test:

- **datasets**: what data, what types, how many items, which attributes are keys and
  which are values?
- **people**: who reads it, with what literacy, color vision, device, prior knowledge?
- **tasks**: which questions must be answered? Low level (find a value) or high level
  (which region got safer)?
- **more effectively**: than what? Than a table, a number, a statistic, a sentence.

Visualization augments human capabilities; it is not needed when a trusted fully
automatic solution exists, when the answer is a calculation, or when the reader already
knows exactly what to look for (Stasko's Dirty Harry point: "a man's got to know his
limitations"; Munzner: if a trusted automatic solution exists, or the answer is a
calculation, you do not need a visualization). Visualization shines when the problem is ill-specified
and the reader does not yet know which questions to ask (exploration), or when a known
result must be communicated with impact (presentation: Rosling, Snow, Nightingale).

Three modes (Munzner; Schwabish's explanatory vs exploratory; Tukey's EDA):

| Mode | What is known | Goal | Typical form |
|---|---|---|---|
| **Exploration** | nothing | gather knowledge, find the questions, insights | interactive, many variables, overview → zoom/filter → details |
| **Analysis** | hypotheses | verify or falsify | many variables, comparison, overview + detail; may be hard at first glance |
| **Presentation / explanatory** | "everything" | communicate, explain, provide evidence, persuade | few variables, one message, static or scrollytelling, takeaway title |

Judge a chart against *its* mode. An explanatory chart that shows two variables is not
"missing data"; an exploratory tool that is unreadable in five seconds is not "unclear".
But a chart that claims to be analysis while hiding distribution and context, or claims
to be presentation while having no message, fails on its own terms.

"Not visualization" (Wilke's ugly/bad/wrong taxonomy; Cairo): throwing a dataset at any
chart type; making a chart from random or irrelevant data; encoding too much or
irrelevant information; unsuitable palettes. These are value-zero objects regardless of
polish.

## 2. V = T + I + E + C (Stasko)

Score each component 0–3. The score is a communication device; the justification is
what matters.

### T — Time to answer questions

The ability to minimize the total time needed to answer a wide variety of questions
about the data. Enumerate the ten low-level tasks (Amar, Eagan & Stasko) and rate each
for this chart: **immediate** (preattentive or one glance), **work** (serial search,
legend lookup, mental arithmetic, hovering), **impossible** (data not encoded or
hidden).

| Task | Typical question | What makes it immediate |
|---|---|---|
| Retrieve value | What is Y for item X? | labels/axis ticks, direct labels, tooltip on demand |
| Filter | Which items satisfy condition C? | visible grouping, color/position, filtering widgets |
| Compute derived value | What is the total / average / difference? | stacked totals, annotated aggregates, difference plotted directly |
| Find extremum | Which is largest / smallest? | sorting, common baseline, position/length |
| Sort | Rank the items | sorted bars/dots, ordered axis |
| Determine range | What is the span of values? | visible axis, min/max labels |
| Characterize distribution | How are values spread? | histogram, dots, violin, not a mean bar |
| Find anomalies | Which items are unusual? | pop-out highlighting, outlier annotation, residuals |
| Cluster | Which items are similar? | proximity, color grouping, reordered matrix |
| Correlate | Do A and B co-vary? | scatterplot, adjacent PCP axes, aligned small multiples |

Only the tasks relevant to the chart's purpose count against it. For presentation, two
or three tasks being immediate (extremum, trend, part-to-whole) may be all that is
needed; for analysis, most of the table should be at least "work", and interaction
should turn "work" into "immediate".

Score: 3 = the relevant tasks are immediate; 2 = mostly immediate, some work;
1 = mostly work, some impossible; 0 = the main task is impossible or slower than a table.

### I — Insight

The ability to spur and discover insights or insightful questions that would be hard to
get from the raw data. Three views of insight: Saraiya/North/Duca (an individual
observation, a unit of discovery: complex, deep, qualitative, unexpected, relevant);
psychology (sudden understanding of new relations); Chang et al. (knowledge building and
model confirmation, not a eureka moment).

Ask: what can the reader see here that a summary table would hide? Anscombe's quartet
and the Datasaurus are the archetype: same statistics, different data. A chart that
only re-encodes four numbers already printed on it, or a mean bar that hides the
distribution, offers little insight. A chart that shows the distribution, the outliers,
the trend break, the cluster, the correlation, offers a lot.

Score: 3 = reveals patterns/anomalies/relations the reader could not get from numbers;
2 = reveals the main pattern; 1 = shows what a table would show; 0 = hides or distorts
patterns (aggregation, truncation, clutter).

### E — Essence

The ability to convey the overall essence or take-away sense of the data: the big
picture, the whole being more than the sum of the parts (Tufte's weather chart with
2,220 values; Table Lens; treemaps of the market). Related to overview + detail and
focus + context.

Ask: in five seconds, what does a reader take away? Is it the intended message or a
distractor (a legend, a saturated irrelevant mark, a decoration)? Is there a title that
states it (explanatory)? Does the overview show the structure of the whole dataset
(exploratory)?

Score: 3 = the gist is immediate and correct; 2 = correct with a little reading;
1 = requires effort or reading the text; 0 = the five-second impression is wrong or
empty.

### C — Confidence

The ability to generate confidence, knowledge and trust about the data, its domain and
its context, as a by-product of analysis. Ask: does the chart show where the data comes
from (source, date, n), what is missing, how it was aggregated and normalized, how
uncertain it is? Does it look honest (geometry proportional to data, no cherry-picked
window)? Does it provide enough context (Stokes & Hearst: readers want context even at
the price of simplicity) without steering the reader? Would a skeptical reader trust it?

Score: 3 = provenance, completeness and uncertainty visible, nothing suspicious;
2 = mostly; 1 = missing source/n/normalization; 0 = distorted or demonstrably
misleading.

Note: the components are additive, so a strong presentation chart can be E=3, C=2, T=1,
I=1 and still be valuable for its purpose. Say which components the purpose demands.

## 3. The three design criteria (Mackinlay 1986; Card 2008; Munzner 2014)

- **Expressiveness** (data ↔ task): the vis shows exactly the information in the data,
  nothing more and nothing less. Card: "expressive if and only if it encodes all the
  data relations intended and no other data relations." Violations: ordered channel for
  nominal data (false order), unordered hues for ordered data (lost order), lines over
  nominal categories (false continuity), stacking non-additive values, pies of parts that
  are not a whole, truncated bars (false ratios), decorative variation (false data).
- **Effectiveness** (data ↔ user): the encoding exploits the human visual system for
  this task and medium. Most important attribute on the most accurate channel
  (Mackinlay ranking), preattentive highlighting, Gestalt grouping that matches the
  data's structure, memory load within 3–4 chunks, legibility on the target device.
  Effective = novel (enables analysis not possible before) or faster (speeds up an
  existing workflow).
- **Appropriateness** (task ↔ user): cost–value ratio. Time (computation, reading time)
  and space (screen real estate) spent versus benefit gained. van Wijk: value = knowledge
  gained × users × uses, minus development, perception/exploration and interaction
  costs. A huge chart for four values is inappropriate; so is a 50-line spaghetti chart
  for a trend question.

## 4. Interaction (Stasko: interaction is the power source)

For interactive artifacts (Streamlit, Plotly, Altair selections, D3): the three options
for too much data are (a) pack everything in one complex representation, (b) multiple
coordinated views, (c) interaction revealing subsets. Interaction should be a dialogue
with the data, not a facilitator. Intents (Yi et al. 2007): select, explore,
reconfigure, encode, abstract/elaborate, filter, connect. In practice most tools only
offer tooltips, navigation and brushing & linking. Judge:

- Does the **default state** already answer the main task (meaningful defaults, minimum
  number of interactions to solve the stated tasks)?
- Does the design follow **overview first, zoom and filter, details on demand**? Is the
  overview an overview (no details) or a wall of detail?
- Are views **coordinated** (linked highlighting, linked navigation) where the task
  needs comparison across views? For anything with more than one view, read
  `multiple-views.md` and run its dashboard pass.
- Is interaction hiding what should be visible? If the key insight requires hovering
  every mark, T and E collapse.
- Latency: feedback within 0.1 s; filtering updates under 100 ms; more than 1 s needs
  a progress cue; more than 10 s loses the user.
- Animation: "eyes beat memory"; change blindness and 3–4 chunk working memory make
  animated comparisons weak; small multiples usually beat animation for analysis; bar
  chart races show rank changes but not values, and interpolate data that does not exist.

## 5. Robustness: the perturbation test (Kindlmann & Scheidegger 2014; Correll 2023)

Two questions that catch what the other criteria miss. (1) Name a change in the data
that matters for the task (one group shifts, a second mode appears, an outlier is
added): would the picture change visibly? If not, the chart is a confuser or
misleader for that task. (2) Name a change that should not matter (row order, a
re-render, a random seed, one more value at the mode, the default bin count of another
library): would the picture change? If so, part of what the reader sees is an artefact
(random jitter, bin edges, renormalized scales). Record both answers under C. See
RAIN-9 and EXP-15, EXP-21, EXP-22, DAT-14.

## 6. Scoring sheet

```
Purpose assumed: <explanatory | analysis | exploratory>; reader: <...>; task(s): <...>
T  Time        _/3  <which tasks immediate / work / impossible>
I  Insight     _/3  <what is revealed beyond a table; what is hidden>
E  Essence     _/3  <five-second takeaway vs intended message>
C  Confidence  _/3  <source, n, normalization, missing data, honesty>
Expressive?     yes / no  <false or lost relations>
Effective?      yes / partly / no <channel choice, memory, legibility>
Appropriate?    yes / no  <cost vs value; would a table/sentence win?>
```

A chart with any Critical finding caps at I ≤ 1 or C ≤ 1 (whichever the finding hits):
you cannot gain insight or trust from a distorted picture, however pretty.
