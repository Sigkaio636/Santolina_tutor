---
tags: [synthesis, finetuning_distillation]
papers: 7
date: 2026-11-14
---
# Fine-tuning and distillation: synthesis by junction

This note is an explanation for the team. It says what the 7 papers in this folder show about fine-tuning and distillation, and what that means for our copilot. The note groups the papers by junction: one question that several papers answer together (see [GLOSSARY.md](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md)). Steps to try are in [What to try](#what-to-try). Unresolved points are in [Open questions](#open-questions).

Our deployed language model is Qwen3.5 0.8B Q8_0 ([config.env](https://github.com/Sigkaio636/Santolina_tutor/blob/main/config.env)). The base model to fine-tune is not chosen yet. Gemma 3 is one option that the team explores, so this note plans with Gemma 3 students.

For a 270M–1B student on the UNO Q, this folder supports one main recipe:

- Supervised fine-tuning (SFT) on short explanations written by a larger teacher model.
- LoRA (low-rank adaptation: small trainable matrices added to the frozen weights) on all linear layers of an instruct model.
- Merge the adapters into a BF16 (bfloat16, a 16-bit number format) base. Then convert it to GGUF, the model file format of llama.cpp.

Logit distillation scores better in the papers. In it, the student copies the teacher's next-token probabilities (logits), not only its text. It needs a teacher with the same vocabulary, and much more compute. MiniLLM's on-policy version is the strongest. The student learns from its own outputs, and the loss is the reverse KL (Kullback–Leibler divergence, a distance between two probability distributions). It needs training similar to reinforcement learning (RL).

The most important number for us is a length. Even the shortest student outputs in Li 2025 average about 576 tokens. That is more than twice the board's budget of about 150–250 output tokens (see [J3](#j3-training-data-for-small-model-math-reasoning)). So our training data must be shorter than anything these papers tested.

## Junctions at a glance

| Junction | Papers | Decision it informs |
|---|---|---|
| J1: Distillation objective: soft targets, text, or reverse KL | [Hinton KD](https://arxiv.org/abs/1503.02531), [DistilBERT](https://arxiv.org/abs/1910.01108), [MiniLLM](https://arxiv.org/abs/2306.08543), [Li 2025](https://arxiv.org/abs/2502.12143), [TinyGSM](https://arxiv.org/abs/2312.09241) | Whether to train the student on teacher text (SFT), on teacher logits, or on-policy with reverse KL |
| J2: Parameter-efficient fine-tuning on a laptop GPU | [LoRA](https://arxiv.org/abs/2106.09685), [QLoRA](https://arxiv.org/abs/2305.14314), Li 2025 (SFT setup) | LoRA vs QLoRA vs full fine-tuning on an 8 GB RTX 4060 (a team member's laptop), rank, target modules, merge before GGUF, recovery after pruning |
| J3: Training data for small-model math reasoning | TinyGSM, Li 2025, QLoRA (data quality) | Chain-of-thought (CoT) length, data mix, synthetic data volume, verifier use, under a ~150–250-token output budget |
| J4: Teacher size and the capacity gap | Li 2025, MiniLLM, Hinton KD, TinyGSM | Which teacher to use for a 270M–1B Gemma student: Gemma 3 4B, 12B, Salamandra 7B, or a mix |

Papers:

- Hinton KD: Hinton, Vinyals, Dean 2015 ([arXiv 1503.02531](https://arxiv.org/abs/1503.02531))
- DistilBERT: Sanh et al. 2019 ([arXiv 1910.01108](https://arxiv.org/abs/1910.01108))
- LoRA: Hu et al. 2021 ([arXiv 2106.09685](https://arxiv.org/abs/2106.09685))
- QLoRA: Dettmers et al. 2023 ([arXiv 2305.14314](https://arxiv.org/abs/2305.14314))
- MiniLLM: Gu et al. 2023 ([arXiv 2306.08543](https://arxiv.org/abs/2306.08543))
- TinyGSM: Liu et al. 2023 ([arXiv 2312.09241](https://arxiv.org/abs/2312.09241))
- Li 2025: Li et al., "Small Models Struggle to Learn from Strong Reasoners" ([arXiv 2502.12143](https://arxiv.org/abs/2502.12143))

Dataset for our evaluation: [M3Kang dataset card](https://huggingface.co/datasets/qualcomm/M3Kang). No problem text from it appears in this note.

## J1: Distillation objective: soft targets, text, or reverse KL

**Question.** How should a 270M–1B student learn from a larger teacher to write math explanations? Should it match the teacher's token distributions (logits), or use plain SFT on teacher-written text, or MiniLLM's on-policy reverse KL?

**How the papers relate.**

- **Lineage.** Hinton defines distillation as matching temperature-softened teacher outputs. DistilBERT applies it to a pretrained Transformer and adds two losses. MiniLLM argues that the forward KL behind both is wrong for open-ended generation, and replaces it with reverse KL.
- **Two families of "distillation".** MiniLLM calls them white-box KD and black-box KD (§1). In white-box KD (knowledge distillation), the teacher's distributions are available. In black-box KD, only the teacher's text is available. TinyGSM and Li 2025 are both black-box: they fine-tune on teacher-generated text. MiniLLM names this baseline SeqKD and shows it is weaker than logit distillation and reverse KL on its instruction-following tasks (§3.1–3.2).
- **Same-family pairs only.** Every teacher–student pair in Hinton, DistilBERT and MiniLLM comes from the same model family. Logit distillation needs teacher and student to share one output vocabulary.

**Key evidence.**

- **Hinton: the loss.** Soft targets come from a softmax at temperature T. The student uses the same T in training and T = 1 at inference. A second, lower-weighted cross-entropy on hard labels helps. Soft-target gradients scale as 1/T², so multiply them by T² (§2).
- **Hinton: temperature depends on student size.** On MNIST, students with 300+ units per layer did about equally well at all T above 8. A student with only 30 units per layer worked best at T = 2.5–4 (§3). The authors read this as: "when the distilled model is much too small", intermediate temperatures that ignore very negative logits work best (§2.1).
- **Hinton: soft targets as a regularizer with little data.** With 3% of the speech data, hard targets overfit (44.5% test frame accuracy, early-stopped). Soft targets reached 57.0%, against 58.9% for the full-data baseline (§6, Table 5). This matters because M3Kang has only 1,747 problems ([dataset card](https://huggingface.co/datasets/qualcomm/M3Kang)).
- **Hinton: ensemble distillation.** A distilled single model got 60.8% frame accuracy against 61.1% for the 10-model ensemble and 58.9% for the baseline. The single model kept more than 80% of the ensemble's gain (§4.1, Table 1).
- **DistilBERT: triple loss and initialization.** The loss is soft-target cross-entropy (L_ce) + masked LM (L_mlm) + cosine alignment of hidden states (L_cos) (§2). The student keeps one teacher layer out of two as its initialization (§3). Ablation, change in GLUE macro-score (§4.2, Table 4). GLUE (General Language Understanding Evaluation) is a suite of English classification tasks.
    - without L_ce: −2.96
    - without L_cos: −1.46
    - without L_mlm: −0.31
    - triple loss with random initialization instead of teacher weights: −3.69
- **DistilBERT: result.** 40% fewer parameters, 60% faster on CPU, 97% of BERT's GLUE score (77.0 vs 79.5) (§4, Tables 1 and 3).
- **MiniLLM: why reverse KL.** Forward KL makes a low-capacity student "cover all modes" of the teacher. The student then puts mass on regions the teacher thinks unlikely. Reverse KL is mode-seeking: the student focuses on the teacher's major modes (§1, §2.1, Fig. 2).
- **MiniLLM: results.** It beats SFT, logit distillation (the paper's "word-level KD") and SeqKD in almost all settings. This holds across GPT-2, OPT and LLaMA students from 120M to 13B (§3.2, Fig. 1). More findings:
    - **Calibration on SST2, a sentiment task (LLaMA-7B student).** ECE is the expected calibration error: the gap between confidence and accuracy, lower is better. ECE: teacher 0.025, KD 0.191, SeqKD 0.243, MiniLLM 0.099. Accuracy: 93.0 / 84.7 / 66.5 / 89.7 (§3.3, Table 2).
    - **Exposure bias** (errors that build up because the model trains on correct text but generates from its own output). It stops accumulating beyond about 150 generated tokens for MiniLLM, while it keeps growing for the baselines (§3.3, Fig. 6).
    - **Response length.** Its advantage appears on responses of 6 tokens or more. On responses of 5 tokens or fewer, all methods score about the same (§3.3, Fig. 7).
- **MiniLLM: a pre-training loss keeps general skills.** For the 1.3B student, the authors added the language-modeling loss on the pre-training corpus. This kept classification accuracy at 70.2 instead of 65.7. Instruction-following stayed almost unchanged (52.8 vs 53.2) (App. C.4, Table 7). This is relevant if fine-tuning erodes Catalan/Spanish fluency.

**Negative results and limits.**

- **MiniLLM is RL-like and unstable without its tricks.** On GPT-2-125M, validation Rouge-L (word overlap with a reference answer) is 27.4 for the full method. It drops to 17.4 without length normalization and to 22.3 without teacher-mixed sampling (§3.4, Table 4). Length normalization divides the reward by the response length, so that short outputs are not favored. Teacher-mixed sampling draws each token from a mix of the teacher's and the student's distributions. Without these, the student learns to output "repeated, short, or meaningless strings" that the teacher scores highly (reward hacking) (§3.4).
- **MiniLLM's cost is high.** Distilling LLaMA-7B from LLaMA-13B took "less than 10 hours on 16 GPUs" (V100 32 GB) (App. B.1).
- **MiniLLM's evaluation does not fit our task.** It is instruction following scored by Rouge-L and GPT-4 feedback. The paper reports no math or multilingual task.
- **MiniLLM Table 1 parses badly in our copy.** Rows do not match their method labels, so this note cites no cell from it.
- **DistilBERT distillation ran at pre-training scale.** It took about 90 hours on 8 × 16 GB V100 (§3). DistilBERT is an encoder evaluated on classification and QA, not on generation.
- **DistilBERT reports two different numbers for SQuAD with distillation during fine-tuning.** The text gives "79.8 F1 and 70.4 EM" (§4.1). Table 2 gives 79.1 EM / 86.9 F1.
- **Hinton's experiments are classification only** (MNIST, speech frames, JFT images).

**What this means on the UNO Q.**

- **The objective changes training only, not the board.** Whatever we choose, the board runs the same GGUF student in llama.cpp. Inference cost does not change.
- **SFT on teacher-written explanations (SeqKD) comes first.** It is the only option that works with any teacher, including Salamandra 7B. It is also what TinyGSM and Li 2025 did.
- **Logit distillation comes second, and only with a teacher that shares the student's vocabulary.**
    - Storing full teacher distributions over a vocabulary of about 256k tokens ([CHALLENGE_CONTEXT §3](../../../CHALLENGE_CONTEXT.md#3-base-model-candidates)) for every training token is heavy. Running teacher and student side by side on the RTX 4060 is the alternative. These papers measure neither cost. Measure it.
- **Skip MiniLLM's on-policy reverse KL for now.** It needs an RL loop with student rollouts, a teacher in memory, and three stabilization tricks. Fig. 7 shows its advantage on responses longer than about 6 tokens, which our explanations are.
- **A general-text loss term may protect language skills.** MiniLLM's L_PT result (Table 7) suggests this. Mixing in plain multilingual text (Catalan, Spanish) may protect the language skills that tutoring SFT would erode. This is our extrapolation, not a tested claim.
- The order in which to try these is in [What to try](#what-to-try).

**Open questions.**

- Does logit distillation beat SeqKD for math explanations in Catalan? None of these papers tests math generation with logit distillation.
- What temperature should we use for a vocabulary of about 256k tokens? Hinton's temperatures come from MNIST (10 classes) and a speech model with 14,000 output labels (§3–4).

## J2: Parameter-efficient fine-tuning on a laptop GPU

**Question.** Our training GPU is an 8 GB RTX 4060 in a team member's laptop (see [CHALLENGE_CONTEXT](../../../CHALLENGE_CONTEXT.md#team-hardware)). Which fine-tuning method, rank and target modules should we use there for a 270M–1B student? How do we get a merged model into GGUF? Is LoRA enough to recover a pruned model?

**How the papers relate.**

- **QLoRA extends LoRA.** It freezes a 4-bit NF4 (NormalFloat 4) base model and backpropagates through it into LoRA adapters.
- **They disagree on which modules to adapt.**
    - LoRA, on GPT-3 175B, finds W_q + W_v enough under a constant parameter budget (§7.1).
    - QLoRA, on LLaMA-7B with Alpaca, finds that matching full fine-tuning needs adapters on all linear layers (§4, Fig. 2).
    - QLoRA's setup (decoder-only, instruction SFT, generative output scored by Rouge-L) is closer to ours, so its finding should guide us.
- **They agree that rank barely matters.**
- **Li 2025 does not use LoRA below 14B.** It used full-parameter SFT for students under 14B and LoRA only above (§3.1, App. A.2). So [J3](#j3-training-data-for-small-model-math-reasoning)'s small-model findings are full fine-tuning results.

**Key evidence.**

- **LoRA mechanism.** W = W₀ + BA, with B initialized to zero and the update scaled by α/r. Here α is LoRA's scaling constant, not the mix weight α of J3. After training, BA can be added into W₀, which gives "no additional inference latency" (§4.1).
- **LoRA memory, GPT-3 175B.** Training VRAM dropped from 1.2 TB to 350 GB. The checkpoint shrank from 350 GB to 35 MB with r = 4 on W_q and W_v (§4.2).
- **LoRA target modules (GPT-3, 18M-parameter budget, Table 5).**
    - W_q alone at r = 8: 70.4 on WikiSQL (a text-to-SQL task).
    - W_q + W_v at r = 4: 73.7.
    - All four attention matrices at r = 2: 73.7.
    - Conclusion: spread the rank over more matrices instead of raising it on one matrix (§7.1).
- **LoRA rank.** For W_q + W_v, r = 1 gave 73.4 on WikiSQL and r = 64 gave 73.5 (§7.2, Table 6). On GPT-2 Medium, the best rank was "between 4 and 16" depending on the metric. The authors say the link between model size and optimal rank "is still an open question" (App. H.2).
- **LoRA with little data.** On MNLI (a sentence-pair inference task) with 100 training examples (GPT-3), LoRA scored 63.8 against 60.2 for full fine-tuning. With 1k examples they were comparable: 85.6 vs 85.8 (App. F.3, Table 16).
- **LoRA scope.** The paper adapts attention weights only and leaves MLP, LayerNorm and biases "to a future work" (§4.2).
- **QLoRA components (§3).**
    - **NF4:** a 4-bit data type built from normal-distribution quantiles.
    - **Double quantization:** quantizes the quantization constants. Per-parameter overhead falls from 0.5 to 0.127 bits, a saving of 0.373 bits per parameter.
    - **Paged optimizers:** use NVIDIA unified memory to survive memory spikes.
    - Storage is NF4. Compute is BF16.
- **QLoRA matches BF16, including at small sizes.** On Super-NaturalInstructions with T5 (Table 3, Rouge-L):

| T5 size | BF16 full fine-tuning | QLoRA NF4 + DQ |
|---|---|---|
| 80M | 40.1 | 40.4 |
| 250M | 42.1 | 42.7 |
| 780M | 48.0 | 47.7 |
| 3B | 54.3 | 55.3 |

- **Data type matters.** Mean Pile-CC perplexity across 125M–13B models: Int4 34.34, FP4 (E2M1) 31.07, NF4 + DQ 27.41 (§4, Table 2).
- **QLoRA hyperparameters (App. A.1, B.2).**
    - r = 64, LoRA α = 16, adapters on all linear layers.
    - LoRA dropout 0.1 for models up to 13B.
    - Constant learning-rate schedule, max grad norm 0.3.
    - "LoRA r is unrelated to final performance if LoRA is used on all layers" (App. A.1, Fig. 4).
- **QLoRA: train on the response only.** MMLU (Massive Multitask Language Understanding) is a multiple-choice knowledge test. On LLaMA-7B, mean 5-shot MMLU was 38.6 with loss on the target only. With loss on instruction and target, it was 37.5 (App. B.3, Table 10). The authors did not measure chatbot quality for this ablation.
- **QLoRA: data quality beats data size.** A 9k-sample dataset (OASST1) beat a 450k subsample of FLAN v2 on chatbot performance (§1). More data or more epochs moved MMLU by only 0.0–0.5 points. Switching datasets moved it by 1.5–8.0 (App. B.4).
- **QLoRA memory.** Full 16-bit fine-tuning of LLaMA 65B needs more than 780 GB. QLoRA needs less than 48 GB (§1). A 33B model "does not quite fit" into 24 GB without paged optimizers, measured at batch size 1, sequence length 512, with gradient checkpointing (App. G).

**Negative results and limits.**

- **QLoRA's default-LoRA failure.** LoRA on query and value only did not reach full fine-tuning on LLaMA-7B (§4, Fig. 2).
- **QLoRA scale limits.** It did not show that QLoRA matches full 16-bit fine-tuning at 33B and 65B (§8). It did not test 3-bit bases (§8).
- **QLoRA paging.** It gives no hard measurements of paged optimizers, because paging is "rare" (§4).
- **LoRA rank evidence comes from huge models** (GPT-3 175B, GPT-2 M/L). LoRA's own module ablation covers attention weights only.
- **QLoRA trains against NF4 weights.** Deployment is GGUF Q4_0/Q4_K, a different quantizer. Neither paper tests merging NF4-trained adapters into a BF16 base and re-quantizing to another format.
- **No paper here gives training memory for a 270M–1B model or for an 8 GB GPU.**

**What this means on the UNO Q.**

- **BF16 LoRA on all linear layers is the first choice.** Rank barely matters when adapters cover all layers (QLoRA App. A.1). The recipe is in [What to try](#what-to-try).
    - Our own arithmetic, not from the papers: 1B parameters × 2 bytes ≈ 2 GB of BF16 weights. This plausibly fits in 8 GB with adapters, activations and gradient checkpointing. Measure peak VRAM on the RTX 4060 before deciding.
- **Use QLoRA only where BF16 does not fit.** The likely case is fine-tuning a 4B teacher on the laptop. Our arithmetic: 4B × 2 bytes ≈ 8 GB in BF16 alone, which leaves no room. QLoRA Table 3 shows NF4 costs nothing at T5 sizes from 80M to 3B, so it is safe to use if needed.
- **Full fine-tuning of the 270M model is also an option.** Li 2025 used full-parameter SFT for all students under 14B (App. A.2). We did not test LoRA against full fine-tuning on our data.
- **LoRA adapters cost nothing on the board after merging** (LoRA §4.1). The export steps are in [What to try](#what-to-try).
- **LoRA as recovery after pruning.** The pruning papers use LoRA, QLoRA or distillation to heal a pruned model: see Links to other folders. LoRA itself has no pruning experiments.
    - With structured pruning, the merged BA stays dense inside the smaller matrices, so merging is safe. This is our reasoning, consistent with [CHALLENGE_CONTEXT §6](../../../CHALLENGE_CONTEXT.md#6-fine-tuning).

**Open questions.**

- Which rank and which modules are best at 270M? Both papers leave the link between model size and rank open.
- Does LoRA preserve Catalan/Spanish fluency better than full fine-tuning on a small model? Not tested here.
- Does fine-tuning after quantization recover GGUF Q4_0 losses the way QLoRA recovers NF4 losses (§4, Table 3)? The quantization-aware training link below is the closer evidence.

## J3: Training data for small-model math reasoning

**Question.** What should our SFT explanations look like: length, style, which teacher wrote them, how many? The board decodes about 4.8 tok/s, and one problem has 60 s, including the time to read it. So the budget is about 150–250 output tokens.

**How the papers relate.**

- **Both use synthetic data from a stronger model.** TinyGSM shows that a large, clean, synthetic dataset can push 125M–1.3B models far on grade-school math. Li 2025 shows that what the teacher writes matters: small students learn worse from long or "too strong" chains of thought.
- **They answer different questions.** TinyGSM is about volume and test-time selection (verifier). Li 2025 is about trace complexity and mixing.
- **QLoRA adds a general point:** dataset suitability beats size (App. B.4).

**Key evidence.**

- **TinyGSM dataset.** 12.3M GSM8K-style problems with Python solutions, 1.8B tokens, all generated by GPT-3.5-turbo from the 7,473 GSM8K training problems. About a third are variants with irrelevant information added (§1, §3).
- **TinyGSM filtering is weak.** The authors removed problems that were too short, had no numbers, or had code that did not run. They did not check correctness. They rejected majority-vote filtering because it kept only easy problems (§3).
- **TinyGSM results.**
    - Phi-1.5 1.3B went from 44.6% to 68.2% on GSM8K after SFT on TinyGSM (§1).
    - The 125M model reached 63.1% (§1, Table 1). Appendix B Table 2 gives 63.3 for the same model.
    - Training: Adam, FP16, max learning rate 1e-4, effective batch 1024, up to 20k steps (§4.1).
- **TinyGSM: pretraining helps.** Pretrained initialization beat random initialization by about 10 points at every size. The scores are 63.3 vs 53.1 at 125M and 68.2 vs 57.3 at 1.3B (App. B, Table 2).
- **TinyGSM: diminishing returns from data.** Going from about one third to two thirds of TinyGSM gave about +10%. The last third gave "only marginal gain" (§4.2).
- **TinyGSM verifier.** The 1.3B generator + 1.3B verifier choosing among 48 samples reached 81.5%, above the GPT-3.5 teacher's 77.4% (§1, Fig. 4). Details:
    - **The verifier is the more efficient place to add parameters.** 125M generator + 1.3B verifier: 76.1%. 1.3B generator + 125M verifier: 71.7% (§4.2, Fig. 4).
    - **Generator scaling helps less.** From 125M to 1.3B it adds +5.1% (§1, Table 1). §4.2 says "6%" for the same comparison.
    - **Verifier data diversity matters.** Generations from several checkpoints raised accuracy from 78.9% to 81.5% (§4.2).
    - **Verifiers transfer across generators.** A 350M verifier with the 1.3B generator gave 78.1% (§4.2).
- **TinyGSM contamination check.** 22 of 11.0M unique questions had a 13-gram match with the GSM8K test set. About 0.35% had 8-gram matches (§5.1).
- **Li 2025: the learnability gap.**
    - **Setup.** Students fine-tuned on 7,500 MATH prompts. Average over MATH, GSM8K, AMC 2023, AIME 2024 and OlympiadBench, greedy decoding, max 16k tokens (§3.1).
    - **Short CoT beats long CoT for small students** (Table 1, below).
    - **Long CoT starts to win at 7B and above.** Qwen2.5-7B: +1.7. Qwen2.5-32B: +13.7 (Table 1).
    - **The result is not a hyperparameter artifact.** On Qwen2.5-1.5B, short CoT (0.341 average) beat every long-CoT setting. The settings covered 2–5 epochs and learning rates 5e-6 to 1e-4, and the best scored 0.286 (App. B.4, Table 12).

| Student | Long CoT | Short CoT |
|---|---|---|
| Qwen2.5-0.5B | 14.8 | 19.5 |
| Qwen2.5-1.5B | 27.0 | 34.2 |
| Llama-3.2-1B | 15.8 | 19.5 |

- **Li 2025: Mix Distillation.**
    - **The mix.** Mix weight α (not LoRA's α) goes on the hard data, which is long CoT or large-teacher CoT. The weight 1 − α goes on the easy data. α = 0.2 was best for Qwen2.5-3B (§4.1–4.2, Fig. 6).
    - **Mix-Long result.** Qwen2.5-3B average 45.9, against 40.3 on long CoT and 43.4 on short CoT (§4.2, Table 3).
    - **Mix-Long result (Llama-3.2-3B).** 35.1, against 32.5 on long CoT and 33.1 on short CoT (Table 3).
- **Li 2025 lengths: two different measures.**
    - **Teacher training data:** short CoT averaged 432.98 tokens from the 72B teacher and 440.70 from the 3B teacher (§3.3).
    - **Student output after SFT** (Qwen2.5-3B): 3,384.7 tokens for long CoT, 575.7 for short CoT, 1,248.9 for Mix-Long (§4.2).
- **Li 2025: other factors.**
    - **Domain knowledge narrows the gap.** Qwen2.5-Math-1.5B shows a smaller gap than Qwen2.5-1.5B (§3.4, Fig. 4).
    - **Base models show a larger gap than instruct models** (§3.4, Fig. 5).
    - **The tokens that shift most are stylistic.** Words like "wait", "But" and "Let" move most after long-CoT or large-teacher SFT (§3.4, App. C).
- **Li 2025 data pipeline.** Teachers generate by rejection sampling with greedy decoding. The authors keep a pair only if both compared teachers got the answer right (App. A.2).

**Negative results and limits.**

- **No paper here tests outputs under about 400 tokens.** Li's shortest condition is a student averaging about 576 tokens.
- **No paper here tests pedagogy or languages other than English.** Li's limitations section says it covers math reasoning only, not instruction following (Limitations).
- **Li's AMC and AIME scores move in steps of a single problem.** Steps of 2.5 and 3.33 points mean about 40 and 30 items. Li reports no seed variance. Trust the MATH and GSM8K deltas more than the AMC and AIME ones.
- **Li's small-model results use full-parameter SFT** (App. A.2), not LoRA.
- **TinyGSM's verifier works at test time with 48 samples per problem.**
- **TinyGSM's code-format solutions are weaker on equations.** They "tend to perform worse at questions that require equation solving" (§6). The paper leaves combining code and natural language to future work (§6).
- **TinyGSM's verifier is opaque.** Its token-level scores are "rather strange" on some generations. The authors say it "relies on special patterns of the model generations that may not be universally generalizable" (§4.2, Fig. 5).
- **Most of TinyGSM's volume is not available to us.** It used 12.3M generated problems. M3Kang has 1,747 problems, plus whatever we synthesize.

**What this means on the UNO Q.**

- **The token budget dominates.** The [challenge brief](../../../CHALLENGE_CONTEXT.md#6-fine-tuning) assumes about 5 tok/s. On our board we measured 10.1 tok/s prefill (reading the prompt) and 4.8 tok/s decode (writing) ([UNO_Q_BOARD_REFERENCE §14.3](../../../UNO_Q_BOARD_REFERENCE.md#143-speed)).
    - A problem has 80–300 tokens ([BOARD_SETUP step 5.5](../../../BOARD_SETUP.md#55-how-fast-is-it)), so reading it takes about 8–30 s of the 60 s.
    - That leaves about 150–250 output tokens (our arithmetic). The [Jev note, J2](../jev/_synthesis.md#j2-calculation-heavy-items-and-the-value-of-reasoning) reaches the same range.
    - Li's "short CoT" student output (575.7 tokens) would take about 120 s to write. Mix-Long (1,248.9 tokens) would take about 260 s.
    - So Mix-Long and any long-CoT data are out.
    - Short, small-teacher-style explanations are the right direction, and they must be shorter than any condition tested here.
- **Use an instruct student.** Li's base-vs-instruct finding (Takeaway 5) supports starting from Gemma 3 IT, not the pretrained checkpoint.
- **Do not run a verifier on the board.** TinyGSM's best-of-48 is impossible at board speed. Our arithmetic: 48 × 200 tokens ÷ 4.8 tok/s ≈ 33 min per problem.
    - The usable form is offline, to filter the training data (see [What to try](#what-to-try)).
    - The paper does not test a verifier used only to filter SFT data.
- **Python solutions are a poor fit.** Kangaroo items are multiple choice, often geometric or logical, and the copilot must explain in prose. TinyGSM's own §6 caveat on equation-style problems also argues against code-only solutions.
- **Quality over volume.** QLoRA (App. B.4) and TinyGSM's diminishing returns (§4.2) both suggest a few thousand clean, short, verified explanations in the target language beat a large noisy set. How to keep the validation set clean is in [What to try](#what-to-try).
- **Pedagogical format.** Hints and Socratic turns come from the tutoring corpora: see [Links to other folders](#links-to-other-folders). The papers here only say to keep each turn short.

**Open questions.**

- Does the learnability gap still hold below 250 tokens? Could a 270M model need even shorter traces than a 0.5B one? Test 100-, 200- and 300-token versions of the same explanation.
- What should the mix weight α be for our budget? Li tuned α = 0.2 for a 3B student with a 16k-token cap.
- Do Kangaroo-style problems (visual, multiple choice) behave like MATH or GSM8K for CoT length? Untested.
- Language: do Catalan explanations written by a teacher that is weaker in Catalan widen the distribution mismatch (Li Takeaway 4)?

## J4: Teacher size and the capacity gap

**Question.** Which teacher should write or score the training data for a Gemma 3 270M or 1B student? The candidates are Gemma 3 4B, Gemma 3 12B, Salamandra 7B, or a mix.

**How the papers relate.**

- **They seem to contradict each other.**
    - MiniLLM: student quality rises with teacher size (§3.3, Fig. 5, App. C.2).
    - Li 2025: students of 1.5B or fewer learn better from a small teacher (§3.3).
- **The settings differ, which may explain it.**
    - **Teacher-to-student ratio.** MiniLLM's GPT-2 study uses a 125M student with teachers of 340M to 1.5B, so ratios up to about 12×. Li uses 72B vs 3B teachers for 0.5B–1.5B students, so ratios up to about 144× (our arithmetic from §3.1).
    - **Training signal.** MiniLLM trains on teacher distributions on-policy. Li trains on teacher text.
- **Hinton points the same way for logit distillation.** A much-too-small student does best at intermediate temperatures. These temperatures drop part of the teacher's information (§2.1, §3).
- **TinyGSM shows the opposite extreme.** A huge teacher (GPT-3.5) still helps 125M–1.3B students when the data is large and simple (§1).

**Key evidence.**
Li 2025, large teacher (Qwen2.5-72B) vs small teacher (Qwen2.5-3B), average score (Table 2):

| Student | Large teacher | Small teacher | Δ |
|---|---|---|---|
| Qwen2.5-0.5B | 16.9 | 20.4 | −3.5 |
| Qwen2.5-1.5B | 32.2 | 33.0 | −0.8 |
| Llama-3.2-1B | 16.5 | 18.5 | −1.9 |
| Qwen2.5-3B | 39.7 | 39.4 | +0.3 |
| Qwen2.5-7B | 48.9 | 42.3 | +6.6 |

Both teachers produced short CoT of nearly equal length (433 vs 441 tokens), so length is not the confound (§3.3).

- **Li 2025, Gemma 2 27B vs 9B teachers: mixed** (App. B.2, Table 9, average Δ):
    - Llama-3.2-1B: −1.83
    - Qwen2.5-0.5B: −0.645
    - Qwen2.5-1.5B: −0.174
    - Qwen2.5-3B: +1.29

    With Llama 70B vs 8B teachers, Qwen2.5-1.5B gets +1.11, so the sign is not stable at 1.5B.

- **Li 2025: prompting the large teacher to "simplify" does not close the gap.** Qwen2.5-0.5B scored 0.204 with the 3B teacher. With the 72B teacher and a "simpler and more concise" prompt, it scored 0.161 (App. B.5, Table 13).
- **Li 2025: perplexity shows the mismatch.** Small students assign higher perplexity to large-teacher and long CoT data. Example: Qwen-0.5B scores long CoT at 2.237 and short CoT at 1.278 (App. B.3, Table 10). Student outputs are lexically and semantically closer to small-teacher text (Table 11).
- **Li 2025: Mix-Large.** 20% large-teacher + 80% small-teacher data gave Qwen2.5-3B 45.8. The large teacher alone gave 39.7, and the small teacher alone gave 39.4 (Table 3).
- **MiniLLM.** It "constantly outperforms SeqKD" as teacher size grows, and student performance is "positively correlated with the teacher model sizes" (§3.3, Fig. 5). Some MiniLLM students beat their teacher on Rouge-L. The authors conjecture this comes from exposure bias in the teacher (§3.2).
- **TinyGSM.** GPT-3.5 (77.4% on GSM8K) as teacher: 125M–1.3B students reached 63.1–68.2% alone, and 81.5% with a verifier (§1, Table 1, Fig. 4).

**Negative results and limits.**

- **Li's teacher-size effects are a few points.** Many cells move by a single AMC or AIME problem. The Gemma 2 comparison (Table 9) is the closest same-family evidence for us, and it gives mixed results.
- **Li's tables mislabel two students.** "Llama3.1-8B/70B" in Tables 2, 7 and 9 should be Llama-3.1-8B and Llama-3.3-70B per §3.1. The Table 2 caption also says P_Long where it means P_Large.
- **MiniLLM's teacher-scaling result** uses small teachers (at most 1.5B for GPT-2, 13B for OPT) and Rouge-L on instruction following, not math.
- **No paper tests a cross-family teacher** writing in a language the student is weak in.

**What this means on the UNO Q.**

- **Default teacher for text distillation:** the smallest teacher that solves our training problems correctly in the target language, likely Gemma 3 4B. A 4B teacher to a 270M–1B student is a ratio of about 4–15×. That sits between MiniLLM's range (where bigger helped) and Li's 72B-to-0.5B case (where bigger hurt).
- **Use a larger model as a minority source.** It can supply about 20% of examples (Mix-Large, mix weight α = 0.2). Candidates are Gemma 3 12B, or Salamandra 7B for Catalan/Spanish phrasing. Filter these examples for correctness. Prompting the large model to "write simply" is not enough on its own (Table 13).
- **For logit distillation ([J1](#j1-distillation-objective-soft-targets-text-or-reverse-kl)), only a same-vocabulary teacher works.** That rules out Salamandra. Gemma 3 4B/12B qualify if they share the student's tokenizer (see [Open questions](#open-questions)).
- **Measure, don't assume.** Score candidate teacher outputs with the student's perplexity before training (Li App. B.3, Table 10). Lower perplexity predicts easier learning.

**Open questions.**

- Does the small-teacher advantage hold for 270M, below Li's smallest student (0.5B)?
- Gemma 3 4B vs 12B as teacher for Gemma 3 1B: the ratio is in between, and the Gemma 2 evidence gives mixed results. Run both on a few hundred problems.
- Is Salamandra 7B's Catalan worth the cross-family mismatch? Li's distribution-mismatch argument (Takeaway 4) predicts a cost. Language gains could outweigh it. Untested.

## Links to other folders

- **J2 (LoRA as recovery after pruning), J1 (distillation after pruning):**
    - [LLM-Pruner](https://arxiv.org/abs/2305.11627): LoRA recovery after structured pruning.
    - [Gromov et al.](https://arxiv.org/abs/2403.17887): layer dropping + QLoRA healing.
    - [Minitron](https://arxiv.org/abs/2407.14679) and [Minitron in practice](https://arxiv.org/abs/2408.11796): pruning followed by logit distillation from the unpruned teacher. This is the closest follow-up to DistilBERT's initialize-from-teacher idea.
- **J2 (fine-tuning against the deployed quantizer):** [LLM-QAT](https://arxiv.org/abs/2305.17888). It is relevant to the open question of whether NF4-trained adapters survive GGUF quantization.
- **J3 (pedagogical format of the SFT data):** [MathDial](https://arxiv.org/abs/2305.14536) and [SocraticMATH](https://arxiv.org/abs/2407.17349). See also the [tutoring and pedagogy note, J1–J2](../tutoring_pedagogy/_synthesis.md#j1-tutoring-datasets-and-their-formats).
- **J1 and J4 (tokenizer, sizes and QAT checkpoints of the student and teacher family):** [Gemma 3 report](https://arxiv.org/abs/2503.19786).

## What to try

These steps come from the junctions above, in the order to try them.

1. **SFT with BF16 LoRA ([J1](#j1-distillation-objective-soft-targets-text-or-reverse-kl), [J2](#j2-parameter-efficient-fine-tuning-on-a-laptop-gpu)).** Train on teacher-written explanations (SeqKD). Use BF16 LoRA (no 4-bit base) on all linear layers of the student, for example Gemma 3 270M or 1B IT.
    - Use a rank r between 8 and 64 (QLoRA App. A.1).
    - Put the loss on the response tokens only (QLoRA Table 10).
    - Measure peak VRAM on the RTX 4060 before deciding.
2. **Logit distillation, only with a same-vocabulary teacher (J1).** Use a soft-target loss at moderate T. Hinton found T = 2.5–4 for a much-too-small student (§3). Add a lower-weighted hard-label loss, and multiply the soft-target loss by T² (§2).
3. **A general-text loss term (J1).** Mix plain Catalan and Spanish text into fine-tuning, like MiniLLM's L_PT term (Table 7). This is our extrapolation.
4. **MiniLLM, later (J1).** Revisit it only if SFT plus logit distillation plateaus and there is GPU time left.
5. **Export to GGUF (J2).** Merge W = W₀ + BA into a BF16 or F16 base (LoRA §4.1). Convert it to GGUF. Then quantize it with llama.cpp (Q8_0, Q4_K_M, Q4_0).
    - If training used QLoRA, merge into the original BF16 weights, not into the dequantized NF4 weights.
    - Compare quality before and after quantization. No paper tests the mismatch between NF4 training and GGUF quantization (J2, Negative results and limits).
6. **Filter the training data offline ([J3](#j3-training-data-for-small-model-math-reasoning)).** On the laptop, sample several teacher or student explanations per training problem. Keep only those that reach the correct option. Li's rejection sampling (App. A.2) does the same thing with answer checking.
7. **Keep the validation set clean (J3).** Keep the validation set out of all synthesis prompts. Copy TinyGSM's 13-gram check (§5.1) as a cheap contamination test.

## Open questions

The junctions flagged these points to check. The per-junction open questions above stay where they are.

- **One tokenizer for all Gemma 3 sizes? ([J1](#j1-distillation-objective-soft-targets-text-or-reverse-kl), [J4](#j4-teacher-size-and-the-capacity-gap))** Do Gemma 3 270M, 1B, 4B and 12B share one tokenizer and vocabulary? The [Gemma 3 report](https://arxiv.org/abs/2503.19786) covers 1B to 27B, not 270M (see the [surveys note, J2](../surveys/_synthesis.md#j2-base-model-gemma-3-vs-salamandra-2b)). Read it from each model's tokenizer files. If they share one, logit distillation from Gemma 3 4B or 12B is possible. Salamandra 7B is another model family, so only text distillation is possible from it.
