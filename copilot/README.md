# copilot/

The Python package behind `predict.py`: one [M3Kang](../GLOSSARY.md) problem
in, one letter A to E out. Start here to change how `predict.py` answers. It
runs on the board (the Arduino UNO Q) and on a laptop, uses only the Python
standard library, and reads its settings from [`config.env`](../config.env).

`predict.py`, `eval.py`, `build_index.py` (repository root) and
`explorer/server.py` import it, and so do `laptop/eval_vision.py` and `laptop/prior_txto_no.py`. `predict.py` must keep the Contract (see
[GLOSSARY.md](../GLOSSARY.md)).

`SOLVER` in `config.env` chooses how to answer: `prior` (the default, the
Prior solver: no model call) or `letter` (the Baseline: one letter from the
language model).

## Files

| File | What it does |
|---|---|
| `__init__.py` | Package marker. |
| `pipeline.py` | `solve()`: the only entry point. It gets a letter from the Prior solver first. With `SOLVER=prior` and no image, it stops there. Otherwise it asks a model, optionally with retrieval. Any failure gives `FALLBACK_ANSWER` (D in `config.env`). |
| `prior.py` | The Prior solver: a letter from the options alone. |
| `llm.py` | Builds the prompt and asks the language model (`math-llm`, port 8081) for one letter. |
| `embed.py` | Turns a text into a vector with the embedding model (`math-embed`, port 8082). |
| `rag.py` | Retrieval: searches the Index (`data/index.db`) for the most similar solved problems. `build_index.py` builds the Index. The Index is not in Git. `student_app/` (free mode, learning path, clues) and `teacher_app/kangaroo.py` read its `problems` table directly: keep its columns and keys. |
| `client.py` | A small JSON client for the llama.cpp servers. |
| `config.py` | Reads `config.env`, the settings file that the board scripts also read. |

## Run

On the board, in `~/Santolina_tutor` (see [`board/`](../board/README.md)):

```bash
python3 predict.py --input data/sample_problems.jsonl --output results/smoke.csv
```

`results/smoke.csv` has one row per problem with `status` `ok`. To test the
language model, start
the model services and run `SOLVER=letter python3 predict.py ...`. More in
[Try the Prior solver](../docs/how-to/try-prior-solver.md).

Tests: `make test-copilot`, on the laptop or the board (see [`tests/`](../tests/README.md)).

## Docs

- [Board setup guide](../docs/BOARD_SETUP.md), steps 8-12: first run, M3Kang data, the Baseline and retrieval.
- [Use the copilot on the board](../docs/how-to/use-copilot-on-board.md): `predict.py`, `eval.py` and `--rag`.
- [Deploy the copilot on the board](../docs/how-to/deploy-copilot-on-board.md): check and smoke test with the board scripts.
- [Try the Prior solver](../docs/how-to/try-prior-solver.md): compare `SOLVER=prior` and `SOLVER=letter`.
- Terms: [GLOSSARY.md](../GLOSSARY.md) (M3Kang, Board, Copilot, Contract, Prior solver, Baseline, Language model, Embedding model, Model services, Retrieval, Index).
