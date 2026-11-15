# Santolina tutor

A math copilot that runs entirely on an Arduino UNO Q 4 GB, for the Qualcomm challenge of Datathon FME 2026. It works with the M3Kang dataset.

## Language

**M3Kang**:
The dataset of Kangaroo math competition problems that the challenge uses: 1,747 problems in 108 languages, for research use only. Never commit its problems (see `CLAUDE.md`). Dataset card: https://huggingface.co/datasets/qualcomm/M3Kang
_Avoid_: Kangaroo data, Cangur set

**Organizers**:
The Qualcomm challenge team of Datathon FME 2026. They wrote `docs/BOARD_SETUP.md` and score each team's `predict.py` on the hidden test.
_Avoid_: jury

**Hidden test**:
The organizers' own problems that they use to score `predict.py`. The team never sees them.
_Avoid_: test set (alone)

**Token**:
The unit of text that a language model reads and writes, about one short word or part of a word. Speeds are in tokens per second (tok/s): reading the prompt is prefill, writing the answer is decode.
_Avoid_: word (for a token)

**Copilot**:
The program in this repository that answers M3Kang problems and helps a student, and that runs offline on the board.
_Avoid_: tutor, assistant, bot. "Tutor" and "tutoring model" are correct only for the systems in the papers.

**Board**:
The Arduino UNO Q 4 GB. In the docs, "the board" always means the Linux side (the Qualcomm QRB2210), not the STM32 microcontroller.
_Avoid_: device, Arduino, SBC

**UNO Q**:
The whole Arduino UNO Q board: the Linux side and the STM32 microcontroller together. Use "the board" when you mean only the Linux side.
_Avoid_: SBC, the PCB

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
_Avoid_: test set (the hidden test belongs to the organizers), dev set, hold-out set

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

**Student app**:
The interface the board serves to the student's phone over its own Wi-Fi (`student_app/`): code login, homework, practice, free mode, and the copilot chat.
_Avoid_: student interface (fine in prose), frontend, client

**Hotspot**:
The board's own Wi-Fi network, `Santolina-<board name>`, created by the teacher app at setup. Phones that join it open the student app by themselves.
_Avoid_: access point, AP, board Wi-Fi (alone)

**Sticker**:
The label on the board's case: board name, a QR code that joins the hotspot, the Wi-Fi password and the address. Printed from the teacher app.
_Avoid_: label, tag

**Assignment**:
Homework: exercises from one exercise pack that the teacher gives to a group, with an optional due date. Boards receive it in `assignments.json`.
_Avoid_: task, homework (fine in the student app's text)

**Free mode**:
Learning by doing: one conversation where problems arrive one after another, chosen by the learning path, and the student can ask anything.
_Avoid_: chat mode, open mode

**Learning path**:
The rule that picks the next problem in free mode (`student_app/planner.py`). The stand-in picks a random problem, or an easier one after a failure.
_Avoid_: recommender, curriculum

**Clue**:
A hint about the current exercise that doesn't give the answer away. Logged as `hint_requested`.
_Avoid_: tip, help

**Solved with help**:
An exercise whose solution the student asked for. Answers after that are logged but don't count as correct.
_Avoid_: revealed, cheated

**Junction**:
In the paper vault (`docs/vault/papers/`), one question that several papers answer together, such as "Do small models quantize worse?". Each synthesis note is organized by junction (J1, J2, ...). `_junctions.md` links the questions across folders (X1, X2, ...).
_Avoid_: topic, theme

**Logit distillation**:
Training a small student model to copy the next-token probabilities (logits) of a larger teacher model.
_Avoid_: token-level KD, word-level KD, logit KD

### Model compression and fine-tuning

**PTQ**:
Post-training quantization: quantizing the weights of a model that is already trained.

**QAT**:
Quantization-aware training: training a model so that it keeps its quality after quantization.

**Per-channel scale**:
One quantization scale per output row of a weight matrix.

**Group-wise scale**:
One quantization scale per block of N weights.

**GGUF**:
The llama.cpp model file format.

**Quantization type**:
A llama.cpp format for quantized weights, such as Q4_0, Q8_0 or Q4_K_M.

**Structured pruning**:
Removing whole neurons, heads or channels, so the matrices stay dense but get smaller.

**Unstructured pruning**:
Setting individual weights to zero, which gives sparse matrices. It needs sparse formats or kernels to give any benefit.

**N:M sparsity**:
In every block of M weights, N are zero (for example 2:4). Some NVIDIA GPUs accelerate it in hardware.

**CSR**:
Compressed Sparse Row, a storage format for sparse matrices.

**LoRA**:
Low-rank adapter fine-tuning: training two small low-rank matrices instead of the full weights.

**QLoRA**:
LoRA on a frozen base model quantized to 4 bits.

**Taylor importance**:
The estimated change in loss when weights are removed, about |gradient × weight|.
