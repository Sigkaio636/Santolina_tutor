# Challenge Context: On-Device Math Tutor LLM for Arduino UNO Q

> **Purpose of this file:** shared context for coding agents (Claude Code and others) working on this challenge.
> It condenses a planning chat between Pau Soler (team) and Martí (an ML/hardware colleague with pruning experience from Semidynamics),
> plus web research done on 2026-11-14 on each topic mentioned.
> Martí explicitly said his advice comes from memory (and 4 hours of sleep), so **if research or experiments contradict him, trust the evidence and flag it.**
> Board facts, ports and the llama.cpp build follow `docs/BOARD_SETUP.md`, which rules. Full board details: `docs/UNO_Q_BOARD_REFERENCE.md`.
> Items marked **⚠️ VERIFY** are assumptions or open questions the team has not settled yet.

---

## 1. The challenge (what we know)

| Item | Detail |
|---|---|
| Goal | Fine-tune a small LLM to act as a **math teacher's assistant / home tutor** ("having a teacher at home") |
| Target hardware | **Arduino UNO Q** (Qualcomm Dragonwing QRB2210 Linux SoC + STM32 MCU). See §2 |
| RAM | ✅ **Resolved: 4 GB variant (ABX00173)**, about 3.6 GiB usable plus 1.8 GiB swap. See `docs/UNO_Q_BOARD_REFERENCE.md` |
| Training data provided | ~**1000 Kangaroo math contest problems** ("proves Cangur") |
| Answer format of data | Multiple choice, one letter **A to E** (`docs/BOARD_SETUP.md`, `predict.py` contract) |
| Key requirement | The model must **not** just output the right letter. It must **explain pedagogically**, like a teacher. The Kangaroo set is probably mostly for benchmarking, but the model should also handle Kangaroo-style problems |
| Evaluation | Team found a benchmark that evaluates **pedagogical explanation of answers** (better than MCQ benchmarks like MMLU). ⚠️ VERIFY which one; candidates in §7 |
| Language | ⚠️ VERIFY: Kangaroo data is likely in **Catalan** (Societat Catalana de Matemàtiques). If the tutor must speak Catalan/Spanish, base-model language coverage matters a lot (see §3) |
| Framework | Not decided yet. PyTorch + Hugging Face is the default assumption |

### Team's initial plan
1. Start from a **small Gemma** model.
2. **Prune** it (only math knowledge needed → remove capacity).
3. **Fine-tune** on math tutoring data.
4. **Quantize** and deploy on the UNO Q.

### Martí's recommended priority order
1. **Quantize first.** It's the "safe bet", with big gains and low risk.
2. Prune **only if needed**, and only **structured** (rows/columns).
3. Fine-tune after pruning to recover quality (LoRA).

---

## 2. Target hardware: Arduino UNO Q

### Specs (official store page + Qualcomm)
- **SoC:** Qualcomm Dragonwing **QRB2210**
- **CPU:** 4× **Arm Cortex-A53** @ 2.0 GHz (64-bit)
- **GPU:** **Adreno 702** @ 845 MHz. Supports OpenGL ES 3.1, **OpenCL 2.0**, Vulkan 1.1
- **DSP:** Qualcomm Hexagon. **No dedicated NPU** and no TOPS figure is published
- **RAM:** **4 GB LPDDR4X** (our variant; a 2 GB / 16 GB variant also exists). **Storage:** 32 GB eMMC (4 GB variant)
- **MCU:** STM32U585 (Cortex-M33 @160 MHz, 2 MB flash, 786 KB SRAM). This is the "classic Arduino" side. Irrelevant for the LLM itself
- **OS:** Debian Linux (upstream), Docker supported. Dev tool: **Arduino App Lab**
- **Power:** USB-C **PD supply required** (≥15 W recommended). A non-PD supply won't boot
- Connectivity: Wi-Fi 5, BT 5.1. Audio in/out on a header (a voice tutor is possible later)

