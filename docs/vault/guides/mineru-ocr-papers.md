# How to extract the vault papers to Markdown with MinerU

This guide installs [MinerU](https://github.com/opendatalab/MinerU) 3.4.5 in the
Santolina_tutor uv environment. Then it converts the PDFs in `docs/vault/papers/` to
Markdown, with formulas as LaTeX and figures as images, so you can read and search them in
Obsidian. The `pipeline` backend that this guide uses works on a machine without a GPU,
and MinerU does not use the network after the setup.

The setup follows the DigestBooks project (`~/Documents/Digestive`,
`docs/development.md`, section "MinerU setup"), which measured its benchmarks with
MinerU 3.4.5. We checked the flags in this guide against the installed 3.4.5
(`mineru --help`).

## Before you start

- Linux, and [`uv`](https://docs.astral.sh/uv/) installed.
- Python 3.12 (`pyproject.toml` requires `~=3.12.0`; uv gets it if you do not have it).
- About 8 GB of free disk: `.venv` measured 6.3 GB after the install (it includes the CUDA
  build of torch), and the model weights are 1.6 GB.
- Network access for the setup only.
- Run every command from the repository root.

## 1. Install MinerU in the project environment

MinerU is in the dependency group `ocr` (`[dependency-groups]` in `pyproject.toml`,
`mineru[core]==3.4.5`). It pulls torch and the CUDA libraries, so a normal install does
not include it. Install it with:

```bash
uv sync --group ocr
```

On a slow network the first install takes a long time. At about 2 MB/s it took 50 minutes.

Check the installed version:

```bash
uv run --group ocr mineru --version
```

The output must be `mineru, version 3.4.5`.

> [!warning] A plain `uv sync` removes MinerU
> `uv sync` without `--group ocr` (and `make requirements`, which calls it) makes the
> environment match the default groups exactly. It uninstalls MinerU and its packages.
> The next `uv run --group ocr` installs them again, which takes as long as the first
> install. Always add `--group ocr` when you sync. To see what a sync would change, add
> `--dry-run`.

## 2. Put the model weights in `models/mineru-home/`

MinerU needs about 1.6 GB of layout, OCR, formula and table models. By default it writes
its config to `~/mineru.json` and its weights to `~/.cache/huggingface`. This guide keeps
both in `models/mineru-home/`, which git ignores.

### Option A: download the weights

```bash
mkdir -p models/mineru-home
```

```bash
MINERU_TOOLS_CONFIG_JSON="$PWD/models/mineru-home/mineru.json" MINERU_MODEL_SOURCE=huggingface HF_HOME="$PWD/models/mineru-home/huggingface" uv run --group ocr mineru-models-download -m pipeline -s huggingface
```

If HuggingFace is slow, download from ModelScope. Set `MINERU_MODEL_SOURCE=modelscope`,
use `-s modelscope`, and add `MODELSCOPE_CACHE="$PWD/models/mineru-home/modelscope"`.
Without `MODELSCOPE_CACHE`, the weights go to `~/.cache/modelscope`.

The download writes `mineru.json` itself, with `models-dir` set to the downloaded files.

> [!note] Not tested in this repository
> These commands follow the DigestBooks recipe, adapted to the paths of this repository.
> On the first machine we copied the weights (Option B) and did not run a download.

### Option B: copy weights you already have

Use this option if another MinerU 3.4.5 install on your machine already has the weights,
for example DigestBooks in `~/Documents/Digestive/src/mineru-home/`.

```bash
mkdir -p models/mineru-home && cp -r ~/Documents/Digestive/src/mineru-home/pipeline models/mineru-home/
```

Then create `models/mineru-home/mineru.json`. Write the **absolute** path of your copy in
`models-dir.pipeline`:

```json
{
    "latex-delimiter-config": {
        "display": {"left": "$$", "right": "$$"},
        "inline": {"left": "$", "right": "$"}
    },
    "models-dir": {
        "pipeline": "/ABSOLUTE/PATH/TO/Santolina_tutor/models/mineru-home/pipeline",
        "vlm": ""
    },
    "model-source": "huggingface",
    "config_version": "1.3.2"
}
```

`models-dir.pipeline` can be any directory that contains `models/Layout`, `models/MFR`,
`models/OCR`, `models/TabCls` and `models/TabRec`.

> [!warning] Do not write `"model-source": "local"` in `mineru.json`
> MinerU accepts only `huggingface` or `modelscope` in that field. It rejects `local`
> with a warning and then tries the network. To work offline, set the environment variable
> `MINERU_MODEL_SOURCE=local` (step 3).

## 3. Set the environment in your shell

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

## 4. Check the setup with one page

```bash
uv run --group ocr mineru -p docs/vault/papers/pruning/sun2023_wanda_2306.11695.pdf -o /tmp/mineru-check -b pipeline -m auto -s 0 -e 0
```

- `-o /tmp/mineru-check` keeps this one-page test out of the vault. Do not write it to
  `parsed/`: the academic-paper-summarizer skill skips a paper that already has a
  Markdown file there, so it would read this single page as the whole paper.
- `-b pipeline` is necessary. The default backend (`hybrid-engine`) needs a vision-language
  model that we did not install.
- `-s 0 -e 0` parses only the first page. Page numbers start at 0.

On our machine (CPU only) this took 35–37 s and used about 2.6 GB of RAM at the peak.
Most of the time is a fixed start cost: each `mineru` command starts a temporary local
`mineru-api` service.

The result is `/tmp/mineru-check/sun2023_wanda_2306.11695/auto/sun2023_wanda_2306.11695.md`.
Open it and look at the title and the abstract.

## 5. Extract the papers

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

A paper takes minutes, not seconds. DigestBooks measured 5–13 s per page on a CPU, plus
the start cost. Extract the folders one at a time.

## 6. Find the output

For each PDF, MinerU writes a folder `<output>/<pdf name>/auto/` that contains:

| File | Content |
|---|---|
| `<name>.md` | The Markdown text. Formulas use `$...$` and `$$...$$`, which Obsidian shows as LaTeX |
| `images/` | The figures and tables as images, linked from the `.md`. MinerU writes it only when the pages have figures |
| `<name>_content_list.json`, `<name>_content_list_v2.json` | The content as a list of blocks (text, equation, table, image, chart). Titles are text blocks with a `text_level` |
| `<name>_middle.json`, `<name>_model.json` | Intermediate data from the models |
| `<name>_layout.pdf`, `<name>_span.pdf` | The PDF with the detected blocks drawn on it. Use them to check bad extractions |
| `<name>_origin.pdf` | A copy of the input |

## Options

| Need | Flag |
|---|---|
| Faster, without formulas or tables | `-f false -t false`. DigestBooks measured a 2.4× speed-up on a dense mathematics chapter |
| A scanned PDF with no text layer | `-m ocr`. The arXiv PDFs have a text layer, so `-m auto` is correct for them |
| Only some pages | `-s <first> -e <last>`, starting at 0 |
| OCR language | `-l <lang>`. Without `-l`, MinerU uses `ch`, whose model also reads the Latin alphabet. `-l en` is accepted and becomes `ch` |

All flags: `uv run --group ocr mineru --help`.

## Problems

- **MinerU installs its packages again before it runs.** Someone ran `uv sync` without
  `--group ocr`, and `uv run --group ocr` puts them back. If you call `.venv/bin/mineru`
  directly, you get `No such file or directory` instead. Run `uv sync --group ocr`.
- **MinerU tries to download models.** The variables from step 3 are not set in this
  terminal. Paste the block again.
- **MinerU stops with an error about the local model path.** `models/mineru-home/mineru.json`
  is missing, or `models-dir.pipeline` has a wrong path. Do step 2 again.
- **The process stops on a long paper (out of memory).** Extract the paper in page ranges
  with `-s` and `-e`. `-f false -t false` helps less: DigestBooks measured a saving of only
  about 0.8 GB. DigestBooks also suggests the variable `MINERU_VIRTUAL_VRAM_SIZE`, which we
  did not test.
