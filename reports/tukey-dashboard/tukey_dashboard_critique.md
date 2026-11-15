# Critique: Tukey decision dashboard for the solver choice

**Input**: `tukey_dashboard.py`, `specs/*.vl.json`, Firefox screenshots of `tukey_dashboard.html`. One linked block of four views (gradient interval ×2, dumbbell, span), plus a timeline, three bar panels, one dot panel, one heatmap and a decisions table. Data: 8 solvers plus a chance row, 50 problems × 2 languages.
**Assumed purpose**: analysis with an explanatory headline. Reader: Tukey judges (statistics literate) and the team. Task: choose the solver `predict.py` ships for a 20-problem test.

## Verdict

The first draft already answered the question in its default state. The headline, the KPI strip and the linked block agree, and the decisions table cites the same numbers. It had one statistical flaw a Tukey judge would catch: intervals counted 100 rows as independent when they are 50 problems asked twice. It also left the chance comparison in the final-test column as a single line, which hid how much luck a 20-problem test allows. Both are fixed. With them fixed, the program solver still clears chance, and the dashboard now says honestly that its median (7 of 20) sits at the top of chance's 90% range.

## Value scorecard (V = T + I + E + C)

| Component | Score | Why |
|---|---|---|
| T · Time | 3/3 | Best solver, clears chance, fits 60 s, Catalan gap: all immediate in the default state; exact values by tooltip |
| I · Insight | 3/3 | Shows what a results table hides: every forced letter collapses onto one letter; the prior's M3Kang gain disappears on the practice set; points come from the program path only |
| E · Essence | 3/3 | Headline and computed title state the decision; the five-second read is right |
| C · Confidence | 2/3 → 3/3 after fixes | Source per row in tooltips, n stated, intervals defined; the row-vs-problem issue lowered it before the fix |

Expressive: yes · Effective: yes (position for every compared quantity, hue + shape for board/laptop) · Appropriate: yes. The panels are small, and the decisions table carries what a chart would not add.

## Findings

### Major (fixed)
- **[DAT-13]** Wilson intervals and the predictive used n = 100 rows, but the rows are 50 problems in two languages, so the answers are correlated. Consequence: intervals were too narrow by up to √2, which overstated the separation from chance. Fix applied: k_eff = accuracy × 50, n = 50. The program solver's 95% interval became 25–51% (was 28–47%).
- **[CMP-12 / DAT-03]** The final-test column compared predictive bands to a single dashed line at 4 of 20. A fixed letter itself scores 1 to 7 of 20 (90%). Consequence: the reader could not see that the program solver's median is still inside luck's range. Fix applied: a grey "Any fixed letter (chance)" row with the exact binomial band, and text that says so.
- **[TXT-02]** The decision table and the takeaway text typed their intervals in by hand (two were off by one point). Fix applied: they are now filled from the computed values.

### Minor
- **[EFF-16]** Four board runs at 01:05 overlap in the timeline (15–24%). Tooltips separate them, and the panel's job is the step, not those four values. Kept.
- **[DAT-03]** The RAM view summed the RSS of two servers, which counts shared pages twice and seems to contradict the 2,359 MB that `free -m` still showed. Fix applied: a subtitle says so. The recommended next configuration was missing, so it was added as an orange file-size estimate.
- **[CLT-03]** The router panel is full width with empty space on the right. It costs scroll, not understanding. Kept.
- **[TXT-05]** "Timeout (answers D)" at 35% could read as a good path. Fix applied: the takeaway explains it is luck (D is right on 20% of rows).

## Deterministic check log
- `inspect_vegalite.py` on 8 specs: SCL-06 flags for field names of reference layers (rules, text). Dismissed: layered axes render the real titles, as the screenshot confirms. COL-05 on Vega's default palette. Dismissed: every colour scale has an explicit Okabe-Ito range. SCL-08 on accuracy % vs out of 20. Dismissed: different measures. TXT-07 for `legend=null`. Dismissed: the page key sits directly above the block.
- Selection: one param `pick` with views `view_1…view_4`; no dead selection.
- All length marks start at zero (domains [0,80], [0,20], [0,62], [0,60], [0,3700], [0,100]).

## What to preserve
- One y order shared by the four core columns, sorted by accuracy, with the chance row as a divider.
- Blue = board, orange = laptop, grey = chance, on every view.
- Intervals counted by problem, and the predictive final-test column.
- The decisions table, which cites only numbers shown above it.

## Second pass (v2, text removed)

The user asked for less text so readers interpret the plots themselves. Checked that the cut kept what the reader needs: n, interval definitions, the chance reference and sources all remain, in the subtitles, the grey chance row and the footnote. Three findings from the cut, all fixed with neutral marks rather than prose:

- **[TXT-04]** Timeline points had lost their names, and the decisions table cited runs the reader could not find. Fix: run names as direct labels (no adjectives).
- **[TXT-05]** "Timeout (answers D)" at 35% read as a strong path once the explanation was gone. Fix: a tick on each bar at the count expected by chance (20%).
- **[CMP-11 / coherence]** The decisions table cited the vision result, which no chart shows. Fix: marked as "laptop report, not plotted".

Scorecard v2: T 3, I 3, E 2 (the five-second message now needs the reader to look at the chance row; accepted, by design), C 3.
