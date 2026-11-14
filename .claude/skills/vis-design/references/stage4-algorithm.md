# Stage 4 · Algorithm design

Goal: runnable code that renders exactly the stage-3 encoding from the stage-2 data
abstraction, reproducibly and fast enough, plus the run log that proves it.

## Decisions to make (asked in call 4 of the questionnaire)

- **Library**: asked every run; the project's last choice (`project.yaml → library`) is
  the recommended option. Each option says whether it is importable here and whether a PNG
  renderer exists (Altair needs `vl_convert`; Plotly needs `kaleido`; matplotlib renders
  natively). The record's `solution.library_notes` give per-library hints for the idiom;
  the catalog's `library_support` says native / workaround / none.
- **Host**: script (saves files), Streamlit app (widgets map 1:1 to the interaction plan;
  default widget state answers the main question), notebook cell.
- **Validation method for stage 3** and **output location**.

## Pipeline

`load()` → explicit parsing: delimiter and decimal detected by `profile_data.py`, date
columns parsed with the detected format, code columns kept as strings, sentinel values
dropped and reported, required columns asserted. `derive()` → every derived attribute of
the design document with the same name, pre-aggregated in pandas so the chart receives
the final table (Altair's 5,000-row default limit, Plotly's size). `takeaway(df)` →
computes the title text from the data (extremum, share, change), never a literal number.
`build_chart(df)` → the encodings, scales, order, palette, text and interaction of stage
3. `save()` → per library: Altair writes `.html` and `.vl.json` always and `.png` when
`vl_convert` exists; matplotlib writes `.png` at 200 dpi and optionally `.svg`; Plotly
writes `.html` always and `.png` when `kaleido` exists.

## Performance and limits

State rows in, rows after derivation, runtime of the run check, and known limits (Altair
inline data size, Plotly HTML size, matplotlib without interaction, Streamlit rerun cost).
If the derived table exceeds ~5k rows for Altair, aggregate further or disable the row
limit deliberately and say so.

## Validation (threat: wrong algorithm)

`scripts/run_check.py chart.py --library L --out-dir OUT [--data D] [--streamlit app.py]`:
imports preflight, headless execution with timeout, output listing, sibling inspectors
when installed (critical deterministic findings on EXP-01/02/03/05/06/08/09/11 and
COL-02/05 block acceptance; fix and re-run, at most twice), `inspect_image.py` on the
PNG, Streamlit `AppTest` smoke test. The JSON goes into section 4 of the design document.
Then compare the render with stage 3 by eye: same idiom, same order, same baseline, same
labels. Without a PNG renderer, serve the HTML (`python3 -m http.server`) and screenshot
it in the browser tool.

## Rejected alternatives

Record the libraries/hosts not chosen and why (not installed, no native support for the
idiom, interaction needed, print target).
