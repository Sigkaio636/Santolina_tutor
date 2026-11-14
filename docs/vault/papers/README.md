# Papers: pruning, quantization, constrained LLM inference, math tutoring

PDFs downloaded from arXiv on 2026-11-14 (the `benchmarks/` and `tutoring_pedagogy/` folders and the rows complementing `CHALLENGE_CONTEXT.md` were added the same day). Each arXiv ID was checked against the arXiv API, and the titles match.
File name pattern: `<category>/<firstauthor><year>_<short_name>_<arxivID>.pdf`. The PDF column opens the local copy in Obsidian.

The PDFs are not in git. After cloning, run `./download.sh` in this folder to fetch them from arXiv (the list is in `papers.tsv`).

Relevance notes refer to our target: a small math-tutor LLM served with llama.cpp on the Arduino UNO Q (4× Cortex-A53, 2–4 GB RAM). See `CHALLENGE_CONTEXT.md`.

## pruning/

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2015 | Learning both Weights and Connections for Efficient Neural Networks (Han et al.) | [1506.02626](https://arxiv.org/abs/1506.02626) | [[han2015_learning_weights_connections_1506.02626.pdf\|PDF]] | Classic magnitude pruning + retraining loop |
| 2015 | Deep Compression (Han et al.) | [1510.00149](https://arxiv.org/abs/1510.00149) | [[han2015_deep_compression_1510.00149.pdf\|PDF]] | Pruning + quantization + coding pipeline: the original "compress for the edge" paper |
| 2018 | The Lottery Ticket Hypothesis (Frankle & Carbin) | [1803.03635](https://arxiv.org/abs/1803.03635) | [[frankle2018_lottery_ticket_1803.03635.pdf\|PDF]] | Theory behind why sparse subnetworks can train well |
| 2020 | Movement Pruning (Sanh et al.) | [2005.07683](https://arxiv.org/abs/2005.07683) | [[sanh2020_movement_pruning_2005.07683.pdf\|PDF]] | Pruning during fine-tuning of pretrained transformers |
| 2022 | Optimal Brain Compression (Frantar & Alistarh) | [2208.11580](https://arxiv.org/abs/2208.11580) | [[frantar2022_optimal_brain_compression_2208.11580.pdf\|PDF]] | OBS framework that unifies post-training pruning and quantization; basis of SparseGPT/GPTQ |
| 2023 | SparseGPT (Frantar & Alistarh) | [2301.00774](https://arxiv.org/abs/2301.00774) | [[frantar2023_sparsegpt_2301.00774.pdf\|PDF]] | One-shot unstructured / 2:4 pruning of LLMs |
| 2023 | LLM-Pruner (Ma et al.) | [2305.11627](https://arxiv.org/abs/2305.11627) | [[ma2023_llm_pruner_2305.11627.pdf\|PDF]] | Structured pruning + LoRA recovery. Martí's top suggestion |
| 2023 | Wanda (Sun et al.) | [2306.11695](https://arxiv.org/abs/2306.11695) | [[sun2023_wanda_2306.11695.pdf\|PDF]] | Weight × activation pruning, no retraining. Can be adapted to structured pruning |
| 2023 | Sheared LLaMA (Xia et al.) | [2310.06694](https://arxiv.org/abs/2310.06694) | [[xia2023_sheared_llama_2310.06694.pdf\|PDF]] | Structured pruning to a target shape + continued pretraining |
| 2023 | An Efficient Multilingual LM Compression through Vocabulary Trimming (Ushio et al.) | [2305.15020](https://arxiv.org/abs/2305.15020) | [[ushio2023_vocabulary_trimming_2305.15020.pdf\|PDF]] | Basis for trimming Gemma 3 270M's 256k vocabulary (CHALLENGE_CONTEXT §3) |
| 2023 | Compressing LLMs: The Truth is Rarely Pure and Never Simple (LLM-KICK, Jaiswal et al.) | [2310.01382](https://arxiv.org/abs/2310.01382) | [[jaiswal2023_llm_kick_compressing_llms_truth_2310.01382.pdf\|PDF]] | Pruning breaks knowledge-heavy tasks at 25–30% sparsity even when perplexity looks fine; quantization degrades less. Backs Martí's warning |
| 2023 | FLAP (An et al.) | [2312.11983](https://arxiv.org/abs/2312.11983) | [[an2023_flap_2312.11983.pdf\|PDF]] | Retraining-free structured pruning |
| 2024 | SliceGPT (Ashkboos et al.) | [2401.15024](https://arxiv.org/abs/2401.15024) | [[ashkboos2024_slicegpt_2401.15024.pdf\|PDF]] | Deletes rows/columns → smaller dense matrices |
| 2024 | ShortGPT (Men et al.) | [2403.03853](https://arxiv.org/abs/2403.03853) | [[men2024_shortgpt_2403.03853.pdf\|PDF]] | Layer (depth) pruning by redundancy |
| 2024 | The Unreasonable Ineffectiveness of the Deeper Layers (Gromov et al.) | [2403.17887](https://arxiv.org/abs/2403.17887) | [[gromov2024_unreasonable_ineffectiveness_deeper_layers_2403.17887.pdf\|PDF]] | Layer dropping + QLoRA healing |
| 2024 | Compact Language Models via Pruning and Knowledge Distillation (Minitron) | [2407.14679](https://arxiv.org/abs/2407.14679) | [[muralidharan2024_minitron_2407.14679.pdf\|PDF]] | Width/depth pruning + distillation recipe |
| 2024 | LLM Pruning and Distillation in Practice: The Minitron Approach | [2408.11796](https://arxiv.org/abs/2408.11796) | [[sreenivas2024_llm_pruning_distillation_practice_2408.11796.pdf\|PDF]] | Practical follow-up of Minitron |

## quantization/

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2017 | Quantization and Training of NNs for Efficient Integer-Arithmetic-Only Inference (Jacob et al.) | [1712.05877](https://arxiv.org/abs/1712.05877) | [[jacob2017_integer_arithmetic_only_inference_1712.05877.pdf\|PDF]] | Foundations of int8 inference and QAT on mobile CPUs |
| 2018 | Quantizing deep convolutional networks for efficient inference: A whitepaper (Krishnamoorthi) | [1806.08342](https://arxiv.org/abs/1806.08342) | [[krishnamoorthi2018_quantization_whitepaper_1806.08342.pdf\|PDF]] | PTQ vs QAT basics |
| 2021 | A Survey of Quantization Methods for Efficient NN Inference (Gholami et al.) | [2103.13630](https://arxiv.org/abs/2103.13630) | [[gholami2021_quantization_survey_2103.13630.pdf\|PDF]] | Broad survey |
| 2021 | A White Paper on Neural Network Quantization (Nagel et al.) | [2106.08295](https://arxiv.org/abs/2106.08295) | [[nagel2021_quantization_whitepaper_2106.08295.pdf\|PDF]] | Practical PTQ/QAT guide |
| 2022 | ZeroQuant (Yao et al.) | [2206.01861](https://arxiv.org/abs/2206.01861) | [[yao2022_zeroquant_2206.01861.pdf\|PDF]] | Fine-grained PTQ for transformers |
| 2022 | LLM.int8() (Dettmers et al.) | [2208.07339](https://arxiv.org/abs/2208.07339) | [[dettmers2022_llm_int8_2208.07339.pdf\|PDF]] | Outlier features in LLMs; mixed-precision int8 |
| 2022 | GPTQ (Frantar et al.) | [2210.17323](https://arxiv.org/abs/2210.17323) | [[frantar2022_gptq_2210.17323.pdf\|PDF]] | Second-order 3–4 bit weight PTQ |
| 2022 | SmoothQuant (Xiao et al.) | [2211.10438](https://arxiv.org/abs/2211.10438) | [[xiao2022_smoothquant_2211.10438.pdf\|PDF]] | Moves activation outliers into weights (W8A8) |
| 2023 | LLM-QAT (Liu et al.) | [2305.17888](https://arxiv.org/abs/2305.17888) | [[liu2023_llm_qat_2305.17888.pdf\|PDF]] | Data-free QAT for LLMs |
| 2023 | AWQ (Lin et al.) | [2306.00978](https://arxiv.org/abs/2306.00978) | [[lin2023_awq_2306.00978.pdf\|PDF]] | Activation-aware 4-bit weights; edge deployment (TinyChat) |
| 2023 | SpQR (Dettmers et al.) | [2306.03078](https://arxiv.org/abs/2306.03078) | [[dettmers2023_spqr_2306.03078.pdf\|PDF]] | Near-lossless low-bit with sparse outliers |
| 2023 | QuIP (Chee et al.) | [2307.13304](https://arxiv.org/abs/2307.13304) | [[chee2023_quip_2307.13304.pdf\|PDF]] | 2-bit via incoherence processing |
| 2023 | OmniQuant (Shao et al.) | [2308.13137](https://arxiv.org/abs/2308.13137) | [[shao2023_omniquant_2308.13137.pdf\|PDF]] | Learned clipping/transform PTQ |
| 2023 | BitNet (Wang et al.) | [2310.11453](https://arxiv.org/abs/2310.11453) | [[wang2023_bitnet_2310.11453.pdf\|PDF]] | 1-bit transformers trained from scratch |
| 2024 | Extreme Compression of LLMs via Additive Quantization (AQLM) | [2401.06118](https://arxiv.org/abs/2401.06118) | [[egiazarian2024_aqlm_2401.06118.pdf\|PDF]] | 2-bit codebook quantization |
| 2024 | QuIP# (Tseng et al.) | [2402.04396](https://arxiv.org/abs/2402.04396) | [[tseng2024_quip_sharp_2402.04396.pdf\|PDF]] | Hadamard + lattice codebooks |
| 2024 | The Era of 1-bit LLMs: BitNet b1.58 (Ma et al.) | [2402.17764](https://arxiv.org/abs/2402.17764) | [[ma2024_bitnet_b158_2402.17764.pdf\|PDF]] | Ternary weights |
| 2024 | QuaRot (Ashkboos et al.) | [2404.00456](https://arxiv.org/abs/2404.00456) | [[ashkboos2024_quarot_2404.00456.pdf\|PDF]] | Rotations remove outliers → 4-bit W/A/KV |
| 2024 | SpinQuant (Liu et al.) | [2405.16406](https://arxiv.org/abs/2405.16406) | [[liu2024_spinquant_2405.16406.pdf\|PDF]] | Learned rotations for 4-bit |
| 2024 | How Does Quantization Affect Multilingual LLMs? (Marchisio et al.) | [2407.03211](https://arxiv.org/abs/2407.03211) | [[marchisio2024_quantization_multilingual_llms_2407.03211.pdf\|PDF]] | Math reasoning degrades fastest under quantization; human eval sees more damage than metrics |
| 2025 | BitNet b1.58 2B4T Technical Report | [2504.12285](https://arxiv.org/abs/2504.12285) | [[ma2025_bitnet_b158_2b4t_2504.12285.pdf\|PDF]] | Open 2B ternary model, runs on CPU |
| 2026 | Calibrating Beyond English (Chimoto et al.) | [2601.18306](https://arxiv.org/abs/2601.18306) | [[chimoto2026_calibrating_beyond_english_2601.18306.pdf\|PDF]] | Multilingual calibration beats English-only for 4-bit PTQ: use Catalan/Spanish text for `llama-imatrix` |

## inference/

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2020 | MCUNet (Lin et al.) | [2007.10319](https://arxiv.org/abs/2007.10319) | [[lin2020_mcunet_2007.10319.pdf\|PDF]] | Model/runtime co-design for microcontrollers (extreme constraints) |
| 2022 | FlashAttention (Dao et al.) | [2205.14135](https://arxiv.org/abs/2205.14135) | [[dao2022_flashattention_2205.14135.pdf\|PDF]] | IO-aware attention; memory-hierarchy thinking |
| 2022 | Efficiently Scaling Transformer Inference (Pope et al.) | [2211.05102](https://arxiv.org/abs/2211.05102) | [[pope2022_efficiently_scaling_transformer_inference_2211.05102.pdf\|PDF]] | Why decode is memory-bandwidth bound |
| 2022 | Fast Inference from Transformers via Speculative Decoding (Leviathan et al.) | [2211.17192](https://arxiv.org/abs/2211.17192) | [[leviathan2022_speculative_decoding_2211.17192.pdf\|PDF]] | Draft-and-verify decoding |
| 2023 | Accelerating LLM Decoding with Speculative Sampling (Chen et al.) | [2302.01318](https://arxiv.org/abs/2302.01318) | [[chen2023_speculative_sampling_2302.01318.pdf\|PDF]] | Concurrent speculative sampling paper |
| 2023 | FlexGen (Sheng et al.) | [2303.06865](https://arxiv.org/abs/2303.06865) | [[sheng2023_flexgen_2303.06865.pdf\|PDF]] | Offloading under tight memory |
| 2023 | H2O: Heavy-Hitter Oracle (Zhang et al.) | [2306.14048](https://arxiv.org/abs/2306.14048) | [[zhang2023_h2o_heavy_hitter_2306.14048.pdf\|PDF]] | KV-cache eviction |
| 2023 | FlashAttention-2 (Dao) | [2307.08691](https://arxiv.org/abs/2307.08691) | [[dao2023_flashattention2_2307.08691.pdf\|PDF]] | Faster attention kernels |
| 2023 | PagedAttention / vLLM (Kwon et al.) | [2309.06180](https://arxiv.org/abs/2309.06180) | [[kwon2023_pagedattention_vllm_2309.06180.pdf\|PDF]] | KV-cache memory management |
| 2023 | StreamingLLM: Attention Sinks (Xiao et al.) | [2309.17453](https://arxiv.org/abs/2309.17453) | [[xiao2023_streamingllm_2309.17453.pdf\|PDF]] | Bounded KV cache for long chats |
| 2023 | Deja Vu: Contextual Sparsity (Liu et al.) | [2310.17157](https://arxiv.org/abs/2310.17157) | [[liu2023_deja_vu_2310.17157.pdf\|PDF]] | Input-dependent sparsity at inference |
| 2023 | LLM in a flash (Alizadeh et al.) | [2312.11514](https://arxiv.org/abs/2312.11514) | [[alizadeh2023_llm_in_a_flash_2312.11514.pdf\|PDF]] | Run models larger than DRAM from flash storage |
| 2023 | PowerInfer (Song et al.) | [2312.12456](https://arxiv.org/abs/2312.12456) | [[song2023_powerinfer_2312.12456.pdf\|PDF]] | Hot/cold neuron split, CPU–GPU hybrid |
| 2024 | KIVI (Liu et al.) | [2402.02750](https://arxiv.org/abs/2402.02750) | [[liu2024_kivi_2402.02750.pdf\|PDF]] | 2-bit KV-cache quantization |
| 2024 | MobileLLM (Liu et al.) | [2402.14905](https://arxiv.org/abs/2402.14905) | [[liu2024_mobilellm_2402.14905.pdf\|PDF]] | Sub-billion architecture design for on-device |
| 2024 | PowerInfer-2 (Xue et al.) | [2406.06282](https://arxiv.org/abs/2406.06282) | [[xue2024_powerinfer2_2406.06282.pdf\|PDF]] | LLM inference on a smartphone |
| 2024 | T-MAC (Wei et al.) | [2407.00088](https://arxiv.org/abs/2407.00088) | [[wei2024_tmac_lut_cpu_lowbit_2407.00088.pdf\|PDF]] | Lookup-table low-bit matmul on edge CPUs (no dot-product instructions needed) |
| 2024 | 1-bit AI Infra: BitNet b1.58 Inference on CPUs (bitnet.cpp) | [2410.16144](https://arxiv.org/abs/2410.16144) | [[wang2024_bitnet_cpp_1bit_infra_2410.16144.pdf\|PDF]] | Ternary-model CPU kernels |

## finetuning_distillation/

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2015 | Distilling the Knowledge in a Neural Network (Hinton et al.) | [1503.02531](https://arxiv.org/abs/1503.02531) | [[hinton2015_distillation_1503.02531.pdf\|PDF]] | Original knowledge distillation |
| 2019 | DistilBERT (Sanh et al.) | [1910.01108](https://arxiv.org/abs/1910.01108) | [[sanh2019_distilbert_1910.01108.pdf\|PDF]] | Distillation of a pretrained transformer |
| 2021 | LoRA (Hu et al.) | [2106.09685](https://arxiv.org/abs/2106.09685) | [[hu2021_lora_2106.09685.pdf\|PDF]] | Low-rank adapters; post-pruning recovery |
| 2023 | QLoRA (Dettmers et al.) | [2305.14314](https://arxiv.org/abs/2305.14314) | [[dettmers2023_qlora_2305.14314.pdf\|PDF]] | LoRA on a 4-bit base |
| 2023 | MiniLLM (Gu et al.) | [2306.08543](https://arxiv.org/abs/2306.08543) | [[gu2023_minillm_2306.08543.pdf\|PDF]] | Distillation for generative LLMs (reverse KL) |
| 2023 | TinyGSM (Liu et al.) | [2312.09241](https://arxiv.org/abs/2312.09241) | [[liu2023_tinygsm_2312.09241.pdf\|PDF]] | >80% GSM8K with 1.3B models trained on synthetic data: synthetic SFT quality matters more than size |
| 2025 | Small Models Struggle to Learn from Strong Reasoners (Li et al.) | [2502.12143](https://arxiv.org/abs/2502.12143) | [[li2025_small_models_strong_reasoners_2502.12143.pdf\|PDF]] | Models ≤3B learn better from short chains of thought; fits our short-answer budget on the board |

## surveys/

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2023 | A Survey on Model Compression for LLMs (Zhu et al.) | [2308.07633](https://arxiv.org/abs/2308.07633) | [[zhu2023_model_compression_llm_survey_2308.07633.pdf\|PDF]] | Compression overview |
| 2023 | Efficient Large Language Models: A Survey (Wan et al.) | [2312.03863](https://arxiv.org/abs/2312.03863) | [[wan2023_efficient_llms_survey_2312.03863.pdf\|PDF]] | Model-, data- and system-level efficiency |
| 2024 | On-Device Language Models: A Comprehensive Review | [2409.00088](https://arxiv.org/abs/2409.00088) | [[xu2024_on_device_language_models_review_2409.00088.pdf\|PDF]] | On-device focus |
| 2025 | Gemma 3 Technical Report | [2503.19786](https://arxiv.org/abs/2503.19786) | [[gemma3_technical_report_2503.19786.pdf\|PDF]] | Our candidate base model family (incl. QAT checkpoints) |
| 2025 | Salamandra Technical Report (Gonzalez-Agirre et al., BSC) | [2502.08489](https://arxiv.org/abs/2502.08489) | [[gonzalezagirre2025_salamandra_technical_report_2502.08489.pdf\|PDF]] | Open 2B/7B/40B models with Catalan and Spanish oversampled: base model or Catalan data teacher |
| 2025 | Optimizing LLMs for Resource-Constrained Environments (Girija et al.) | [2505.02309](https://arxiv.org/abs/2505.02309) | [[girija2025_llm_compression_resource_constrained_survey_2505.02309.pdf\|PDF]] | Compression survey from the resource-constrained angle |

## benchmarks/

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2025 | Evaluating Visual Mathematics in Multimodal LLMs: A Multilingual Benchmark Based on the Kangaroo Tests (Igualde-Sáez et al.) | [2506.07418](https://arxiv.org/abs/2506.07418) | [[igualde2025_kangaroo_multilingual_visual_math_2506.07418.pdf\|PDF]] | Kangaroo 2014–2024 in English, Spanish, French and Catalan; Catalan vs Spanish results depend on the model family |
| 2026 | M3Kang: Evaluating Multilingual Multimodal Mathematical Reasoning in VLMs (Torres-Camps et al., Qualcomm) | [2601.16218](https://arxiv.org/abs/2601.16218) | [[torrescamps2026_m3kang_2601.16218.pdf\|PDF]] | The paper behind the challenge dataset: 1,747 Kangaroo problems in 108 languages, human baseline from 68k students |

## tutoring_pedagogy/

| Year | Paper | arXiv | PDF | Why it matters here |
|---|---|---|---|---|
| 2023 | MathDial (Macina et al.) | [2305.14536](https://arxiv.org/abs/2305.14536) | [[macina2023_mathdial_2305.14536.pdf\|PDF]] | ~3k teacher–student tutoring dialogues with scaffolding questions; candidate SFT data |
| 2023 | Bridging the Novice-Expert Gap: Remediating Math Mistakes (Bridge, Wang et al.) | [2310.10648](https://arxiv.org/abs/2310.10648) | [[wang2023_bridge_remediating_math_mistakes_2310.10648.pdf\|PDF]] | Error → strategy → intention before answering: a template for synthetic explanations. Source data of MRBench |
| 2024 | Boosting LLMs with Socratic Method for Conversational Mathematics Teaching (Ding et al.) | [2407.17349](https://arxiv.org/abs/2407.17349) | [[ding2024_socratic_math_teaching_2407.17349.pdf\|PDF]] | SocraticMATH: Socratic primary-school math dataset, close to the Kangaroo level |
| 2024 | LearnLM: Improving Gemini for Learning (LearnLM Team) | [2412.16429](https://arxiv.org/abs/2412.16429) | [[learnlm2024_improving_gemini_for_learning_2412.16429.pdf\|PDF]] | Pedagogy as system-level instructions: design of the tutor prompt and SFT format |
| 2025 | From Problem-Solving to Teaching Problem-Solving (Dinucu-Jianu et al.) | [2505.15607](https://arxiv.org/abs/2505.15607) | [[dinucujianu2025_teaching_problem_solving_rl_2505.15607.pdf\|PDF]] | Multi-turn RL tutor that avoids leaking the solution; same group as MathTutorBench |

## Not on arXiv (not downloaded)

- Optimal Brain Damage (LeCun et al., 1989) and Optimal Brain Surgeon (Hassibi & Stork, 1993): the origin of second-order pruning. Published at NeurIPS (NIPS); no arXiv version.
- llama.cpp / GGUF quantization formats (Q4_0, K-quants): documented in the llama.cpp repository, not in a paper.
