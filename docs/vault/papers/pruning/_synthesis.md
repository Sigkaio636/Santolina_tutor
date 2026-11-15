---
tags: [synthesis, pruning]
papers: 17
date: 2026-11-14
---
# Pruning: synthesis by junction

This note is an explanation for the team members who decide whether to prune the copilot's language model. It sums up what 17 pruning papers mean for the UNO Q. The note groups the papers by junction: one question that several papers answer together (see the [glossary](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md)).

The copilot's deployed language model is Qwen3.5 0.8B Q8_0 ([`config.env`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/config.env)). The fine-tune base is not chosen yet. Gemma 3 is one option that the team explores, so the advice below targets Gemma 3 270M and 1B.

Pruning removes weights from a trained model. There are three kinds (see the [glossary](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md)):

- *Unstructured* pruning sets single weights to zero. The matrices keep their shape.
- *N:M* (semi-structured) sparsity sets N weights to zero in every block of M weights. In 2:4 sparsity, 2 of every 4 weights are zero.
- *Structured* pruning removes whole rows and columns, attention heads or layers. The result is a smaller dense model.

Most quality numbers below are perplexity: how well a model predicts a reference text. Lower is better.

For the copilot, this folder mostly argues against pruning:

- Unstructured and 2:4 sparsity give no gain in llama.cpp.
- Retraining-free structured methods either lose too much, or produce shapes that standard GGUF may not hold.
- The structured methods that work (Sheared LLaMA, Minitron) needed billions of recovery tokens on GPU clusters, at 7B scale and above.
- In these papers, small models, math and long generation degrade first.

Two things are worth trying:

- Vocabulary trimming after fine-tuning, for Gemma 3 270M. Embeddings are about 170M of its 270M parameters.
- Only for Gemma 3 1B, and only if quantized speed is not enough: uniform pruning of the feed-forward network (FFN) width. Uniform means that every layer loses the same number of FFN channels. Recover with [logit distillation](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) from the fine-tuned 1B.

Always compare the result against dense Gemma 3 270M, scored on generated explanations.

## Junctions at a glance

