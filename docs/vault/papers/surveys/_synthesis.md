---
tags: [synthesis, surveys]
papers: 6
date: 2026-11-14
---
# Surveys and model reports: synthesis by junction

> Changes to the proposed junctions: J1 (survey crosswalk) and J2 (base model) are kept. The proposed J3 (on-device deployment lessons) is dropped as a junction. The surveys are too thin on CPU-only ARM to support it: Xu 2024 is about phones, NPUs and processing-in-memory, and gives llama.cpp one paragraph with no ARM-CPU numbers. Girija 2025 gives only qualitative "edge suitability" ratings. Those few facts now sit in the "on the UNO Q" parts of J1 and J2. A new J3 replaces it: **how much QAT costs**. The three surveys describe QAT as full retraining. The Gemma 3 report does it in about 5,000 steps. This decides whether we run a short QAT after our fine-tune.

The four surveys map what exists, but none of them covers GGUF formats, CPU decode, multilingual effects of compression, or models under 1B. The Gemma 3 report gives a text-only 1B model with official int4 QAT checkpoints, a small KV cache and the better math. The Salamandra report gives a 2B model with Catalan and Spanish oversampled, weak math and a large KV cache. Neither report compares the two, so our own Catalan/Spanish eval decides.

Papers:
- [[zhu2023_model_compression_llm_survey_2308.07633.pdf|Zhu survey]] ([arXiv 2308.07633](https://arxiv.org/abs/2308.07633)). LLM compression survey: quantization, pruning, distillation, low-rank.
- [[wan2023_efficient_llms_survey_2312.03863.pdf|Wan survey]] ([arXiv 2312.03863](https://arxiv.org/abs/2312.03863)). Efficient LLMs: model-, data- and framework-centric.
- [[xu2024_on_device_language_models_review_2409.00088.pdf|Xu review]] ([arXiv 2409.00088](https://arxiv.org/abs/2409.00088)). On-device LLMs: architectures, compression, frameworks, phone deployments.
- [[girija2025_llm_compression_resource_constrained_survey_2505.02309.pdf|Girija survey]] ([arXiv 2505.02309](https://arxiv.org/abs/2505.02309)). Compression for resource-constrained settings (Google authors).
- [[gemma3_technical_report_2503.19786.pdf|Gemma 3 report]] ([arXiv 2503.19786](https://arxiv.org/abs/2503.19786)). Gemma 3, 1B–27B, with QAT checkpoints.
- [[gonzalezagirre2025_salamandra_technical_report_2502.08489.pdf|Salamandra report]] ([arXiv 2502.08489](https://arxiv.org/abs/2502.08489)). BSC's 2B/7B/40B models, trained on 35 European languages.

## Junctions at a glance
| Junction | Papers | Decision it informs |
|---|---|---|
| J1: Survey crosswalk to the vault | [[zhu2023_model_compression_llm_survey_2308.07633.pdf\|Zhu]], [[wan2023_efficient_llms_survey_2312.03863.pdf\|Wan]], [[xu2024_on_device_language_models_review_2409.00088.pdf\|Xu]], [[girija2025_llm_compression_resource_constrained_survey_2505.02309.pdf\|Girija]] | Which methods to add to the vault, and which survey claims not to trust for a CPU/GGUF target |
| J2: Base model, Gemma 3 vs Salamandra 2B | [[gemma3_technical_report_2503.19786.pdf\|Gemma 3]], [[gonzalezagirre2025_salamandra_technical_report_2502.08489.pdf\|Salamandra]] | Which checkpoint to fine-tune for a ca/es/en math tutor in 2–4 GB RAM on llama.cpp, and what role the other model gets |
| J3: How much QAT costs | [[gemma3_technical_report_2503.19786.pdf\|Gemma 3]], [[wan2023_efficient_llms_survey_2312.03863.pdf\|Wan]], [[zhu2023_model_compression_llm_survey_2308.07633.pdf\|Zhu]], [[girija2025_llm_compression_resource_constrained_survey_2505.02309.pdf\|Girija]] | Whether to run a short QAT after our fine-tune, or stop at PTQ with an importance matrix |

## J1: Survey crosswalk to the vault

**Question.** Where does each survey's taxonomy land in our vault folders? What does it cover that our primary papers don't? Where is it wrong or outdated for a CPU-only llama.cpp target?

**How the papers relate.** They are parallel overviews with almost the same four-way split. Zhu (Fig. 1) and Wan (§2.1, Fig. 4) both use quantization / pruning / low-rank / distillation. Xu §4 uses the same four. Girija §III covers distillation / quantization / pruning, plus MoE and early exit (§III.D). They add different things. Wan adds efficient pre-training, PEFT, inference systems, architectures, data-centric methods and frameworks (§2.2–§4). Xu adds on-device architectures, edge-cloud collaboration, frameworks and phone case studies (§3, §5, §6). Girija adds a comparison table with "edge suitability" ratings (Table III). Zhu adds metrics and benchmarks (§2) and per-method perplexity tables (Tables 1–2). Girija is the only one that cites another survey in this folder. It cites Zhu (TACL 2024 version, ref. [9]) and [[gholami2021_quantization_survey_2103.13630.pdf|Gholami 2021]] (ref. [32]) as prior work that "often focuses on one or two compression techniques" (§I). Zhu's arXiv ID dates from 2023, but the parsed version cites 2024 work (e.g. BitDistiller, CoRR abs/2402.10631), so read it as a 2024 revision. Girija is from May 2025 and does not mention Gemma 3 or any QAT checkpoint.

**Crosswalk.**

| Our folder | Zhu | Wan | Xu | Girija |
|---|---|---|---|---|
| quantization | §3 (QAT, weight-only, weight-activation, KV), Table 1 | §2.1.1 (PTQ, QAT) | §4.1, §3.2 | §III.B, Table II, §IV.B, §IV.D |
| pruning | §4 (unstructured, structured, semi-structured), Table 2 | §2.1.2 | §4.2 | §III.C |
| finetuning_distillation | §5 (black-box: CoT, ICL, instruction following; white-box) | §2.1.4, §2.3 (PEFT, memory-efficient fine-tuning) | §4.3 | §III.A, Table I, §IV.A, §IV.E |
| inference | §3.2.3 (KV quantization), §7.3 (deployment) | §2.4 (speculative decoding, KV cache, serving systems), §2.5 (efficient attention), §4 (frameworks) | §3.3–§3.6, §5 (frameworks, hardware) | §III.D (MoE, early exit) |

**Covered by the surveys but not in the vault.** This is a short list, limited to sub-2B models, CPU, math or CoT distillation, calibration and QAT with PEFT. IDs are the ones printed in each survey's reference list.
- *Calibration data:* Williams & Aletras 2023, "How does calibration data affect the post-training pruning and quantization of LLMs?" (CoRR abs/2311.09755). Cited in Zhu Remark 4: downstream performance "can vary significantly" with the calibration set. This is the general-language counterpart to [[chimoto2026_calibrating_beyond_english_2601.18306.pdf|Chimoto 2026]].
- *QAT with PEFT, low-bit QAT:* LoftQ (CoRR abs/2310.08659), L4Q (CoRR abs/2402.04902), BitDistiller (CoRR abs/2402.10631), OneBit (CoRR abs/2402.11295). Zhu §3.1, Remark 1. PEQA (Wan §2.3.2; NeurIPS 2023, no arXiv ID in Zhu or Wan).
- *Distillation for reasoning:* Fine-tune-CoT, "Large Language Models Are Reasoning Teachers" ([arXiv 2212.10071](https://arxiv.org/abs/2212.10071)) and Distilling Step-by-Step ([arXiv 2305.02301](https://arxiv.org/abs/2305.02301)), both in Girija §IV.A. Fu et al. 2023, "Specializing smaller language models towards multi-step reasoning" (ICML 2023, no arXiv ID in Zhu). Zhu §5.1.1 says it focuses on math and warns that task specialization "may inadvertently lead to reduced performance" on general problems. GKD / on-policy distillation (ICLR 2024, no arXiv ID in Zhu or Girija). DistiLLM ([arXiv 2402.03898](https://arxiv.org/abs/2402.03898), Girija Table I).
- *Embedding compression:* TensorGPT ([arXiv 2307.00526](https://arxiv.org/abs/2307.00526), Wan §2.1.3) compresses the embedding layer with a tensor-train decomposition. It is the only embedding-specific method in the four surveys. It matters because 302M of Gemma 3 1B's parameters are embeddings (see J2). Compare [[ushio2023_vocabulary_trimming_2305.15020.pdf|vocabulary trimming]].
- *Low-rank:* SVD-LLM ([arXiv 2403.07378](https://arxiv.org/abs/2403.07378), Wan §2.1.3). Low priority.
- *On-device measurement:* MELTing Point ([arXiv 2403.12844](https://arxiv.org/abs/2403.12844), Xu §3.4). It benchmarks LLMs on Android, iOS and Jetson and finds that quantization "incurs an accuracy cost". It is the closest thing in these surveys to an on-device benchmark harness.
- *Small base models:* TinyLlama ([arXiv 2401.02385](https://arxiv.org/abs/2401.02385), Xu §7).

**Where the surveys disagree, are wrong, or are outdated for our target.**
- *Zhu assumes weight-only quantization dequantizes before the matmul.* Zhu §3.2 says weight-only quantization "inevitably introduces additional computational overhead" and "cannot enjoy the accelerated low-bit operation". Low-bit CPU kernels are built to avoid exactly that; see [[wei2024_tmac_lut_cpu_lowbit_2407.00088.pdf|T-MAC]] and [[wang2024_bitnet_cpp_1bit_infra_2410.16144.pdf|bitnet.cpp]]. On a memory-bound board, weight-only quantization is the main lever. Weight-activation W8A8 is less relevant.
- *Semi-structured speedups are Ampere-only.* Every 2:4 speedup in Zhu Table 2 (1.24×–2×) is on NVIDIA Ampere, and Zhu §4.3 says "the current implementation of the Ampere architecture supports only the 2:4 ratio". Wan §2.1.2 says unstructured pruning is hard to deploy "except specific types of hardware such as Nvidia Ampere GPUs". Girija §III.C says the same for GPUs. All three agree with the CHALLENGE_CONTEXT §2 finding that llama.cpp gets no speed from sparsity.
- *Girija is optimistic about pruning accuracy.* Girija Table III rates pruning's accuracy loss as "Very Low to Medium" and says distillation "often improves accuracy". It gives no evidence for either rating. Check them against [[jaiswal2023_llm_kick_compressing_llms_truth_2310.01382.pdf|LLM-KICK]] in the pruning folder before relying on them.
- *Wan ranks quantization above the alternatives.* Wan §2.1.1 cites Li et al. 2024c: quantization has "superior compression-accuracy trade-offs" compared with pruning and low-rank approximation. This matches CHALLENGE_CONTEXT §4: quantize first.
- *The surveys disagree on vLLM.* Xu §5.1 lists it as an "edge-cloud" framework with Vulkan, Metal and WebGPU support. Wan §4 describes it as GPU serving with "efficient kernels for both Nvidia and AMD GPUs". For our board, neither description matters.
- *The surveys file BitNet differently.* Wan §2.1.1 puts BitNet under QAT: it "pioneers QAT for 1-bit LLMs". Xu §4.1 puts BitNet b1.58 under post-training weight-activation co-quantization. For the method itself, read [[ma2024_bitnet_b158_2402.17764.pdf|BitNet b1.58]] in the quantization folder.
- *Errors to ignore.* Wan §2.1.2 prints "OPT-135B" for SparseGPT at about 60% sparsity. Zhu §4.1 says "over 50%" on OPT-175B. Xu §4.2 attributes LLM-Pruner to "Kaddour et al., 2023", while Zhu §4.2 and Wan §2.1.2 both attribute it to Ma et al. 2023. Girija Table II cites ZeroQuant-V2 as [43], which is its lottery-ticket reference.
- *Wan's framework list leaves out llama.cpp.* Wan §4 (Table 2) lists 17 frameworks, all for GPU training or serving apart from MLC LLM. Only Xu §5.1 lists llama.cpp: "edge-only", "CPU and CPU+GPU hybrid inference across ARM and x86", on-device LoRA fine-tuning.
- *Gaps in all four.* No survey covers GGUF, K-quants or importance matrices. No survey covers multilingual or non-English effects of compression. Use [[marchisio2024_quantization_multilingual_llms_2407.03211.pdf|Marchisio 2024]] and [[chimoto2026_calibrating_beyond_english_2601.18306.pdf|Chimoto 2026]] for that. None discusses distillation teacher size. The Gemma 3 report does (§5.4, Fig. 8): for short training horizons the smaller teacher is better, but "the trend is reversed for longer training". This bears on teacher choice in finetuning_distillation.

**Negative results and limits.**
- The survey tables copy numbers from the original papers ("solely derived from the original papers", Zhu Tables 1–2), mostly perplexity on 7B–175B models. None of the numbers is for a sub-2B model or for an ARM CPU.
- Zhu's efficiency metrics are FLOPs, MFU, latency, speedup and compression ratio (§2.1). Memory bandwidth is not among them. Zhu §7.3 suggests the roofline model for deployment analysis, which is the right tool for a bandwidth-bound board.
- Girija's cost model is "2 FLOPS ... per active parameter per token" (§II). It describes compute, but our decode is bound by memory, not compute (CHALLENGE_CONTEXT §2).
- Xu's hardware section (§5.2) covers GPU, NPU and FPGA only. It gives no guidance for CPU-only inference. Its only energy figure is about 0.7 J per token for a 7B model on a phone (§2.5).

**What this means on the UNO Q.**
- Use the surveys to find names, not settings. For a quant recipe, go to the quantization folder and to llama.cpp's own formats (CHALLENGE_CONTEXT §4).
- Skip everything that needs Ampere sparse tensor cores, W8A8 GPU kernels, PIM/PNM memory, MoE expert offload or multi-device sharding (Xu §3.3–§3.5). None of it applies to a 4× Cortex-A53 board.
- Two cheap items to take: calibration-set choice (Williams & Aletras, with Chimoto) for `llama-imatrix`, and on-device measurement in the MELT style (TTFT, decode tok/s, RAM, per Xu §2.5) as the template for our `llama-bench` runs.
- Add Fine-tune-CoT and Distilling Step-by-Step to finetuning_distillation if the team plans teacher-generated rationales for tutoring.

**Open questions.**
- Does any compression survey from late 2025 or 2026 cover GGUF formats, CPU decode, or multilingual degradation? None of these four does.
- Girija Table III's ratings have no sources. Can any of them be checked against our own runs?

## J2: Base model, Gemma 3 vs Salamandra 2B

**Question.** Which model should we fine-tune for a Catalan/Spanish/English math tutor that runs from GGUF under llama.cpp in 2–4 GB RAM on a CPU-only board?

**How the papers relate.** The two models compete. Neither report evaluates the other. Salamandra's 2B baselines are EuroLLM 1.7B, FLOR 1.3B and **Gemma-2 2B** (§5.2.3), not Gemma 3. The Gemma 3 report compares only against Gemma 2 and Gemini (§4.2: "We do not compare directly with external models"). The only bridge is Gemma-2 2B, which both reports evaluate, but with different setups.

**Key evidence: Gemma 3.**
- *Sizes.* The report covers 1B, 4B, 12B and 27B (Abstract, Table 1). **It does not cover a 270M model.** Facts about 270M must come from another source.
- *1B shape.* 302M embedding parameters, 698M non-embedding, and **0 vision-encoder parameters**, so the 1B model is text-only (Table 1). Context is 32K for 1B and 128K for the others (§2). There are 5 local sliding-window layers for each global layer. The window is 1024 tokens. Attention is GQA with QK-norm (§2, §1).
- *Vocabulary.* The figures conflict. The Table 1 caption says "256k entries". §2.2 says the Gemini 2.0 SentencePiece tokenizer has "262k entries", with split digits, preserved whitespace and byte-level encodings, and is "more balanced for non-English languages".
- *Training.* The 1B model saw 2T tokens (§2.2). All sizes are distilled from a teacher, sampling 256 logits per token (§2.2). The amount of multilingual data was increased, but per-language shares are not given (§2.2).
- *QAT checkpoints.* Each model was fine-tuned "for a small number of steps, typically 5,000" with QAT. The targets were the non-quantized checkpoint's probabilities. There are three formats: "per-channel int4, per-block int4, and switched fp8". They were chosen "based on the most popular open source quantization inference engines (e.g. llama.cpp)" (§2.3). For the 1B model, Table 3 gives 2.0 GB in bf16, 0.5 GB per-channel int4, 0.7 GB int4 with blocks of 32, and 1.0 GB SFP8. With a 32,768-token KV cache the figures are 2.9 / 1.4 / 1.6 / 1.9 GB. The caption says "quantized in 8 bits", and it does not say whether that applies to the KV cache. **The report gives no accuracy numbers for the QAT checkpoints.** It does not say GGUF or Q4_0. That "int4, blocks=32" matches llama.cpp's Q4_0 block size is our inference.
- *Math and multilingual, 1B IT.* GSM8K 62.8, MATH 48.0, HiddenMath 15.0, IFEval 80.2, Global-MMLU-Lite 34.2, WMT24++ 35.9 (Table 18). Table 6 prints HiddenMath 15.8 for the same model; the report does not explain the difference.
- *Multilingual math, 1B pre-trained.* MGSM is **2.04** (8-shot), against 34.7 for 4B and 18.7 for Gemma-2 2B (Table 13, Table 19). The 1B base model barely does multilingual grade-school math before instruction tuning. The report gives no MGSM number for the IT models and no per-language numbers, so nothing for Catalan or Spanish specifically.
- *Format.* The PT models end with `<eos>` and the IT models with `<end_of_turn>`. "Fine-tuning either model type thus also requires adding their respective end tokens." `[BOS]` must be added explicitly (§3, Table 4).
- *Licence.* The report does not state one. Check the model card.

**Key evidence: Salamandra 2B.**
- *Shape.* 2,253,490,176 parameters, 24 layers, hidden size 2,048, 16 attention heads and **16 K/V heads**, context 8,192, vocabulary 256,000 (Table 1). "The smaller 2B parameter model relies on multi-head attention"; only 7B and 40B use GQA (§2.1). The report does not say whether the input and output embeddings are tied.
- *Tokenizer.* SentencePiece BPE with byte fallback, digit splitting, NFC normalization, and 100 reserved tokens (§2.3.2). It was trained on a uniform sample across 35 languages and code (§2.3.3). The authors say each language's fertility is "close to monolingual baselines" (§2.3.3). In Fig. 15, Catalan fertility is about 1.16 tokens per word for Salamandra against about 1.35 for Gemma 2 (approx., read from the figure). This compares Gemma 2's tokenizer, not Gemma 3's.
- *Catalan and Spanish oversampling.* Spanish, Catalan, Galician and Basque are sampled for 2 epochs. Code is sampled for 0.5 (Table 2). After sampling, word shares are English 41.706%, Spanish 16.570% and Catalan 1.738% (Table 2). The text says English and code "were undersampled by half" (§3.1.3), but Table 2 lists English at 1 epoch. The report does not reconcile the two. The Catalan data covers the Central, Valencian and Balearic dialects (§3.1.3).
- *Instruction tuning.* The mix is 272,869 instructions: 12.99% Catalan, 14.89% Spanish, 67.16% English (Table 5). There is no preference alignment: "none of the released checkpoints has undergone any sort of preference optimization" (§4). The chat format is ChatML (§4.1.3).
- *Math.* MGSM exact match (scale 0–1) for the base 2B model is 0.02 in Spanish and 0.04 in Catalan. Gemma-2 2B scores 0.07 and 0.04 (Table 9). The instructed models score 0.01 and 0.02 against 0.00 and 0.00 (Table 10). LLM-as-judge "Correctness (0/1)" on MGSM gives Salamandra 2B 0.65 (es) and 0.63 (ca), against 0.94 and 0.93 for Gemma-2 2B (Table 11, Table 12). The authors: "Mathematical reasoning remains a weak area for all models" (§5.2.3). The instructed models show "significant performance declines" in math (§5.2.4).
- *Reading comprehension.* Belebele for the base 2B model: ca 23.22, es 23.78, en 22.44. Gemma-2 2B scores 58.89, 64.22 and 71.89 (Table 9).
- *Where it is strong.* "Gemma-2 seems to dominate in the 2B range, with the notable exception of translation, where Salamandra 2B seems to perform on par with and even outperform it" (§5.2.4). Salamandra is among the best models "particularly in Catalan and Basque" for some base-model categories (§5.2.3).
- *Licence.* Apache 2.0 for all checkpoints, research and commercial use (Abstract, §7).

**Negative results and limits.**
- **Salamandra's two math measures conflict.** MGSM exact match is about 0.02–0.04 (Tables 9–10). Judge-scored correctness is about 0.63–0.65 (Tables 11–12). The paper does not reconcile them. Treat this as a measurement problem, not as evidence that Salamandra can do math.
- **No transitive ranking.** Gemma 3 1B IT is not better than Gemma-2 2B IT across the board. MATH is 48.0 vs 27.2, but Global-MMLU-Lite is 34.2 vs 41.9 and WMT24++ is 35.9 vs 37.4 (Table 6, Table 18). The pre-trained MGSM is 2.04 vs 18.7 (Table 13). "Gemma 3 1B ≥ Gemma-2 2B ≥ Salamandra 2B" therefore does not hold on multilingual tasks.
- The Gemma 3 report warns that probe benchmarks may be contaminated "despite the use of decontamination techniques" (§5.1).
- Salamandra's instructed models were evaluated 5-shot, and the authors plan 0-shot runs (§5.2.4). The setups differ from Gemma's 0-shot IT evaluation (Table 21).
- Salamandra's instruction tuning lowered translation, truthfulqa_gen and generative QA scores (§5.2.4). In the harness, the instructed Gemma-2 2B beats the instructed Salamandra 2B on FLORES: ca 23.61 vs 19.43, es 20.61 vs 15.03 (Table 10). Salamandra 2B leads only as a base model (FLORES ca 24.93 vs 23.88, Table 9) and in the judge-scored translation tables (Tables 11–12). Its translation edge is therefore only partly supported.
- For Gemma-1B on M3Kang, see the benchmarks synthesis (Links).

**What this means on the UNO Q.**
- *RAM (our arithmetic, not from the papers).* At about 4.5 bits per weight (Q4_0), Salamandra 2B's weights are about 2.253B × 4.5 / 8 ≈ 1.27 GB. Gemma 3 1B is 0.7 GB with int4 blocks of 32 (Table 3). Salamandra's KV cache with full multi-head attention at 16 bits is 2 × 24 layers × 2,048 × 2 bytes ≈ 192 KiB per token. That is ≈ 0.75 GiB at 4,096 tokens and ≈ 1.5 GiB at its full 8,192. Gemma 3's GQA and 1024-token local window keep the KV cache of 5 of every 6 layers fixed in size (§5.2, Fig. 5–6). In the report's 2B ablation at 32k context, the KV overhead is 60% for a global-only model and under 15% with a 1:3 local:global ratio and a 1024-token window (§5.2, Fig. 5). Both models fit in 4 GB at short context. On a 2 GB board, or next to the embedding server from BOARD_SETUP, Salamandra 2B is tight.
- *Speed (our estimate).* Decode is bound by memory bandwidth (CHALLENGE_CONTEXT §2). Salamandra 2B moves about 1.8× the weight bytes of Gemma 3 1B per token. If Gemma 3 1B decodes at about 5 tok/s on the board (CHALLENGE_CONTEXT §2), Salamandra 2B should land near 2.5–3 tok/s, under the 4–7 tok/s reading-speed target. Measure it with `llama-bench` before deciding.
- *What the papers support.*
  - **Gemma 3 1B (IT, QAT int4) as the base to fine-tune first.** It has an official QAT checkpoint, the smaller RAM and KV footprint, and much better English math. The cost is a weak multilingual base (MGSM 2.04 pre-trained), so Catalan and Spanish math has to come from our fine-tune data.
  - **Salamandra (2B base, or 7B) on the laptop, in a supporting role.** It can produce or check Catalan/Spanish text, translate problems and hints, and judge fluency. Its licence is Apache 2.0. The translation claim rests mainly on the judge scores (§5.2.4, Tables 11–12). The instructed 2B loses to instructed Gemma-2 2B on FLORES in the harness (Table 10), so test the base 2B or the 7B for translation. Its math is not good enough to generate solution traces.
  - **The deciding test is ours.** Run Gemma 3 1B IT vs Salamandra 2B instruct on the same ca/es/en math items, using the M3Kang protocol from the benchmarks folder. Run it at Q4_0 on the board for tok/s and RAM. Neither paper has run this comparison.
- *Fine-tuning details from the reports.* Keep Gemma's `<end_of_turn>` and explicit `[BOS]` in the training data (§3). Wrong end tokens are a likely cause of format failures. If we use Salamandra, its template is ChatML (§4.1.3).
- *Alternatives (linked, not summarized here).* [[liu2024_mobilellm_2402.14905.pdf|MobileLLM]] for sub-billion deep-and-thin designs, also cited in Xu §3.2. [[ma2025_bitnet_b158_2b4t_2504.12285.pdf|BitNet b1.58 2B4T]] for a ternary 2B model with its own CPU runtime.

**Open questions.**
- How good is Gemma 3 1B in Catalan specifically? Neither report gives per-language numbers. Gemma's Table 13 averages over languages.
- How do Gemma 3's QAT int4 checkpoints score against bf16? §2.3 reports memory only.
- Does fine-tuning from the QAT checkpoint keep its quantization robustness after a LoRA merge? Neither report tests it.
- Is the vocabulary 256k or 262k? It matters for [[ushio2023_vocabulary_trimming_2305.15020.pdf|vocabulary trimming]]. Read it from the tokenizer file.
- Does the 270M model share the 1B's tokenizer, QAT formats and end tokens? The report does not cover it.

## J3: How much QAT costs

**Question.** Is QAT too expensive for us, or can we run a short QAT pass after fine-tuning so the deployed int4 model keeps its quality?

**How the papers relate.** The Gemma 3 report contradicts the three surveys. Wan §2.1.1: "QAT requires training using the complete training dataset, it is much more expensive and time consuming than PTQ." Girija §III.B.2 says QAT costs more training time, needs lower learning rates, and is "more complex to implement", but "generally achieves much higher accuracy than PTQ". Zhu Remark 1 says retraining "demands a lot of effort" and suggests combining QAT with PEFT (QLoRA, PEQA, LoftQ, L4Q). The Gemma 3 report (§2.3) does QAT as a short fine-tune: "typically 5,000" steps, with the full-precision model's probabilities as targets and data matched to the pre- and post-training distributions. That is self-distillation into the quantized model. LLM-QAT (in the quantization folder, cited by Zhu §3.1 and Wan §2.1.1) uses the same idea.

**Key evidence.**
- Gemma 3: about 5,000 steps per model, three weight formats, distillation targets from the non-quantized checkpoint (§2.3).
- Girija Table III rates QAT's accuracy loss "Very Low" and PTQ's "High". It gives no numbers.
- Zhu Table 1 lists LLM-QAT on LLaMA-30B at W4A8 with a perplexity increase of 0.5 (WikiText-2) and 0.9 (C4), as reported by the original paper.

**Negative results and limits.**
- The Gemma 3 report does not give the QAT batch size, learning rate or token count. It does not give accuracy before and after QAT either. "5,000 steps" alone does not tell us the compute cost.
- None of the surveys tests QAT on a model under 1B or on multilingual data.

**What this means on the UNO Q.**
- First path: fine-tune from the Gemma 3 1B QAT int4 checkpoint, export, quantize with `llama-quantize` (Q4_0, `--pure` if the Adreno OpenCL path is tried), and compare against PTQ from bf16 with an importance matrix on ca/es/en math calibration text. This costs no training beyond the fine-tune.
- Second path, only if PTQ loses too much on our eval: a short QAT pass after the fine-tune, using the fine-tuned bf16 model as the distillation target. That follows Gemma §2.3 and LLM-QAT. The training data should mix tutoring dialogues with general text.

**Open questions.**
- Is the QAT checkpoint published in a form we can fine-tune, such as unquantized weights trained with QAT? §2.3 only says quantized versions are provided "in different standard formats". Check the model hub.
- Does a LoRA fine-tune on the QAT checkpoint, merged and re-quantized, keep the QAT benefit? No paper here tests this.
- How many QAT steps does a 1B model need when the data is only tutoring dialogues?

## Papers not covered by any junction

None.

## Links to other folders
- J1: [[jaiswal2023_llm_kick_compressing_llms_truth_2310.01382.pdf|LLM-KICK]] (pruning; check against Girija's pruning ratings). [[frantar2023_sparsegpt_2301.00774.pdf|SparseGPT]] and [[sun2023_wanda_2306.11695.pdf|Wanda]] (pruning; the primary sources behind the surveys' sparsity tables).
- J1, J3: [[marchisio2024_quantization_multilingual_llms_2407.03211.pdf|Marchisio 2024]] and [[chimoto2026_calibrating_beyond_english_2601.18306.pdf|Chimoto 2026]] (quantization; the multilingual gap no survey covers), [[liu2023_llm_qat_2305.17888.pdf|LLM-QAT]] (quantization; QAT by self-distillation).
- J1: [[wei2024_tmac_lut_cpu_lowbit_2407.00088.pdf|T-MAC]] and [[wang2024_bitnet_cpp_1bit_infra_2410.16144.pdf|bitnet.cpp]] (inference; low-bit CPU kernels, against Zhu §3.2).
- J2: [[ushio2023_vocabulary_trimming_2305.15020.pdf|Vocabulary trimming]] (pruning; Gemma 3's 256k/262k vocabulary and its 302M embedding parameters).
- J2: [[liu2024_mobilellm_2402.14905.pdf|MobileLLM]] (inference) and [[ma2025_bitnet_b158_2b4t_2504.12285.pdf|BitNet b1.58 2B4T]] (quantization), alternative base models.
- J2: [[torrescamps2026_m3kang_2601.16218.pdf|M3Kang]] (benchmarks). Gemma-1B fails on format there, and the benchmarks synthesis covers it. The Gemma 3 report's Table 1 shows the 1B model has no vision encoder. This suggests M3Kang gave `gemma-3-1b-it` the text version of figure problems. M3Kang should confirm it.
- J2, J3: [[dettmers2023_qlora_2305.14314.pdf|QLoRA]] (finetuning_distillation; Zhu Remark 1 and Girija §IV.E). [[li2025_small_models_strong_reasoners_2502.12143.pdf|Small models, strong reasoners]] (finetuning_distillation; teacher choice, with Gemma 3 §5.4).
- Dataset: [M3Kang dataset card](https://huggingface.co/datasets/qualcomm/M3Kang).
