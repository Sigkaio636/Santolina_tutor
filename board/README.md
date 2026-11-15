# board/

Shell scripts that set up the board (the Linux side of the Arduino UNO Q) to
run the [copilot](../README.md) and the student app, the systemd units they
install, and an App Lab app for the LED matrix. The scripts run on the board.
The App Lab sketch runs on the UNO Q's microcontroller.

## Setup scripts

First get a shell on the board and the repository there
([board setup guide](../docs/BOARD_SETUP.md), [step 0](../docs/BOARD_SETUP.md#step-0-connect-to-the-board)
and [step 8.1](../docs/BOARD_SETUP.md#81-clone-this-repository-on-the-board)). Then, on the board:

```bash
cd ~/Santolina_tutor
./board/00_check_board.sh
```

Run 00-05 in that order. 06-08 add the student app and are not needed by
`predict.py`. Each script reads its settings from
[`config.env`](../config.env). The scripts that need root call `sudo` themselves
and ask for the password once.

| Script | What it does |
|---|---|
| `00_check_board.sh` | Checks RAM, disk, clock, SSH, the package list, the network and what is installed. It changes nothing. |
| `01_install_packages.sh` | Installs the system packages that the llama.cpp build needs. Needs internet. |
| `02_build_llama_cpp.sh` | Downloads llama.cpp at the pinned commit and builds it. |
| `03_download_models.sh` | Downloads the pinned language model and embedding model and checks their SHA256. Resumes a partial download. |
| `04_install_services.sh` | Installs and starts the model services `math-llm` and `math-embed`. To run again after a change: see the table in [Deploy the copilot](../docs/how-to/deploy-copilot-on-board.md). |
| `05_smoke_test.sh` | Checks both model services, one embedding, and `predict.py` on `data/sample_problems.jsonl`. |
| `06_install_student_app.sh` | Starts the student app at every boot (`santolina-student.service`, port 80). Points every web address on the hotspot to the board, so phones open the student app. |
| `07_install_led_app.sh` | Installs the App Lab app `app-lab/santolina-leds` and starts it at every boot. Its first start needs internet. It needs 06. It does not use sudo. |
| `08_install_tutor.sh` | Installs `math-tutor.service`, the Tutor model. The fine-tuned model is not published: copy `qwen35-tutor-Q8_0.gguf` to `~/models/` first. If it is missing, the script stops and prints the `adb push` command. Without it, the student app uses fixed texts. |

## Other files

| Path | What it is |
|---|---|
| `common.sh` | Helpers that the scripts source. Do not run it. |
| `ocr_speed.sh` | Times the OCR (optical character recognition) engines on the board CPU. Used only by the [Tesseract text-only report](../docs/experiments/2026-11-tesseract-text-only.md#speed). |
| `systemd/math-llm.service` | Template for the language model service (port 8081, `LLM_PORT`). |
| `systemd/math-embed.service` | Template for the embedding model service (port 8082, `EMBED_PORT`). |
| `systemd/math-tutor.service` | Template for the Tutor model service (port 8084, `TUTOR_PORT`). The student app does not read `TUTOR_PORT`: it uses 8084 or `SANTOLINA_TUTOR_URL`. |
| `systemd/santolina-student.service` | Template for the student app service (port 80). |
| `app-lab/santolina-leds/` | App Lab app. `python/main.py` runs on the Linux side, in App Lab's container. It asks the student app whether the hotspot is on, a phone is connected and the Tutor model is writing. `sketch/sketch.ino` draws it on the 8x13 LED matrix. |

The install scripts fill in the `@...@` fields of the `systemd/` templates. Do
not copy a template to `/etc/systemd/system/` by hand.

## Docs

- [Board setup guide](../docs/BOARD_SETUP.md): the organizers' step-by-step guide, which scripts 00-05 automate.
- [Deploy the copilot on the board](../docs/how-to/deploy-copilot-on-board.md): check, smoke test, and what to run again after a change.
- [Use the student app](../docs/how-to/use-student-app.md): scripts 06-08.
- [Back up and restore a board](../docs/how-to/back-up-and-restore-a-board.md).
- [LED matrix design](../docs/LED_MATRIX_DESIGN.md) and [board reference](../docs/UNO_Q_BOARD_REFERENCE.md).
- Terms: [GLOSSARY.md](../GLOSSARY.md) (Board, UNO Q, Copilot, Model services, Language model, Embedding model, Tutor model, Student app, Hotspot).
