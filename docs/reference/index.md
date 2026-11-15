# Reference

Facts to look up while you work: the board, the data that the apps share, the tutor's design and the models. To do a task, see [How-to guides](../how-to/index.md). To rebuild the shipped build, see [Tutorials](../tutorials/index.md).

## The board

| Page | What it holds |
| --- | --- |
| [UNO Q board reference](../UNO_Q_BOARD_REFERENCE.md) | The canonical page for the board: specs, ports, limits, the Bridge between Linux and the microcontroller, measured speeds |
| [Board limits (interactive)](../GUIA_RESTRICCIONES_UNOQ.html) | One HTML page with the challenge constraints and the board specs that limit the copilot |
| [LED matrix design](../LED_MATRIX_DESIGN.md) (in Spanish) | What the 8 × 13 LED matrix shows and how the App Lab app computes it |
| [Board data contract](board-data-contract.md) | The files a board keeps under `~/santolina/`, shared by the teacher app and the student app |

## The tutor

| Page | What it holds |
| --- | --- |
| [Tutor response types](../TUTOR_RESPONSE_TYPES.md) (in Spanish) | The kinds of reply the tutor can give to a student message, when each one fits, and how to write it |
| [Student data and privacy](../explanation/student-data-privacy.md) | What a teacher in Catalonia could legally collect, compared with what the app collects. Not legal advice. |

## Models

| Page | What it holds |
| --- | --- |
| [Models](../models/index.md) | Every model we use or tested, its role, and whether the shipped build runs it |
| [The tutor fine-tune](../models/qwen35-tutor.md) | How we trained `qwen35-tutor`: data, settings, run log, results and how to train it again |
| [decider-2b-vision](../models/decider-2b-vision.md) and [InternVL3.5-1B](../models/internvl3.5-1b.md) | One row per run of each vision model, and the verdict |

## Terms

The [glossary](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) defines the project's terms, for example contract, baseline, hidden test, validation set and free mode.
