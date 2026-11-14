# Paper vault: index of papers by folder

This page is a reference index of the paper vault, for team members who choose a compression, fine-tuning or evaluation method.
It lists every paper by folder, with one line on why it matters for our copilot.

Relevance notes refer to our target: the copilot.
The copilot uses a small language model that llama.cpp serves on the Arduino UNO Q (4× Cortex-A53, 4 GB RAM).
The language model deployed now is Qwen3.5 0.8B Q8_0.
The plan behind these papers is in [Challenge context](../../CHALLENGE_CONTEXT.md).
Its [glossary](../../CHALLENGE_CONTEXT.md#10-glossary) explains PTQ, QAT, LoRA, QLoRA, GGUF and 2:4 sparsity.

Each folder has a `_synthesis.md` that reads its papers together, one section per junction.
A [junction](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) is one question that several papers answer together.
[Cross-folder junctions](_junctions.md) links them and says what to read first for each decision.

We compared the IDs and titles with arXiv when we downloaded the PDFs (2026-11-14).
The PDFs are not in Git.
After cloning, run `./download.sh` in `docs/vault/papers/` to fetch them from arXiv. The list is in `papers.tsv`.
The script prints `OK` or `FAIL` for each arXiv ID.

The PDF column links to the PDF on arXiv.
Most local file names follow `<category>/<firstauthor><year>_<short_name>_<arxivID>.pdf`.
A few use the model or team name instead, for example `gemma3_technical_report` and `learnlm2024_improving_gemini_for_learning`.

## pruning/

Synthesis: [pruning/_synthesis](pruning/_synthesis.md).

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2015 | Learning both Weights and Connections for Efficient Neural Networks (Han et al.) | [1506.02626](https://arxiv.org/abs/1506.02626) | [PDF](https://arxiv.org/pdf/1506.02626) | Classic magnitude pruning + retraining loop |
| 2015 | Deep Compression (Han et al.) | [1510.00149](https://arxiv.org/abs/1510.00149) | [PDF](https://arxiv.org/pdf/1510.00149) | Pruning + quantization + coding pipeline: the original "compress for the edge" paper |
| 2018 | The Lottery Ticket Hypothesis (Frankle & Carbin) | [1803.03635](https://arxiv.org/abs/1803.03635) | [PDF](https://arxiv.org/pdf/1803.03635) | Theory behind why sparse subnetworks can train well |
| 2020 | Movement Pruning (Sanh et al.) | [2005.07683](https://arxiv.org/abs/2005.07683) | [PDF](https://arxiv.org/pdf/2005.07683) | Pruning during fine-tuning of pretrained transformers |
| 2022 | Optimal Brain Compression (Frantar & Alistarh) | [2208.11580](https://arxiv.org/abs/2208.11580) | [PDF](https://arxiv.org/pdf/2208.11580) | Optimal Brain Surgeon (OBS) framework that unifies post-training pruning and quantization. Basis of SparseGPT/GPTQ |
| 2023 | SparseGPT (Frantar & Alistarh) | [2301.00774](https://arxiv.org/abs/2301.00774) | [PDF](https://arxiv.org/pdf/2301.00774) | One-shot unstructured / 2:4 pruning of LLMs |
| 2023 | LLM-Pruner (Ma et al.) | [2305.11627](https://arxiv.org/abs/2305.11627) | [PDF](https://arxiv.org/pdf/2305.11627) | Structured pruning + LoRA recovery. Top suggestion of [Martí](../../CHALLENGE_CONTEXT.md), an ML and hardware colleague of the team |
| 2023 | Wanda (Sun et al.) | [2306.11695](https://arxiv.org/abs/2306.11695) | [PDF](https://arxiv.org/pdf/2306.11695) | Weight × activation pruning, no retraining. Can be adapted to structured pruning |
| 2023 | Sheared LLaMA (Xia et al.) | [2310.06694](https://arxiv.org/abs/2310.06694) | [PDF](https://arxiv.org/pdf/2310.06694) | Structured pruning to a target shape + continued pretraining |
| 2023 | An Efficient Multilingual LM Compression through Vocabulary Trimming (Ushio et al.) | [2305.15020](https://arxiv.org/abs/2305.15020) | [PDF](https://arxiv.org/pdf/2305.15020) | Basis for trimming Gemma 3 270M's 256k vocabulary ([Challenge context §3](../../CHALLENGE_CONTEXT.md#3-base-model-candidates)) |
| 2023 | Compressing LLMs: The Truth is Rarely Pure and Never Simple (LLM-KICK, Jaiswal et al.) | [2310.01382](https://arxiv.org/abs/2310.01382) | [PDF](https://arxiv.org/pdf/2310.01382) | Pruning breaks knowledge-heavy tasks at 25–30% sparsity even when perplexity looks fine. Quantization degrades less. Backs Martí's warning |
| 2023 | FLAP (An et al.) | [2312.11983](https://arxiv.org/abs/2312.11983) | [PDF](https://arxiv.org/pdf/2312.11983) | Retraining-free structured pruning |
| 2024 | SliceGPT (Ashkboos et al.) | [2401.15024](https://arxiv.org/abs/2401.15024) | [PDF](https://arxiv.org/pdf/2401.15024) | Removes rows/columns → smaller dense matrices |
| 2024 | ShortGPT (Men et al.) | [2403.03853](https://arxiv.org/abs/2403.03853) | [PDF](https://arxiv.org/pdf/2403.03853) | Layer (depth) pruning by redundancy |
| 2024 | The Unreasonable Ineffectiveness of the Deeper Layers (Gromov et al.) | [2403.17887](https://arxiv.org/abs/2403.17887) | [PDF](https://arxiv.org/pdf/2403.17887) | Layer dropping + QLoRA healing |
| 2024 | Compact Language Models via Pruning and Knowledge Distillation (Minitron) | [2407.14679](https://arxiv.org/abs/2407.14679) | [PDF](https://arxiv.org/pdf/2407.14679) | Width/depth pruning + distillation recipe |
| 2024 | LLM Pruning and Distillation in Practice: The Minitron Approach | [2408.11796](https://arxiv.org/abs/2408.11796) | [PDF](https://arxiv.org/pdf/2408.11796) | Practical follow-up of Minitron |

## quantization/

Synthesis: [quantization/_synthesis](quantization/_synthesis.md).

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2017 | Quantization and Training of NNs for Efficient Integer-Arithmetic-Only Inference (Jacob et al.) | [1712.05877](https://arxiv.org/abs/1712.05877) | [PDF](https://arxiv.org/pdf/1712.05877) | Foundations of int8 inference and QAT on mobile CPUs |
| 2018 | Quantizing deep convolutional networks for efficient inference: A whitepaper (Krishnamoorthi) | [1806.08342](https://arxiv.org/abs/1806.08342) | [PDF](https://arxiv.org/pdf/1806.08342) | PTQ vs QAT basics |
| 2021 | A Survey of Quantization Methods for Efficient NN Inference (Gholami et al.) | [2103.13630](https://arxiv.org/abs/2103.13630) | [PDF](https://arxiv.org/pdf/2103.13630) | Broad survey |
| 2021 | A White Paper on Neural Network Quantization (Nagel et al.) | [2106.08295](https://arxiv.org/abs/2106.08295) | [PDF](https://arxiv.org/pdf/2106.08295) | Practical PTQ/QAT guide |
| 2022 | ZeroQuant (Yao et al.) | [2206.01861](https://arxiv.org/abs/2206.01861) | [PDF](https://arxiv.org/pdf/2206.01861) | Fine-grained PTQ for transformers |
| 2022 | LLM.int8() (Dettmers et al.) | [2208.07339](https://arxiv.org/abs/2208.07339) | [PDF](https://arxiv.org/pdf/2208.07339) | Outlier features in LLMs. Mixed-precision int8 |
| 2022 | GPTQ (Frantar et al.) | [2210.17323](https://arxiv.org/abs/2210.17323) | [PDF](https://arxiv.org/pdf/2210.17323) | Second-order 3–4 bit weight PTQ |
| 2022 | SmoothQuant (Xiao et al.) | [2211.10438](https://arxiv.org/abs/2211.10438) | [PDF](https://arxiv.org/pdf/2211.10438) | Moves activation outliers into weights, for 8-bit weights and activations (W8A8) |
| 2023 | LLM-QAT (Liu et al.) | [2305.17888](https://arxiv.org/abs/2305.17888) | [PDF](https://arxiv.org/pdf/2305.17888) | Data-free QAT for LLMs |
| 2023 | AWQ (Lin et al.) | [2306.00978](https://arxiv.org/abs/2306.00978) | [PDF](https://arxiv.org/pdf/2306.00978) | Activation-aware 4-bit weights. Edge deployment (TinyChat) |
| 2023 | SpQR (Dettmers et al.) | [2306.03078](https://arxiv.org/abs/2306.03078) | [PDF](https://arxiv.org/pdf/2306.03078) | Near-lossless low-bit with sparse outliers |
| 2023 | QuIP (Chee et al.) | [2307.13304](https://arxiv.org/abs/2307.13304) | [PDF](https://arxiv.org/pdf/2307.13304) | 2-bit via incoherence processing |
| 2023 | OmniQuant (Shao et al.) | [2308.13137](https://arxiv.org/abs/2308.13137) | [PDF](https://arxiv.org/pdf/2308.13137) | Learned clipping/transform PTQ |
| 2023 | BitNet (Wang et al.) | [2310.11453](https://arxiv.org/abs/2310.11453) | [PDF](https://arxiv.org/pdf/2310.11453) | 1-bit transformers trained from scratch |
| 2024 | Extreme Compression of LLMs via Additive Quantization (AQLM) | [2401.06118](https://arxiv.org/abs/2401.06118) | [PDF](https://arxiv.org/pdf/2401.06118) | 2-bit codebook quantization |
| 2024 | QuIP# (Tseng et al.) | [2402.04396](https://arxiv.org/abs/2402.04396) | [PDF](https://arxiv.org/pdf/2402.04396) | Hadamard + lattice codebooks |
| 2024 | The Era of 1-bit LLMs: BitNet b1.58 (Ma et al.) | [2402.17764](https://arxiv.org/abs/2402.17764) | [PDF](https://arxiv.org/pdf/2402.17764) | Ternary weights |
| 2024 | QuaRot (Ashkboos et al.) | [2404.00456](https://arxiv.org/abs/2404.00456) | [PDF](https://arxiv.org/pdf/2404.00456) | Rotations remove outliers → 4-bit weights, activations and KV cache |
| 2024 | SpinQuant (Liu et al.) | [2405.16406](https://arxiv.org/abs/2405.16406) | [PDF](https://arxiv.org/pdf/2405.16406) | Learned rotations for 4-bit |
| 2024 | How Does Quantization Affect Multilingual LLMs? (Marchisio et al.) | [2407.03211](https://arxiv.org/abs/2407.03211) | [PDF](https://arxiv.org/pdf/2407.03211) | Math reasoning degrades fastest under quantization. Human eval sees more damage than metrics |
| 2025 | BitNet b1.58 2B4T Technical Report | [2504.12285](https://arxiv.org/abs/2504.12285) | [PDF](https://arxiv.org/pdf/2504.12285) | Open 2B ternary model, runs on CPU |
| 2026 | Calibrating Beyond English (Chimoto et al.) | [2601.18306](https://arxiv.org/abs/2601.18306) | [PDF](https://arxiv.org/pdf/2601.18306) | Multilingual calibration beats English-only for 4-bit PTQ: use Catalan/Spanish text for `llama-imatrix`, llama.cpp's importance-matrix tool |

## inference/

Synthesis: [inference/_synthesis](inference/_synthesis.md).

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2020 | MCUNet (Lin et al.) | [2007.10319](https://arxiv.org/abs/2007.10319) | [PDF](https://arxiv.org/pdf/2007.10319) | Model/runtime co-design for microcontrollers (extreme constraints) |
| 2022 | FlashAttention (Dao et al.) | [2205.14135](https://arxiv.org/abs/2205.14135) | [PDF](https://arxiv.org/pdf/2205.14135) | IO-aware attention: it cuts reads and writes to GPU memory. Memory-hierarchy thinking |
| 2022 | Efficiently Scaling Transformer Inference (Pope et al.) | [2211.05102](https://arxiv.org/abs/2211.05102) | [PDF](https://arxiv.org/pdf/2211.05102) | Why decode is memory-bandwidth bound |
| 2022 | Fast Inference from Transformers via Speculative Decoding (Leviathan et al.) | [2211.17192](https://arxiv.org/abs/2211.17192) | [PDF](https://arxiv.org/pdf/2211.17192) | Draft-and-verify decoding |
| 2023 | Accelerating LLM Decoding with Speculative Sampling (Chen et al.) | [2302.01318](https://arxiv.org/abs/2302.01318) | [PDF](https://arxiv.org/pdf/2302.01318) | Concurrent speculative sampling paper |
| 2023 | FlexGen (Sheng et al.) | [2303.06865](https://arxiv.org/abs/2303.06865) | [PDF](https://arxiv.org/pdf/2303.06865) | Offloading under tight memory |
| 2023 | H2O: Heavy-Hitter Oracle (Zhang et al.) | [2306.14048](https://arxiv.org/abs/2306.14048) | [PDF](https://arxiv.org/pdf/2306.14048) | Eviction from the KV cache (the stored attention keys and values) |
| 2023 | FlashAttention-2 (Dao) | [2307.08691](https://arxiv.org/abs/2307.08691) | [PDF](https://arxiv.org/pdf/2307.08691) | Faster attention kernels |
| 2023 | PagedAttention / vLLM (Kwon et al.) | [2309.06180](https://arxiv.org/abs/2309.06180) | [PDF](https://arxiv.org/pdf/2309.06180) | KV-cache memory management |
| 2023 | StreamingLLM: Attention Sinks (Xiao et al.) | [2309.17453](https://arxiv.org/abs/2309.17453) | [PDF](https://arxiv.org/pdf/2309.17453) | Bounded KV cache for long chats |
| 2023 | Deja Vu: Contextual Sparsity (Liu et al.) | [2310.17157](https://arxiv.org/abs/2310.17157) | [PDF](https://arxiv.org/pdf/2310.17157) | Input-dependent sparsity at inference |
| 2023 | LLM in a flash (Alizadeh et al.) | [2312.11514](https://arxiv.org/abs/2312.11514) | [PDF](https://arxiv.org/pdf/2312.11514) | Run models larger than DRAM from flash storage |
| 2023 | PowerInfer (Song et al.) | [2312.12456](https://arxiv.org/abs/2312.12456) | [PDF](https://arxiv.org/pdf/2312.12456) | Hot/cold neuron split, CPU–GPU hybrid |
| 2024 | KIVI (Liu et al.) | [2402.02750](https://arxiv.org/abs/2402.02750) | [PDF](https://arxiv.org/pdf/2402.02750) | 2-bit KV-cache quantization |
| 2024 | MobileLLM (Liu et al.) | [2402.14905](https://arxiv.org/abs/2402.14905) | [PDF](https://arxiv.org/pdf/2402.14905) | Sub-billion architecture design for on-device |
| 2024 | PowerInfer-2 (Xue et al.) | [2406.06282](https://arxiv.org/abs/2406.06282) | [PDF](https://arxiv.org/pdf/2406.06282) | LLM inference on a smartphone |
| 2024 | T-MAC (Wei et al.) | [2407.00088](https://arxiv.org/abs/2407.00088) | [PDF](https://arxiv.org/pdf/2407.00088) | Lookup-table low-bit matmul on edge CPUs (no dot-product instructions needed) |
| 2024 | 1-bit AI Infra: BitNet b1.58 Inference on CPUs (bitnet.cpp) | [2410.16144](https://arxiv.org/abs/2410.16144) | [PDF](https://arxiv.org/pdf/2410.16144) | Ternary-model CPU kernels |

## finetuning_distillation/

Synthesis: [finetuning_distillation/_synthesis](finetuning_distillation/_synthesis.md).

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2015 | Distilling the Knowledge in a Neural Network (Hinton et al.) | [1503.02531](https://arxiv.org/abs/1503.02531) | [PDF](https://arxiv.org/pdf/1503.02531) | Original knowledge distillation |
| 2019 | DistilBERT (Sanh et al.) | [1910.01108](https://arxiv.org/abs/1910.01108) | [PDF](https://arxiv.org/pdf/1910.01108) | Distillation of a pretrained transformer |
| 2021 | LoRA (Hu et al.) | [2106.09685](https://arxiv.org/abs/2106.09685) | [PDF](https://arxiv.org/pdf/2106.09685) | Low-rank adapters. Post-pruning recovery |
| 2023 | QLoRA (Dettmers et al.) | [2305.14314](https://arxiv.org/abs/2305.14314) | [PDF](https://arxiv.org/pdf/2305.14314) | LoRA on a 4-bit base |
| 2023 | MiniLLM (Gu et al.) | [2306.08543](https://arxiv.org/abs/2306.08543) | [PDF](https://arxiv.org/pdf/2306.08543) | Distillation for generative LLMs, with reverse KL divergence as the loss |
| 2023 | TinyGSM (Liu et al.) | [2312.09241](https://arxiv.org/abs/2312.09241) | [PDF](https://arxiv.org/pdf/2312.09241) | >80% on GSM8K (grade-school math word problems) with 1.3B models trained on synthetic data. The quality of synthetic supervised fine-tuning (SFT) data matters more than size |
| 2025 | Small Models Struggle to Learn from Strong Reasoners (Li et al.) | [2502.12143](https://arxiv.org/abs/2502.12143) | [PDF](https://arxiv.org/pdf/2502.12143) | Models ≤3B learn better from short chains of thought. Fits our short-answer budget on the board |

## surveys/

Synthesis: [surveys/_synthesis](surveys/_synthesis.md).

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2023 | A Survey on Model Compression for LLMs (Zhu et al.) | [2308.07633](https://arxiv.org/abs/2308.07633) | [PDF](https://arxiv.org/pdf/2308.07633) | Compression overview |
| 2023 | Efficient Large Language Models: A Survey (Wan et al.) | [2312.03863](https://arxiv.org/abs/2312.03863) | [PDF](https://arxiv.org/pdf/2312.03863) | Model-, data- and system-level efficiency |
| 2024 | On-Device Language Models: A Comprehensive Review | [2409.00088](https://arxiv.org/abs/2409.00088) | [PDF](https://arxiv.org/pdf/2409.00088) | On-device focus |
| 2025 | Gemma 3 Technical Report | [2503.19786](https://arxiv.org/abs/2503.19786) | [PDF](https://arxiv.org/pdf/2503.19786) | One base model family that we explore for the fine-tune (incl. QAT checkpoints). The deployed language model is Qwen3.5 0.8B Q8_0. The fine-tune base is not chosen yet |
| 2025 | Salamandra Technical Report (Gonzalez-Agirre et al., BSC) | [2502.08489](https://arxiv.org/abs/2502.08489) | [PDF](https://arxiv.org/pdf/2502.08489) | Open 2B/7B/40B models with Catalan and Spanish oversampled: base model or Catalan data teacher |
| 2025 | Optimizing LLMs for Resource-Constrained Environments (Girija et al.) | [2505.02309](https://arxiv.org/abs/2505.02309) | [PDF](https://arxiv.org/pdf/2505.02309) | Compression survey from the resource-constrained angle |

## benchmarks/

Synthesis: [benchmarks/_synthesis](benchmarks/_synthesis.md).

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2025 | Evaluating Visual Mathematics in Multimodal LLMs: A Multilingual Benchmark Based on the Kangaroo Tests (Igualde-Sáez et al.) | [2506.07418](https://arxiv.org/abs/2506.07418) | [PDF](https://arxiv.org/pdf/2506.07418) | Kangaroo 2014–2024 in English, Spanish, French and Catalan. Catalan vs Spanish results depend on the model family |
| 2026 | M3Kang: Evaluating Multilingual Multimodal Mathematical Reasoning in VLMs (Torres-Camps et al., Qualcomm) | [2601.16218](https://arxiv.org/abs/2601.16218) | [PDF](https://arxiv.org/pdf/2601.16218) | The paper behind the challenge dataset: 1,747 Kangaroo problems in 108 languages, human baseline from 68k students |

## tutoring_pedagogy/

Synthesis: [tutoring_pedagogy/_synthesis](tutoring_pedagogy/_synthesis.md).

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2023 | MathDial (Macina et al.) | [2305.14536](https://arxiv.org/abs/2305.14536) | [PDF](https://arxiv.org/pdf/2305.14536) | ~3k teacher–student tutoring dialogues with scaffolding questions. Candidate SFT data |
| 2023 | Bridging the Novice-Expert Gap: Remediating Math Mistakes (Bridge, Wang et al.) | [2310.10648](https://arxiv.org/abs/2310.10648) | [PDF](https://arxiv.org/pdf/2310.10648) | Error → strategy → intention before answering: a template for synthetic explanations. Source data of [MRBench](https://arxiv.org/abs/2412.09416), a benchmark of tutor responses to student math mistakes |
| 2024 | Boosting LLMs with Socratic Method for Conversational Mathematics Teaching (Ding et al.) | [2407.17349](https://arxiv.org/abs/2407.17349) | [PDF](https://arxiv.org/pdf/2407.17349) | SocraticMATH: Socratic primary-school math dataset, close to the Kangaroo level |
| 2024 | LearnLM: Improving Gemini for Learning (LearnLM Team) | [2412.16429](https://arxiv.org/abs/2412.16429) | [PDF](https://arxiv.org/pdf/2412.16429) | Pedagogy as system-level instructions: design of the copilot prompt and SFT format |
| 2025 | From Problem-Solving to Teaching Problem-Solving (Dinucu-Jianu et al.) | [2505.15607](https://arxiv.org/abs/2505.15607) | [PDF](https://arxiv.org/pdf/2505.15607) | Multi-turn reinforcement learning (RL) tutor that avoids leaking the solution. Same group as [MathTutorBench](https://arxiv.org/abs/2502.18940), a benchmark of math tutors |

## jev/

Synthesis: [jev/_synthesis](jev/_synthesis.md).

Jev is TypeSafe AI's decision model, which TypeSafe calls "System One".
A decision model answers typed Choice / Noul (yes-no) / Score questions with a probability for each option instead of writing text.

Jev is in early access.
The early access started in September 2026 (team note, no public source).
No technical paper and no weights from TypeSafe are public.
The hosted model runs only in the cloud.

These are third-party papers that evaluate Jev, use it, or build open Jev-style models.
What they suggest for our copilot is under [What to try](#what-to-try).

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2026 | Jev in the Wild: Functionality, Applications and Ecosystem (Ling et al.) | [2609.30216](https://arxiv.org/abs/2609.30216) | [PDF](https://arxiv.org/pdf/2609.30216) | Overview of the model and its ecosystem |
| 2026 | Evaluating and Benchmarking the System One Model Jev (Deußer et al.) | [2609.37647](https://arxiv.org/abs/2609.37647) | [PDF](https://arxiv.org/pdf/2609.37647) | Main evaluation (37 datasets). Gives the letter-logit recipe for open models (read the model's scores for the letters A–E) (§3.6). It also shows a ~4B Gemma loses 15 points on calculation-heavy subjects without reasoning |
| 2026 | Specialized Decision Models vs. General-Purpose LLMs: Benchmarking Jev Across Knowledge, Reasoning, and Multilingual Tasks (Li et al.) | [2610.11978](https://arxiv.org/abs/2610.11978) | [PDF](https://arxiv.org/pdf/2610.11978) | Jev is last of 20 models on MathQA (5-option math word problems). The gap grows with reasoning demand. Smallest LLM compared is 4B |
| 2026 | Type-Safe Is Not Error-Free (Sun et al.) | [2609.26758](https://arxiv.org/abs/2609.26758) | [PDF](https://arxiv.org/pdf/2609.26758) | Decision models follow the option name, not its definition: matters for how we word the A–E options |
| 2026 | When the Right Answer Is Missing: An Arithmetic-Dependent Rejection Bottleneck in Jev (Zhong et al.) | [2609.39496](https://arxiv.org/abs/2609.39496) | [PDF](https://arxiv.org/pdf/2609.39496) | Closest to multiple-choice problems that need calculation |
| 2026 | NumericJev: Jev-like LLM Numerical Decoding with Multiway Decision Trees (Ye et al.) | [2609.28587](https://arxiv.org/abs/2609.28587) | [PDF](https://arxiv.org/pdf/2609.28587) | Getting numeric answers out of a decision model |
| 2026 | Correct Choices, Failed Sequences: Choice2Seq (Lai et al.) | [2610.16191](https://arxiv.org/abs/2610.16191) | [PDF](https://arxiv.org/pdf/2610.16191) | Accuracy when picking an option vs when generating the answer |
| 2026 | JEV-as-a-Judge: Accept When Confident, Escalate When Unsure (Li et al.) | [2609.26550](https://arxiv.org/abs/2609.26550) | [PDF](https://arxiv.org/pdf/2609.26550) | Confidence-based escalation: fits a small → large model cascade on the board |
| 2026 | The Value of Thinking: Learning When to Reason in Hybrid Decision Models (Yu et al.) | [2611.16961](https://arxiv.org/abs/2611.16961) | [PDF](https://arxiv.org/pdf/2611.16961) | When step-by-step reasoning pays off vs answering directly |
| 2026 | Visual Jev: Accurate and Efficient Decisions from Shared Visual Context (Yu & Yao) | [2609.25845](https://arxiv.org/abs/2609.25845) | [PDF](https://arxiv.org/pdf/2609.25845) | Several questions about one image, encoded once |
| 2026 | Intern-Decision: Efficient Multimodal Decision Making with Autoregressive Masked LM (Zhu et al.) | [2610.22131](https://arxiv.org/abs/2610.22131) | [PDF](https://arxiv.org/pdf/2610.22131) | Open multimodal decision models from 0.8B (Qwen3.5 base). Vision results are demos only |
| 2026 | DecisionRobust: Robustness for JEV-Style Decision Models Across Text and Vision (Lan et al.) | [2610.19118](https://arxiv.org/abs/2610.19118) | [PDF](https://arxiv.org/pdf/2610.19118) | Robustness with text and image inputs |
| 2026 | Beyond CLIP: Calibrated (Few-Shot) Defect Detection With System One Decision Models (Megahed et al.) | [2610.41199](https://arxiv.org/abs/2610.41199) | [PDF](https://arxiv.org/pdf/2610.41199) | Few-shot image classification compared with CLIP, a common image–text model |
| 2026 | Small Heads, Strong Decisions: A Controlled Study of Typed-Decision Models (Rastogi) | [2611.15592](https://arxiv.org/abs/2611.15592) | [PDF](https://arxiv.org/pdf/2611.15592) | Controlled study with small models |
| 2026 | From LLMs to Efficient System One Models via Adaptive Computation (Nguyen) | [2611.16321](https://arxiv.org/abs/2611.16321) | [PDF](https://arxiv.org/pdf/2611.16321) | Turning an LLM into an efficient decision model |
| 2026 | Flide: Accelerating Decision Inference with Exact State Forking (Li et al.) | [2610.42148](https://arxiv.org/abs/2610.42148) | [PDF](https://arxiv.org/pdf/2610.42148) | GPU engine. Also shows zero-training letter readout on Qwen3.5-0.8B, and that packing items with delimiters shifts probabilities |
| 2026 | Zuse: A Decision Model for European Languages (Imam) | [2611.06238](https://arxiv.org/abs/2611.06238) | [PDF](https://arxiv.org/pdf/2611.06238) | European multilingual decision model (closed weights). 4-bit costs ≤0.6 points. Language reach comes from the base model |
| 2026 | SO-Arena: Capability Spectrum and Reliability of System One Models (Li et al.) | [2611.15777](https://arxiv.org/abs/2611.15777) | [PDF](https://arxiv.org/pdf/2611.15777) | Benchmark for this model class |

## Not on arXiv (not downloaded)

- Optimal Brain Damage (LeCun et al., 1989) and Optimal Brain Surgeon (Hassibi & Stork, 1993): the origin of second-order pruning. Published at NeurIPS (NIPS). They have no arXiv version.
- llama.cpp / GGUF quantization types: Q4_0 (blocks of 32 weights with one scale) and K-quants (mixed-precision blocks). The llama.cpp repository documents them, not a paper.

## What to try

- Add a short reasoning pass before "Answer:", within the 60 s limit per problem.
  Our copilot now asks for one letter A–E in one pass, under a grammar that allows only those letters.
  The Jev papers find this one-pass letter scoring weak on calculation-heavy items.
  See [Jev J2](jev/_synthesis.md#j2-calculation-heavy-items-and-the-value-of-reasoning).
