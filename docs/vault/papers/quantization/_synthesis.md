---
tags: [synthesis, quantization]
papers: 22
date: 2026-11-14
---
# Quantization: synthesis by junction

This note is an explanation for the team members who choose how to quantize the copilot's language model. It summarizes what 22 quantization papers mean for the UNO Q. It groups the papers by junction: one question that several papers answer together (see the [glossary](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md)).

The copilot's deployed language model is Qwen3.5 0.8B Q8_0 ([`config.env`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/config.env)). The fine-tune base is not chosen yet. The team explores Gemma 3 as one option, so the advice below targets Gemma 3 270M and 1B.

Terms used throughout (see also the [glossary](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md)):

- *PTQ* (post-training quantization) quantizes a trained model with no further training. *QAT* (quantization-aware training) simulates the quantization during training, so the model learns to cope with it.
- *WxAy* means x-bit weights and y-bit activations. W4A8 is 4-bit weights with 8-bit activations. KV4 adds a 4-bit KV cache. A16W4 is the same as W4A16.
- *Per-tensor*, *per-channel* and *per-token* scales mean one scale per matrix, per output row, or per token of activations. *g128* means group-wise scales: one scale per group of 128 weights.
- *RTN* (round-to-nearest) rounds each weight to the closest grid value. It is the baseline that GPTQ and AWQ improve on.
- *Perplexity* measures how well a model predicts a reference text. Lower is better.