### What already runs on it (important baseline!)
- App Lab ships an **LLM "Brick"** (`arduino:llm`) that talks to a llama.cpp server on the board (third-party reports say port 9999). **Our project does not use it**: `docs/BOARD_SETUP.md` runs its own `llama-server` services (language model on **8081**, embeddings on **8082**, optional vision on 8083, all on `127.0.0.1`).
- Models offered by App Lab for UNO Q: **Qwen 3.5 0.8B (Q4_0)** (default, supports tool calling) and **Gemma 3 1B IT (Q4_0)**.
- Measured on a 4 GB board (mischianti.org): **Qwen 3.5 0.8B ≈ 4.4–4.5 tok/s, Gemma 3 1B ≈ 5.0 tok/s**. Time to first token was about 0.85–2.2 s once the model was loaded (9 s on cold load). The model needs close to **~1 GB RAM**.
- Community also runs llama.cpp GGUF models via **yzma** (Go wrapper for llama.cpp).
- ⇒ **The most pragmatic deployment path: produce a GGUF of our fine-tuned model and serve it with llama.cpp on the board** (as our own `llama-server` systemd service, the way `docs/BOARD_SETUP.md` does it, not through the App Lab LLM Brick).

### Hardware implications for agents (important)
- **Cortex-A53 is ARMv8.0-A.** It has NEON SIMD but **no SDOT/UDOT dot-product instructions and no I8MM**, which newer Arm cores use to accelerate int8/int4 matmuls in llama.cpp. Expect modest throughput. Decode is **memory-bandwidth-bound**, so **fewer bytes per weight ⇒ more tokens/s**. ✅ **Confirmed on our board:** `Features: fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid`, no `asimddp`, no `i8mm`.
- **GPU (Adreno 702):** llama.cpp has an **OpenCL backend designed for Adreno**, optimized for **pure Q4_0** (`llama-quantize --pure ... Q4_0`). Q8_0 and Q6_K are supported (Q6_K not optimized). Qualcomm's Dragonwing docs say llama.cpp models on those boards run on the GPU via OpenCL. **But** the verified devices list only high-end Adreno (750/830/X85), the docs say **Adreno 6xx doesn't work**, and older phone A6x drivers are "likely not supported". **⚠️ VERIFY whether OpenCL llama.cpp actually works / is faster on Adreno 702**. CPU may well be the only practical path. Benchmark both with `llama-bench`.
- Martí's point: **check that the GPU has integer kernels.** In llama.cpp the quantized kernels dequantize/compute inside the kernel (Q4_0/Q8_0 blocks), so "integer support" really means "does the backend have an optimized kernel for our quant type".
- **Sparse kernels:** Martí asked whether the GPU supports **2:4 sparse matmul** (NVIDIA Ampere+ style). There is no evidence that Adreno 702 or llama.cpp exploit 2:4 or unstructured sparsity. **llama.cpp stores and computes zeros like any other weight.** ⇒ Unstructured or 2:4 pruning gives **no speed or memory win** in the standard deployment path unless we write custom kernels. See §5.
- **Memory budget (4 GB board, ~3.6 GiB usable; the two servers in BOARD_SETUP use ~1.1 GB):** OS + App Lab + llama.cpp + model + KV cache. A ~1B model at Q4_0 (~0.7–0.8 GB) fits. A 270M model at Q4_0 is ~0.25–0.3 GB. Keep context modest (KV cache grows with context length).
- **Latency target:** human reading speed is roughly 4–7 tok/s. Current baselines (~5 tok/s for 1B) are at the bottom of that range, so a smaller or pruned model gives a real UX win.

---

## 3. Base model candidates

| Model | Params | Notes |
|---|---|---|
| **Gemma 3 270M** (IT) | 270M (≈170M are **embeddings** for a 256k vocab, ≈100M in transformer blocks) | Built for task-specific fine-tuning. Official **QAT Q4_0** checkpoints exist. Google tutorial: fine-tune with QLoRA → quantize → under 300 MB on-device. IFEval 51.2%. Weak reasoning out of the box. Listed as English-focused |
| **Gemma 3 1B** (IT) | 1B | Already runs on UNO Q (Q4_0, ~5 tok/s). Q4_K_M GGUF ≈ 815 MB. Better math/reasoning than 270M. Weak beyond 3–4 reasoning steps. ⚠️ VERIFY multilingual (Catalan) ability |
| **Qwen 3.5 0.8B** | 0.8B | App Lab default on UNO Q (~4.5 tok/s). Qwen models are generally strong at math and multilingual. A good alternative baseline even though the plan says Gemma |

