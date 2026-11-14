# Challenge Context: On-Device Math Copilot for the Arduino UNO Q

> **What this is:** an explanation for team members and coding agents (Claude Code and others) who plan
> model work for this challenge. It covers the challenge, the hardware limits, and the options for
> quantization, pruning and fine-tuning.
>
> It condenses a planning chat between Pau Soler (team) and Martí, an ML and hardware colleague.
> Martí has pruning experience from Semidynamics. It also adds web research done on 2026-11-14 on
> each topic mentioned.
>
> Martí said his advice comes from memory, after 4 hours of sleep. **If research or experiments
> contradict him, trust the evidence and flag it.**
>
> Board facts follow one precedence rule: a measurement on our board comes first, then
> [BOARD_SETUP.md](BOARD_SETUP.md), then Arduino's docs. Full board details are in
> [UNO_Q_BOARD_REFERENCE.md](UNO_Q_BOARD_REFERENCE.md). Questions the team has not settled are in
> [§9](#9-open-questions-todo-checklist). Terms are in the
> [glossary](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md).

---

## 1. The challenge (what we know)

| Item | Detail |
|---|---|
| Goal | Fine-tune a small language model into a **math copilot**: a teacher's assistant at home ("having a teacher at home") |
| Target hardware | **Arduino UNO Q** (Qualcomm Dragonwing QRB2210 Linux SoC + STM32 MCU). See §2 |
| RAM | ✅ **Resolved: 4 GB variant (ABX00173)**: 3.6 GiB total, about 2.9 GiB available when idle, plus 1.8 GiB swap. See [UNO_Q_BOARD_REFERENCE.md](UNO_Q_BOARD_REFERENCE.md) |
| Training data provided | **M3Kang**: 1,747 Kangaroo math contest problems, translated into 108 languages ([dataset card](https://huggingface.co/datasets/qualcomm/M3Kang), [BOARD_SETUP.md step 9](BOARD_SETUP.md#step-9-prepare-m3kang-on-your-laptop)) |
| Answer format of data | Multiple choice, one letter **A to E** ([BOARD_SETUP.md](BOARD_SETUP.md), [`predict.py`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/predict.py) contract) |
| Key requirement | The copilot must do one of two things ([BOARD_SETUP.md, "The challenge"](BOARD_SETUP.md#the-challenge)). **Teach:** guide the student without giving away the answer. **Reason:** choose the correct letter for a Kangaroo-style problem |
| Evaluation | The organizers run each team's `predict.py` on a hidden test and score the letters. For Teach, the team found a benchmark that evaluates **pedagogical explanation of answers**. It is better than multiple-choice benchmarks such as MMLU. Which one is open; candidates in §7 |
| Language | M3Kang has all 1,747 problems in English and Catalan, and fewer in other languages (BOARD_SETUP.md step 9). If the copilot must speak Catalan or Spanish, base-model language coverage matters a lot (see §3) |
| Framework | Not decided yet. PyTorch + Hugging Face is the default assumption |

### Team's initial plan
1. Start from a **small Gemma** model.
2. **Prune** it (only math knowledge needed → remove capacity).
3. **Fine-tune** on math tutoring data.
4. **Quantize** and deploy on the UNO Q.

The deployed language model is Qwen3.5 0.8B Q8_0
([`config.env`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/config.env)). The fine-tune
base is not chosen yet. Gemma 3 is one option being explored.

### Martí's recommended priority order
1. **Quantize first.** It's the "safe bet", with big gains and low risk.
2. Prune **only if needed**, and only **structured** (rows/columns).
3. Fine-tune after pruning to recover quality (LoRA, low-rank adapters; see §6).

---

## 2. Target hardware: Arduino UNO Q

### Specs (summary)
[UNO_Q_BOARD_REFERENCE.md](UNO_Q_BOARD_REFERENCE.md) is the full and canonical copy. In short:

- **SoC:** Qualcomm Dragonwing **QRB2210**: 4× **Arm Cortex-A53** @ 2.0 GHz, **Adreno 702** GPU.
  **No NPU** is published, and no TOPS (tera operations per second) figure
- **RAM and storage:** **4 GB LPDDR4X**, 32 GB eMMC
- **MCU:** STM32U585, the "classic Arduino" side. Irrelevant for the language model itself
- **OS:** Debian Linux. Dev tool: **Arduino App Lab**
- **Power:** USB-C **PD supply required**, 5 V / 3 A
- Audio in/out on a header (a voice copilot is possible later)

### What already runs on it
- App Lab ships an **LLM "Brick"** (`arduino:llm`) that talks to a llama.cpp server on the board
  (third-party reports say port 9999). **Our project does not use it.** [BOARD_SETUP.md](BOARD_SETUP.md)
  runs its own `llama-server` services: language model on **8081**, embeddings on **8082**, optional
  vision on 8083, all on `127.0.0.1`.
- Models offered by App Lab for UNO Q: **Qwen 3.5 0.8B (Q4_0)** (default, supports tool calling) and **Gemma 3 1B IT (Q4_0)**. IT means instruction-tuned.
- Measured on a 4 GB board (mischianti.org): **Qwen 3.5 0.8B ≈ 4.4–4.5 tok/s, Gemma 3 1B ≈ 5.0 tok/s**. Time to first token was about 0.85–2.2 s once the model was loaded (9 s on cold load). The model needs close to **~1 GB RAM**.
- Community also runs llama.cpp GGUF models via **yzma** (Go wrapper for llama.cpp).
- ⇒ **The most pragmatic deployment path:** produce a GGUF (llama.cpp's model file format) of our
  fine-tuned model. Serve it with llama.cpp on the board. Run it as our own `llama-server` systemd
  service, the way [BOARD_SETUP.md](BOARD_SETUP.md) does it, not through the App Lab LLM Brick.

### Hardware implications for agents (important)
- **Cortex-A53 is ARMv8.0-A.** It has NEON SIMD but **no SDOT/UDOT dot-product instructions and no
  I8MM**. Newer Arm cores use them to accelerate int8/int4 matmuls in llama.cpp. Expect modest
  throughput. ✅ **Confirmed on our board** (no `asimddp`, no `i8mm`, see
  [UNO_Q_BOARD_REFERENCE.md §14.2](UNO_Q_BOARD_REFERENCE.md#142-cpu-flags-answers-an-open-question)).
  Whether decode is limited by memory bandwidth is open (§9).
- **GPU (Adreno 702):** llama.cpp has an **OpenCL backend designed for Adreno**. It is optimized for
  **pure Q4_0** (`llama-quantize` with `--pure`). Q8_0 and Q6_K are supported (Q6_K not optimized).
  Qualcomm's Dragonwing docs say llama.cpp models on those boards run on the GPU via OpenCL. **But**
  the verified devices list only high-end Adreno (750/830/X85). The docs say **Adreno 6xx doesn't
  work**, and older phone A6x drivers are "likely not supported". Whether OpenCL llama.cpp works or
  is faster on Adreno 702 is open (§9). CPU may well be the only practical path.
- Martí's point: **check that the GPU has integer kernels.** In llama.cpp the quantized kernels dequantize/compute inside the kernel (Q4_0/Q8_0 blocks), so "integer support" really means "does the backend have an optimized kernel for our quant type".
- **Sparse kernels:** Martí asked whether the GPU supports **2:4 sparse matmul** (NVIDIA Ampere+ style). There is no evidence that Adreno 702 or llama.cpp exploit 2:4 or unstructured sparsity. **llama.cpp stores and computes zeros like any other weight.** ⇒ Unstructured or 2:4 pruning gives **no speed or memory win** in the standard deployment path unless we write custom kernels. See §5.
- **Memory budget:** the 4 GB board has 3.6 GiB total and about 2.9 GiB available when idle. The
  two model services use about 920 MiB on our board
  ([UNO_Q_BOARD_REFERENCE.md §14.4](UNO_Q_BOARD_REFERENCE.md#144-build-and-services)). The
  organizers quote about 1.1 GB. The budget covers the OS, App Lab, llama.cpp, the model and the KV
  cache (the attention keys and values kept for past tokens). A ~1B model at Q4_0 (~0.7–0.8 GB,
  [Raspberry Pi 5 benchmark](https://www.kunalganglani.com/blog/gemma-3-raspberry-pi-5-benchmark.md))
  fits. A 270M model at Q4_0 is ~0.25–0.3 GB. Keep context modest, because the KV cache grows with
  context length.
- **Latency target:** human reading speed is roughly 4–7 tok/s (a rough estimate, no source). Current measurements (~5 tok/s for 1B) are at the bottom of that range, so a smaller or pruned model gives a real UX win.

---

## 3. Base model candidates

| Model | Params | Notes |
|---|---|---|
| **Gemma 3 270M** (IT) | 270M (≈170M are **embeddings** for a 256k vocab, ≈100M in transformer blocks) | Built for task-specific fine-tuning. Official **QAT** (quantization-aware training) **Q4_0** checkpoints exist. Google tutorial: fine-tune with QLoRA → quantize → under 300 MB on-device. IFEval (an instruction-following benchmark) 51.2% ([model card](https://huggingface.co/google/gemma-3-270m)). Weak reasoning out of the box. Listed as English-focused |
| **Gemma 3 1B** (IT) | 1B | Already runs on UNO Q (Q4_0, ~5 tok/s). Q4_K_M GGUF ≈ 815 MB ([Raspberry Pi 5 benchmark](https://www.kunalganglani.com/blog/gemma-3-raspberry-pi-5-benchmark.md)). Better math/reasoning than 270M. Weak beyond 3–4 reasoning steps. Its Catalan ability is open (§9) |
| **Qwen 3.5 0.8B** | 0.8B | App Lab default on UNO Q (~4.5 tok/s). Qwen models are generally strong at math and multilingual. Our deployed language model is Qwen3.5 0.8B Q8_0 ([`config.env`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/config.env)) |

**Observations for agents:**
- For Gemma 3 270M, **most parameters are the embedding table**. Pruning transformer blocks gains little. **Vocabulary trimming** (keep only tokens needed for Catalan/Spanish/English + math, then remap the embedding/LM head) could cut size massively. This is advanced and needs tokenizer surgery plus GGUF compatibility checks. ⚠️ Optional idea, not from the chat.
- Fine-tuning a 1B-class model on a single GPU with LoRA/QLoRA is cheap (minutes to hours).
- Always compare a compressed model against the **unpruned quantized model** it came from. Also
  compare it against the **baseline**: the organizers' copilot with Qwen3.5 0.8B Q8_0 (see
  [Baseline](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) in the glossary).

---

## 4. Quantization (Martí: "do this first")

### How quantization works
- Convert weights from **FP16/BF16 → INT8 or INT4**. FP16→INT8 roughly **halves memory** ("almost" half, because scales must also be stored). Integer ops are much faster than floating point on small hardware.
- **Problem:** weights don't all share the same scale. **Solution:** store **scale factors per row/column** (per output channel) of each matrix, and apply the scale **only at the end of each dot product**: `y_i = s_i * Σ_j (q_ij * x_j)`. Martí didn't remember if it's per row or per column. Answer: **per output channel** (one scale per row of W when y = Wx). Modern formats go finer, with **one scale per block of weights** (group-wise).
- Martí said "quantization alone can already give reasonably good performance".

### How llama.cpp does it (our likely deployment format: GGUF)
llama.cpp uses **block-wise quantization**:

| Type | What it is |
|---|---|
| **Q4_0** | Blocks of 32 weights sharing one FP16 scale (~4.5 bits/weight) |
| **Q8_0** | 8-bit blocks |
| **K-quants** (Q4_K_M, Q5_K_M, Q6_K) | Mixed-precision "super-block" recipes, usually better quality per bit |

- At inference, llama.cpp **never fully dequantizes**. It computes dot products directly on packed data (e.g. Q4_0 weights × Q8_0-quantized activations).
- For the Adreno OpenCL backend, use **pure Q4_0** (`--pure`).
- Pipeline: HF checkpoint → `convert_hf_to_gguf.py` → F16 GGUF → `llama-quantize` → Q4_0 / Q4_K_M /
  Q8_0 → measure speed on the board. The conversion and quantization tools run in llama.cpp on the
  laptop. The board build has only `llama-server` and `llama-cli`
  ([build script](https://github.com/Sigkaio636/Santolina_tutor/blob/main/board/02_build_llama_cpp.sh)).

### Options to consider
- **PTQ (post-training quantization):** llama.cpp quantize, optionally with an **importance matrix** (`llama-imatrix`, on the laptop) computed on math-tutoring calibration text. Cheap and should be tried first.
- **QAT (quantization-aware training):** Google publishes **Gemma 3 QAT Q4_0** checkpoints that keep quality close to full precision. Fine-tuning from a QAT checkpoint (or doing short QAT ourselves) may preserve more quality at 4-bit.
- **QLoRA** (fine-tuning on a 4-bit base, see §6) is a *training-memory* technique. The deployed model still needs a separate export → GGUF quantization step.

The experiments to run are in [What to try](#what-to-try).

---

## 5. Pruning (Martí: "careful — only if you have no other option")

### Martí's warnings (important)
- Many pruning methods **keep good metrics on multiple-choice (A/B/C/D) benchmarks** but **break generation**. His pruned Llama **switched to German and started hallucinating** when asked to summarize. Our task is open-ended explanation, so **evaluate pruned models on generation, not MCQ (multiple-choice question) accuracy.**
- **Unstructured pruning (zeroing individual weights) doesn't help on this hardware** (CPU/GPU use dense vector instructions). You'd need compressed storage like **CSR (Compressed Sparse Row)**, decompressed at runtime, which only saves memory and costs speed.
- ⇒ Use **structured pruning**: remove **entire rows/columns** of attention/MLP matrices, i.e. remove **MLP intermediate neurons (FFN channels)** and/or **attention heads**. The result is just a smaller dense model, so llama.cpp runs it natively.
- He suggested trying **2:4 semi-structured sparsity** if the GPU supports it (each block of 4 consecutive weights has 2 zeros, so 50% sparsity). Downsides: **50% is aggressive** and implementation is harder. **Research verdict: there is no evidence of 2:4 support on Adreno 702 or in llama.cpp. Deprioritize.**

### Pruning methods

#### LLM-Pruner
Ma, Fang, Wang, NeurIPS 2023, [arXiv:2305.11627](https://arxiv.org/abs/2305.11627),
[code](https://github.com/horseee/LLM-Pruner).

- Martí's top suggestion for structured pruning (though he says it's not necessarily the best and he never tested it).
- 3 stages:
    1. **Dependency discovery** automatically groups coupled structures (e.g. a head's Q/K/V/O slices, an FFN channel's up/gate/down slices).
    2. **Group importance estimation** with a **first-order Taylor expansion of the loss** (≈ |gradient × weight|, optionally with approximate Hessian terms). This needs **backpropagation** over a small calibration set.
    3. **Fast recovery with LoRA** (paper: ~3 hours, ~50K samples, for 7B models).
- Gradient computation is costlier than Wanda but trivial for a 1B model on one GPU.
- Whether LLM-Pruner supports the **Gemma 3** architecture is open (§9). The original targets
  LLaMA/Vicuna/ChatGLM. Gemma 3 has GQA (grouped-query attention), QK-norm, interleaved local/global
  attention and tied embeddings, so LLM-Pruner may need adaptation.

#### Wanda
Sun, Liu, Bair, Kolter, ICLR 2024, [arXiv:2306.11695](https://arxiv.org/abs/2306.11695),
[code](https://github.com/locuslab/wanda).

- Score = **|W_ij| × ‖X_j‖₂** (weight magnitude × norm of input activation over calibration data). Compared **per output** row. **No retraining, no weight update, one forward pass.** Much faster than LLM-Pruner.
- Natively **unstructured** (also supports N:M like 2:4). Martí: **adapt it to structured pruning** by aggregating element scores per row/column/neuron/head (**sum, RMS, max**, etc.) and removing whole structures. Coupled matrices must be pruned consistently (e.g. removing FFN channel *k* ⇒ remove row *k* of up/gate and column *k* of down).
- Martí: "much faster, but no guarantee it's better".

#### SparseGPT
Frantar & Alistarh, ICML 2023, [arXiv:2301.00774](https://arxiv.org/abs/2301.00774).

- One-shot pruning with second-order **weight updates** in the style of OBS (Optimal Brain Surgeon) to compensate for removed weights. Supports unstructured and **2:4 / 4:8**. Compatible with quantization. Mainly useful for unstructured/N:M sparsity, which doesn't help us here.
- (Martí's "the third method I don't remember" is likely SparseGPT, which he names later.)

### Practical pruning guidance for agents
- **Prune uniformly across layers** (same FFN width / head count in every layer) so the result is a standard config that HF `transformers` and `convert_hf_to_gguf.py` accept. Non-uniform per-layer shapes may not be supported by the GGUF converter for Gemma 3. Check this before you try non-uniform pruning (§9).
- Keep GQA consistent: prune **KV groups together with their query heads**, or prune only FFN channels first (simplest, and the FFN is the bulk of transformer-block params).
- **Calibration data:** use math-tutoring text in the **target language**. Pruning with English-only or generic calibration data can damage other languages (cf. Martí's "German" anecdote).
- Moderate ratios first (10–30%), then always **LoRA recovery** and **generation-based evaluation**.
- For Gemma 3 270M, transformer-block pruning has limited upside (embeddings dominate). Consider vocab trimming instead (§3).

---

## 6. Fine-tuning

### Which weights to train
After pruning the model may be "broken", so fine-tuning is needed. You **don't have to fine-tune all weights**:
- **Freezing:** only train the last layers (the "lazy" option).
- **LoRA** (Low-Rank Adaptation): train two low-rank matrices A, B with **W = W⁰ + A·B**. Considered state of the art in many papers. Variant **QLoRA** = LoRA on a quantized base.
  - **With structured pruning:** train A, B, then **merge** A·B into W⁰ so A, B don't need to be stored at inference. ✅
  - **With unstructured pruning:** merging breaks sparsity, because A·B is dense and will write non-zeros into pruned positions. You'd have to keep A, B separate at inference, or re-apply the mask after merging (which loses some of the adaptation). Another reason to prefer structured pruning.

### QLoRA and on-device fine-tuning
- **QLoRA** (Dettmers et al., arXiv:2305.14314): backpropagates through a frozen **4-bit NF4** base into LoRA adapters. Adds **Double Quantization** (quantizing the quantization constants, saving ~0.37 bits/param) and **paged optimizers**. NF4 is a *storage/training* format (bitsandbytes). It is **not** the deployed GGUF format, so after training: merge the adapters into a **higher-precision** base (BF16/F16), then convert and quantize to GGUF.
- Google's official tutorial fine-tunes **Gemma 3 270M with QLoRA**, then quantizes for on-device use (<300 MB).
- LLM-Pruner itself uses LoRA for post-pruning recovery.

### Team hardware
The team trains on an 8 GB NVIDIA RTX 4060 GPU in a team member's laptop.

### Data strategy (key for "teacher, not answer key")
- The M3Kang problems are **multiple-choice, with a letter answer**. They don't directly teach pedagogy.
- We will likely need to **synthesize tutoring dialogues or explanations**, for example with a larger
  teacher model. Another option is **distillation** from a strong model. Useful content: step-by-step
  explanation, hints before answers, Socratic questions, checks of student understanding, and common
  mistakes. Keep a **validation set** of M3Kang problems for evaluation, to avoid train/test
  contamination with the benchmark.
- Public tutoring dialogue data may help: **MathDial** (teacher–student dialogues on student mistakes) and others from §7. Their licenses and languages are open (§9).
- Train in the **target language**. Small models are fragile at language-switching.
- Keep outputs **short-ish** (~5 tok/s on device means 200 tokens ≈ 40 s).

---

## 7. Evaluation

### Martí's warning
MCQ benchmarks (MMLU-style A/B/C/D) **hide** generation damage from pruning/quantization. Evaluate **open-ended explanations**.

### Candidate pedagogical benchmarks (which one the team chose is open)
- **MathTutorBench** (ETH Zurich / TU Darmstadt, EMNLP 2025, arXiv:2502.18940): open-source, evaluates **math expertise, student understanding, pedagogical ability**, with a trained **reward model** for scoring open-ended tutor responses. Finds a trade-off between math skill and pedagogy.
- **MRBench** (MBZUAI, NAACL 2025, arXiv:2412.09416): 192 conversations with 1,596 tutor responses
  on **student mistakes in math**. The data comes from Bridge and MathDial. Responses are annotated on
  **8 pedagogical dimensions**, such as mistake identification, providing guidance, actionability,
  coherence, tutor tone and human-likeness.

The evaluation harness to build is in [What to try](#what-to-try).

---

## 8. Recommended pipeline (synthesis)

1. **Reference models:** Gemma 3 1B IT and Gemma 3 270M IT, plus Qwen3.5 0.8B, the deployed
   language model, for comparison. Convert to GGUF Q4_0, run on the UNO Q, and measure tutoring
   score, tok/s and RAM.
2. **Data:** build a tutoring SFT (supervised fine-tuning) set: the M3Kang training split plus
   synthesized explanations or dialogues, in the target language. Keep the M3Kang validation set and
   the pedagogical benchmark for evaluation.
3. **Fine-tune** (LoRA/QLoRA) the base model on tutoring data → merge → evaluate (FP16).
4. **Quantize** (Q8_0, Q4_K_M, Q4_0, optionally with imatrix) → evaluate on the laptop → measure on
   the board.
5. **Only if size or speed is still insufficient:** structured pruning (LLM-Pruner or structured
   Wanda, FFN channels first, uniform across layers) → LoRA recovery on tutoring data → merge →
   quantize → re-evaluate (generation, not MCQ!).
6. **Deploy:** GGUF served by our own llama.cpp `llama-server` service on the UNO Q (ports 8081/8082,
   pinned build `2cbe0ec`, CPU-only, see [BOARD_SETUP.md](BOARD_SETUP.md)). An OpenCL (Adreno 702)
   test is optional.

Note: the team's original order was prune → fine-tune. Fine-tuning first (step 3) and pruning later with **task-specific calibration data** is also valid, and lets pruning keep exactly what the copilot needs. Either way, **always finish with recovery fine-tuning after pruning**.

---

## 9. Open questions / TODO checklist
- [x] 2 GB or 4 GB UNO Q? **4 GB.**
- [x] M3Kang: language and number of options. 1,747 problems in 108 languages, all of them in English and Catalan. Options A–E (BOARD_SETUP.md step 9).
- [ ] M3Kang: are solutions or explanations included?
- [x] Official evaluation: the organizers run `predict.py` on a hidden test ([BOARD_SETUP.md, "The challenge"](BOARD_SETUP.md#the-challenge)).
- [ ] Which pedagogical benchmark exactly, for Teach (§7)?
- [ ] Required response language(s)?
- [ ] Does Gemma 3 1B handle Catalan well (§3)?
- [ ] Does llama.cpp's OpenCL backend work on Adreno 702? Is it faster than CPU? Compare speeds with the `timings` field of the server's answer (`prompt_per_second`, `predicted_per_second`) or with `llama-cli`'s timing output. The board build has no `llama-bench`.
- [ ] Is decode limited by memory bandwidth, so that fewer bytes per weight give more tokens per second? This document assumed it in §2. It is not measured on our board.
- [x] CPU feature flags on QRB2210 (`/proc/cpuinfo`): confirmed, no `asimddp`/`i8mm`
- [x] Custom GGUF: we run our own `llama-server` as a systemd service ([BOARD_SETUP.md](BOARD_SETUP.md) step 7). To swap the model, change `LLM_REPO`, `LLM_REVISION`, `LLM_FILE` and `LLM_SHA256` in `config.env` (see [Settings in config.env](BOARD_SETUP.md#settings-in-configenv)). Then change the service file from step 7, and run `sudo systemctl daemon-reload` and `sudo systemctl restart math-llm math-embed`.
- [ ] Does LLM-Pruner support Gemma 3 (§5)? Does `convert_hf_to_gguf.py` accept non-uniform pruned Gemma 3 configs?
- [ ] MathDial and other public tutoring dialogue data: licenses and languages (§6)?
- [x] Challenge rules on model size and allowed base models: any GGUF model that fits in RAM, answers in time, and has a license you can use (BOARD_SETUP.md 13.3).
- [ ] Challenge rules on external data and synthetic data?

---

## 10. Glossary
The terms of this document (PTQ, QAT, scales, GGUF, quantization types, pruning, N:M sparsity, CSR,
LoRA, QLoRA, Taylor importance) are in the project
[glossary](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md).

---

## What to try

**Compare quantizations (§4).**

1. Take the base model at F16, Q8_0, Q4_K_M and Q4_0.
2. For each one, measure the tutoring benchmark score, tok/s and RAM on the board.
3. For letter accuracy on the validation set, run `python3 eval.py --name <name>` on the board. Each
   run is one experiment, and it adds one line to `results/ablations.csv`.
4. Pick the smallest quantization whose tutoring quality is acceptable. The team has not set the
   threshold yet.

**Build an evaluation harness (§7).**

1. **Pedagogical score** on the chosen benchmark.
2. **M3Kang validation-set accuracy** (did the explanation reach the correct option?).
3. **Generation sanity checks:** language consistency (stays in Catalan/target language), no hallucinated rambling, response length.
4. **On-device metrics:** tok/s (prompt + decode), time-to-first-token, peak RAM, model file size.
   Read tok/s on the UNO Q from the `timings` field of the server's answer (`prompt_per_second`,
   `predicted_per_second`). The board build has no `llama-bench`.
5. Run this harness after **every** compression step (quantize → prune → recover) to catch regressions.

---

## Sources
- [Arduino UNO Q 4GB — Arduino Store (specs)](https://store.arduino.cc/products/uno-q-4gb)
- [Qualcomm Dragonwing QRB2210 product page](https://www.qualcomm.com/products/internet-of-things/industrial/industrial-automation/qualcomm-robotics-rb1-platform)
- [Arduino UNO Q: a local AI agent that drives the hardware — mischianti.org (models + tok/s on UNO Q)](https://mischianti.org/?p=36049)
- [Can the Arduino UNO Q Run an LLM? — raspberry.tips](https://raspberry.tips/en/?p=16730)
- [Running local LLMs and VLMs on the Arduino UNO Q with yzma — Arduino Project Hub](https://projecthub.arduino.cc/marc-edgeimpulse/running-local-llms-and-vlms-on-the-arduino-uno-q-with-yzma-74e288)
- [llama.cpp OpenCL backend docs (Adreno)](https://sources.debian.org/src/llama.cpp/8064%2Bdfsg-2/docs/backend/OPENCL.md)
- [llama.cpp OpenCL docs PR #17011 (datatype support, A6x note)](https://github.com/ggml-org/llama.cpp/pull/17011/files)
- [Qualcomm Dragonwing docs — llama.cpp workflow](https://dragonwingdocs.qualcomm.com/Ubuntu/ai-workflows/llama-cpp.md)
- [Introducing Gemma 3 270M — Google Developers Blog](https://developers.googleblog.com/en/introducing-gemma-3-270m/)
- [Own your AI: fine-tune Gemma 3 270M and run it on-device — Google](https://developers.googleblog.com/own-your-ai-fine-tune-gemma-3-270m-for-on-device/)
- [Gemma 3 270M model card — Hugging Face (IFEval score)](https://huggingface.co/google/gemma-3-270m)
- [Gemma 3 270M architecture (embeddings vs blocks) — eWeek](https://www.eweek.com/pt/news/google-gemma-3-270m/)
- [Gemma 3 on Raspberry Pi 5 benchmark (sizes)](https://www.kunalganglani.com/blog/gemma-3-raspberry-pi-5-benchmark.md)
- [LLM-Pruner: On the Structural Pruning of LLMs (arXiv:2305.11627)](https://arxiv.org/pdf/2305.11627)
- [Wanda: A Simple and Effective Pruning Approach for LLMs (arXiv:2306.11695)](https://arxiv.org/html/2306.11695v1) · [code](https://github.com/locuslab/wanda)
- [SparseGPT (arXiv:2301.00774)](https://arxiv.org/abs/2301.00774v3)
- [QLoRA (arXiv:2305.14314)](https://arxiv.org/abs/2305.14314)
- [MathTutorBench (arXiv:2502.18940)](https://arxiv.org/pdf/2502.18940v1)
- [MRBench / Unifying AI Tutor Evaluation (arXiv:2412.09416)](https://arxiv.org/html/2412.09416v2)
- [Arm learning path: llama.cpp decode roofline (Q4_0 vs Q8_0 on Arm)](https://learn.arm.com/learning-paths/cross-platform/llm-decode-roofline/diagnose/)
