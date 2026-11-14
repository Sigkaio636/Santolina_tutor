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
