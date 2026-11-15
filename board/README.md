# board/

Shell scripts that set up the board (the Linux side of the Arduino UNO Q), the
systemd units they install, and the App Lab app for the LED matrix. Everything
here runs on the board.

## Setup scripts

Run them in order, on the board, from the repository folder
(`~/Santolina_tutor`), for example `./board/00_check_board.sh`. Each script
reads its settings from [`config.env`](../config.env). The scripts that need
root call `sudo` themselves and ask for the password once.

| Script | What it does |
|---|---|
| `00_check_board.sh` | Checks RAM, disk, clock, SSH, the package index, the network and what is installed. It changes nothing. Safe to run at any time. |
| `01_install_packages.sh` | Installs the system packages that the llama.cpp build needs. Needs internet. |
| `02_build_llama_cpp.sh` | Downloads llama.cpp at the pinned commit and builds it. |
| `03_download_models.sh` | Downloads the pinned language model and embedding model and checks their SHA256. Resumes a partial download. |
| `04_install_services.sh` | Installs and starts the model services `math-llm` and `math-embed`. Run it again after each change to `config.env`. |
| `05_smoke_test.sh` | Checks both servers, one embedding, and `predict.py` on `data/sample_problems.jsonl`. |
| `06_install_student_app.sh` | Starts the student app at every boot (`santolina-student.service`, port 80) and sends every web address on the hotspot to the board. |
| `07_install_led_app.sh` | Installs the App Lab app `app-lab/santolina-leds` and starts it at every boot. Needs internet on the first start and the student app (06). No sudo. |
| `08_install_tutor.sh` | Installs `math-tutor.service`, the tutor model. The model is not downloadable: copy it from the laptop to `~/models/` first. If the file is missing, the script stops and prints the `adb push` command. |

Scripts 00-05 set up the copilot. Scripts 06-08 add the student app and are
optional for `predict.py`.

## Other files

| Path | What it is |
|---|---|
| `common.sh` | Helpers that the scripts source. Do not run it. |
| `ocr_speed.sh` | Times the OCR engines on the board CPU. Used only by the [Tesseract text-only report](../docs/experiments/2026-11-tesseract-text-only.md) (section Speed). |
| `systemd/math-llm.service` | Template for the language model service (port `LLM_PORT`). |
| `systemd/math-embed.service` | Template for the embedding model service (port `EMBED_PORT`). |
| `systemd/math-tutor.service` | Template for the tutor model service (port `TUTOR_PORT`). |
| `systemd/santolina-student.service` | Template for the student app service (port 80). |
| `app-lab/santolina-leds/` | App Lab app: `python/main.py` asks the student app for the board state, `sketch/sketch.ino` draws it on the 8x13 LED matrix. |

The install scripts fill in the `@...@` fields of the `systemd/` templates. Do
not copy a template to `/etc/systemd/system/` by hand.

## Docs

- [Board setup guide](../docs/BOARD_SETUP.md): the organizers' step-by-step guide, which scripts 00-05 automate.
- [Deploy the copilot on the board](../docs/how-to/deploy-copilot-on-board.md): scripts 00-05 and what to run again after a change.
- [Use the student app](../docs/how-to/use-student-app.md): scripts 06-08.
- [Back up and restore a board](../docs/how-to/back-up-and-restore-a-board.md).
- [LED matrix design](../docs/LED_MATRIX_DESIGN.md) and [board reference](../docs/UNO_Q_BOARD_REFERENCE.md).
- Terms: [GLOSSARY.md](../GLOSSARY.md) (Model services, Tutor model, Student app, Hotspot).