**Observations for agents:**
- For Gemma 3 270M, **most parameters are the embedding table**. Pruning transformer blocks gains little. **Vocabulary trimming** (keep only tokens needed for Catalan/Spanish/English + math, then remap the embedding/LM head) could cut size massively. This is advanced and needs tokenizer surgery plus GGUF compatibility checks. ⚠️ Optional idea, not from the chat.
- Fine-tuning a 1B-class model on a single GPU with LoRA/QLoRA is cheap (minutes to hours).
- Always compare against the **unpruned quantized baseline** (Gemma 3 1B Q4_0 / Qwen 3.5 0.8B Q4_0 that already runs on the board).

---

## 4. Quantization (Martí: "do this first")

### Concepts from the chat
- Convert weights from **FP16/BF16 → INT8 or INT4**. FP16→INT8 roughly **halves memory** ("almost" half, because scales must also be stored). Integer ops are much faster than floating point on small hardware.
- **Problem:** weights don't all share the same scale. **Solution:** store **scale factors per row/column** (per output channel) of each matrix, and apply the scale **only at the end of each dot product**: `y_i = s_i * Σ_j (q_ij * x_j)`. Martí didn't remember if it's per row or per column. Answer: **per output channel** (one scale per row of W when y = Wx). Modern formats go finer, with **one scale per block of weights** (group-wise).
- Martí said "quantization alone can already give reasonably good performance".

### How llama.cpp does it (our likely deployment format: GGUF)
- **Block-wise quantization**, e.g. **Q4_0** = blocks of 32 weights sharing one FP16 scale (~4.5 bits/weight). **Q8_0** = 8-bit blocks. **K-quants** (Q4_K_M, Q5_K_M, Q6_K) are mixed-precision "super-block" recipes with usually better quality per bit.
- At inference, llama.cpp **never fully dequantizes**. It computes dot products directly on packed data (e.g. Q4_0 weights × Q8_0-quantized activations).
- For the Adreno OpenCL backend, use **pure Q4_0** (`--pure`).
- Pipeline: HF checkpoint → `convert_hf_to_gguf.py` → F16 GGUF → `llama-quantize` → Q4_0 / Q4_K_M / Q8_0 → `llama-bench` on the board.

### Options to consider
- **PTQ (post-training quantization):** llama.cpp quantize, optionally with an **importance matrix** (`llama-imatrix`) computed on math-tutoring calibration text. Cheap and should be tried first.
- **QAT (quantization-aware training):** Google publishes **Gemma 3 QAT Q4_0** checkpoints that keep quality close to full precision. Fine-tuning from a QAT checkpoint (or doing short QAT ourselves) may preserve more quality at 4-bit.
- **QLoRA** (fine-tuning on a 4-bit base, see §6) is a *training-memory* technique. The deployed model still needs a separate export → GGUF quantization step.

### Experiments agents should run
1. Baseline model at F16 / Q8_0 / Q4_K_M / Q4_0 → measure the tutoring benchmark score + tok/s + RAM on the board.
2. Pick the smallest quant whose tutoring quality is acceptable.

---

## 5. Pruning (Martí: "careful — only if you have no other option")

### Martí's warnings (important)
- Many pruning methods **keep good metrics on multiple-choice (A/B/C/D) benchmarks** but **break generation**. His pruned Llama **switched to German and started hallucinating** when asked to summarize. Our task is open-ended explanation, so **evaluate pruned models on generation, not MCQ accuracy.**
- **Unstructured pruning (zeroing individual weights) doesn't help on this hardware** (CPU/GPU use dense vector instructions). You'd need compressed storage like **CSR (Compressed Sparse Row)**, decompressed at runtime, which only saves memory and costs speed.
- ⇒ Use **structured pruning**: remove **entire rows/columns** of attention/MLP matrices, i.e. remove **MLP intermediate neurons (FFN channels)** and/or **attention heads**. The result is just a smaller dense model, so llama.cpp runs it natively.
- He suggested trying **2:4 semi-structured sparsity** if the GPU supports it (each block of 4 consecutive weights has 2 zeros, so 50% sparsity). Downsides: **50% is aggressive** and implementation is harder. **Research verdict: there is no evidence of 2:4 support on Adreno 702 or in llama.cpp. Deprioritize.**

