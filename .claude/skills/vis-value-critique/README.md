# vis-value-critique

A Claude Code skill that critiques a data visualization by the **value** it delivers
to its reader (Stasko's V = T + I + E + C; Munzner's expressiveness, effectiveness and
appropriateness; perception laws; Tufte; Correll 2020, Stokes & Hearst 2022, Wilmer &
Kerns 2022), not by how it looks. It is self-contained: nothing in it depends on the
repository it sits in.

## Install

Copy this folder, unchanged, to one of:

- `<repo>/.claude/skills/vis-value-critique/` to make it available in one project;
- `~/.claude/skills/vis-value-critique/` to make it available in every project.

Claude Code loads `SKILL.md` automatically. Trigger it by asking to critique, review,
grade, audit or improve a chart, figure, dashboard, map or infographic, or by typing
`/vis-value-critique`.

A packaged copy can be produced with the skill-creator's
`python -m scripts.package_skill <path>`; the resulting `.skill` file installs through
the claude.ai "Save skill" button.

## Requirements

Python 3.9+. The inspectors degrade gracefully when a library is missing and say so in
their `warnings`.

| Need | Used by |
|---|---|
| `numpy`, `Pillow` (required) | `inspect_image.py`, `measure_pie.py`, color-vision simulation |
| `matplotlib` | `inspect_matplotlib.py` (also `seaborn` scripts) |
| `plotly` | `inspect_plotly.py` on `.py` inputs (`.json`/`.html` need nothing) |
| `altair` | `inspect_vegalite.py` on `.py` inputs (`.json`/`.html` need nothing) |
| `vl_convert` | PNG rendering of Vega-Lite; otherwise an HTML fallback is written |
| `tesseract` CLI | text-size statistics in `inspect_image.py`; optional |

No network access is needed. The scripts never write outside the `--out-dir` you give
them (default: a fresh temporary directory).

## Layout

```
SKILL.md                      workflow and rules of the critique
references/value-framework.md purpose, V = T + I + E + C, design criteria, tasks, scoring
references/rules-catalog.md   ~170 rules tagged DET/SEMI/JUDG with severity, source, exception
references/chart-types.md     per idiom: data, tasks, limits, anti-patterns, alternatives
references/perception.md      channels, preattentive features, Gestalt, JND, Stevens, color, memory
references/papers.md          TRUNC/TEXT/MEANBAR/RAIN rules from four papers
references/multiple-views.md  composition, linking, overview/detail, the dashboard pass
references/report-template.md output format
scripts/inspect_vegalite.py   Altair / Vega-Lite (.json, .html, .py)
scripts/inspect_matplotlib.py matplotlib / seaborn scripts (runs them headless)
scripts/inspect_plotly.py     Plotly (.json, .html, .py)
scripts/inspect_image.py      PNG/JPG: palette, CVD simulations, grayscale, OCR text size
scripts/measure_pie.py        slice count, spans, order, start angle, exploded slices in an image
scripts/lie_factor.py         Tufte's lie factor from measured magnitudes
scripts/vischeck/             shared library (findings, color maths, palettes)
examples/                     deliberately bad charts and full critiques of them
evals/                        four test cases in the `claude plugin eval` layout
```

## Extending

- Add a rule: give it the next ID in its section of `rules-catalog.md`, tag its kind and
  severity, cite a source, state the exception. If it is mechanical, implement it in the
  matching inspector and emit the same ID.
- Keep IDs stable: the scripts, the examples and the eval graders cite them.
- Run the evals after changes: `claude plugin eval . --allow-tools Write,Edit,Bash
  --scaffold` from this folder (Claude Code ≥ 2.1.269), or run the four prompts by hand.
