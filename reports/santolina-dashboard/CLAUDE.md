# Working on the Santolina dashboard

Read `README.md` first. The root `CLAUDE.md` applies, above all the M3Kang red line. The rules of `../tukey-dashboard/CLAUDE.md` (minimal text, numbers filled from data, intervals by problem) apply here too.

## Rules

- **Edit the sources, never `santolina_dashboard.html`.** Rebuild with the command in `README.md`.
- **One meaning per colour**, as listed in the README table. A new view uses the existing meanings; it adds no new hue for something those meanings already cover. If you add a colour, add its dark-mode pair to `DARK_SWAP` in `page_template.html`, and a chip to the header key.
- **Text-light.** Use descriptive titles. A subtitle only defines marks and measures. Allowed labels are neutral facts. Conclusions go only in the decisions table, and every number there must be visible in a chart or marked "not plotted".
- **Say which "right" a view counts.** Part 2 counts the program's own answer, on one language (Ferran's grid). Part 3 counts the final answer after the letter fallback, on both languages. Keep the definitions in the subtitles.
- **Paired changes** (`changes()`) use the funnel's definition, outcome = right, on the same problem ids. Add a pair there only when both runs exist on the same problems.
- **Aggregates and ids only** in `data/`. Never copy text, options, programs or images from M3Kang or the practice set. The guard hook checks paths, not content.
- **Width budget:** every view must fit 1180 px. Check with one headless screenshot:
  `firefox --headless --no-remote --profile /tmp/ff --window-size=1280,7400 --screenshot /tmp/s.png "file://$PWD/santolina_dashboard.html"`.

## Skills

Use `/vis-design` to change a view's design. The record is `.claude/vis-decisions/p-…-santolina-dashboard-…`. Use `/vis-value-critique` after any change, and add the outcome to `santolina_dashboard_design.md`.

## Publish

Publish `santolina_dashboard.html` with the Artifact tool to <https://claude.ai/artifact/2aGz9HNXDeYBkwxekEHiiL>, passing that URL as `url`. That URL first held the Tukey-only page, so read it before publishing from a new session.