### Methods mentioned

**LLM-Pruner** (Ma, Fang, Wang, NeurIPS 2023, arXiv:2305.11627, code: github.com/horseee/LLM-Pruner)
- Martí's top suggestion for structured pruning (though he says it's not necessarily the best and he never tested it).
- 3 stages: (1) **Dependency discovery** automatically groups coupled structures (e.g. a head's Q/K/V/O slices, an FFN channel's up/gate/down slices). (2) **Group importance estimation** with a **first-order Taylor expansion of the loss** (≈ |gradient × weight|, optionally with approximate Hessian terms). This needs **backpropagation** over a small calibration set. (3) **Fast recovery with LoRA** (paper: ~3 hours, ~50K samples, for 7B models).
- Gradient computation is costlier than Wanda but trivial for a 1B model on one GPU.
- ⚠️ VERIFY that LLM-Pruner supports the **Gemma 3** architecture (the original targets LLaMA/Vicuna/ChatGLM). It may need adaptation (Gemma 3 has GQA, QK-norm, interleaved local/global attention, tied embeddings).

**Wanda** (Sun, Liu, Bair, Kolter, ICLR 2024, arXiv:2306.11695, code: github.com/locuslab/wanda)
- Score = **|W_ij| × ‖X_j‖₂** (weight magnitude × norm of input activation over calibration data). Compared **per output** row. **No retraining, no weight update, one forward pass.** Much faster than LLM-Pruner.
- Natively **unstructured** (also supports N:M like 2:4). Martí: **adapt it to structured pruning** by aggregating element scores per row/column/neuron/head (**sum, RMS, max**, etc.) and removing whole structures. Coupled matrices must be pruned consistently (e.g. removing FFN channel *k* ⇒ remove row *k* of up/gate and column *k* of down).
- Martí: "much faster, but no guarantee it's better".

