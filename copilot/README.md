# copilot/

The Python package behind `predict.py`: one M3Kang problem in, one letter A to
E out. It runs on the board, uses only the standard library, and reads its
settings from [`config.env`](../config.env).

`predict.py`, `eval.py`, `build_index.py` (repository root) and
`explorer/server.py` import it. `predict.py` must keep the
[contract](../GLOSSARY.md): one letter per problem, at most 60 seconds, no
network, the same answers every time.

## Files

| File | What it does |
|---|---|
| `__init__.py` | Package marker. |
| `pipeline.py` | `solve()`: the only entry point. It gets a letter from the Prior solver first. With `SOLVER=prior` (the default) and no image, it stops there and calls no model. Otherwise it asks the language model, optionally with retrieval. Any failure gives `FALLBACK_ANSWER`. |
| `prior.py` | The Prior solver: a letter from the options alone, with no model. |
| `llm.py` | Builds the prompt and asks the language model (`math-llm`, port 8081) for one letter. |
| `embed.py` | Turns a text into a vector with the embedding model (`math-embed`, port 8082). |
| `rag.py` | The retrieval index: a SQLite file (`data/index.db`) that holds the solved training problems and their embeddings, searched by similarity. |
| `client.py` | A small JSON client for llama-server. |
| `config.py` | Reads `config.env`, the settings file that the board scripts also read. |

`SOLVER` in `config.env` chooses the solver: `prior` (Prior solver, the
default) or `letter` (Baseline: one letter from the language model).

## Run

On the board, from the repository folder, with the model services running:

```bash
python3 predict.py --input data/sample_problems.jsonl --output results/smoke.csv
```

Tests (no model and no M3Kang data needed), on the laptop or the board:

```bash
make test-copilot
```

## Docs

- [Board setup guide](../docs/BOARD_SETUP.md), steps 8-12: the first run, the Baseline and retrieval.
- [Use the copilot on the board](../docs/how-to/use-copilot-on-board.md): `predict.py`, `eval.py` and `--rag`.
- [Deploy the copilot on the board](../docs/how-to/deploy-copilot-on-board.md).
- [Try the Prior solver](../docs/how-to/try-prior-solver.md).
- Terms: [GLOSSARY.md](../GLOSSARY.md) (Copilot, Prior solver, Baseline, Contract, Retrieval, Index).