| Junction | Papers | Decision it informs |
|---|---|---|
| J1: Unstructured and N:M sparsity, and the CPU question | [OBC](https://arxiv.org/abs/2208.11580), [SparseGPT](https://arxiv.org/abs/2301.00774), [Wanda](https://arxiv.org/abs/2306.11695), [Deep Compression](https://arxiv.org/abs/1510.00149), [Movement Pruning](https://arxiv.org/abs/2005.07683) | Whether any zero-weight sparsity (unstructured, 2:4) is worth doing for a llama.cpp/GGUF model on a Cortex-A53 |
| J2: Retraining-free structured pruning: criterion and output shape | [FLAP](https://arxiv.org/abs/2312.11983), [SliceGPT](https://arxiv.org/abs/2401.15024), Wanda-sp (in FLAP), [LLM-Pruner](https://arxiv.org/abs/2305.11627) (before tuning) | Which importance score to rank FFN channels/heads with, and whether the pruned model stays a standard Gemma 3 config |
| J3: Structured pruning with recovery: data and compute | LLM-Pruner, [Sheared LLaMA](https://arxiv.org/abs/2310.06694), [Minitron](https://arxiv.org/abs/2407.14679), [Minitron in practice](https://arxiv.org/abs/2408.11796), Wanda §5, SliceGPT (recovery fine-tuning, RFT) | LoRA vs distillation vs continued pre-training after pruning, how many tokens, which teacher |
| J4: Depth pruning vs width pruning | [ShortGPT](https://arxiv.org/abs/2403.03853), [Gromov 2024](https://arxiv.org/abs/2403.17887), Minitron, Minitron in practice | Drop layers or narrow the FFN, which layers, how to heal |
| J5: What pruning breaks | [LLM-KICK](https://arxiv.org/abs/2310.01382), ShortGPT, Gromov 2024, Minitron in practice, Sheared LLaMA, SparseGPT, Wanda, SliceGPT, LLM-Pruner | How to evaluate a pruned model, pruning vs quantization, small-model risk, calibration data |
| J6: Vocabulary trimming for Gemma 3's 256k vocabulary | [Vocabulary Trimming](https://arxiv.org/abs/2305.15020), Minitron (vocabulary share), Sheared LLaMA (embedding vs speed) | Whether and when to trim Gemma 3 270M/1B to Catalan + Spanish + English + math tokens |
| J7: Foundations: what pre-LLM pruning still teaches | [Han 2015](https://arxiv.org/abs/1506.02626), Deep Compression, [Lottery Ticket](https://arxiv.org/abs/1803.03635), Movement Pruning | Background only: retraining, iterative pruning, distillation during pruning |

Papers:

- Han 2015: Han et al., "Learning both Weights and Connections" ([arXiv 1506.02626](https://arxiv.org/abs/1506.02626))
- Deep Compression: Han et al. ([arXiv 1510.00149](https://arxiv.org/abs/1510.00149))
- Lottery Ticket: Frankle & Carbin ([arXiv 1803.03635](https://arxiv.org/abs/1803.03635))
- Movement Pruning: Sanh et al. ([arXiv 2005.07683](https://arxiv.org/abs/2005.07683))
- OBC: Frantar & Alistarh, Optimal Brain Compression ([arXiv 2208.11580](https://arxiv.org/abs/2208.11580))
- SparseGPT: Frantar & Alistarh ([arXiv 2301.00774](https://arxiv.org/abs/2301.00774))
- LLM-Pruner: Ma et al. ([arXiv 2305.11627](https://arxiv.org/abs/2305.11627))
- Wanda: Sun et al. ([arXiv 2306.11695](https://arxiv.org/abs/2306.11695))
- Sheared LLaMA: Xia et al. ([arXiv 2310.06694](https://arxiv.org/abs/2310.06694))
- Vocabulary Trimming: Ushio et al. ([arXiv 2305.15020](https://arxiv.org/abs/2305.15020))
- LLM-KICK: Jaiswal et al., "Compressing LLMs: The Truth is Rarely Pure and Never Simple" ([arXiv 2310.01382](https://arxiv.org/abs/2310.01382))
- FLAP: An et al. ([arXiv 2312.11983](https://arxiv.org/abs/2312.11983))
- SliceGPT: Ashkboos et al. ([arXiv 2401.15024](https://arxiv.org/abs/2401.15024))
- ShortGPT: Men et al. ([arXiv 2403.03853](https://arxiv.org/abs/2403.03853))
- Gromov 2024: Gromov et al., "The Unreasonable Ineffectiveness of the Deeper Layers" ([arXiv 2403.17887](https://arxiv.org/abs/2403.17887))
- Minitron: Muralidharan et al., "Compact Language Models via Pruning and Knowledge Distillation" ([arXiv 2407.14679](https://arxiv.org/abs/2407.14679))
- Minitron in practice: Sreenivas et al., "LLM Pruning and Distillation in Practice" ([arXiv 2408.11796](https://arxiv.org/abs/2408.11796))

Dataset for our evaluation: [M3Kang dataset card](https://huggingface.co/datasets/qualcomm/M3Kang). No problem text from it appears in this note.

## J1: Unstructured and N:M sparsity, and the CPU question

**Question.** Unstructured and semi-structured 2:4 / 4:8 sparsity are versions of "set individual weights to zero". Does any of them make a GGUF model smaller or faster on the UNO Q's 4× Cortex-A53 under llama.cpp?

**How the papers relate.**

- **Lineage.** OBC turns the Optimal Brain Surgeon framework into an exact layer-wise solver for both pruning and quantization (§1, §4). SparseGPT is the approximate, LLM-scale version of the same layer-wise reconstruction. It runs in the column-wise framework of GPTQ and can prune and quantize in one pass (§3.5). GPTQ is the quantization branch of this lineage (linked below, not summarized here).
- **Competitor.** Wanda drops the weight update and the Hessian (the matrix of second derivatives of the loss). Its score is |W_ij| · ‖X_j‖, compared per output row (§3). It matches SparseGPT at 50% unstructured sparsity.
- **Speed evidence comes from older work.** Deep Compression and Movement Pruning predate LLMs. They are the only papers here that measure sparse inference at batch size 1, as in our case.

**Key evidence.**

- **OBC, quality.** At 4× FLOP reduction (unstructured), BERT keeps 82.10 F1 against 88.53 dense. AdaPrune reaches 18.75 and global magnitude 9.23 (§6, Table 1).
- **OBC, CPU speed.** It reaches 4× and 5× real speedup at 1% and 2% accuracy loss on ResNet50. This uses the DeepSparse engine on a 12-core Xeon, batch 64, with 8-bit weights plus block-4 sparsity. The dense int8 model alone is ≈2.7× faster, and sparsity multiplies on top (§6, Fig. 3d).
- **SparseGPT, scale.** OPT-175B reaches 60% unstructured sparsity with a "negligible" perplexity increase. Magnitude pruning keeps accuracy only to 10% and collapses beyond 30% (§1, Fig. 1). Calibration is 128 segments of 2048 tokens from C4 (§4).
- **SparseGPT, small models suffer most.** At 50% sparsity, WikiText2 perplexity goes from 27.66 to 36.85 for OPT-125M and from 22.00 to 31.58 for 350M. For 1.3B it goes from 14.62 to 17.46 (§4.1, Table 1). The authors "speculate" this is due to overparametrization of large models.
- **SparseGPT, 2:4.** At 175B, 2:4 adds only 0.39 perplexity (§4.1). Results for smaller models are worse.
- **SparseGPT, sparse + 4-bit.** 50% sparsity + 4-bit beats 3-bit GPTQ at 175B (8.29 vs 8.68) (§4.1, Fig. 6). The memory equivalence assumes that the format stores only non-zeros, plus a bitmask.
- **SparseGPT, CPU speed.** The setup is OPT-2.7B with DeepSparse on an 18-core i9 and a 400-token batch. Speedups are 1.57×, 1.82× and 2.16× at 40%, 50% and 60% sparsity (App. E, Table 7). 2:4 on NVIDIA GPUs gives 1.54–1.79× per layer at a 2048-token batch (Table 8).
- **Wanda.** LLaMA-7B at 50% unstructured sparsity: perplexity 7.26 (Wanda), 7.22 (SparseGPT), 17.29 (magnitude), 5.68 (dense) (§4.2, Table 3). At 2:4 the numbers are 11.53 vs 11.00.
- **Wanda, speed of pruning.** Computing the score takes 0.54 s against 203.1 s for SparseGPT on LLaMA-7B (Table 4).
- **Wanda, calibration.** With one calibration sample, Wanda reaches 7.46 against SparseGPT's 10.22 (App. D.1, Table 17).
- **Wanda, small models.** OPT-125M at 50%: 38.96 (Wanda) and 37.07 (SparseGPT) vs 27.66 dense (App. B, Table 10).
- **Wanda, speed of inference.** Its only speedup is 2:4 on NVIDIA GPUs with CUTLASS. On LLaMA-7B, this gives about 1.6× on linear layers and 1.24× end-to-end (§4.3, Table 5).
- **Deep Compression, CPU speed.** At batch 1, sparse matrix-vector kernels on CSR (Compressed Sparse Row) storage give 3–4× layer-wise speedup on FC layers (§6.3). The kernels are MKL on a Core i7 and cuSPARSE on GPU and on Tegra K1. The pruning there is extreme: 96% of FC weights in VGG-16. With batching, "pruned network no longer shows its advantage". Sparse indexes take about as much storage as the weights (§6.4).
- **Movement Pruning.** Even extremely sparse models get no significant inference speedup in standard PyTorch. The authors write: "sparse matrices are simply matrices with lots of 0 inside" (App. A.3).

**Negative results and limits.**

- Every CPU speedup above comes from a sparsity-aware runtime on x86: DeepSparse or MKL CSR. None of these papers tests llama.cpp, ARM or Cortex-A53.
- Wanda: without fine-tuning, there is "a noticeable gap" between sparse and dense models (§4.1). At 80% sparsity the best model (25.86) is far worse than dense LLaMA-7B (5.68). The authors say this "suggests that at extreme sparsity levels, it may be better to use a small dense model" (App. D.3).
- Wanda: large sparse beats small dense only for unstructured sparsity. For structured N:M sparsity "the trend is reversed" (§4.1).
- LLM-KICK finds no "matching" N:M model on any of its knowledge tasks (see J5).

**What this means on the UNO Q.**

- **Skip unstructured and 2:4 pruning.** llama.cpp stores and computes zeros like any other weight ([CHALLENGE_CONTEXT §2](../../../CHALLENGE_CONTEXT.md#2-target-hardware-arduino-uno-q)). So a 50%-sparse GGUF has the same size and the same speed.
- The CPU wins in these papers need a sparse runtime and high sparsity. Deep Compression needed batch 1, CSR and ~96% sparsity. LLMs collapse long before that (Wanda App. D.3).
- SparseGPT's "50% + 4-bit = 3-bit memory" needs bitmask storage, which GGUF does not have.
- **What carries over is the quantization side of the lineage.** Layer-wise reconstruction with calibration data is the idea behind GPTQ.

**Open questions.**

- Would a custom sparse kernel on the A53 ever beat Q4_0 dense? CSR indexes cost about as much as the weights (Deep Compression §6.4). So the papers give no reason to expect a win at the 50% sparsity LLMs tolerate. Whether decode on the board is memory-bound is in the final [Open questions](#open-questions).
- Activation (contextual) sparsity is a different idea from weight sparsity. See Deja Vu in [inference J4](../inference/_synthesis.md#j4-activation-sparsity-and-offloading).

## J2: Retraining-free structured pruning: criterion and output shape

**Question.** Can we remove whole FFN channels, heads or hidden dimensions from Gemma 3 with only calibration data and no training? Do `convert_hf_to_gguf.py` and llama.cpp then still accept the model?

**How the papers relate.**

- **Compete on the score.**
    - Wanda-sp: FLAP's structured version of Wanda, summing |W_ij| · ‖X_j‖ over a column (FLAP App. B.1).
    - FLAP: variance of each input channel over calibration samples × squared norm of the weight column. FLAP also adds a bias that compensates with the channel mean (Methodology).
    - SliceGPT: rotate each block with PCA (principal component analysis) so the signal sits in the leading dimensions, then remove rows and columns (§3).
    - LLM-Pruner without tuning: first-order Taylor importance on dependency groups (§3.2). Taylor importance estimates the loss change from removing a group, about |gradient × weight|.
- **FLAP and LLM-Pruner compete directly.** FLAP's claim is that its bias compensation does the job of LoRA recovery.
- **SliceGPT and ShortGPT.** SliceGPT is also a baseline in ShortGPT (J4).

**Key evidence.**

- **FLAP vs others, LLaMA-7B, WikiText2 perplexity (dense 12.62)** (Table 1):

| Method | 20% pruned | 50% pruned |
|---|---|---|
| FLAP (no retraining) | 14.62 | 31.80 |
| LLM-Pruner | 19.77 | 112.44 |
| LLM-Pruner + LoRA | 17.37 | 38.12 |
| Wanda-sp | 22.12 | 366.43 |

- **FLAP, uniform vs adaptive.** At 50%, forcing the same ratio in all layers and modules costs a lot. With the same metric, uniform gives 57.57 and adaptive gives 31.80 (Table 3).
- **FLAP, cost.** 1024 calibration samples. Pruning LLaMA-7B takes 3–5 minutes on one GPU (Ablation).
- **FLAP, speed (A100, Table 4).** The prose percentages in that section do not match the table. These numbers are from the table:
    - Dense: 25.84 tok/s
    - FLAP 20%: 5.07B parameters, 33.90 tok/s
    - FLAP 50%: 3.26B, 42.88 tok/s
    - Wanda's unstructured model: no change (25.67 tok/s)
- **FLAP, calibration.** C4 vs WikiText2 calibration gives 50.37 vs 48.33 average zero-shot accuracy (App. C.3, Table 7). The authors call this "about ±1%".
- **FLAP vs SparseGPT.** The FLAP authors "fail to obtain reasonable results" when adapting SparseGPT to structured pruning (App. A).
- **SliceGPT, perplexity.** WikiText2 for LLaMA-2 7B: 5.47 dense, 7.24 at 25% slicing, 8.12 at 30%, 8.69 for SparseGPT 2:4. For OPT-125M: 27.64 → 37.74 at 25% (§4.1, Table 1).
- **SliceGPT, Phi-2 (2.8B).** At 25% slicing + LoRA recovery on Alpaca, average zero-shot accuracy is 65.2% vs 72.2% dense (§4.1).
- **SliceGPT, speed.** 25% slicing makes per-token generation 16–17% faster on RTX6000 and 11–13% faster on A100 (Table 2).
- **SliceGPT, smallest pruned norm columns.** The authors' first baseline was very poor, "perplexity ... soaring into the 1000s after pruning just a few columns" (§4).
- **LLM-Pruner without recovery, LLaMA-7B at 20%** (average of 7 zero-shot tasks, dense 63.25):
    - Taylor importance: 56.69
    - random group selection: 52.69
    - magnitude (L2): 42.65 (Table 1)
- **LLM-Pruner, uniform channel pruning.** "Channel" pruning (all layers alike, prunes the hidden dimension) is much worse than "Block" pruning. On LLaMA-13B at 20%, the scores are 50.29 vs 61.79 (Table 2). The authors explain that the first and last layers are sensitive (Fig. 3).

**Negative results and limits.**

- The FLAP authors test it only on LLaMA-7B to 65B and Vicuna-7B. Its quality measures are perplexity and commonsense multiple-choice. The paper shows generation only as examples (App. C.4).
- SliceGPT works worse on LLaMA-2 than on OPT (§4.1). It needs double precision for PCA (App. A.2).
- SliceGPT's conclusion admits that dense models of similar size beat sliced models of 13B parameters or less.
- Every result in this junction is on 125M–70B models with English calibration data.

**What this means on the UNO Q.**

- **The output shape is the main problem for us.** None of these methods yields a standard, uniform Gemma 3 config without extra work. The following is our reading of the methods, not a tested result:
    - FLAP picks different widths per layer and module, and adds bias vectors to pruned linear layers.
    - SliceGPT adds a new D×D linear layer (Q_ℓᵀQ_ℓ₊₁) inside every residual connection (§3.3). It also assumes an RMSNorm-connected network (§3.2). RMSNorm is root-mean-square normalization.
    - LLM-Pruner's best variant leaves the first layers and the last layer unpruned (App. B.1).
    - Neither the extra biases nor the residual matrices exist in the standard Gemma 3 graph that llama.cpp runs.
- **The uniform alternative is much worse without retraining.** FLAP's own ablation shows this (57.57 vs 31.80), and so does LLM-Pruner's Channel result.
- **So we should not ship a retraining-free structured-pruned Gemma 3.** We may not prune width at all. If we do, a cheap forward-only score should only rank FFN channels. The candidates are FLAP's fluctuation metric or Minitron's activation score (J3). Keep the ratio the same in every layer so the config stays standard. Then always recover (J3).

**Open questions.**

- Does `convert_hf_to_gguf.py` accept a Gemma 3 config with per-layer FFN widths? (Also open in [CHALLENGE_CONTEXT §9](../../../CHALLENGE_CONTEXT.md#9-open-questions-todo-checklist).)
- Does Gemma 3's norm layout satisfy SliceGPT's invariance assumption?
- Calibration in Catalan and Spanish vs English: no paper here tests calibration language (see J5).

## J3: Structured pruning with recovery: data and compute

**Question.** After structured pruning, what recovery makes the model good again (LoRA, continued pre-training, or distillation), and how much data and compute did that take?

**How the papers relate.**

- **A cost ladder:**
    - LLM-Pruner: LoRA, about 50K samples, hours.
    - Sheared LLaMA: learned pruning masks + 50B tokens of continued pre-training.
    - Minitron: forward-only importance + logit distillation, 94B tokens.
- **Sheared LLaMA criticizes LLM-Pruner.** It gives worse loss, an odd shape and slower speed at equal size (App. F.2).
- **Minitron in practice extends Minitron.** It covers the case without the original pre-training data by adding "teacher correction".
- **Side results.** Wanda (§5) and SliceGPT (§4.1) add LoRA-recovery numbers for unstructured and sliced models.

**Key evidence.**

- **LLM-Pruner, recipe.** Calibration is 10 Bookcorpus samples of 128 tokens. Recovery uses LoRA rank 8 on all linear layers, about 50K Alpaca samples and 2 epochs. It takes about 3 hours on one GPU (2.5 h on an RTX 4090) (§4.1, App. B.2).
- **LLM-Pruner, LLaMA-7B at 20%.** Average accuracy goes from 56.69 to 59.23 with tuning, against 63.25 dense. The Element² variant reaches 60.07 (Table 1).
- **LLM-Pruner, at 50%.** 42.13 → 48.69 (App. C.5, Table 16).
- **LLM-Pruner, more recovery data.** With 2.59M samples instead of 50K, the 20% model reaches 62.36 (App. C.1, Table 12).
- **LLM-Pruner, overfitting.** Average accuracy rises from 56.69 to 59.24 within 200 steps, peaks at 59.68 (600 steps) and then drifts down. Perplexity drops within 300 steps and then rises slowly (§4.3, Fig. 5, App. C.4, Table 15).
- **LLM-Pruner, local vs global.** Ranking groups within each module ("local", uniform widths) is slightly better than global ranking: 56.69 vs 56.49 (App. C.3, Table 14).
- **Sheared LLaMA, recipe.**
    - Sheared LLaMA learns masks for layers, hidden dimension, heads and intermediate dimension. Lagrangian constraints (penalty terms in the loss) force a pre-chosen target shape (§2.1).
    - Data: 0.4B tokens for pruning and 50B tokens for continued pre-training on RedPajama (§3.1).
    - Hardware: 8 GPUs for pruning, 16 GPUs for continued pre-training (App. C, Table 7).
- **Sheared LLaMA, result.** The 1.3B model averages 51.0 over 11 tasks. TinyLlama-1.1B (trained on 3T tokens) gets 50.0 and Pythia-1.4B gets 48.9 (Table 2).
- **Sheared LLaMA, uniform target shape.** The uniform shape runs faster than non-uniform CoFiPruning at 1.3B (58 vs 51 tok/s). It starts with a higher perplexity (10.3 vs 9.1) and needs about 0.5B more tokens to catch up (§4.2, Table 4).
- **Sheared LLaMA vs LLM-Pruner at equal size.** LLM-Pruner: 43 tok/s, perplexity 7.09. Sheared LLaMA: 58 tok/s, perplexity 6.85 (App. F.2, Table 12). LLM-Pruner's shape ends with an FFN intermediate size (2201) smaller than the hidden size (4096) (Table 11).
- **Sheared-Pythia, the smallest result in the folder.** The authors pruned Pythia-410M to 160M (the text also says 440M). It needed 10B tokens just to match Pythia-160M trained from scratch (43.51 vs 43.56). With 33B tokens it reached 45.78 (App. F.5, Table 14). The authors call these "very preliminary results".
- **Minitron, recipe.** Importance scores for heads, neurons, embedding channels and layers come from activations on 1024 samples, with forward passes only (§2.2). Candidates get "lightweight retraining" of about 1.8B tokens. The final models used 94B tokens (§4, Table 2). Hardware: 16 DGX A100 nodes (App. A.8).
- **Minitron, distillation is decisive.** For a 4B model (MMLU, Table 11):

| Training of the 4B model | MMLU |
|---|---|
| random init, 150B tokens | 24.36 |
| pruned + conventional training | 24.57 |
| pruned + logit distillation, 100B tokens | 37.81 |
| pruned in two steps (15B → 8B → 4B) + distillation | 42.45 |

KL divergence on logits alone works best when depth is not cut much (best practices 5–7, §4.1).

- **Minitron, prune the final checkpoint.** Pruning the final-stage (aligned) checkpoint and retraining on that stage's data is better (best practice 10). The authors suggest "it may suffice to prune the aligned model and retrain with a portion of the alignment dataset" (§4.3).
- **Minitron in practice, teacher correction.** Without the original data, first fine-tune the teacher on the distillation data (about 100B tokens). This gives "over a 6% reduction in LM validation loss" (Insights).
- **Minitron in practice, budget.** Distillation used 94B tokens (4B) and 380B tokens (8B) on 32 DGX H100 nodes (Table 4, Distillation).
- **Minitron in practice, which width to cut.** "Retaining attention heads and pruning the other dimensions (MLP intermediate dimension, embedding channels)" gives stronger accuracy (Insights).
- **Wanda + LoRA.** LoRA rank 8 on q/v, 1 GPU, 12 h, on C4. LLaMA-7B at 2:4 goes from 48.53 to 54.46. At 50% unstructured, it goes from 54.21 to 56.53. Full fine-tuning (4 GPUs, 3 days) reaches 58.15, against 59.99 dense (§5, App. D.5, Table 22).
- **SliceGPT + RFT.** Slicing LLaMA-2 7B by 30% took 44 min, and LoRA recovery 23 min, on one H100 (Table 3). Recovery on Alpaca beat recovery on WikiText-2 by a wide margin, "attributed to the similarity between Alpaca and the benchmark tasks" (§4.1).

**Negative results and limits.**

- Every recovery recipe here starts from a model of 7B or more, except Sheared-Pythia. All except LLM-Pruner, SliceGPT and Wanda-LoRA use multi-node GPU clusters and billions of tokens.
- LLM-Pruner: "considerable performance degradation" at 50%, plus "incoherent sentences" and repetitive tokens in long generations (§5, §4.3).
- Sheared LLaMA depends on open pre-training data. The authors warn: "if a specific domain is not covered in the pre-training data, the method may not recover performance well on that domain" (§6).

**What this means on the UNO Q.**

- **Budget gap.** Our training GPU is an 8 GB RTX 4060 in a team member's laptop ([CHALLENGE_CONTEXT, Team hardware](../../../CHALLENGE_CONTEXT.md#team-hardware)). The billion-token recipes (Sheared LLaMA, Minitron) are out of reach. The only sub-1B evidence (Sheared-Pythia) says a pruned small model needs ~10B tokens just to tie a dense model of the target size.
- **Required baseline.** Any pruned Gemma 3 1B must beat dense Gemma 3 270M (and Qwen 3.5 0.8B) on our tutoring evaluation at equal speed. Beating the unpruned 1B is not enough.
- **Recipe if we prune the 1B.** It follows Minitron best practices 5, 7 and 10. The steps are in [What to try](#what-to-try).

**Open questions.**

- How many tokens does logit distillation need to recover a 10–30% FFN-pruned 1B? No paper tests this scale.
- Is our tutoring data plus some general Catalan/Spanish text enough recovery data, or does it narrow the model the way LLM-Pruner's Alpaca recovery overfits?

## J4: Depth pruning vs width pruning

**Question.** Should we remove whole layers (depth) or narrow every layer (width)? If depth, which layers, and how do we heal?

**How the papers relate.**

- **They disagree, and retraining explains it.** ShortGPT finds depth pruning beats width methods (LLM-Pruner, SliceGPT) without post-training. Minitron finds width beats depth after retraining. Minitron's own Table 1 shows depth+width ahead before retraining, with the order flipping after about 200 steps.
- **Gromov vs ShortGPT on the metric.** Gromov drops a *contiguous* block chosen by angular distance between the input of layer ℓ and layer ℓ+n. ShortGPT ranks *single* layers by Block Influence (1 − cosine between a layer's input and output).
- **Minitron in practice sides with Gromov.** Contiguous removal works better.

**Key evidence.**

- **ShortGPT vs width methods, no post-training.** At ~27% of LLaMA-2-7B parameters removed, relative performance retained is (Table 2):
    - ShortGPT (layer removal): 86.31%
    - LaCo (layer merging): 80.39%
    - LLM-Pruner: 72.79%
    - SliceGPT: 68.73%
- **ShortGPT, 13B.** Removing 10 of 40 layers of LLaMA-2-13B moves MMLU from 55.0 to 52.2 (§1).
- **ShortGPT on a GPTQ 4-bit LLaMA-2-7B** (Table 4). Removing 25% of layers (24 of 32 kept):

| | Dense GPTQ | 25% layers removed |
|---|---|---|
| Perplexity | 8.03 | 22.29 |
| MMLU | 43.17 | 41.68 |
| Throughput | 1.00× | 1.16× |

- **ShortGPT, cliff.** MMLU shows "a sharp drop at a specific layer" (§4.3).
- **Gromov, robustness.** MMLU holds until a model-dependent pruning fraction, then falls to random (§4.1, Fig. 2):
    - Llama-2: about 45–55% of layers
    - Mistral-7B: about 35%
    - Phi-2: about 25%
    - Qwen: about 20%

    The authors offer two hypotheses for the robustness of larger, deeper models. Smaller models may be "more overtrained", or deeper models "can afford to lose more layers".

- **Gromov, healing.** QLoRA on C4: 164M tokens for 7B models, 5000 steps, batch 16, one 40 GB A100 (App. B.1). Healing restores C4 loss to near-unpruned levels (§4.2, Fig. 3).
- **Gromov, simple heuristic.** Dropping the deepest layers except the final one matches the similarity method after healing (§4.4). This is "strong evidence that the purpose of post-pruning finetuning is the healing of damage at the pruning interface and not the acquisition of additional knowledge".
- **Gromov, final layer.** Never drop the final layer (§4.3).
- **Gromov, LoRA rank.** Lower ranks (down to 2) gave better MMLU but worse C4 loss. The authors suspect overfitting (App. C.3).
- **Minitron, after 1.8B tokens of retraining** (Table 10, LM loss):
    - width-pruned: 2.049
    - depth + width: 2.062
    - depth-pruned (perplexity-ranked): 2.155
    - depth-pruned (BI-ranked): 2.177

    Best practice: "Prefer width pruning over depth for the model scales we consider (≤ 15B)" (§4.1).

- **Minitron in practice, which layers.** Dropping 16 layers ranked one by one gives random Winogrande (0.5). Dropping layers 16–31 as a block gives 0.595 (Fig. 9).
- **Minitron in practice, width vs depth.** Width-pruned Llama-3.1-Minitron-4B has lower loss throughout training (Fig. 7). Base MMLU: 60.5 vs 58.7 (Table 1).
- **Minitron in practice, speed.** Depth is faster: 2.7× vs 1.8× throughput over Llama 3.1 8B (TensorRT-LLM, FP8, H100, batch 32–64). The Insights section says 1.7× for width.

**Negative results and limits.**

- **ShortGPT:** "the negative effect of layer removal is more significant on generative tasks". The authors write that removing 25% of layers from 7B models makes XSum and C3 "decrease to nearly zero" (§5). In Table 6, with 27.1% of parameters removed, XSum goes from 19.40 to 0.67. Replacing removed layers with small MLPs and retraining lifts XSum only to 4.89 (§4.6, Table 6).
- **Gromov:** GSM8K and HellaSwag degrade "with any amount of pruning" on Llama-2-70B (§5, Fig. 6). See J5.
- **Gromov's evaluation is mostly multiple-choice** (MMLU, BoolQ) plus C4 loss.

**What this means on the UNO Q.**

- **Depth is the easiest change for GGUF:** same shapes, fewer layers. It gives the largest speedup per removed parameter (Minitron in practice: 2.7× vs 1.8×).
- **But depth is the riskiest choice for a copilot that writes math explanations.** Generative tasks collapse first (ShortGPT XSum). Math drops with any layer removed (Gromov GSM8K, see J5).
- **Order of preference for Gemma 3 1B:**
    1. Quantize only.
    2. Width (FFN) pruning with distillation.
    3. Depth pruning of a contiguous block, never the final layer, healed with QLoRA.
- **For Gemma 3 270M, depth pruning buys little.** Transformer blocks are only ≈100M of 270M parameters ([CHALLENGE_CONTEXT §3](../../../CHALLENGE_CONTEXT.md#3-base-model-candidates)). Our own arithmetic: removing a quarter of the blocks touches only ≈25M parameters.

**Open questions.**

- Gemma 3 interleaves local and global attention layers ([CHALLENGE_CONTEXT §5](../../../CHALLENGE_CONTEXT.md#5-pruning-marti-careful-only-if-you-have-no-other-option)). After we remove a block, does the converter or llama.cpp still assign the correct layers as global? Check this before any depth-pruning test.
- Is a distilled, heavily trained small model harder to depth-prune? Gromov raises this ("are scaling-law over-trained or distilled models more difficult to prune?", §5), but does not test it.

## J5: What pruning breaks

**Question.** Which abilities fail first when we prune an LLM? Does perplexity or multiple-choice accuracy reveal it? How does pruning compare with quantization, and does model size matter?

**How the papers relate.**

- **Evaluation critique.** LLM-KICK targets the evaluation that SparseGPT and Wanda used (perplexity).
- **Same pattern elsewhere.** ShortGPT (§5), Gromov (§5) and Minitron in practice report the same thing from the structured side. Multiple-choice knowledge holds, but generation and math do not.
- **[Martí](../../../CHALLENGE_CONTEXT.md)'s warning.** Martí is an ML and hardware colleague of the team. This is the evidence behind his warning: good multiple-choice scores, broken generation ([CHALLENGE_CONTEXT §5](../../../CHALLENGE_CONTEXT.md#5-pruning-marti-careful-only-if-you-have-no-other-option)).

**Key evidence.**

- **LLM-KICK, perplexity hides damage.** Setup: Vicuna 7B/13B/33B pruned by magnitude, Wanda and SparseGPT, and quantized with GPTQ, with no fine-tuning. Perplexity barely moves up to 45–60% sparsity (§2, Fig. 1). Yet on factoid QA, no pruning method stays within 5% of dense beyond about 20–25% sparsity. All methods fail "even at trivial sparsities such as 30-35%". For N:M patterns the drop is ≥50% (§3.1, Fig. 2).
- **LLM-KICK, instruction following.** On MT-Bench-style questions judged by GPT-4, which include math, pruned models stay within 5% "only up to sparsity ratio of ~25%". They produce "more repetitive texts" with fewer unique tokens (§3.3, Fig. 6).
- **LLM-KICK, quantization fares better.** "Current SoTA LLM quantization is seemingly more successful". On MMLU, 8-bit stays within 5% for Vicuna-7B, and 4-bit stays within 5% for Vicuna-13B (§3.1).
- **LLM-KICK, in-context retrieval holds.** Pruned models stay within 5% up to about 40% (7B) and 50% (13B) sparsity (§3.2).
- **LLM-KICK, simple baselines.** Inside the tolerance regime, one-shot magnitude pruning performs about as well as Wanda and SparseGPT (§3.1, §3.3).
- **LLM-KICK, small dense vs large sparse.** Vicuna-13B pruned to 7B-parameter size (46.16% sparsity) gets MMLU 31.7 (magnitude), 45.3 (Wanda) and 46.3 (SparseGPT). Dense Vicuna-7B gets 46.7 (§4).
- **Generation vs multiple-choice.** ShortGPT: XSum 19.40 → 0.67 with 27.1% of parameters removed, while MMLU only goes 45.39 → 43.96 (Table 6). LLM-Pruner: long generations sometimes turn "meaningless" or repetitive (§4.3).
- **Math, Gromov.** "GSM8K and HellaSwag, our two reasoning tasks, exhibit immediate degradation in performance with any amount of pruning". In contrast, chain-of-thought MMLU stays flat (§5, Fig. 6). The authors call this "some initial evidence" that deeper layers matter for reasoning.
- **Math, Minitron in practice.** Llama-3.1-Minitron-4B base, GSM8K (Table 1, Insights): depth-pruned 16.8, width-pruned 41.2. After instruction tuning: 71.11 vs 79.76 (Table 2). The authors note the gap "reduces with instruct tuning".
- **Math, Sheared LLaMA.** GSM8K: Sheared-LLaMA-2.7B scores 2.7 and 2.4, against 13.7 for its LLaMA2-7B source. The authors say "the math ability of existing 3B parameter models, including Sheared-LLaMA, is still far below that of larger models" (App. F.3, Table 13).
- **Math, Minitron.** Minitron 4B scores 24.1 on GSM8K, against 55 for Phi-2 and 58.5 for Qwen2-1.5B (Table 3). Minitron 8B scores 51.3, against 48.5 for its 15B teacher (Table 2).
- **Small models suffer more.**
    - At 50% sparsity, OPT-125M perplexity rises from 27.66 to 36.85 (SparseGPT, Table 1) or to 38.96 (Wanda, Table 10).
    - SliceGPT at 25%: OPT-125M goes from 27.64 to 37.74, and OPT-2.7B only from 12.46 to 14.56 (Table 1).
    - Gromov: Phi-2 (2.7B) collapses at about 25% of layers, Llama-2-70B at about 45–55% (§4.1).
- **Pruning vs quantization, head to head.** Two papers compare them directly. Their tables follow.

**LLM-Pruner, LLaMA-7B (App. C.2, Table 13):**

| Model | Avg. accuracy | Memory |
|---|---|---|
| Dense | 63.25 | 12884.5 MiB |
| LLM.int8() | 63.09 | 6777.7 MiB |
| 20% pruned, recovered on 2.59M samples | 62.36 | 10488.4 MiB |

**ShortGPT, LLaMA-2-7B MMLU (Table 5):**

| Setting | MMLU |
|---|---|
| Dense | 45.4 |
| 4-bit quantization | 44.9 |
| 27.1% of parameters removed | 44.0 |
| Quantize, then remove layers | 42.4 |
| Remove layers, then quantize | 41.2 |

- **Calibration data.**
    - SparseGPT results vary little with the random choice of calibration samples (13.52 ± 0.075 over 5 seeds, App. A).
    - LLM-KICK finds SparseGPT, unlike Wanda, benefits from more calibration samples at 70% sparsity (§4, Fig. 7).
    - FLAP: C4 vs WikiText2 calibration changes average accuracy by about 2 points (J2).
    - No pruning paper here calibrates in a language other than English. ShortGPT's Chinese benchmarks (CMNLI, CHID, C3, CMMLU) are the only non-English evaluations of pruned models.

**Negative results and limits.**

- LLM-KICK tests only unstructured and N:M pruning, without any fine-tuning, on Vicuna. It does not test structured pruning or recovery. Its authors list LoRA/QLoRA recovery as future work (§5).
- The math results are GSM8K accuracy, not explanation quality.
- No paper here reproduces Martí's "switched to German" failure. No paper tests language drift after pruning.

**What this means on the UNO Q.**

- **Evaluate every pruned candidate on generated explanations,** in the target languages, with the format-failure rate tracked as its own metric ([benchmarks J3](../benchmarks/_synthesis.md#j3-small-models-and-answer-format-failure)). Perplexity and multiple-choice letter accuracy can stay flat while generation and math collapse (LLM-KICK, ShortGPT, Gromov).
- **Quantize first.** At equal effort, the papers that test both find quantization keeps more quality per byte than pruning (LLM-KICK, LLM-Pruner App. C.2, ShortGPT Table 5). This supports [Martí's priority order](../../../CHALLENGE_CONTEXT.md#1-the-challenge-what-we-know).
- **Expect our 270M–1B models to be at the fragile end.** Every size trend in this folder says that smaller models lose more.

**Open questions.**

- Does pruning with English calibration data hurt Catalan/Spanish more than English? (Martí's anecdote. [Marchisio 2024](https://arxiv.org/abs/2407.03211), in [quantization J7](../quantization/_synthesis.md#j7-multilingual-and-math-damage-calibration-language), is the closest evidence.)
- Do LoRA or distillation recovery restore math explanation quality, or only multiple-choice accuracy? Minitron in practice suggests instruction tuning narrows the GSM8K gap. No paper tests explanations.

## J6: Vocabulary trimming for Gemma 3's 256k vocabulary

**Question.** Gemma 3 270M has ≈170M of its parameters in the embedding table of a 256k vocabulary, and ≈100M in transformer blocks ([CHALLENGE_CONTEXT §3](../../../CHALLENGE_CONTEXT.md#3-base-model-candidates)). Can we drop the tokens that a Catalan/Spanish/English math copilot never uses, and should we do it before or after fine-tuning?

**How the papers relate.**

- **Ushio is the only paper on the method.** Minitron reports total and non-embedding parameters side by side for 256k-vocabulary models, which shows the share.
- **Sheared LLaMA points the other way on speed.** It states that "embedding sizes do not affect inference speed" (App. F.2), for 7B models on GPU.

**Key evidence.**

- **Method.** Keep only the tokens that appear in a target-language corpus, or only the top-n most frequent ones. Ushio uses mC4, the multilingual version of the C4 web-text corpus. Remove the other rows of the embedding matrix. Trim either before fine-tuning (pre-FT) or after it (post-FT) (§3).
- **Embedding share.** In multilingual LMs the embedding matrix can exceed 80% of parameters. mT5-small has 300M parameters vs 140M for T5-small, only because of a 250k vs 50k vocabulary (§1, Fig. 1).
- **Spanish, keeping every token seen in the corpus.** For mT5-small, trimming keeps 131K tokens (52.4%) and 178M parameters (59.4%). Post-FT trimming leaves Spanish question answering (QA) unchanged (55.9/34.7), and pre-FT trimming improves it (57.8/37.5). For mBART, Spanish keeps 87K tokens (34.8%) (§4.2.1, Table 1).
- **Top-n trimming, mT5.**
    - Post-FT trimming to 60K tokens costs at most 0.3% on QA and question generation (QG) in all languages, at 35% of the original parameters.
    - Trimming to 5K tokens costs no more than 0.4% in English, French and Italian, at 16% of the parameters (§5.1).
- **Pre-FT is less stable.** Examples: −2.6 Ans-F1 (F1 score on the answer span) for mT5 Korean QA, −3.2 for mBART Russian QA (§4.2.1). The authors call post-FT "more robust as a compression mechanism" and recommend pre-FT only with limited fine-tuning compute (§7).
- **Minitron.** With a 256k vocabulary, Minitron 4B has 4.2B total parameters but 2.6B non-embedding parameters (Tables 3, 5).

**Negative results and limits.** All of these come from Ushio's own limitations, model list and tasks:

- **Model types.** All models are encoder or encoder–decoder (mT5, mBART, XLM-R, XLM-V), at most 600M parameters. Ushio tests no decoder-only chat model.
- **Languages.** "We have not tested our methodology in truly low-resource languages". Ushio does not test Catalan.
- **Token counts.** Frequencies come from mC4 as "a proxy".
- **Tasks.** Generation tasks are short-answer QA and QG, not long explanations.

**What this means on the UNO Q.**

- **For Gemma 3 270M, this is the only pruning in the folder with a large upside.** The vocabulary to keep is the union of:
    - Catalan, Spanish and English tokens, counted on mC4 or on our own tutoring corpus
    - digits and math or LaTeX symbols
    - every special and chat-template token
- **Illustration (our arithmetic, not from a paper).** Suppose we kept a third of the 256k vocabulary. The embedding table would then shrink from ≈170M to ≈57M. The model would shrink from ≈270M to ≈157M parameters.
- **RAM is not the reason.** The 270M at Q4_0 is already ~0.25–0.3 GB ([CHALLENGE_CONTEXT §2](../../../CHALLENGE_CONTEXT.md#2-target-hardware-arduino-uno-q)).
- **Speed is a hypothesis to test.** Gemma 3 ties the embedding and the output head ([CHALLENGE_CONTEXT §5](../../../CHALLENGE_CONTEXT.md#5-pruning-marti-careful-only-if-you-have-no-other-option)). Our reasoning: the output head multiplies the hidden state by the whole vocabulary matrix for every generated token. So a smaller vocabulary could make decoding faster if decode is memory-bound. That is not measured on our board (see [Open questions](#open-questions)).
    - Sheared LLaMA's statement that embedding size does not affect speed comes from 7B models on GPU, where the blocks dominate. Measure it on the board before claiming it.
- **Trim after fine-tuning and after any distillation.** Ushio finds post-FT trimming more stable. Logit distillation from Gemma 3 4B/12B needs the teacher and student to share one vocabulary ([fine-tuning synthesis J1](../finetuning_distillation/_synthesis.md#j1-distillation-objective-soft-targets-text-or-reverse-kl)). Trimming last keeps both options open.
- **For Gemma 3 1B the embedding share is smaller.** Compute it from `config.json` before deciding.

**Open questions.**

- **Tokenizer surgery.** Trimming changes token IDs and the tokenizer model. Does `convert_hf_to_gguf.py` accept the rebuilt tokenizer, and does llama.cpp tokenize Catalan text the same way afterwards? Ushio's tool targets Hugging Face models only.
- What does the trimmed model do with a token outside the kept set (a name, a foreign word, an unusual symbol)? Test with byte-fallback inputs.
- What quantization does `llama-quantize` apply to the (tied) embedding/output tensor, and how much of the GGUF file is that tensor before and after trimming?

## J7: Foundations: what pre-LLM pruning still teaches

**Question.** What from the pre-LLM pruning papers still matters for our decision?

**How the papers relate.**

- **Han 2015 sets the basic loop:** train → prune by magnitude → retrain.
- **Deep Compression** adds trained quantization and Huffman coding to it.
- **Lottery Ticket** asks why sparse subnetworks train well.
- **Movement Pruning** adapts pruning to fine-tuning of pretrained Transformers. It is the ancestor of the first-order (Taylor) scores in LLM-Pruner.

**Key evidence.**

- **Han 2015, pruning ratios.** AlexNet goes from 61M to 6.7M parameters (9×) with no accuracy loss. VGG-16 goes from 138M to 10.3M (13×), also with no loss (Table 1).
- **Han 2015, retraining.** Without retraining, accuracy starts dropping at 1/3 of connections kept. With retraining it holds to 1/10 (§5).
- **Han 2015, iterative pruning and initialization.** Iterative pruning raises AlexNet's ratio from 5× to 9× (§3.4). Keeping the surviving weights beats re-initializing them (§3.3).
- **Deep Compression.** AlexNet shrinks from 240MB to 6.9MB (35×) and VGG-16 from 552MB to 11.3MB (49×) without accuracy loss (Abstract).
- **Lottery Ticket.** Winning tickets are 10–20% of the original size on MNIST and CIFAR10 (Abstract).
- **Movement Pruning, sparsity regimes.** Magnitude pruning wins at low sparsity (more than 70% of weights kept). Movement pruning wins at high sparsity. On SQuAD with 3% of weights, F1 is 54.5 for magnitude vs 79.9 for soft movement pruning (§6, Table 2).
- **Movement Pruning, distillation.** With distillation it reaches 95% of BERT-base with about 5% of encoder weights (§6).

**Negative results and limits.**

- **Han 2015** targets "fixed-function hardware specialized for sparse DNN" (§5).
- **Lottery Ticket** covers only small vision datasets. Its sparse architectures "are not optimized for modern libraries or hardware". Deeper networks need learning-rate warmup (§6).
- **Movement Pruning:** "from an inference speed perspective, it might often desirable to use a small dense model such as mini-BERT over a sparse alternative of the same size" (§6).

**What this means on the UNO Q.** All four papers use unstructured pruning, so none applies directly (see J1). The lessons that carry over:

- recovery training matters (Han 2015)
- keep surviving weights rather than re-initializing (Han 2015)
- distillation helps recovery (Movement Pruning, consistent with Minitron)
- importance scores that see the fine-tuning task beat magnitude when pruning is aggressive (Movement Pruning)

**Open questions.** Consider task-aware pruning during our tutoring fine-tune, in Movement-Pruning style, applied to FFN channels instead of single weights. Would it beat task-agnostic pruning for a narrow math copilot? Movement Pruning's conclusion proposes this group-sparsity extension but does not test it.

## What to try

### Prune Gemma 3 1B, only if quantized speed is not enough

These steps come from [J3](#j3-structured-pruning-with-recovery-data-and-compute). They follow Minitron best practices 5, 7 and 10, and the "fine-tune first" option in [CHALLENGE_CONTEXT §8](../../../CHALLENGE_CONTEXT.md#8-recommended-pipeline-synthesis).

1. Fine-tune Gemma 3 1B on tutoring data. This doubles as Minitron's "teacher correction".
2. Prune FFN channels only, with the same ratio in every layer, using a forward-only activation score.
3. Recover with logit distillation from the fine-tuned 1B. It shares the vocabulary, which logit distillation needs ([fine-tuning synthesis J1](../finetuning_distillation/_synthesis.md#j1-distillation-objective-soft-targets-text-or-reverse-kl)). LoRA is the cheaper fallback.
4. Keep recovery short. LLM-Pruner degraded after a few hundred steps.
5. If you recover with LoRA, merge it into the pruned dense weights, so GGUF sees a plain smaller model.

## Open questions

- **Is decode on the board memory-bound?** [CHALLENGE_CONTEXT §9](../../../CHALLENGE_CONTEXT.md#9-open-questions-todo-checklist) lists it as open. The [inference synthesis J1](../inference/_synthesis.md#j1-where-the-time-goes-prefill-vs-decode) and [quantization J1](../quantization/_synthesis.md#j1-foundations-grids-granularity-ptq-vs-qat) discuss whether it is partly compute-bound. This is not measured on our board ([UNO Q board reference, Open questions](../../../UNO_Q_BOARD_REFERENCE.md#open-questions)). The answer matters for sparse kernels (J1) and for the speed gain of vocabulary trimming (J6).

## Links to other folders

- **J1 (lineage, quantization side):** [GPTQ](https://arxiv.org/abs/2210.17323).
- **J1 (activation sparsity instead of weight sparsity):** [Deja Vu](https://arxiv.org/abs/2310.17157).
- **J3 (recovery after pruning):** [LoRA](https://arxiv.org/abs/2106.09685), [Hinton KD](https://arxiv.org/abs/1503.02531), and the [fine-tuning synthesis](../finetuning_distillation/_synthesis.md). Its [J1](../finetuning_distillation/_synthesis.md#j1-distillation-objective-soft-targets-text-or-reverse-kl) says that logit distillation needs a same-vocabulary teacher. Its [J2](../finetuning_distillation/_synthesis.md#j2-parameter-efficient-fine-tuning-on-a-laptop-gpu) covers LoRA recovery and merging.
- **J4 (healing after layer removal):** [QLoRA](https://arxiv.org/abs/2305.14314).
- **J5 (calibration and evaluation language):** [Marchisio 2024](https://arxiv.org/abs/2407.03211). For format-failure tracking after pruning: [benchmarks synthesis](../benchmarks/_synthesis.md).
- **J6 (Gemma 3 vocabulary, tied embeddings, model sizes):** [Gemma 3 report](https://arxiv.org/abs/2503.19786), and [fine-tuning synthesis J1](../finetuning_distillation/_synthesis.md#j1-distillation-objective-soft-targets-text-or-reverse-kl) for the vocabulary constraint on distillation.
