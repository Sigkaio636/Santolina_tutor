# How to extract the vault papers to Markdown with MinerU

This how-to guide is for a team member who wants to read or search the papers of the paper vault as text. The paper vault (`docs/vault/papers/`) holds the research papers that we read, with one synthesis note per topic. See the [vault index](../vault/papers/README.md).

The guide installs [MinerU](https://github.com/opendatalab/MinerU) 3.4.5 in the
Santolina_tutor uv environment. MinerU converts the PDFs of the vault to Markdown.
It writes formulas as LaTeX and figures as images. You can then read and search them in
Obsidian, a Markdown note app that can open `docs/vault/` as a vault.

The guide uses MinerU's `pipeline` backend. This backend works on a machine without a GPU.
After the setup, MinerU does not use the network.

We checked the flags in this guide against the installed 3.4.5 (`mineru --help`).

## Before you start

- Linux, and [`uv`](https://docs.astral.sh/uv/) installed.
- Python 3.12 (`pyproject.toml` requires `~=3.12.0`; uv gets it if you do not have it).
- About 8 GB of free disk. After the install, `.venv` took 6.3 GB, because it includes the
  CUDA build of torch. The model weights take 1.6 GB more. (Measured on one laptop, 2026-11.)
- Network access for the setup only.
- Run every command from the repository root.

## 1. Download the PDFs

The PDFs are not in Git. A script downloads them from arXiv. Run it once:

```bash
bash docs/vault/papers/download.sh
```

It prints `OK <arXiv ID>` for each paper that it downloads, and skips the files that are
already there. The list of papers is in
[`papers.tsv`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/docs/vault/papers/papers.tsv).

Check:

```bash
ls docs/vault/papers/pruning/
```

You should see `sun2023_wanda_2306.11695.pdf` in the list.

## 2. Install MinerU in the project environment

MinerU is in the dependency group `ocr` (`[dependency-groups]` in `pyproject.toml`,
`mineru[core]==3.4.5`). It pulls torch and the CUDA libraries, so a normal install does
not include it. Install it with:

```bash
uv sync --group ocr
```

On a slow network the first install takes a long time. At about 2 MB/s it took 50 minutes
(measured on one laptop, 2026-11).

Check the installed version:

```bash
uv run --group ocr mineru --version
```

The output must be `mineru, version 3.4.5`.

!!! warning "A plain `uv sync` removes MinerU"
    `uv sync` without `--group ocr` makes the environment match the default groups exactly.
    `make requirements` calls it too. It uninstalls MinerU and its packages.
    The next `uv run --group ocr` installs them again, which takes as long as the first
    install. Always add `--group ocr` when you sync. To see what a sync would change, add
    `--dry-run`.

## 3. Put the model weights in `models/mineru-home/`

MinerU needs about 1.6 GB of layout, OCR, formula and table models. By default it writes
its config to `~/mineru.json` and its weights to `~/.cache/huggingface`. This guide keeps
both in `models/mineru-home/`, which git ignores.

Use one of the two ways below.

### Copy weights you already have (tested)

Use this way if another MinerU 3.4.5 install on your machine already has the weights.
Set `SRC` to the folder that holds its `pipeline` folder, then copy:

```bash
SRC=/path/to/other/mineru-home
mkdir -p models/mineru-home && cp -r "$SRC/pipeline" models/mineru-home/
```

Then write `models/mineru-home/mineru.json`. The command puts the **absolute** path of your
copy in `models-dir.pipeline`:

```bash
cat > models/mineru-home/mineru.json <<EOF
{
    "latex-delimiter-config": {
        "display": {"left": "\$\$", "right": "\$\$"},
        "inline": {"left": "\$", "right": "\$"}
    },
    "models-dir": {
        "pipeline": "$PWD/models/mineru-home/pipeline",
        "vlm": ""
    },
    "model-source": "huggingface",
    "config_version": "1.3.2"
}
EOF
```

The backslashes keep the `$` signs of the LaTeX delimiters. `$PWD` becomes the
absolute path of the repository.

`models-dir.pipeline` can be any directory that contains `models/Layout`, `models/MFR`,
`models/OCR`, `models/TabCls` and `models/TabRec`.

!!! warning "Do not set `model-source` to `local` in `mineru.json`"
    MinerU accepts only `huggingface` or `modelscope` in that field. It rejects `local`
    with a warning and then tries the network. To work offline, set the environment variable
    `MINERU_MODEL_SOURCE=local` (step 4).

### Download the weights (not tested)

!!! note "Not tested in this repository"
    We did not run these commands in this repository. On the first machine we copied the
    weights (the way above).

```bash
mkdir -p models/mineru-home
export MINERU_TOOLS_CONFIG_JSON="$PWD/models/mineru-home/mineru.json"
export MINERU_MODEL_SOURCE=huggingface
export HF_HOME="$PWD/models/mineru-home/huggingface"
uv run --group ocr mineru-models-download -m pipeline -s huggingface
```

If HuggingFace is slow, download from ModelScope instead:

```bash
mkdir -p models/mineru-home
export MINERU_TOOLS_CONFIG_JSON="$PWD/models/mineru-home/mineru.json"
export MINERU_MODEL_SOURCE=modelscope
export HF_HOME="$PWD/models/mineru-home/huggingface"
export MODELSCOPE_CACHE="$PWD/models/mineru-home/modelscope"
uv run --group ocr mineru-models-download -m pipeline -s modelscope
```

Without `MODELSCOPE_CACHE`, the weights go to `~/.cache/modelscope`.

The download writes `mineru.json` itself, with `models-dir` set to the downloaded files.
Step 4 sets `MINERU_MODEL_SOURCE` to `local` again.

### Check the weights

For both ways, list the model folders that `mineru.json` points to:

```bash
ls "$(python3 -c 'import json; print(json.load(open("models/mineru-home/mineru.json"))["models-dir"]["pipeline"])')/models"
```

You should see `Layout`, `MFR`, `OCR`, `TabCls` and `TabRec` in the list.

## 4. Set the environment in your shell

Paste this block in each new terminal before you run MinerU:

```bash
export MINERU_HOME="$PWD/models/mineru-home"
export MINERU_TOOLS_CONFIG_JSON="$MINERU_HOME/mineru.json"
export MINERU_MODEL_SOURCE=local
export HF_HOME="$MINERU_HOME/huggingface"
export HF_HUB_CACHE="$MINERU_HOME/huggingface/hub"
export MODELSCOPE_CACHE="$MINERU_HOME/modelscope"
export PADDLE_PDX_CACHE_HOME="$MINERU_HOME/paddlex"
```

What each variable does:

- `MINERU_TOOLS_CONFIG_JSON` makes MinerU read `models/mineru-home/mineru.json` in place of
  `~/mineru.json`. The path must be absolute; `$PWD` makes it absolute.
- `MINERU_MODEL_SOURCE=local` makes MinerU use the local weights. It never downloads in
  this mode: if the weights are not configured, it stops with an error.
- The four cache variables send any unexpected download to `models/mineru-home/`, not to
  your home directory.

## 5. Check the setup with one page

```bash
uv run --group ocr mineru -p docs/vault/papers/pruning/sun2023_wanda_2306.11695.pdf -o /tmp/mineru-check -b pipeline -m auto -s 0 -e 0
```

- `-o /tmp/mineru-check` keeps this one-page test out of the vault. Do not write it to
  `parsed/`. The academic-paper-summarizer skill (a Claude Code skill that summarizes
  papers) skips a paper that already has a Markdown file there. It would then read this
  single page as the whole paper.
- `-b pipeline` is necessary. The default backend (`hybrid-engine`) needs a vision-language
  model that we did not install.
- `-s 0 -e 0` parses only the first page. Page numbers start at 0.

On one laptop (CPU only, 2026-11) this took 35–37 s and used about 2.6 GB of RAM at the peak.
Most of the time is a fixed start cost: each `mineru` command starts a temporary local
`mineru-api` service.

The result is `/tmp/mineru-check/sun2023_wanda_2306.11695/auto/sun2023_wanda_2306.11695.md`.
Open it. You should see the paper's title and the start of its abstract as readable text.

## 6. Extract the papers

Write the output to a `parsed/` folder next to the PDFs. Git ignores every
`docs/vault/**/parsed/` folder, because the output is derived and large.

One complete paper:

```bash
uv run --group ocr mineru -p docs/vault/papers/quantization/frantar2022_gptq_2210.17323.pdf -o docs/vault/papers/quantization/parsed -b pipeline -m auto
```

A complete category folder (`-p` also accepts a directory; it does not go into
subfolders):

```bash
uv run --group ocr mineru -p docs/vault/papers/pruning -o docs/vault/papers/pruning/parsed -b pipeline -m auto
```

A paper takes minutes, not seconds. Extract the folders one at a time.

Check:

```bash
ls docs/vault/papers/pruning/parsed/
```

You should see one folder per PDF. Each folder holds an `auto/` folder with the files in the
next section.

## What MinerU writes

For each PDF, MinerU writes a folder `<output>/<pdf name>/auto/` that contains:

| File | Content |
|---|---|
| `<name>.md` | The Markdown text. Formulas use `$...$` and `$$...$$`, which Obsidian shows as LaTeX |
| `images/` | The figures and tables as images, linked from the `.md`. MinerU writes it only when the pages have figures |
| `<name>_content_list.json`, `<name>_content_list_v2.json` | The content as a list of blocks (text, equation, table, image, chart). Titles are text blocks with a `text_level` |
| `<name>_middle.json`, `<name>_model.json` | Intermediate data from the models |
| `<name>_layout.pdf`, `<name>_span.pdf` | The PDF with the detected blocks drawn on it. Use them to check bad extractions |
| `<name>_origin.pdf` | A copy of the input |

## Useful MinerU flags

| Need | Flag |
|---|---|
| Faster, without formulas or tables | `-f false -t false` |
| A scanned PDF with no text layer | `-m ocr`. The arXiv PDFs have a text layer, so `-m auto` is correct for them |
| Only some pages | `-s <first> -e <last>`, starting at 0 |
| OCR language | `-l <lang>`. Without `-l`, MinerU uses `ch`, whose model also reads the Latin alphabet. `-l en` is accepted and becomes `ch` |

All flags: `uv run --group ocr mineru --help`.

## If something fails

- **MinerU installs its packages again before it runs.** A `uv sync` without
  `--group ocr` removed them (see the warning in step 2). `uv run --group ocr` puts them
  back. If you call `.venv/bin/mineru` directly, you get `No such file or directory`
  instead. Run `uv sync --group ocr`.
- **MinerU tries to download models.** The variables from step 4 are not set in this
  terminal. Paste the block again.
- **MinerU stops with an error about the local model path.** `models/mineru-home/mineru.json`
  is missing, or `models-dir.pipeline` has a wrong path. Do step 3 again.
- **The process stops on a long paper (out of memory).** Extract the paper in page ranges
  with `-s` and `-e`.