**SparseGPT** (Frantar & Alistarh, ICML 2023, arXiv:2301.00774)
- One-shot pruning with second-order (OBS-style) **weight updates** to compensate for removed weights. Supports unstructured and **2:4 / 4:8**. Compatible with quantization. Mainly useful for unstructured/N:M sparsity, which doesn't help us here.
- (Martí's "the third method I don't remember" is likely SparseGPT, which he names later.)

### Practical pruning guidance for agents
- **Prune uniformly across layers** (same FFN width / head count in every layer) so the result is a standard config that HF `transformers` and `convert_hf_to_gguf.py` accept. Non-uniform per-layer shapes may not be supported by the GGUF converter for Gemma 3. ⚠️ VERIFY before trying non-uniform pruning.
- Keep GQA consistent: prune **KV groups together with their query heads**, or prune only FFN channels first (simplest, and the FFN is the bulk of transformer-block params).
- **Calibration data:** use math-tutoring text in the **target language**. Pruning with English-only or generic calibration data can damage other languages (cf. Martí's "German" anecdote).
- Moderate ratios first (10–30%), then always **LoRA recovery** and **generation-based evaluation**.
- For Gemma 3 270M, transformer-block pruning has limited upside (embeddings dominate). Consider vocab trimming instead (§3).

---

## 6. Fine-tuning

### From the chat
After pruning the model may be "broken", so fine-tuning is needed. You **don't have to fine-tune all weights**:
- **Freezing:** only train the last layers (the "lazy" option).
- **LoRA** (Low-Rank Adaptation): train two low-rank matrices A, B with **W = W⁰ + A·B**. Considered state of the art in many papers. Variant **QLoRA** = LoRA on a quantized base.
  - **With structured pruning:** train A, B, then **merge** A·B into W⁰ so A, B don't need to be stored at inference. ✅
  - **With unstructured pruning:** merging breaks sparsity, because A·B is dense and will write non-zeros into pruned positions. You'd have to keep A, B separate at inference, or re-apply the mask after merging (which loses some of the adaptation). Another reason to prefer structured pruning.

### Research notes
- **QLoRA** (Dettmers et al., arXiv:2305.14314): backpropagates through a frozen **4-bit NF4** base into LoRA adapters. Adds **Double Quantization** (quantizing the quantization constants, saving ~0.37 bits/param) and **paged optimizers**. NF4 is a *storage/training* format (bitsandbytes). It is **not** the deployed GGUF format, so after training: merge the adapters into a **higher-precision** base (BF16/F16), then convert and quantize to GGUF.
- Google's official tutorial fine-tunes **Gemma 3 270M with QLoRA**, then quantizes for on-device use (<300 MB).
- LLM-Pruner itself uses LoRA for post-pruning recovery.

### Data strategy (key for "teacher, not answer key")
- The ~1000 Kangaroo items are **MCQ with a letter answer**. They don't directly teach pedagogy.
- Likely need to **synthesize tutoring dialogues/explanations** (e.g. with a larger teacher LLM), or use **distillation** from a strong model: step-by-step explanation, hints before answers, Socratic questions, checking student understanding, addressing common mistakes. Keep a **held-out split** of Kangaroo problems for evaluation (avoid train/test contamination with the benchmark).
- Public tutoring dialogue data may help: **MathDial** (teacher–student dialogues on student mistakes) and others from §7. ⚠️ VERIFY licenses and language.
- Train in the **target language**. Small models are fragile at language-switching.
- Keep outputs **short-ish** (~5 tok/s on device means 200 tokens ≈ 40 s).

---

## 7. Evaluation

### Martí's warning
MCQ benchmarks (MMLU-style A/B/C/D) **hide** generation damage from pruning/quantization. Evaluate **open-ended explanations**.

### Candidate pedagogical benchmarks (⚠️ VERIFY which one the team chose)
- **MathTutorBench** (ETH Zurich / TU Darmstadt, EMNLP 2025, arXiv:2502.18940): open-source, evaluates **math expertise, student understanding, pedagogical ability**, with a trained **reward model** for scoring open-ended tutor responses. Finds a trade-off between math skill and pedagogy.
- **MRBench** (MBZUAI, NAACL 2025, arXiv:2412.09416): 192 conversations / 1,596 tutor responses on **student mistakes in math** (from Bridge + MathDial), annotated on **8 pedagogical dimensions** (e.g. mistake identification, providing guidance, actionability, coherence, tutor tone, human-likeness).

### First results on the board (2026-11-14)
Qwen3.5 0.8B Q8_0, 50 validation problems (28 Catalan, 22 English), `docs/BOARD_SETUP.md` steps 11 and 12:
- **Baseline: 10/50 (20.0%)**, mean 12.0 s per problem. This is below the 22.0% you get if you always answer `D`.
- **Retrieval with one example (`--rag 1`): 7/50 (14.0%)**, mean 27.9 s. English goes up (3 → 5), Catalan goes down (7 → 2). The embedding model is English-only.
- ⇒ A 0.8B model is weak at picking the letter. This supports the tutor goal in §1: put the effort into hints and explanations, not into letter accuracy. Details: `docs/UNO_Q_BOARD_REFERENCE.md` §14.7.

### Suggested eval harness (for agents to build)
1. **Pedagogical score** on the chosen benchmark.
2. **Kangaroo held-out accuracy** (did the explanation reach the correct option?).
3. **Generation sanity checks:** language consistency (stays in Catalan/target language), no hallucinated rambling, response length.
4. **On-device metrics:** tok/s (prompt + decode), time-to-first-token, peak RAM, model file size. Use `llama-bench` on the actual UNO Q.
5. Run this harness after **every** compression step (quantize → prune → recover) to catch regressions.

---

## 8. Recommended pipeline (synthesis)

```
0. Baseline: Gemma 3 1B IT / Gemma 3 270M IT (and Qwen 3.5 0.8B for comparison)
   → GGUF Q4_0 → run on UNO Q → measure tutoring score + tok/s + RAM
1. Data: build tutoring SFT set (Kangaroo train split + synthesized explanations/dialogues,
   target language), keep Kangaroo held-out + pedagogical benchmark for eval
2. Fine-tune (LoRA/QLoRA) the base model on tutoring data → merge → evaluate (FP16)
3. Quantize (Q8_0, Q4_K_M, Q4_0 [+imatrix]) → evaluate on PC → benchmark on board
4. ONLY IF size/speed is still insufficient:
   structured pruning (LLM-Pruner or structured-Wanda, FFN channels first, uniform across layers)
   → LoRA recovery on tutoring data → merge → quantize → re-evaluate (generation, not MCQ!)
5. Deploy: GGUF served by our own llama.cpp `llama-server` service on the UNO Q (ports 8081/8082,
   pinned build `2cbe0ec`, CPU-only, see docs/BOARD_SETUP.md). An OpenCL (Adreno 702) test is optional.
```

Note: the team's original order was prune → fine-tune. Fine-tuning first (step 2) and pruning later with **task-specific calibration data** is also valid, and lets pruning keep exactly what the tutor needs. Either way, **always finish with recovery fine-tuning after pruning**.

---

## 9. Open questions / TODO checklist
- [x] 2 GB or 4 GB UNO Q? **4 GB.**
- [ ] Kangaroo dataset: language, number of options (answered: A–E), are solutions/explanations included?
- [ ] Which pedagogical benchmark exactly? Is there an official evaluation script/rules from the challenge?
- [ ] Required response language(s)?
- [ ] Does llama.cpp's OpenCL backend work on Adreno 702? Is it faster than CPU?
- [x] CPU feature flags on QRB2210 (`/proc/cpuinfo`): confirmed, no `asimddp`/`i8mm`
- [x] Custom GGUF: we run our own `llama-server` as a systemd service (`docs/BOARD_SETUP.md` step 7). Swap the model file in `config.env` and the service.
- [ ] Does LLM-Pruner support Gemma 3? Does `convert_hf_to_gguf.py` accept non-uniform pruned Gemma 3 configs?
- [ ] Challenge rules on model size / allowed base models / external data / synthetic data?

---

## 10. Glossary
- **PTQ / QAT:** post-training quantization / quantization-aware training.
- **Per-channel / group-wise scales:** one scale per output row / per block of N weights.
- **GGUF:** llama.cpp model file format. **Q4_0, Q8_0, Q4_K_M:** llama.cpp quantization types.
- **Structured pruning:** remove whole neurons/heads/channels → smaller dense matrices.
- **Unstructured pruning:** zero individual weights → sparse matrices (needs sparse formats/kernels to benefit).
- **N:M (2:4) sparsity:** in every block of M weights, N are zero. Hardware-accelerated on some NVIDIA GPUs.
- **CSR:** Compressed Sparse Row storage format.
- **LoRA / QLoRA:** low-rank adapter fine-tuning / LoRA on a 4-bit quantized frozen base.
- **Taylor importance:** estimated loss change from removing weights ≈ |gradient × weight|.

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
- [Gemma 3 270M architecture (embeddings vs blocks) — eWeek](https://www.eweek.com/pt/news/google-gemma-3-270m/)
- [Gemma 3 on Raspberry Pi 5 benchmark (sizes)](https://www.kunalganglani.com/blog/gemma-3-raspberry-pi-5-benchmark.md)
- [LLM-Pruner: On the Structural Pruning of LLMs (arXiv:2305.11627)](https://arxiv.org/pdf/2305.11627)
- [Wanda: A Simple and Effective Pruning Approach for LLMs (arXiv:2306.11695)](https://arxiv.org/html/2306.11695v1) · [code](https://github.com/locuslab/wanda)
- [SparseGPT (arXiv:2301.00774)](https://arxiv.org/abs/2301.00774v3)
- [QLoRA (arXiv:2305.14314)](https://arxiv.org/abs/2305.14314)
- [MathTutorBench (arXiv:2502.18940)](https://arxiv.org/pdf/2502.18940v1)
- [MRBench / Unifying AI Tutor Evaluation (arXiv:2412.09416)](https://arxiv.org/html/2412.09416v2)
- [Arm learning path: llama.cpp decode roofline (Q4_0 vs Q8_0 on Arm)](https://learn.arm.com/learning-paths/cross-platform/llm-decode-roofline/diagnose/)
