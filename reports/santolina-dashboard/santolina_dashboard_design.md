# Design: Santolina dashboard

| | |
|---|---|
| Decision record | new (see `.claude/vis-decisions/`); fuses the Tukey record `…-20261115-2`, Ferran's solver record `p-compare-two-keys--where-each-solver-setup-loses-20261115` and his M3Kang records |
| Library / host | Altair 5.5.0, one HTML page with vega-embed 6.26 |
| Data | `data/*.csv` (aggregates from M3Kang shard 0, the practice set and the solver frames) and `../tukey-dashboard/data/*.csv` |
| Language | dialogue en, code en |

## 1. Domain

- Reader: Tukey judges and the team. Analysis mode, text-light (the owner's rule).
- Questions, in order: what the data looks like (part 1), how the solvers improved (part 2), what to ship (part 3).
- Validation: the user confirmed the three-part structure and the colour plan on 2026-11-15.

## 2. Abstraction

- **EDA:** problems by level × year and by language; correct-letter counts and figure need by dataset × level (Wilson 95%); statement length per problem (no id); option-reading coverage; slice shares of the grid problems.
- **Progress:** run timeline (Tukey `progress.csv`); per-run outcome shares (22 runs × 5 outcomes); per-problem read and written tokens for the board-time estimate; per-slice program accuracy.
- **Paired changes:** for each pair of runs on the same problem ids, the difference is (newly right − newly wrong) / n, with a Wald interval for a paired difference. 10 pairs: 6 fine-tuning, 4 translation.
- **Results:** as in the Tukey design.
- Rejected: the EDA problem browser (it shows problem text, which breaks the M3Kang red line); two funnel rows compared by eye instead of an explicit difference (CMP-12).

## 3. Encoding

- One page, three sections, 16 Vega views. One linked composition in part 2: the funnel click (`run`) filters the board-time scatters and the slice panels, and two speed sliders reconfigure the scatters. One linked composition in part 3: the solver block (`pick`). The other views are independent, each a separate decision on the same page.
- Colour plan: see the README table. This replaces Ferran's blues and oranges in the funnel (they clashed with board and laptop), his light-blue M3Kang (now reddish purple) and the Tukey blue sequential for commits (now greys).
- Idioms: heatmaps with numbers (level × year, funnel); sorted bars (languages, OCR, RAM, paths); dot + interval (letters, figure, levels, router, accuracy); strip of ticks with median (length); scatter with a limit line (board time); difference dot plot with intervals and a zero line (changes).

## 4. Critique passes (/vis-value-critique)

1. **Layout (render):** the progress block overflowed 1180 px, so the slice panels were off-screen. Dataset shapes merged into the outcome legend. Year labels collided. EDA charts overflowed their columns. Fixed: three-row block, independent scales, '07-style labels, narrower views.
2. **Coherence [DAT-13]:** part 2 "right" (the program's own answer, one language) and part 3 "right" (final answer, both languages) differ, for example 46% vs 58% for Qwen-Math English. Fixed: the funnel subtitle defines it. The paired changes use the funnel definition, and one problem whose program was right but cut at the cap no longer counts as right.
3. **Decisions table:** two rows on Qwen-Math overlapped, and one claimed that fine-tuning "lowers" accuracy, which no interval supports (practice-set intervals cross zero). Fixed: one row, "not shown to help".
4. **[EFF-11]:** the funnel legends were repeated. Fixed: shown once.
5. **Dismissed inspector flags:** SCL-06 on reference layers, COL-05 on Vega defaults, COL-04 and IDM-STACK on the solid band tints, TXT-01 on descriptive titles (the user's style), EFF-08 (outcome shapes are a deliberate second cue).

Scorecard: T 3 · I 3 · E 2 (by design, conclusions only in the table) · C 3.

## 5. Open points

- Board time in part 2 is estimated from laptop token counts; only the Noema-2B program run is measured on the board (part 3).
- The paired intervals are Wald intervals; with 50 problems they are approximate.
