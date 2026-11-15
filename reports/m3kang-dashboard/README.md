# M3Kang exploration dashboard

An exploration dashboard for the M3Kang dataset (high_quality shard 0, English problems). It answers five questions:
where the data is thin by level, year and language; how biased the answer key is; how much each level needs the
image; how long the problems are against the board's reading budget; and which problems sit behind each pattern.

Only the code is in Git. The built page shows the opening of every problem statement and loads the problem images,
so it counts as M3Kang derived data and stays on your machine (root `CLAUDE.md`, red line 1). Build your own copy:

```bash
cd reports/m3kang-dashboard
U="uv run --no-project --with altair==6.3.0 --with vl-convert-python==1.9.0 --with pandas --with pyarrow --with pillow --with huggingface_hub"
$U python build_data.py        # downloads shard 0 from Hugging Face; or pass --parquet <local shard>
$U python m3kang_dashboard.py  # writes m3kang_dashboard.html, .vl.json and .png
```

Open `m3kang_dashboard.html` in a browser. It loads images from `img/eng/` next to it.
`python test_interaction.py` (needs Playwright) clicks through the linked views and saves screenshots to `check/`.

The download needs a Hugging Face account that accepted the terms on the
[dataset card](https://huggingface.co/datasets/qualcomm/M3Kang).

## Files

| File | What it is |
|---|---|
| `build_data.py` | Flattens the parquet shard into `data/m3kang_rows.csv` (one row per problem and language) and writes `img/eng/<id>.png` |
| `m3kang_dashboard.py` | Builds the linked Altair views and the problem browser into one offline HTML file |
| `test_interaction.py` | Browser test of the selections |
| `m3kang_dashboard_design.md` | Design document (vis-design skill) |
| `m3kang_dashboard_critique.md` | Critique pass (vis-value-critique skill) and the fixes it led to |

`.gitignore` keeps `data/`, `img/`, `check/` and every built HTML, PNG and spec out of Git.
