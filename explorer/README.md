# explorer/

The M3Kang explorer: a small web app on the board to look at validation
problems, answer them yourself, then ask the language model. It runs on the
board and uses only the standard library and the `copilot/` package.

## Files

| File | What it does |
|---|---|
| `server.py` | The web server (port 8000, `127.0.0.1` by default). It reads the problems, the images and the retrieval index, and calls `copilot.pipeline.solve()`. |
| `index.html` | The page that the server sends to the browser. |

## Run

On the board, from the repository folder, with the model services running:

```bash
python3 explorer/server.py
```

It needs `data/val.jsonl` and the problem images in `data/images/`
(`laptop/prepare_m3kang.py --save-images`). With `data/index.db` it also shows
the most similar solved problems. With a server that can see images on
`VISION_PORT` ([`config.env`](../config.env)), it can send the image to the
model. `--input`, `--images`, `--index`, `--host`
and `--port` change the defaults (`python3 explorer/server.py --help`).

To open it on the laptop, forward port 8000 over SSH, as the guide shows. Do
not use port 8001: the docs site uses it.

The images are M3Kang problem images: never commit them (see
[`CLAUDE.md`](../CLAUDE.md)).

## Docs

- [Use the copilot on the board](../docs/how-to/use-copilot-on-board.md), section on the explorer: images, start, port forwarding.
- [Board setup guide](../docs/BOARD_SETUP.md), optional explorer step.
- Terms: [GLOSSARY.md](../GLOSSARY.md) (Validation set, Retrieval, Index, Language model).