For the copilot, this folder says: keep llama.cpp, and choose among its stock GGUF types. Spend the effort on evaluation, and on the calibration text for `llama-imatrix`. That llama.cpp tool computes an importance matrix from calibration text ([CHALLENGE_CONTEXT §4](../../../CHALLENGE_CONTEXT.md#4-quantization-marti-do-this-first)).

Most methods here (GPTQ, AWQ, SpQR, QuIP#, AQLM, QuaRot, OmniQuant) need their own kernels or formats, and the pinned llama.cpp cannot load them. Their two main signals are fine groups and activation-aware importance. llama.cpp's block-wise types and importance matrix aim at the same two signals. How `llama-quantize` uses the matrix is still open (see [Open questions](#open-questions)).

Small models and math degrade first, and automatic metrics hide damage that human readers see. So the folder favors:

- Q8_0 for Gemma 3 270M.
- For Gemma 3 1B, a measured comparison of Q8_0, Gemma's QAT Q4_0, and Q4_K_M with a Catalan/Spanish/English + math importance matrix. Q4_K_M is one of llama.cpp's K-quants: mixed-precision block types.

Papers:

- [Jacob 2017](https://arxiv.org/abs/1712.05877) ([arXiv 1712.05877](https://arxiv.org/abs/1712.05877)). Integer-only int8 inference and simulated-quantization training on phone CPUs.
- [Krishnamoorthi 2018](https://arxiv.org/abs/1806.08342) ([arXiv 1806.08342](https://arxiv.org/abs/1806.08342)). PTQ vs QAT whitepaper for CNNs.
- [Gholami 2021](https://arxiv.org/abs/2103.13630) ([arXiv 2103.13630](https://arxiv.org/abs/2103.13630)). Survey of quantization methods.
- [Nagel 2021](https://arxiv.org/abs/2106.08295) ([arXiv 2106.08295](https://arxiv.org/abs/2106.08295)). PTQ/QAT pipelines and debugging.
- [ZeroQuant](https://arxiv.org/abs/2206.01861) ([arXiv 2206.01861](https://arxiv.org/abs/2206.01861)). Group-wise weights, token-wise activations, layer-by-layer distillation.
- [LLM.int8()](https://arxiv.org/abs/2208.07339) ([arXiv 2208.07339](https://arxiv.org/abs/2208.07339)). Emergent activation outliers. Int8 with fp16 outlier decomposition.
- [GPTQ](https://arxiv.org/abs/2210.17323) ([arXiv 2210.17323](https://arxiv.org/abs/2210.17323)). Second-order one-shot weight quantization.
- [SmoothQuant](https://arxiv.org/abs/2211.10438) ([arXiv 2211.10438](https://arxiv.org/abs/2211.10438)). Moves activation outliers into the weights for W8A8.
- [LLM-QAT](https://arxiv.org/abs/2305.17888) ([arXiv 2305.17888](https://arxiv.org/abs/2305.17888)). Data-free QAT with self-generated data.
- [AWQ](https://arxiv.org/abs/2306.00978) ([arXiv 2306.00978](https://arxiv.org/abs/2306.00978)). Activation-aware per-channel scaling for weight-only quantization.
- [SpQR](https://arxiv.org/abs/2306.03078) ([arXiv 2306.03078](https://arxiv.org/abs/2306.03078)). Sparse fp16 outlier weights plus small quantized groups.
- [QuIP](https://arxiv.org/abs/2307.13304) ([arXiv 2307.13304](https://arxiv.org/abs/2307.13304)). Incoherence processing with random orthogonal matrices.
- [OmniQuant](https://arxiv.org/abs/2308.13137) ([arXiv 2308.13137](https://arxiv.org/abs/2308.13137)). Learned clipping and learned equivalent transforms.
- [BitNet](https://arxiv.org/abs/2310.11453) ([arXiv 2310.11453](https://arxiv.org/abs/2310.11453)). 1-bit Transformer trained from scratch.
- [AQLM](https://arxiv.org/abs/2401.06118) ([arXiv 2401.06118](https://arxiv.org/abs/2401.06118)). Additive (multi-codebook) quantization at 2–3 bits.
- [QuIP#](https://arxiv.org/abs/2402.04396) ([arXiv 2402.04396](https://arxiv.org/abs/2402.04396)). Hadamard incoherence plus E8 lattice codebooks. A Hadamard matrix is a fixed rotation made of ±1 entries. The E8 lattice is a regular grid of points in 8 dimensions, used as the codebook.
- [BitNet b1.58](https://arxiv.org/abs/2402.17764) ([arXiv 2402.17764](https://arxiv.org/abs/2402.17764)). Ternary weights {-1, 0, 1}.
- [QuaRot](https://arxiv.org/abs/2404.00456) ([arXiv 2404.00456](https://arxiv.org/abs/2404.00456)). Hadamard rotations for 4-bit weights, activations and KV cache.
- [SpinQuant](https://arxiv.org/abs/2405.16406) ([arXiv 2405.16406](https://arxiv.org/abs/2405.16406)). Learned rotations.
- [Marchisio 2024](https://arxiv.org/abs/2407.03211) ([arXiv 2407.03211](https://arxiv.org/abs/2407.03211)). Quantization damage across languages and tasks, plus human evaluation.
- [BitNet b1.58 2B4T](https://arxiv.org/abs/2504.12285) ([arXiv 2504.12285](https://arxiv.org/abs/2504.12285)). Open 2B ternary model, 4T tokens.
- [Chimoto 2026](https://arxiv.org/abs/2601.18306) ([arXiv 2601.18306](https://arxiv.org/abs/2601.18306)). Language of the calibration set for GPTQ/AWQ.

## Junctions at a glance

| Junction | Papers | Decision it informs |
|---|---|---|
| J1: Foundations: grids, granularity, PTQ vs QAT | [Jacob](https://arxiv.org/abs/1712.05877), [Krishnamoorthi](https://arxiv.org/abs/1806.08342), [Nagel](https://arxiv.org/abs/2106.08295), [Gholami](https://arxiv.org/abs/2103.13630) | How to read GGUF block types. Why group size matters more than the algorithm at 4 bits |
| J2: Outliers at W4A8 with block scales | [LLM.int8()](https://arxiv.org/abs/2208.07339), [SmoothQuant](https://arxiv.org/abs/2211.10438), [AWQ](https://arxiv.org/abs/2306.00978), [SpQR](https://arxiv.org/abs/2306.03078), [QuIP](https://arxiv.org/abs/2307.13304), [QuIP#](https://arxiv.org/abs/2402.04396), [QuaRot](https://arxiv.org/abs/2404.00456), [SpinQuant](https://arxiv.org/abs/2405.16406) | Which outlier fixes still matter when llama.cpp quantizes activations to 8 bits per block (32 or 256 values) |
| J3: Do small models quantize worse? | [GPTQ](https://arxiv.org/abs/2210.17323), [OmniQuant](https://arxiv.org/abs/2308.13137), QuIP, SpinQuant, LLM.int8(), [ZeroQuant](https://arxiv.org/abs/2206.01861), AWQ, Krishnamoorthi, [Marchisio](https://arxiv.org/abs/2407.03211), [BitNet b1.58](https://arxiv.org/abs/2402.17764) | Q8_0 vs 4-bit for Gemma 3 270M and 1B. What to measure |
| J4: Low-bit weight-only PTQ and what maps onto GGUF | GPTQ, AWQ, SpQR, OmniQuant, ZeroQuant, [AQLM](https://arxiv.org/abs/2401.06118), QuIP#, QuaRot, SpinQuant | Which ideas `llama-quantize` + `llama-imatrix` already cover. Which methods to skip because llama.cpp cannot load them |
| J5: QAT: what this folder adds | [LLM-QAT](https://arxiv.org/abs/2305.17888), SpinQuant (Table 1), ZeroQuant (LKD), Krishnamoorthi, Nagel | Whether to start from Gemma's QAT Q4_0 checkpoint or run our own short QAT |
| J6: Ternary models | [BitNet](https://arxiv.org/abs/2310.11453), BitNet b1.58, [BitNet 2B4T](https://arxiv.org/abs/2504.12285) | Whether BitNet 2B4T is a base-model alternative (it is not a PTQ option for Gemma) |
| J7: Multilingual and math damage; calibration language | Marchisio, [Chimoto](https://arxiv.org/abs/2601.18306), AWQ (§5.3, Table 8), AQLM (App. K), ZeroQuant (§5.2) | What text to feed `llama-imatrix`. Which eval slices show quantization damage |

## J1: Foundations: grids, granularity, PTQ vs QAT

**Question.** What do we need from the classic papers to read GGUF types and the LLM papers? Which choice matters most at 4 bits: the grid, the granularity or the rounding algorithm?

**How the papers relate.** Jacob defines the affine scheme and integer-only inference. Krishnamoorthi and Nagel build PTQ and QAT recipes for CNNs on it. Gholami surveys the space. They agree on the basics. They differ only on per-tensor vs per-channel defaults, which depend on the hardware.

**Key evidence.**

- *Affine grid.* Real value r = S(q − Z), with scale S and zero-point Z. Zero must be exactly representable (Jacob §2.1, Eq. 1). Products accumulate in int32 (Jacob Fig. 1.1).
- *Symmetric weights, asymmetric activations.* An asymmetric weight times an asymmetric activation adds a data-dependent term at inference. So the common choice is symmetric weights and asymmetric activations (Nagel §2.4.1, Eq. 13).
- *Granularity beats everything else at low bits.* Weight-only 8-bit PTQ of MobileNet-v1 gives top-1 scores (Krishnamoorthi Table 2 and its caption): per-layer asymmetric 0.001, symmetric per-channel 0.591, asymmetric per-channel 0.704, float 0.709. The prose sentence next to the table says the opposite. This note ignores that sentence. Gholami calls group-wise "a good compromise" between resolution and overhead (§III.E).
- *4 bits needs more than 8 bits.* Nagel's standard PTQ pipeline keeps W8A8 within 0.7% of float for all models. But W4A8 per-tensor drops EfficientDet-D1 from 40.08 to 0.31 mAP (mean average precision, a detection score). Per-channel restores it to 35.08 (§3.6, Table 6).
- *Rounding to nearest is not optimal.* For one ResNet18 layer at 4 bits, the best of 100 stochastic roundings beats round-to-nearest by more than 10% (Nagel §3.4). This is the idea behind AdaRound, GPTQ and QuIP's adaptive rounding (J4).
- *Bigger models tolerate quantization better* (Krishnamoorthi §3.1.3 obs. 3, §8). J3 tests this for LLMs.
- *Integer dot products without dot-product instructions.* On ARM NEON, Jacob multiplies int8 × int8 with SMULL, then SMLAL, then a pairwise add into int32 accumulators (SADALP). Accumulating two products in int16 first works because weights never take the value −128 (App. B). Jacob avoids lookup tables, which "tend to perform poorly" on SIMD (§2.1). T-MAC later argues the opposite (inference folder, J5).
- *Real speedups on phone cores.* 8-bit COCO detection on a Snapdragon 835 LITTLE core: 778 → 687 ms at depth multiplier 100%. At 50%: 270 → 146 ms (Jacob Table 4.4). 8-bit gives 2–3× on a CPU (Krishnamoorthi §6, §8).
- *Simulated (fake) quantization* stores low-bit weights and computes in floating point. Gholami says it can be acceptable for bandwidth-bound workloads (§IV.A).

**Negative results and limits.**

- All four papers are about CNNs (plus BERT in Nagel). None covers decoder LLMs, group sizes like 32, or GGUF.
- Jacob's CPU numbers are for phone cores from 2017 and per-tensor quantization (§2.1). They show what int8 buys on in-order ARM cores. They do not predict LLM decode speed.
- The Nagel AdaRound example is one layer of one CNN.

**What this means on the UNO Q.**

- *How to read GGUF types with these terms.* Q4_0 = blocks of 32 weights with one FP16 scale, about 4.5 bits per weight. Q8_0 = 8-bit blocks. K-quants = mixed-precision "super-block" recipes ([CHALLENGE_CONTEXT §4](../../../CHALLENGE_CONTEXT.md#4-quantization-marti-do-this-first)). So Q4_0 is group-wise with group size 32: finer than the per-channel or g128 settings used in almost every paper here. Whether Q4_0 stores a zero-point, and how K-quants store their scales, is not in the repo docs (see [Open questions](#open-questions)).
- *Activations.* At inference, llama.cpp multiplies packed weights by activations quantized on the fly ([CHALLENGE_CONTEXT §4](../../../CHALLENGE_CONTEXT.md#4-quantization-marti-do-this-first)). In the llama.cpp source at the pinned commit `2cbe0ec`, Q4_0 and Q8_0 weights pair with Q8_0 activations, in blocks of 32 values. K-quants pair with Q8_K activations, in blocks of 256 values. So the board runs W4A8 or W8A8 with per-block activation scales.
- *The A53 multiply path.* The A53 lacks SDOT/UDOT. We checked this on our board: `/proc/cpuinfo` shows no `asimddp` flag ([UNO Q board reference §14.2](../../../UNO_Q_BOARD_REFERENCE.md#142-cpu-flags-answers-an-open-question)). Without them, an int8 dot product needs the multi-instruction SMULL/SMLAL/SADALP sequence that Jacob App. B describes. Whether the pinned llama.cpp ARM kernels use that exact sequence is an open question. So is whether decode on the board is partly compute-bound: this is not measured on our board (see [Open questions](#open-questions)). The [inference synthesis](../inference/_synthesis.md) discusses it in [J1](../inference/_synthesis.md#j1-where-the-time-goes-prefill-vs-decode) and [J5](../inference/_synthesis.md#j5-low-bit-cpu-kernels-without-dot-product-instructions).
- *Debugging recipe.* Nagel's flow (§3.7) maps onto llama.cpp in three steps. First, compare F16 GGUF to the HF model. Then try a higher-precision type for all tensors. Then find the sensitive tensors and keep them at higher precision. K-quant "_M" recipes are a preset version of that last step ([CHALLENGE_CONTEXT §4](../../../CHALLENGE_CONTEXT.md#4-quantization-marti-do-this-first) calls them mixed-precision).

**Open questions.**

- Does Q4_0 use a symmetric grid? Does Q4_K store quantized sub-block scales? Read the pinned `ggml` quant code.
- Which tensors does Q4_K_M keep at higher precision for Gemma 3?

## J2: Outliers at W4A8 with block scales

**Question.** LLM papers fight outliers in activations and weights. On the board, weights are 4 or 8 bits and activations are 8 bits with one scale per block. A block is 32 values for Q4_0 and Q8_0 weights, and 256 values for K-quants (llama.cpp at `2cbe0ec`). Which outlier fixes still matter?

**How the papers relate.** LLM.int8() finds the activation outliers. SmoothQuant moves them into the weights so that W8A8 works. AWQ uses the same activation statistics to protect salient weight channels in weight-only 4-bit. SpQR finds outliers in the weights themselves and stores them sparsely.

Two lines then remove outliers by rotation. QuIP and QuIP# make weights "incoherent" (no weight much larger than the others) with random orthogonal or Hadamard matrices (weight-only). QuaRot and SpinQuant rotate the residual stream so that 4-bit activations and KV cache also work. SpinQuant learns the rotations that QuaRot draws at random.

| Method | Quantizes | Outlier mechanism |
|---|---|---|
| LLM.int8() | W8A8 | fp16 matmul for the outlier feature dimensions |
| SmoothQuant | W8A8 | per-channel scale moved from activations to weights |
| AWQ | weights only (W4/W3) | per-channel scale-up of salient weight channels, found from activations |
| SpQR | weights only (3–4 bits) | < 1% unstructured fp16 outlier weights + small groups |
| QuIP / QuIP# | weights only (2–4 bits) | random orthogonal / randomized Hadamard transform (online at inference) |
| QuaRot | W4A4KV4 | Hadamard rotations, some online |
| SpinQuant | W4A8 or W4A4, KV | learned rotations. The "no_had" variant merges them into the weights |

**Key evidence.**

- *Activation outliers are few, fixed and critical.* At most 7 feature dimensions hold the outliers up to 13B. Zeroing them drops top-1 softmax probability from about 40% to about 20% and raises perplexity by 600–1000% (LLM.int8() §4.2). They spread to all layers suddenly between 6B and 6.7B parameters. Measured against perplexity, emergence is smooth, so the authors tie it to perplexity, not size (§4.2 points 1, 2, 4).
- *Per-channel activation scales fix them. Per-token scales do not.* OPT-6.7B average accuracy: FP16 64.9%, INT8 per-token 42.5%, INT8 per-channel 64.8% (SmoothQuant Table 1). Outlier channels are about 100× larger than the rest and stay in the same channels across tokens (§3).
- *Weights are easy, activations are hard* (SmoothQuant §3 point 1). In BitNet's PTQ comparison at 6.7B, weight-only 4-bit methods beat weight-and-activation 4-bit methods. The authors say this is "mainly because the activation is more difficult to quantify" (BitNet §4.2, Table 3).
- *Activation magnitude, not weight magnitude, marks the salient weights.* OPT-1.3B, INT3 g128 WikiText perplexity: FP16 14.62, RTN 119.00. Keeping the 1% of channels with the largest activations in FP16 gives 16.91. Keeping the 1% largest by weight norm gives 98.55 (AWQ Table 1).
- *Weight outliers exist too.* SpQR finds weight-error outliers along both input and output dimensions, in short segments (§1, §3). SpQR keeps < 1% outliers and uses groups of 16 whose statistics are themselves quantized to 3 bits. It stays within 1% of FP16 perplexity at 4.63–4.71 bits on LLaMA 7B–65B (Table 1).
- *Rotation removes outliers without changing the FP output.* QuaRot fuses randomized Hadamard transforms into the weights and keeps some online. It reaches W4A4KV4 on LLaMA2-70B with at most 0.47 WikiText-2 perplexity loss (Abstract). Random rotations vary: up to 13 points of zero-shot accuracy between seeds (SpinQuant Abstract, Fig. 4).
- *Rotation helps weight-only quantization too, but mostly below 4 bits.* In QuaRot's weight-only ablation (per-column, asymmetric), LLaMA2-7B A16W4: RTN 6.99, GPTQ 8.25, QuaRot-RTN 6.76, QuaRot-GPTQ 5.60 (baseline 5.47) (App. A.4, Table 7).

**Negative results and limits.**

- *GPTQ can lose to RTN.* In the same QuaRot table, per-column GPTQ at W4 (8.25) is worse than RTN (6.99) on LLaMA2-7B (Table 7).
- *Group-wise scaling has a side effect.* In Marchisio, group-wise W4 recovers most of the loss of per-column W4, but it "is actively damaging" for cross-lingual language confusion (§4.5, Table 6).
- *SmoothQuant can hurt math.* On the 103B model, W8A8 with SmoothQuant "harms MGSM (Multilingual Grade School Math) scores slightly" (Marchisio §4.5).
- *Online transforms cost time.* QuIP is about 1.5× slower than OPTQ (GPTQ) per token on an A6000 (QuIP Table 4). SpinQuant's online Hadamard adds about 8% latency on an M1 Pro CPU (§4.5).
- All outlier evidence comes from 1.3B–175B models. None of these papers analyzes a model below 1B or the Gemma 3 family.

**What this means on the UNO Q.**

- *Activation side: probably not the bottleneck, but untested.* At `2cbe0ec`, llama.cpp's activation scale is per block of 32 values (Q4_0 and Q8_0 weights) or 256 values (K-quants). Both are finer than the per-token scale that fails in SmoothQuant Table 1. An outlier channel can only spoil the scale of its own block. *Hypothesis, not a finding:* at 1B, A8 with block scales costs little, so SmoothQuant-, QuaRot- and SpinQuant-style activation fixes are not needed. Test it: compare F16 GGUF with Q8_0 on our eval. If Q8_0 already loses accuracy on math, look at the activation side.
- *Weight side: this is where calibration helps.* AWQ's finding (activation magnitude marks the important weights) is what an importance matrix computed from calibration activations is for. [CHALLENGE_CONTEXT §4](../../../CHALLENGE_CONTEXT.md#4-quantization-marti-do-this-first) lists the importance matrix as an option, computed on math-tutoring calibration text. How `llama-quantize` uses the matrix is not in the repo docs (see [Open questions](#open-questions)). If it weights rounding error by activation magnitude, it captures AWQ's signal without AWQ's channel scaling.
- *Skip W4A4 and KV4 machinery* (QuaRot, SpinQuant_had). The board does not run 4-bit activations. KV-cache quantization is in [inference J2](../inference/_synthesis.md#j2-kv-cache-size-reuse-eviction-quantization).
- *SpinQuant_no_had is the one rotation method that needs no new kernel.* It merges its rotations into the weights, "necessitating no modification to the forward pass" (§4.2). In principle the rotated FP16 checkpoint could be converted to GGUF and quantized as usual. No paper here tests whether Gemma 3's normalization layout allows merging the residual rotation. Settle it before investing time (see [Open questions](#open-questions)). Low priority, because its gains are largest when activations are 4-bit (Table 1).

**Open questions.**

- Does Gemma 3 1B have LLM.int8()-style outlier feature dimensions? Dump activation maxima per channel on our calibration text.
- Does Q8_0 (W8A8 with block scales) lose any accuracy against F16 on Kangaroo math?

## J3: Do small models quantize worse?

**Question.** Our models are 270M and 1B. The LLM papers mostly report 7B and up. What do the smallest reported models say about 3–4 bits?

**How the papers relate.** Most papers agree that relative loss grows as models shrink (GPTQ, OmniQuant, Marchisio, Krishnamoorthi, SpQR's abstract). SpinQuant's LLaMA-3.2 1B rows partly contradict that. One model (OPT-1.3B) is an outlier that breaks under plain per-row rounding in three papers. Much of the size effect shrinks with finer groups, but SpinQuant's 1B and 3B rows remain mixed.

**Key evidence.** WikiText-2 perplexity unless noted.

- *GPTQ, 4-bit per-row (OPT).* 125M: 27.65 → 37.28 (RTN) / 31.12 (GPTQ). 350M: 22.00 → 25.94 / 24.24. 1.3B: 14.63 → 48.17 / 15.47. 175B: 8.34 → 10.54 / 8.37 (Table 3). BLOOM-560M: 22.42 → 25.90 / 24.03 (Table 4). The authors: "larger models generally (with the exception of OPT-66B) appear easier to quantize" (§5).
- *GPTQ, 3-bit.* OPT-125M: 53.85, OPT-1.3B: 20.97 (Table 3). Three bits roughly doubles the 125M model's perplexity.
- *Group size rescues the smallest model.* OPT-125M at W4: per-channel RTN 37.28 vs g128 RTN 30.47, and OmniQuant 29.45 vs 28.86. At 6.7B, g128 RTN is already close: 10.86 → 11.03 (OmniQuant App. A8, Table A20). The parsed table merges the g128 GPTQ cells for 1.3B–6.7B, so this note does not use them.
- *QuIP, OPT-1.3B.* FP16 14.62. W4: QuIP 14.88, OPTQ 15.59, nearest rounding 47.62. W3: QuIP 16.21, OPTQ 21.35. W2: QuIP 41.64, OPTQ 7,856 (Supplement C, Table 11).
- *SpinQuant, W4A8 (KV16) on LLaMA-3.2.* The parsed Table 1 lists seven (zero-shot avg, Wiki) pairs in this order: LLaMA-2 7B, 13B, 70B, LLaMA-3.2 1B, 3B, LLaMA-3 8B, Mistral-7B. We checked the order against the §4.2 prose (Mistral +10.5 and LLaMA-3 8B +4.1 points). The table below gives zero-shot average / Wiki perplexity.

| Model | FP16 | RTN | GPTQ | SpinQuant_no_had |
|---|---|---|---|---|
| LLaMA-3.2 1B | 56.9 / 13.4 | 55.4 / 20.7 | 55.0 / 17.3 | 56.0 / 15.3 |
| LLaMA-3.2 3B | 63.9 / 10.7 | 58.6 / 29.0 | 58.7 / 25.2 | 61.4 / 11.6 |
| LLaMA-2 7B | 66.9 / 5.5 | 62.4 / 7.9 | 64.9 / 20.2 (as printed) | 65.7 / 5.8 |

- *Our reading of the SpinQuant rows:* 1B loses only 1.5 zero-shot points under RTN, less than 7B (4.5) and 3B (5.3). But its perplexity rises 54%. 3B's perplexity rises 171%. A 1B model near chance on these tasks has less accuracy to lose, so small zero-shot drops do not prove robustness.
- *8-bit is safe if the grid is fine.* OPT-125M C4 perplexity 25.65: per-tensor int8 absmax gives 87.76, vector-wise zero-point int8 gives 25.72 (LLM.int8() Table 1, rows realigned from a garbled parse). Granularity, not bit-width, broke the 125M model.
- *ZeroQuant, GPT-3-style 350M, W4 FFN (feed-forward network) / W8 attention:* plain PTQ collapses (perplexity 1.76e5, FP16 21.5). Group-wise ZeroQuant gives 88.6. With layer-by-layer distillation, 30.6 (Table 4). Accuracy tasks hide this: at W8A8, PTQ loses 1.1% average accuracy but 4.7 perplexity points (§5.2).
- *Marchisio, 8B–103B.* At W4-g, 103B and 35B lose 0.9% and 2.8% on average, and 2.9% vs 13.1% on MGSM. Aya 23 35B / 8B lose 2.9% vs 3.7% (§4.4, Tables 1–2).
- *Ternary is worse below 3B.* BitNet b1.58 vs FP16 LLaMA at equal size and data: 700M perplexity 12.87 vs 12.33 and zero-shot 44.3 vs 45.5. It matches only "starting from a 3B size" (Tables 1–2, §3).
- SpQR names the 1–10B range as the one where 3–4-bit quantization "usually leads to moderate-to-high accuracy losses" (Abstract).

**Negative results and limits.**

- No paper here quantizes a model under 125M or any Gemma 3 model. OPT/BLOOM are 2022 models trained on far fewer tokens than Gemma 3. LLM.int8() ties outliers to perplexity rather than size (§4.2), so a heavily trained 1B model may behave differently from OPT-1.3B.
- OPT-1.3B breaks under per-row RTN in three papers (GPTQ Table 3, OmniQuant Table A20, QuIP Table 11). Treat it as one odd model, not a size law.
- Almost all small-model numbers are perplexity. Only ZeroQuant and SpinQuant give task accuracy, and none gives math or generation quality.

**What this means on the UNO Q.**

- *Expect a larger relative loss at 4 bits than the 7B papers report, and do not trust perplexity alone.* Group size matters more than the algorithm for small models. Q4_0's groups of 32 are finer than g128, which helps us. *Inference, not tested:* the papers measure the gains of GPTQ/AWQ over per-channel or g128 RTN. So these gains probably overstate what an importance matrix adds on top of Q4_0 or Q4_K.
- *Gemma 3 270M: start with Q8_0.* [CHALLENGE_CONTEXT §2](../../../CHALLENGE_CONTEXT.md#2-target-hardware-arduino-uno-q) gives about 0.25–0.3 GB for 270M at Q4_0. *Our arithmetic:* 270M weights at about 4.5 bits (Q4_0, [CHALLENGE_CONTEXT §4](../../../CHALLENGE_CONTEXT.md#4-quantization-marti-do-this-first)) would be about 0.15 GB. At about 8 bits (Q8_0, [BOARD_SETUP step 4](../../../BOARD_SETUP.md#step-4-download-the-models)), they would be about 0.27 GB. The documented Q4_0 size is close to the 8-bit size. This suggests that the embedding table (about 170M of the 270M parameters, [CHALLENGE_CONTEXT §3](../../../CHALLENGE_CONTEXT.md#3-base-model-candidates)) is not stored at 4 bits. The tensor types still need a check with a GGUF dump (see [Open questions](#open-questions)). Either way, 4 bits saves little RAM at 270M, and the small-model evidence argues against it. If Q8_0 is too slow or too large, compare it with Google's official 270M QAT Q4_0 checkpoint ([CHALLENGE_CONTEXT §3](../../../CHALLENGE_CONTEXT.md#3-base-model-candidates)), not with a PTQ Q4_0.
- *Gemma 3 1B: measure, in this order.* Q8_0 (quality reference) → Gemma QAT Q4_0 (J5) → Q4_K_M with our importance matrix (J7) → plain Q4_0. Skip 3-bit and 2-bit K-quants: every small-model 3-bit number above at least doubles the loss of 4-bit.
- *Speed is not settled by bits.* The board hint that Q8_0 decoded faster than Q4_K_M, and the `llama-bench` test to settle it, are in [inference J1](../inference/_synthesis.md#j1-where-the-time-goes-prefill-vs-decode). Pick the type by measured accuracy, prefill and decode tok/s, and RAM together.
- *What to measure for each type:* accuracy and format-failure rate on the validation set by slice (J7). Also measure `llama-bench` pp and tg at 1–4 threads, peak RSS, and file size. Add perplexity on held-out Catalan/Spanish/English text only as a cheap first screen.

**Open questions.**

- How large is the loss from F16 to Q8_0 to Q4_K_M for Gemma 3 1B on our validation set, per language?
- How are `token_embd` and the (tied) output tensor quantized in each GGUF type for Gemma 3? At 270M they are most of the file.

## J4: Low-bit weight-only PTQ and what maps onto GGUF

**Question.** Which of the advanced PTQ methods can we use with the pinned llama.cpp? Which of their ideas are already in `llama-quantize` and `llama-imatrix`?

**How the papers relate.**

- GPTQ is the quantization branch of the Optimal Brain Compression lineage ([OBC](https://arxiv.org/abs/2208.11580), [pruning J1](../pruning/_synthesis.md#j1-unstructured-and-nm-sparsity-and-the-cpu-question)). It quantizes one column at a time and updates the remaining weights with inverse-Hessian information from calibration data (§4, Fig. 2).
- AWQ competes with GPTQ. It uses no backpropagation or reconstruction. It searches per-channel scales from average activation magnitudes, and argues this overfits the calibration set less (§1, §5.3).
- SpQR extends GPTQ with sparse outliers and quantized group statistics.
- OmniQuant learns clipping (LWC) and equivalent transforms (LET) block by block.
- ZeroQuant combines group-wise weights with layer-by-layer distillation.
- AQLM and QuIP# leave scalar grids for vector codebooks at 2–3 bits.

**Key evidence.**

- *At 4 bits with g128, the methods are close on 7B+.* Llama-2 7B INT4 g128 WikiText-2: FP16 5.47, RTN 5.73, GPTQ 5.69, AWQ 5.60 (AWQ Table 4). At INT3 g128 the gaps grow: RTN 6.66, GPTQ 6.43, AWQ 6.24. Math: Llama-2-7B GSM8K FP16 13.87, RTN 11.07, GPTQ 12.13, AWQ 13.57 (AWQ Table 8).
- *Calibration overfitting.* With a mismatched calibration domain (PubMed vs Enron), perplexity worsens by 0.5–0.6 for AWQ and by 2.3–4.9 for GPTQ. AWQ reaches good perplexity with 16 calibration sequences, where GPTQ needs 192 (AWQ §5.3, Fig. 8: OPT-6.7B, INT3 g128).
- *Cost.* GPTQ quantizes 1–3B models "in a matter of minutes" on one A100 (§5, Table 2). OmniQuant takes about 5× GPTQ's time (App. A4). Table 4 lists ZeroQuant-LKD on 350M at 1.1 hours, but the text says 3.1 hours (§5.2).
- *Bilevel quantization helps.* At the same footprint, groups of 16 with 3-bit statistics beat 16-bit statistics (LLaMA-65B Wiki 3.74 vs 3.84 at about 3.6 bits, SpQR Table 3).
- *2–3 bits needs codebooks and fine-tuning.* AQLM is Pareto-optimal around 2.5 bits: no other method there is both smaller and more accurate. A 4-bit Llama 2 7B (Wiki 5.21) beats the previous best 2-bit 13B (QuIP#, 6.06) while being smaller (AQLM §4.1). QuIP# 3-bit "outperforms a theoretical lossless 4 bit model" on Llama 2 (§6.2).
- *Codebook size decides speed.* AQLM's 1×16 codebooks take 1 MiB per layer, more than any GPU L1 cache. So AQLM 2-bit decodes slower than FP16 on an RTX 4090 (20.6 vs 33.1 tok/s), while QuIP# 2-bit reaches 106.3 (QuIP# §6.3, Table 6). AQLM's own CPU kernel switches to several small 8-bit codebooks. It runs "up to 4x faster" than FP32 on an 8-core Intel i9, at some accuracy cost (AQLM §4.4, Table 5).
- *Edge CPU data point.* AWQ's TinyChat runs a 7B model at 0.7 tok/s on a Raspberry Pi 4B (AWQ §5.4).

**Negative results and limits.**

- *Math falls fastest at 2 bits.* Llama-2-7B GSM8K: FP16 14.6, QuIP# 6.2, AQLM 5.3, both after end-to-end fine-tuning (AQLM App. K, Table 15).
- *GPTQ is not always better than RTN.* It was worse in QuaRot's per-column table (J2) and on LLaMA-7B at INT4 g128 (6.22 vs RTN 5.96, AWQ Table 4). It was also worse on VLM captioning at INT4 (AWQ Table 6: 32-shot drop −6.72 vs RTN −4.57).
- GPTQ's speedups come from reduced memory traffic, not fewer operations (§6). SpQR, QuIP# and OmniQuant measure speed on GPUs only. AWQ adds one Raspberry Pi 4B run, and AQLM's CPU test is on a desktop i9.
- Every result here is at 7B+ except the OPT/BLOOM rows (J3).

**What this means on the UNO Q.**

| Method | Weight-only? | Needs at inference | Loads in pinned llama.cpp? | Closest llama.cpp lever |
|---|---|---|---|---|
| RTN, group-wise (ZeroQuant scheme, baseline in GPTQ/AWQ) | yes | per-group scales | yes. Q4_0/Q8_0 are this kind of format (our reading, see [Open questions](#open-questions)) | `llama-quantize` |
| GPTQ | yes | standard grid, g128 | no importer in the repo docs | `llama-imatrix` (also driven by calibration activations) |
| AWQ | yes | per-channel scales folded into the previous op | the scaled FP16 model keeps its architecture, so conversion + `llama-quantize` is possible in principle. Folding for Gemma 3's norms is an open question | `llama-imatrix` |
| SpQR | yes | sparse fp16 outliers + bilevel groups | no (needs a sparse kernel) | K-quant super-blocks (quantized scales, an open question) |
| OmniQuant | both | learned clipping / transforms, absorbed | not directly. Grid and group size differ | none |
| ZeroQuant(-LKD) | both | custom fused kernels | no | none |
| AQLM | yes | multi-codebook decode | no (own kernels) | none |
| QuIP / QuIP# | yes | online orthogonal / Hadamard + E8P codebook | no | none |
| QuaRot | W+A+KV | online Hadamard | no | none |
| SpinQuant_no_had | W+A | nothing (rotations merged) | possibly, as a rotated FP16 checkpoint. Untested for Gemma 3 | none |

- *Practical levers inside the rules:* the quant type, the imatrix calibration text (J7), and the starting checkpoint (QAT, J5). [BOARD_SETUP step 3.1](../../../BOARD_SETUP.md#31-download-the-source-at-the-pinned-commit) pins one llama.cpp commit, so a fork with new kernels is a rules question (as in [inference J5](../inference/_synthesis.md#j5-low-bit-cpu-kernels-without-dot-product-instructions)).
- *Skip* AQLM, QuIP#, SpQR, QuaRot and OmniQuant for deployment. They need kernels llama.cpp does not have. AQLM's 1 MiB codebooks would also need to fit the A53's caches, whose sizes are not in the repo docs (see [Open questions](#open-questions)).
- *Optional experiment, low priority:* apply AWQ scaling or SpinQuant_no_had rotation to the fine-tuned FP16 weights, convert to GGUF, and compare with plain imatrix Q4_K_M. Do it only if Q4_K_M loses clearly more than Q8_0 on our eval.

**Open questions.**

- Does imatrix-weighted Q4_K_M already match what AWQ scaling would add for Gemma 3 1B? Only an A/B on our eval can say.
- Is any GPTQ/AWQ-to-GGUF converter part of the pinned llama.cpp? Not in the repo docs.

## J5: QAT: what this folder adds

**Question.** [Surveys J3](../surveys/_synthesis.md#j3-how-much-qat-costs) already covers Gemma 3's QAT. Gemma 3 used about 5,000 steps of self-distillation ([Gemma 3 report](https://arxiv.org/abs/2503.19786) §2.3). Surveys J3 sets two paths: fine-tune from the QAT checkpoint, or run a short QAT after our fine-tune. What does this folder add to that decision?

**How the papers relate.** LLM-QAT is the LLM version of Gemma's recipe: the full-precision model labels data and a fake-quantized copy learns to match it. ZeroQuant-LKD is a cheaper layer-by-layer variant. Krishnamoorthi and Nagel give the CNN-era QAT rules. SpinQuant provides the only third-party test of LLM-QAT on a 1B model.

**Key evidence.**

- *Self-generated data beats real text.* QAT on the model's own sampled text beats QAT on WikiText or C4. Sampling from the softmax beats top-1 generation. Making the first 3–5 tokens greedy and the rest sampled is best (LLM-QAT §2.1, §3.3.1, Table 3). 100k samples were enough (§1).
- *Logit distillation only.* Using the sampled next token as a hard label is worse than soft teacher logits. Adding attention or hidden-state distillation "actually hampers the performance" (§3.3.3, Table 5).
- *Keep outliers. Use symmetric MinMax.* Clipping-based quantizers give perplexity above 10,000 early in training. Symmetric MinMax per-channel weights work best for LLaMA (§2.2.2, §3.3.2, Table 4).
- *Results.* W4-A8-KV4 LLaMA-30B: 69.9 average zero-shot, 1.5 points under full precision, where all PTQ methods "produce poor results" (§3.2, Table 1). The authors recommend 4-bit QAT models over 8-bit models of similar size (§3.2).
- *Cheap partial alternative.* ZeroQuant-LKD trains one layer at a time against its unquantized self. Even random-token inputs cut the 350M model's perplexity from 92.1 to 40.6. Wikipedia text reaches 30.4, close to the original data (§5.6).
- *Match training to inference.* "It is critical to match quantized inference with the forward pass of training" (Krishnamoorthi §8).

**Negative results and limits.**

- *No gain at 1B in a third-party run.* SpinQuant ran LLM-QAT's public code on LLaMA-3.2 1B at W4A8: zero-shot 53.2 and Wiki 21.0, against RTN's 55.4 and 20.7 (SpinQuant Table 1). This is SpinQuant's run, not an LLM-QAT result.
- LLM-QAT tests only LLaMA 7B–30B base models with per-channel (not group-wise) weights, on an 8-GPU node (§1, §2.2.2). It leaves instruction-tuned and RL-tuned models to future work (§5). 4-bit activations did not work (§5).
- No paper here tests QAT on multilingual or math data.

**What this means on the UNO Q.**

- *Path 1 stays first* ([surveys J3](../surveys/_synthesis.md#j3-how-much-qat-costs)): fine-tune from Gemma's QAT checkpoint and export to Q4_0. Krishnamoorthi's rule adds a warning. Google trained the QAT checkpoint to match one target format. Re-quantizing it to Q4_K_M, or merging a LoRA trained in bf16 and re-quantizing, may lose the QAT benefit. Compare QAT-Q4_0 with PTQ Q4_K_M of the same fine-tune on our eval.
- *If we run our own short QAT (path 2):* use the fine-tuned bf16 model as teacher, with logit distillation only. Use the model's own sampled tutoring outputs as data (LLM-QAT recipe). The fake quantizer must reproduce llama.cpp's Q4_0 block rounding exactly. The Q4_0 rounding rule is still open (see [Open questions](#open-questions)). Settle it before writing the quantizer.
- *Do not expect QAT to rescue a 1B model by default.* The only 1B data point here shows no gain. Treat QAT as an experiment with a PTQ baseline beside it.

**Open questions.**

- Is a fine-tune of the QAT checkpoint still better than PTQ after LoRA merge and re-quantization?
- Does self-generated tutoring text in Catalan and Spanish keep its language under QAT, or does it drift to English?

## J6: Ternary models

**Question.** Are BitNet-style ternary models an option for the copilot? Can Gemma be turned ternary after training?

**How the papers relate.** BitNet introduces BitLinear with 1-bit weights and 8-bit activations, trained from scratch (§2). b1.58 adds 0 to the weight set {-1, 0, 1} with absmean scaling (§2, Eq. 1–3). 2B4T scales that to 2B parameters and 4T tokens and releases weights and a GGUF for bitnet.cpp (Abstract). All three need training from scratch. None is a PTQ method.

**Key evidence.**

- *PTQ cannot reach these bit-widths.* On a 6.7B model, weight-only GPTQ at 2 bits gives perplexity 1032 and QuIP at 2 bits 70.43. W1A8 BitNet trained from scratch gives 17.07, against 15.19 for FP16. Average zero-shot accuracy: BitNet 55.9, FP16 57.8, GPTQ 4-bit 52.9 (BitNet Table 3).
- *Small ternary models lag.* See J3: b1.58 matches FP16 only from 3B (b1.58 Tables 1–2).
- *2B4T vs Gemma-3 1B (instruct, all re-run by the authors, 2B4T Table 1).* The parsed Table 1 has its row labels shifted by one row. This note realigns the rows so that 2B4T's MMLU (53.17), GSM8K (58.38) and IFEval (53.48) match Table 2.

| Metric | Gemma-3 1B | BitNet 2B4T |
|---|---|---|
| Non-embedding memory | 1.4 GB | 0.4 GB |
| CPU decode latency (TPOT, time per output token) | 41 ms | 29 ms |
| GSM8K (4-shot) | 31.16 | 58.38 |
| MATH-500 (0-shot) | 42.00 | 43.40 |
| MMLU (5-shot) | 39.91 | 53.17 |
| IFEval (strict) | 66.67 | 53.48 |

- *Setup of that table.* The authors measured latency on an i7-13800H with 8 threads, 2B4T in bitnet.cpp and the others in llama.cpp. The paper does not give the llama.cpp quant type of the baselines (App. B).
- *2B4T vs INT4 PTQ of a similar model.* Qwen2.5 1.5B bf16 / GPTQ-int4 / AWQ-int4 / 2B4T: GSM8K 56.79 / 50.57 / 50.64 / 58.38. Non-embedding memory 2.6 / 0.7 / 0.7 / 0.4 GB (2B4T Table 2).

**Negative results and limits.**

- 2B4T "is primarily trained on English-centric data", and the authors list multilingual support as future work (§7). BitNet (2023) used an English corpus and a 16K vocabulary (§3.1). No Catalan or Spanish result exists.
- 2B4T uses the LLaMA 3 tokenizer (128,256 tokens), squared-ReLU FFNs and subln normalization (§2). Nothing transfers to a Gemma fine-tune.
- The memory figures exclude embeddings. The comparison with Gemma-3 1B mixes engines (bitnet.cpp vs llama.cpp).

**What this means on the UNO Q.**

- *Not a PTQ option for Gemma.* There is no ternary Gemma 3, and ternary needs pretraining from scratch.
- *2B4T as an alternative base model:* its English GSM8K is far above Gemma-3 1B's in the authors' own runs. But it runs in bitnet.cpp, a different engine. Two questions are in [inference J5](../inference/_synthesis.md#j5-low-bit-cpu-kernels-without-dot-product-instructions): whether llama.cpp's own ternary types reproduce it, and how far the speed claims transfer to an A53. Before any investment, run 2B4T on a handful of Catalan and Spanish validation-set problems on a laptop. Also ask the organizers whether the rules allow a non-llama.cpp engine.

**Open questions.**

- How good is 2B4T's Catalan and Spanish? Its math in those languages?
- Would its size (2B, embeddings not counted in 0.4 GB) fit next to the embedding server in the board's RAM? The total file size was not read here.

## J7: Multilingual and math damage; calibration language

**Question.** Quantization papers evaluate almost only in English. How much extra damage do Catalan, Spanish and math take? Which language and content should the `llama-imatrix` calibration text have? Which eval slices show the damage?

**How the papers relate.** Marchisio measures the damage across languages, tasks and evaluation methods, but quantizes with English calibration (128 English samples for GPTQ and SmoothQuant, §3). Chimoto changes only the calibration language. The two papers fit together: part of the damage that Marchisio finds may be due to the English-only calibration that Chimoto replaces. Neither paper tests this directly, since Marchisio never varies the calibration set. AWQ, AQLM and ZeroQuant add the math and generation side.

**Key evidence.**

- *Math degrades fastest.* MGSM at W4-g: 35B Command −13.1% (FP16 49.8 → 43.3), as low as −17.3% in Chinese. 103B: −2.9% (Marchisio Table 1, §4.2). Aya 23 8B at W4: −7.5% on MGSM (Table 2). In English, the same 35B W4-g loses only 2.2% on MGSM, against 12.2% for Latin-script languages (Table 5).
- *Even W8A8 can hurt math.* 35B W8A8: MGSM −5.5%, though its overall average rises 0.2% (Table 1).
- *Automatic metrics underestimate.* Automatic tasks show −0.3% (French) and −1.7% (Japanese). Human evaluators report −16.6% and −16.0% (Marchisio §1, Table 8). In Spanish, humans saw −4.6% at W4-g on the hard internal prompts and −1.4% on Dolly (Table 8). The difficult internal prompts dropped 5.7% on average, against 2.4% on Dolly (§4.7).
- *LLM/RM judges agree that W4 hurts on hard prompts.* LLM judge −25.9% for naive W4 on the internal set (Table 7). The LLM and RM judges sometimes disagree on direction (§4.6).
- *Language and script.* Non-Latin scripts lose more: 103B −0.7% (Latin) vs −1.9% (non-Latin), 8B −3.0% vs −3.7% (§1). Loss correlates with a language's data size in mC4, more strongly at W4 (R² = 0.63) than at W8 (R² = 0.24) (§4.3, Fig. 2).
- *Calibration language matters, most for GPTQ.* Llama3.1 8B, 4-bit g128, average Wikipedia perplexity over 10 languages: FP16 15.816, uniform INT4 19.647. GPTQ: English calibration 21.624, balanced 10-language mix (multi10) 18.104, multi10 + code + math 17.910. AWQ: English 14.879, multilingual 14.639, math + multilingual 14.623 (Chimoto Table 2). GPTQ swings by up to 3.52 points across calibration sets, AWQ by about 0.35 (§4, Fig. 2).
- *Why.* Multilingual and math/code mixes contain more rare tokens, numerals and symbols, which produce longer activation tails. Single-language sets can have a narrower activation range than test data, so the quantizer clips (Chimoto Fig. 5, Fig. 6).
- *Downstream follows, with smaller margins.* GPTQ-quantized Llama3.1 8B, Global MMLU: English calibration 48.90 ± 1.07, multi10 50.20 ± 1.09 (Chimoto Table 1).
- *Authors' guidelines:* a balanced multilingual set for GPTQ, with code/math added. Language-matched calibration for AWQ when one language dominates, with a multilingual fallback (Chimoto §5).
- *Generation hides more than accuracy tasks.* ZeroQuant §5.2 (perplexity 4.7 points vs accuracy 1.1%). AWQ at INT4 g128 keeps Llama-2-7B GSM8K at 13.57 vs 13.87 (Table 8). At 2 bits, GSM8K more than halves (AQLM Table 15).

**Negative results and limits.**

- *English-calibrated GPTQ was worse than plain uniform INT4* on the 10-language average (21.624 vs 19.647, Chimoto Table 2). Two single-language sets also did worse than English: French under AWQ and Swahili under GPTQ (§4).
- In Chimoto Table 2, several AWQ perplexities are lower than FP16 (for example Swahili 5.936 vs 6.510). The paper does not explain this. Read the table as relative rankings.
- Chimoto evaluates mainly perplexity, on two 7–8B models, and has no Spanish or Catalan (Limitations, §3.4). Marchisio covers 8B–103B, includes Spanish but not Catalan, and calibrates only in English.
- Global MMLU differences in Chimoto Table 1 are about one standard error, except the Swahili calibration.

**What this means on the UNO Q.**

- *Calibration text, A/B test and eval slices.* The steps are in [What to try](#what-to-try). They are a recommendation built from Chimoto's guidelines, untested on imatrix.

**Open questions.**

- Does a Catalan-heavy imatrix help Catalan accuracy measurably at Q4_K_M, or only perplexity?
- How large is the human-visible loss in Catalan tutoring explanations at Q4 vs Q8? No paper here has Catalan.

## Papers not covered by any junction

None.

## What to try

### Build the `llama-imatrix` calibration text

These steps come from [J7](#j7-multilingual-and-math-damage-calibration-language). They are a recommendation built from Chimoto's guidelines, untested on imatrix.

1. Use equal shares of Catalan, Spanish and English (the multi10 idea, applied to our three languages).
2. Add math-heavy text with numerals, operators and symbols in all three languages (the math-/codemath- variants).
3. Format part of it like real inputs: our chat template, a problem, and a tutoring explanation. AWQ's same-distribution calibration was best (Fig. 8b), and LLM-QAT found the model's own outputs best for QAT (Table 3).
4. Add general Catalan/Spanish text (for example Wikipedia). This keeps the activation range from being narrower than at inference (Chimoto Fig. 6).

*Sources and the red line.* Problem-like text may come from the M3Kang **training split, used locally** ([dataset card](https://huggingface.co/datasets/qualcomm/M3Kang)). It may also come from the fine-tuned model's own explanations of those problems. Never use validation-set problems.

A calibration file built from M3Kang counts as derived data. Follow these rules for it:

- Keep it under `data/` (git-ignored, covered by the M3Kang guard).
- Never commit it.
- Never quote it.
- Never paste it into docs.

[CLAUDE.md](https://github.com/Sigkaio636/Santolina_tutor/blob/main/CLAUDE.md) lists `data/` and extensions such as `*.jsonl` for the guard. The guard might not catch a `.txt` saved elsewhere.

### A/B test the calibration language

Build Q4_K_M twice from the same fine-tune. Use an imatrix from English-only text for one build. Use an imatrix from the ca/es/en + math mix for the other. Give both the same token budget. Whether imatrix behaves like GPTQ (sensitive) or AWQ (less sensitive) to calibration language is unknown. Compare per-language accuracy, not the average.

### Eval slices to watch after every quantization step

- Per language on the same problem IDs (Catalan, Spanish, English), as [benchmarks J2](../benchmarks/_synthesis.md#j2-language-effects-catalan-spanish-english) defines.
- Text-only problems by topic, with Arithmetic and Algebra as the math-heavy slices ([benchmarks J4](../benchmarks/_synthesis.md#j4-modality-level-and-topic-confounds-which-slices-to-report)).
- Format-failure rate ([benchmarks J3](../benchmarks/_synthesis.md#j3-small-models-and-answer-format-failure)).
- The language of the explanation: does a Catalan question still get a Catalan answer? Group-wise scaling hurt cross-lingual language confusion in Marchisio (§4.5).
- A small human or LLM-judge check of explanations per language. Accuracy and perplexity underestimate damage that readers see (Marchisio §4.7). [LLM-KICK](https://arxiv.org/abs/2310.01382), in [pruning J5](../pruning/_synthesis.md#j5-what-pruning-breaks), makes the same point for compressed models in general.

## Open questions

The repo docs do not settle these questions. Each one names the junctions that raise it.

- **Decode bound.** Is decode on the board memory-bandwidth-bound or partly compute-bound? [CHALLENGE_CONTEXT §9](../../../CHALLENGE_CONTEXT.md#9-open-questions-todo-checklist) lists it as open. The [inference synthesis J1](../inference/_synthesis.md#j1-where-the-time-goes-prefill-vs-decode) gives a hint that it is partly compute-bound. This is not measured on our board (J1).
- **ARM kernels.** Do the pinned llama.cpp ARM kernels use Jacob's SMULL/SMLAL/SADALP sequence for int8 dot products (J1)?
- **Q4_0 and K-quant storage.** Does Q4_0 store a zero-point? How do K-quants store their scales: are the super-block scales themselves quantized (J1, J4)?
- **Q4_0 rounding.** Is `llama-quantize` without an importance matrix plain round-to-nearest? What exact rounding rule does Q4_0 use? A fake quantizer for our own QAT must reproduce it (J4, J5).
- **Importance matrix.** How does `llama-quantize` use the matrix from `llama-imatrix`? Read the `imatrix` tool's README and source in the pinned llama.cpp (J2).
- **Gemma 3 norms.** Does Gemma 3's normalization layout allow merging SpinQuant's residual rotation, or folding AWQ scales, into the weights (J2, J4)?
- **Tensor types at 270M.** Which GGUF type does each tensor get in a Gemma 3 270M Q4_0 file? Check with a GGUF dump whether the file stores the embedding table at 4 bits (J3).
- **A53 caches.** What are the A53's cache sizes? AQLM's 1 MiB codebooks would need to fit in them (J4).

## Links to other folders

- J1, J3 (decode speed vs bit-width on the A53, `llama-bench` test): [inference synthesis J1](../inference/_synthesis.md#j1-where-the-time-goes-prefill-vs-decode). J1, J6 (LUT kernels, bitnet.cpp): [T-MAC](https://arxiv.org/abs/2407.00088), [bitnet.cpp](https://arxiv.org/abs/2410.16144), and [inference synthesis J5](../inference/_synthesis.md#j5-low-bit-cpu-kernels-without-dot-product-instructions).
- J2 (KV-cache quantization, not covered here): [KIVI](https://arxiv.org/abs/2402.02750) and [inference synthesis J2](../inference/_synthesis.md#j2-kv-cache-size-reuse-eviction-quantization).
- J4 (GPTQ lineage): [Optimal Brain Compression](https://arxiv.org/abs/2208.11580) and [pruning synthesis J1](../pruning/_synthesis.md#j1-unstructured-and-nm-sparsity-and-the-cpu-question).
- J3, J7 (compressed models fail first on knowledge and hard tasks, quantization vs pruning): [LLM-KICK](https://arxiv.org/abs/2310.01382) and [pruning synthesis J5](../pruning/_synthesis.md#j5-what-pruning-breaks).
- J3 (Gemma 3 270M embedding share, vocabulary trimming): [pruning synthesis J6](../pruning/_synthesis.md#j6-vocabulary-trimming-for-gemma-3s-256k-vocabulary).
- J5 (Gemma 3 QAT checkpoints and QAT cost): [Gemma 3 report](https://arxiv.org/abs/2503.19786) and [surveys synthesis J3](../surveys/_synthesis.md#j3-how-much-qat-costs). QLoRA as a training-memory technique: [QLoRA](https://arxiv.org/abs/2305.14314).
- J6 (alternative small bases): [MobileLLM](https://arxiv.org/abs/2402.14905) (inference) and [surveys synthesis J2](../surveys/_synthesis.md#j2-base-model-gemma-3-vs-salamandra-2b).
- J7 (eval slices, language comparison on shared IDs, format failures): [M3Kang](https://arxiv.org/abs/2601.16218) and [benchmarks synthesis](../benchmarks/_synthesis.md) [J2](../benchmarks/_synthesis.md#j2-language-effects-catalan-spanish-english)–[J4](../benchmarks/_synthesis.md#j4-modality-level-and-topic-confounds-which-slices-to-report). Dataset: [M3Kang dataset card](https://huggingface.co/datasets/qualcomm/M3Kang).
