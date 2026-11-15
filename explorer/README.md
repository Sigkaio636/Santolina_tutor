# explorer/

The M3Kang explorer: a small web app for people who work on the copilot. It
shows each validation problem. You answer it yourself, then ask the copilot
and compare. It runs on the board and uses only the Python standard library
and the [`copilot/`](../copilot/README.md) package.

With the default `SOLVER=prior`, **Ask the model** returns the Prior solver's letter and
calls no model. Ticking **Send the image** sends the problem image to a server
that can see images, on `VISION_PORT` in [`config.env`](../config.env)
([board setup guide](../docs/BOARD_SETUP.md#let-the-model-see-the-image-experiment)).

## Files

| File | What it does |
|---|---|
| `server.py` | The web server (port 8000, `127.0.0.1` by default). It reads the problems, the images and the Index, and calls `copilot.pipeline.solve()`. |
| `index.html` | The page that the server sends to the browser. |

## Run

Before you start, the board needs `data/val.jsonl` (from
`laptop/prepare_m3kang.py`, copied to the board). Optional: the problem images
in `data/images/`, and the Index `data/index.db` (from `build_index.py`) for
similar solved problems. The images are M3Kang problem images: never commit
them (see [`CLAUDE.md`](../CLAUDE.md)). How to make and copy them:
[Use the copilot on the board](../docs/how-to/use-copilot-on-board.md#view-the-problems-in-a-browser).

On the board, in `~/Santolina_tutor`:

```bash
python3 explorer/server.py
```

The last line it prints is `Open http://127.0.0.1:8000`. Options:
`python3 explorer/server.py --help`. To open it on your laptop, forward port
8000 over SSH as that guide shows.

## Docs

- [Use the copilot on the board](../docs/how-to/use-copilot-on-board.md#view-the-problems-in-a-browser): images, start, port forwarding. It replaces the organizers' [explorer step](../docs/BOARD_SETUP.md#optional-explore-the-problems-in-your-browser) of the board setup guide.
- Terms: [GLOSSARY.md](../GLOSSARY.md) (M3Kang, Board, Copilot, Prior solver, Validation set, Index).
