# Santolina tutor

A math copilot that runs entirely on an Arduino UNO Q 4 GB, for the Qualcomm challenge of Datathon FME 2026. It works with the M3Kang dataset.

## Language

**Copilot**:
The program in this repository that answers M3Kang problems and helps a student, and that runs offline on the board.
_Avoid_: tutor, assistant, bot

**Board**:
The Arduino UNO Q 4 GB. In the docs, "the board" always means the Linux side (the Qualcomm QRB2210), not the STM32 microcontroller.
_Avoid_: device, Arduino, SBC

**Model services**:
The two llama.cpp servers that start at boot: `math-llm` on port 8081 and `math-embed` on port 8082. They listen on `127.0.0.1` only.
_Avoid_: servers (when you mean both), daemons

**Language model**:
The small model that reads a problem and writes the answer: Qwen3.5 0.8B, Q8_0, served by `math-llm`.
_Avoid_: LLM, the model

**Embedding model**:
The model that turns a text into 384 numbers so similar problems can be found: bge-small-en-v1.5, served by `math-embed`.
_Avoid_: encoder, vectorizer

**Contract**:
The rules that `predict.py` must keep for the organizers' hidden test: one letter A to E per problem, at most 60 seconds, no network, the same answers every time.
_Avoid_: spec, interface

**Baseline**:
The copilot as the organizers shipped it: one letter from the language model, with no retrieval. The reference score is 22.5% on 40 English problems whose options OCR read.
_Avoid_: default, starting model

**Retrieval (RAG)**:
Adding the most similar solved problems to the prompt, found with the embedding model. Turned on with `--rag K`.
_Avoid_: lookup, memory

**Index**:
The SQLite file `data/index.db` that holds the embeddings of the training problems for retrieval.
_Avoid_: database (alone), vector store

**Validation set**:
The share of M3Kang problems held out in `data/val.jsonl` to measure the copilot. It is split by problem ID, so a problem and its translations are never on both sides.
_Avoid_: test set (the hidden test set belongs to the organizers)

**Experiment**:
One run of `eval.py`. It adds one line to `results/ablations.csv`, with the Git commit.
_Avoid_: trial, run (alone)

**Teacher app**:
The local web app on the teacher's laptop (`teacher_app/`). It sets up boards, loads exercise packs, unloads student data and shows statistics. It talks to boards over USB with adb.
_Avoid_: dashboard (that is one page of it), admin panel

**Teacher store**:
The teacher app's SQLite file, `~/.local/share/santolina-teacher/teacher.sqlite3` by default. It is centred on students and never goes into Git.
_Avoid_: index (that is the retrieval file on the board), database (alone)

**Board data contract**:
The files a board keeps under `~/santolina/` (identity, mode, roster, exercise packs, outbox, archive) and their JSON formats, implemented by the `classroom/` package. See `docs/reference/board-data-contract.md`.
_Avoid_: contract (alone: that is the `predict.py` rules)

**Student**:
A person in the teacher store, with a display name and a group. The board never sees the name, only the student code.
_Avoid_: user, pupil

**Group**:
A class of students, such as "3r ESO B". A board belongs to one group and receives that group's student codes.
_Avoid_: class (clashes with Python), course

**Student code**:
A short pseudonymous code such as `K7M2`. The student types it on the board, and every event carries it.
_Avoid_: ID, PIN, password

**Mode**:
`student` (locked) or `professor` (unlocked), stored in `~/santolina/mode.json`. Only the teacher app changes it.
_Avoid_: state, lock

**Exercise pack**:
A versioned folder of exercises (`manifest.json`, `exercises.json`, optional `media/`) that the teacher loads on boards.
_Avoid_: problem set, dataset

**Session**:
One student's sitting on a board, from `session_start` to `session_end`, stored as one file in `~/santolina/outbox/`.
_Avoid_: visit, log

**Event**:
One line in a session file: what happened, when, and with which student code.
_Avoid_: log entry, record

**Unload**:
Copying finished sessions from a board into the teacher store. The board keeps a copy in `archive/` until the teacher deletes it.
_Avoid_: sync (alone), download
