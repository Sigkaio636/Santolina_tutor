---
tags: [synthesis, jev]
papers: 18
date: 2026-11-14
---
# Jev decision models: synthesis by junction

> Changes to the proposed junctions:
> - **J1 kept and narrowed** to the readout itself: letter-logit scoring of A–E against free generation, and how to present the options. The calculation cost moved to J2.
> - **J2 is new.** It covers calculation-heavy items: where one-pass scoring breaks and how much reasoning recovers. It became its own junction because 8 of the 18 papers report it, and it decides whether the readout can stand alone.
> - **J3 kept** as confidence, calibration and escalation (cascade).
> - **J4 kept** as small models on the board: size, quantization, languages, option order.
> - **J5 kept** as figures and image input.
> - Jev in the Wild feeds no decision and is listed under "Papers not covered".

Jev is TypeSafe AI's hosted "System One" decision model (early access since September 2026, version jev-1.13.0). It returns a probability for each option of a typed question (Choice, Noul yes-no, Score) instead of writing text. TypeSafe has published no paper and no weights. These 18 papers are third-party work: evaluations of hosted Jev, open Jev-style models, and systems that use one.

For the UNO Q tutor the hosted model itself is out: it runs in the cloud. What carries over is the *technique*. Read the next-token logits of the letters A–E in one forward pass and renormalize over those five. Several papers show that this works with an ordinary instruct LLM and no training. Our copilot already does the decision half of this: `copilot/llm.py` asks for one token after "Answer:" under the grammar `root ::= [A-E]` at temperature 0, which picks the most likely letter and cannot fail on format. What the papers add is (a) reading the five probabilities, not only the winner, to know when the answer is shaky, and (b) strong evidence that this one-pass mode loses heavily on problems that need calculation, so a short reasoning pass before "Answer:" is the main lever, within the 60 s per problem limit. All evidence is from GPUs and, for the claims that matter, from models of 4B parameters or more. No paper tests Gemma 3 270M/1B, llama.cpp, an ARM CPU, Catalan, Spanish or 5-option math with figures. The data we evaluate on is described on the [M3Kang dataset card](https://huggingface.co/datasets/qualcomm/M3Kang); this note contains no problem text from it.

Papers:
- Overview: [[ling2026_jev_in_the_wild_2609.30216.pdf|Jev in the Wild]] ([arXiv 2609.30216](https://arxiv.org/abs/2609.30216)), [[deusser2026_evaluating_benchmarking_jev_2609.37647.pdf|Deußer]] ([2609.37647](https://arxiv.org/abs/2609.37647)), [[li2026_decision_models_vs_llms_benchmark_2610.11978.pdf|Jev vs LLMs]] ([2610.11978](https://arxiv.org/abs/2610.11978)), [[sun2026_typesafe_not_error_free_2609.26758.pdf|Type-Safe Is Not Error-Free]] ([2609.26758](https://arxiv.org/abs/2609.26758)).
- Math and reasoning: [[zhong2026_arithmetic_rejection_bottleneck_2609.39496.pdf|Zhong]] ([2609.39496](https://arxiv.org/abs/2609.39496)), [[ye2026_numericjev_2609.28587.pdf|NumericJev]] ([2609.28587](https://arxiv.org/abs/2609.28587)), [[lai2026_choice2seq_2610.16191.pdf|Choice2Seq]] ([2610.16191](https://arxiv.org/abs/2610.16191)), [[li2026_jev_as_a_judge_2609.26550.pdf|JEV-as-a-Judge]] ([2609.26550](https://arxiv.org/abs/2609.26550)), [[yu2026_value_of_thinking_hybrid_2611.16961.pdf|Value of Thinking]] ([2611.16961](https://arxiv.org/abs/2611.16961)).
- Images: [[yu2026_visual_jev_2609.25845.pdf|Visual Jev]] ([2609.25845](https://arxiv.org/abs/2609.25845)), [[zhu2026_intern_decision_2610.22131.pdf|Intern-Decision]] ([2610.22131](https://arxiv.org/abs/2610.22131)), [[lan2026_decisionrobust_2610.19118.pdf|DecisionRobust]] ([2610.19118](https://arxiv.org/abs/2610.19118)), [[megahed2026_beyond_clip_defect_detection_2610.41199.pdf|Beyond CLIP]] ([2610.41199](https://arxiv.org/abs/2610.41199)).
- Small and efficient models: [[rastogi2026_small_heads_strong_decisions_2611.15592.pdf|Small Heads]] ([2611.15592](https://arxiv.org/abs/2611.15592)), [[nguyen2026_llm_to_system_one_adaptive_2611.16321.pdf|NESTONE]] ([2611.16321](https://arxiv.org/abs/2611.16321)), [[li2026_flide_state_forking_2610.42148.pdf|Flide]] ([2610.42148](https://arxiv.org/abs/2610.42148)), [[imam2026_zuse_european_decision_model_2611.06238.pdf|Zuse]] ([2611.06238](https://arxiv.org/abs/2611.06238)), [[li2026_so_arena_2611.15777.pdf|SO-Arena]] ([2611.15777](https://arxiv.org/abs/2611.15777)).

Reading notes: the PDFs were converted with MinerU, except DecisionRobust (read from the PDF text). Some tables came out of the parser misaligned: Deußer Table 5, Zhong Table 2, SO-Arena Table 2 (math columns), Li Table 4. Where that happened the note says so, and the numbers were matched to the prose.

## Junctions at a glance
| Junction | Papers | Decision it informs |
|---|---|---|
| J1: Letter-logit scoring vs generating the answer (ours already uses a grammar) | [[deusser2026_evaluating_benchmarking_jev_2609.37647.pdf\|Deußer]], [[rastogi2026_small_heads_strong_decisions_2611.15592.pdf\|Small Heads]], [[li2026_flide_state_forking_2610.42148.pdf\|Flide]], [[sun2026_typesafe_not_error_free_2609.26758.pdf\|Type-Safe]], [[yu2026_visual_jev_2609.25845.pdf\|Visual Jev]], [[yu2026_value_of_thinking_hybrid_2611.16961.pdf\|Value of Thinking]] | Whether `copilot/llm.py` should also return the five letter probabilities, and how the options are written in the prompt |
| J2: Calculation-heavy items and the value of reasoning | [[li2026_decision_models_vs_llms_benchmark_2610.11978.pdf\|Jev vs LLMs]], [[zhong2026_arithmetic_rejection_bottleneck_2609.39496.pdf\|Zhong]], [[ye2026_numericjev_2609.28587.pdf\|NumericJev]], [[lai2026_choice2seq_2610.16191.pdf\|Choice2Seq]], [[li2026_so_arena_2611.15777.pdf\|SO-Arena]], [[yu2026_value_of_thinking_hybrid_2611.16961.pdf\|Value of Thinking]], [[deusser2026_evaluating_benchmarking_jev_2609.37647.pdf\|Deußer]], [[li2026_jev_as_a_judge_2609.26550.pdf\|JEV-as-a-Judge]] | Whether to reason before answering, and how many tokens of reasoning the board can afford |
| J3: Confidence, calibration and escalation | [[li2026_jev_as_a_judge_2609.26550.pdf\|JEV-as-a-Judge]], [[yu2026_value_of_thinking_hybrid_2611.16961.pdf\|Value of Thinking]], [[deusser2026_evaluating_benchmarking_jev_2609.37647.pdf\|Deußer]], [[zhong2026_arithmetic_rejection_bottleneck_2609.39496.pdf\|Zhong]], [[imam2026_zuse_european_decision_model_2611.06238.pdf\|Zuse]], [[rastogi2026_small_heads_strong_decisions_2611.15592.pdf\|Small Heads]], [[zhu2026_intern_decision_2610.22131.pdf\|Intern-Decision]] | Whether a fast answer can be trusted, when to switch to reasoning or a larger model, how to fit the threshold |
| J4: Small models on the board | [[rastogi2026_small_heads_strong_decisions_2611.15592.pdf\|Small Heads]], [[imam2026_zuse_european_decision_model_2611.06238.pdf\|Zuse]], [[li2026_flide_state_forking_2610.42148.pdf\|Flide]], [[nguyen2026_llm_to_system_one_adaptive_2611.16321.pdf\|NESTONE]], [[li2026_so_arena_2611.15777.pdf\|SO-Arena]], [[zhu2026_intern_decision_2610.22131.pdf\|Intern-Decision]] | Base model and size, LoRA or not, quantization, language coverage, option-order robustness |
| J5: Figures and image input | [[yu2026_visual_jev_2609.25845.pdf\|Visual Jev]], [[zhu2026_intern_decision_2610.22131.pdf\|Intern-Decision]], [[lan2026_decisionrobust_2610.19118.pdf\|DecisionRobust]], [[megahed2026_beyond_clip_defect_detection_2610.41199.pdf\|Beyond CLIP]] | Whether a vision model on the board is worth its RAM for figure problems |

## J1: Letter-logit scoring vs generating the answer

**Question.** Can we skip text generation, read the probabilities of A–E directly, and so stop the small model from failing on output format? What does it cost, and how should the options be written?

**How the papers relate.** They agree on the method, found independently. Deußer uses it as the open-model baseline. Flide uses it with untrained instruct models. Small Heads shows a trained letter readout ties more complex heads. Visual Jev and Intern-Decision use it for vision-language models. Value of Thinking reads the letters both with and without reasoning. Type-Safe is the caution: a valid answer is not a correct one.

**Key evidence.**
- *The recipe.* Prompt with the problem, options written "A: …" to "E: …", and an instruction to reply with the letter only. Close the turn with thinking disabled. Read the next-token logits of the option letters and softmax over just those (Deußer §3.6; Flide App. C, Fig. 6, Eq. 1). This needs no training and no decoded tokens.
- *Format loss is negligible, at 4B and above.* Instruct models put a median 1.000 (Gemma-4-E4B, about 4B effective) and 0.997 (Qwen 27B) of next-token mass on the valid codes, and at least 0.93 on 99% of questions (Deußer §3.6). Renormalizing therefore discards almost nothing.
- *It works zero-shot at 0.8B on reading comprehension.* Qwen3.5-0.8B reaches 66.4–67.2% on RACE-M, against about 88% for 4B (Flide Table 4). On long QuALITY articles 0.8B gets 38.3–39.5%.
- *A head adds nothing over the letters.* On Qwen3-0.6B, five readouts all land at 81.3–82.0% in-domain after LoRA training. The letter readout (0 new parameters) is best out-of-domain: 79.4%, +1.41 points over the cosine head (Small Heads Table 3). Visual Jev finds the same at 4B: 0.761 for both (Table 2).
- *Uppercase letters are the best codes.* On Belebele (options A–D) the letter readout beats the cosine head by +9.8 (76.1 vs 66.3). Swapping the codes read at evaluation gives 76.1 uppercase, 72.3 number words, 67.4 lowercase, 59.3 symbols (Small Heads Table 5). The authors attribute this to the pretraining prior over letters.
- *Never use the numbers themselves as option keys.* Deußer switched to letter keys after the key "36" matched the answer to an atomic-number question (§3.3). Type-Safe App. E shows a model picking the option *named* "0" over the one whose content is the correct value. Kangaroo answers are often numbers.
- *Option names drive the decision.* When names and definitions conflict, hosted Jev follows the name in 32.5% of yes/no cases, the open Laya model in 76.9% (Type-Safe Table 1). Renaming multi-option labels to A, B, C changed 52.4% of Laya's decisions (Table 5, low-baseline, "directional").
- *Letters carry a positional prior.* The prior does not match where answers sit, and differs by backbone. Value of Thinking App. D suggests content scoring with SUM, MEAN or PMI normalization. Averaging over option orders is the other mitigation (JEV-as-a-Judge §7.3, Zuse Table 5; see J4).

**Negative results and limits.**
- The format result is shown at 4B and above. No paper tests a 270M or 1B model on the letter mass.
- Type-Safe's name–definition study is on binary business questions, English only, with encoders, not decoder LLMs.
- Small Heads uses one seed and English sources only.

**What this means on the UNO Q.**
- The format failure from the benchmarks synthesis J3 is already handled in our pipeline: `copilot/llm.py` `answer_letter` sends `grammar: "root ::= [A-E]"`, `max_tokens: 1`, `temperature: 0` after "\nAnswer:". Under greedy decoding this returns the argmax over the five letters, the same decision as the papers' letter readout. No change is needed for format.
- What is missing is the probabilities. Ask llama-server for the top-token probabilities of that one token (its `n_probs` option; check the name and output in the board's build) and keep all five. J3 needs them for confidence, hints and escalation. This is our inference; no paper uses llama.cpp.
- The grammar hides how much mass the model puts outside A–E. Measure it once without the grammar on a dev set: if it is far below the 0.93 floor seen at 4B, the letter choice is close to a forced guess, and a short LoRA trained on the letter logits is the fix (J4).
- Keep the options as uppercase letters with the numeric answer as content, never as the key. `format_problem` in `copilot/llm.py` already writes "A) <content>", which fits.

**Open questions.**
- Does Gemma 3 1B (or 270M) put most of its next-token mass on A–E when told to answer with a letter? The data stops at 0.6–0.8B with Qwen.
- Are the letter tokens single tokens in Gemma's vocabulary with and without a leading space? Check the tokenizer before reading logits.

## J2: Calculation-heavy items and the value of reasoning

**Question.** Kangaroo answers almost always have to be *derived*. How much does a one-pass letter readout lose there, and how much does reasoning first recover?

**How the papers relate.** They agree, from different angles. One-pass decisions hold when the answer can be read off the text and fail when it must be computed (Zhong, JEV-as-a-Judge, Choice2Seq, NumericJev, SO-Arena). Reasoning closes most of the gap (SO-Arena, Value of Thinking). The only apparent conflict is about hosted Jev: Deußer finds it strong on MMLU calculation subjects, Jev vs LLMs finds it last on MathQA. Deußer suspects MMLU exposure in training, which would explain both (hedged).

**Key evidence.**
- *The gap grows with reasoning demand.* Jev trails the frontier median by −1.2 on MMLU, −7.9 on AQuA-RAT and −17.7 on MathQA, where it is below all 19 LLMs (Jev vs LLMs Table 4, Table 2). AQuA and MathQA are 5-option math word problems, the closest analogue to Kangaroo. Caveat: most compared LLMs generated reasoning, so this is not a controlled test.
- *Matched single-pass evidence.* With no reasoning for any model, calculation-heavy MMLU subjects cost Gemma-4-E4B 15.2 points (54.6 vs 69.8) and Qwen 27B 8.3 (Deußer Table 5; rows misaligned in the parse and matched by n).
- *Letter readout of a generic LLM fails on arithmetic.* On 8-way multiplication, Qwen3.5-27B scores 25.3% by option code but 98.4% when it writes the answer string; Qwen3-8B scores 15.4% by code (chance 12.5%) (Choice2Seq Table 1). On word items the code readout works (94.5–99.7%).
- *Reasoning recovers most of it.* StartLux-4B on medium+hard math: 50.8 without thinking, 92.5 always thinking, 87.5 in auto mode (SO-Arena Table 6). The thinking gain (+41.7) is far larger than the backbone gain from going to 27B (+14.4) (Table 7). Qwen3.5-4B on MMLU-Pro: 0.543 fast vs 0.853 with reasoning (Value of Thinking Table 1).
- *Reasoning is expensive.* StartLux mean latency is 35.1 ms instant vs 3,084 ms in auto mode, about 88× (SO-Arena Table 5, H100). Qwen3.5-4B used 2,281 tokens and 12.3 s per MMLU-Pro question with reasoning (Value of Thinking Table 1). At a 4,096-token budget, 36.1% of 4B questions were truncated (§3.1).
- *Over-acceptance of wrong numbers.* With the correct value present, hosted Jev picks it 99% of the time; with it absent, it rejects the menu only 7% of the time on two-operation arithmetic (Zhong §4.2). Supplying the computed result fixes it (7→100%, §4.3). A reasoning Qwen3.5-9B scores 100% on both (§4.3).
- *Computing, not reading out, is the bottleneck.* Supplying the result raises NumericJev's within-5% rate from 80–83% to 97–100%, a gap of about 16 points for every decoder (§5.3).
- *The hybrid design.* Value of Thinking's slow mode reasons, then reads the answer from the same A–E logits after "\nAnswer:". Nothing is parsed from the generated text, and escalating from fast to slow reuses the fast pass's KV cache (App. A, C).

**Negative results and limits.**
- Every number is from 4B or larger, on GPUs. SO-Arena's math is 4-option, easier than Kangaroo's 5. Its hardest (AIME) tier sits near chance, but those columns are garbled in the parse.
- No paper covers multilingual math or figure-based math.
- Choice2Seq's code-vs-string contrast also changes the prompt format, and has no letter-prior correction.

**What this means on the UNO Q.**
- Our current `answer_letter` is the fast-only mode these papers find weakest on derive-type items: one token, no reasoning. Keep it as the baseline and fallback; it is the lower bound.
- Add a slow mode modelled on Value of Thinking: generate a short reasoning text, append "\nAnswer:", then make the same grammar-constrained one-token call. With `cache_prompt: True` the problem prefix is not recomputed.
- The budget is tight. The limit is 60 s per problem, after which `predict.py` answers D with status `timeout` (`config.env` `TIME_LIMIT_SECONDS=60`). Measured on the board: prefill about 11–12 tok/s, so a 80–300 token problem costs 7–25 s; decode about 5–6 tok/s, so 200 tokens cost 35–40 s (`docs/GUIA_RESTRICCIONES_UNOQ.html`, from BOARD_SETUP §5.5). That leaves room for roughly 150–250 reasoning tokens on a short problem and very few on a long one, far below the 2,000+ tokens the papers use.
- So measure on the board: accuracy and seconds per problem at 0, 64, 128 and 192 reasoning tokens, each followed by the letter call, split by prompt length. Cap the budget per problem from its prefill length so no problem times out.

**Open questions.**
- Does a 1B model gain from short reasoning at all, or does it need hundreds of tokens before it helps? All the gains above are at 4B and above.
- Do figure items and text-only items gain differently from reasoning? No paper splits by this.

## J3: Confidence, calibration and escalation

**Question.** Can the probabilities from the letter readout tell us when the fast answer is wrong, so the tutor reasons, gives a hint, or hands over to a larger model only then?

**How the papers relate.** They agree that the probabilities carry signal even when the argmax is wrong (Zhong, JEV-as-a-Judge, Value of Thinking). They also agree that thresholds must be fitted on local labels and do not transfer between workloads (JEV-as-a-Judge, Zuse, NESTONE, Intern-Decision). Value of Thinking's learned router beats a plain confidence threshold only modestly. Deußer adds the warning that small models are overconfident.

**Key evidence.**
- *Small models are overconfident.* Pooled Choice ECE: Jev 0.028, Qwen 27B 0.063, Gemma-4-E4B 0.208. Gemma's mean top probability is 0.936 at 72.8% accuracy, and its confidence separates right from wrong poorly (Deußer §4.3, Fig. 4).
- *Confidence is weaker where the answer is derived.* JEV-as-a-Judge AUROC: 0.88 on read-off verdicts, 0.73 on reasoning and math, 0.57 on IFEval (§7.1, §9). In Deußer's FrozenLake test the top probability for right and wrong moves differed by at most 0.06 (App. E).
- *The cascade works but escalates a lot on derive-type tasks.* At τ=0.9 a frozen cascade scores 93.4% vs 92.5% for the strong model alone, escalating 31.5% at 41.4% of the cost. On JudgeBench (knowledge, reasoning, math) it escalates 65%; prospectively 68–89% (JEV-as-a-Judge Tables 3–5).
- *Fit the threshold with a lower-bound rule and about 100 labels.* A point estimate loses more than 2 points in 40–50% of resamples; a lower-bound rule with about 100 labels cuts that to about 5%, and per-workload thresholds to 0.6% (JEV-as-a-Judge §8).
- *Threshold the reject probability, not the argmax.* Rejecting when p(NONE) ≥ 0.03 lifts correct rejection on arithmetic from 7% to 79% while selection drops only from 99% to 97% (Zhong Table 2, rebuilt from prose; τ fitted on 20 dev problems). Renaming or moving the NONE option did not help (§4.5).
- *A learned router is only modestly better than confidence.* Tokens needed to reach 90% of always-thinking accuracy, 4B: 792 for the router vs 945 for a confidence threshold (Value of Thinking Table 6). At 27B the router keeps 0.987 vs 0.991 with 54% escalated (Table 2).
- *Temperature scaling helps but does not transfer.* One temperature fitted on held-out rows gives ECE about 0.033 in-domain (Small Heads Table 3). Temperatures are tied to one checkpoint, backend and precision (Intern-Decision Table 8; Visual Jev Table 11). Miscalibration follows the task, not the language: knowledge tasks are overconfident, grammar underconfident (Zuse §6.3). Temperature scaling helped one workload and hurt two others in JEV-as-a-Judge (§7.2).
- *Small first stages are useless as gates.* The 421M Laya is near chance on judging pairs, with confidence AUROC 0.48–0.53, so a cascade escalates almost everything (JEV-as-a-Judge App. M).

**Negative results and limits.**
- Errors both models share cannot be fixed by escalation (15 of 75 on JudgeBench, JEV-as-a-Judge, limitations).
- Value of Thinking's router evidence is one seed for Table 5, and its 4B routed latency (0.179 s) is oddly lower than fast-only (0.226 s).

**What this means on the UNO Q.**
- Before building any cascade, measure the AUROC of the 1B model's top letter probability on a labelled Kangaroo dev set, split by language and by figure vs text-only. If it is near 0.5, as for Laya, a gate will not work.
- Fit one temperature and one threshold on our dev split, for the exact quantized GGUF that runs on the board. Do not reuse published temperatures. Use a lower-bound rule with about 100 labels.
- The likely cascade on the board is fast readout → short reasoning when unsure, not small → large model: a second model costs RAM. The same threshold can also decide when the tutor offers a hint instead of an answer.

**Open questions.**
- Does Gemma 1B's confidence carry any signal on Kangaroo items, given the ECE 0.208 at 4B effective?
- Does the threshold have to differ by language, given Zuse's finding that calibration error follows the task, not the language?

## J4: Small models on the board

**Question.** Which base model and size, which training (none or LoRA), what quantization, and which robustness checks for an A–E readout on a 4-core A53 with 2–4 GB RAM?

**How the papers relate.** The backbone dominates the head and the recipe in every paper that tests it (Small Heads, Zuse, SO-Arena, NESTONE). Math is the exception: there reasoning beats a larger backbone (SO-Arena). Small Heads and Flide agree that the letter readout and causal models are the right choice. Flide warns that packing several items in one prompt shifts the probabilities of untrained models.

**Key evidence.**
- *Size matters more than the head.* With the same head, in-domain / held-out: Qwen3-0.6B 82.0 / 78.0, Qwen3-1.7B 84.3 / 83.1, Qwen3-4B 85.9 / 88.9, Gemma 4 E2B 85.0 / 85.6 (Small Heads Table 7). Base, instruct and thinking checkpoints of one model tie within about 0.25 points (Tables 8–9).
- *Smallest working points.* Qwen3-0.6B at 82% in-domain after LoRA (Small Heads); Qwen3.5-0.8B at 66–67% on RACE-M zero-shot (Flide); Intern-Decision-0.8B at 79.38% average, 52.25% on Jevbench-Hard (Intern-Decision Table 3); Laya 0.4B at 30.9 on SO-Arena (Table 2).
- *LoRA recipe.* Rank 32, α=64, all attention and MLP projections, cross-entropy on the code logits, 2 epochs; a third epoch cost 0.7–2.0 points out-of-domain (Small Heads §3.4, §4.3). Shuffle option order per row (Nimble, cited in Small Heads §2.2). A permutation-consistency loss cut order flips from 10.5% to 6.8% at about −1.5 accuracy (Zuse §7.4).
- *4-bit is nearly free, at 4B and above.* Accuracy −0.1 to −0.6, ECE almost unchanged (Zuse Table 5).
- *Language reach comes from the base model.* Languages outside Qwen's documented list trail by 23–28 points at every size (Zuse Table 6). Base choice outweighed parameter count: EuroLLM-22B scored below Qwen3.5-4B (§7.1, hedged by the author).
- *Order sensitivity concentrates on wrong answers.* Small models (Laya S=0.35, several 4B models S=0.68–0.72) are order-sensitive, and flips cluster on items the model gets wrong (SO-Arena §4.1.2, Fig. 8b). Averaging two orders cut Zuse's flips from 3.7% to 3.3% (Table 5).
- *Do not pack items with delimiters.* SGLang's multi-item scoring changed up to 28.9% of Qwen3.5-0.8B's decisions at a 0.5 threshold; compute the shared prefix once and branch instead (Flide §4.4, Fig. 4).
- *Layer truncation does not pay at small scale.* For a 4B model, 12- and 16-layer exits lose 10–20 points (NESTONE Table 3). Late layers 24–29 can go with no loss (Table 1a), which matches Gromov et al. in the pruning folder.

**Negative results and limits.**
- No paper reports CPU, ARM, llama.cpp or GGUF numbers. All latency is on H100/H200/B300 GPUs.
- Gemma 3 is not tested anywhere; Gemma 4 E2B is the smallest Gemma.
- Zuse's weights are closed, its 27 languages are not listed in the text, and it declares a conflict of interest.

**What this means on the UNO Q.**
- Prefer 1B over 270M, and treat the choice of base model as the main lever. Check that Catalan and Spanish are in the base model's documented language list (Gemma 3 report, in the surveys folder).
- If the zero-shot letter readout underperforms, train a LoRA on the letter logits with shuffled A–E order, merge it into the GGUF, and quantize to Q4. No custom head or llama.cpp patch is needed. This is our inference from Small Heads and Zuse.
- Optional order averaging: score two orders of the options by copying the KV cache of the problem stem into a second sequence. Never put two orders in one prompt. Measure the cost on the board before adopting it.
- Do not cut layers for speed below 4B.

**Open questions.**
- Board latency of one 1B prefill for a typical Kangaroo prompt, at Q4. No paper gives an ARM number.
- Does Gemma 3 1B behave like Qwen3-0.6B/0.8B here? The only small-model evidence is Qwen.

## J5: Figures and image input

**Question.** Many Kangaroo problems have a figure, and Gemma 3 1B has no vision encoder. Is a small vision decision model worth its RAM on the board?

**How the papers relate.** Visual Jev and Intern-Decision build the same design independently: frozen vision tower, adapted language model, letter readout, several questions sharing one image. DecisionRobust attacks these models and is the only paper with diagrams (Geometry3K). Beyond CLIP is the only comparison with CLIP. None evaluates math with figures.

**Key evidence.**
- *Smallest open multimodal decision model: Intern-Decision-0.8B* (Qwen3.5-0.8B base, frozen vision tower; github.com/InternLM/Intern-Decision). Its quantified scores are text-only; image use is shown only in demos (§6).
- *Small vision decision models do poorly on geometry diagrams.* DecisionRobust never reports clean Geometry3K accuracy. From its attack rates, about 11–22 of 30 items were answered correctly before attack by the 4–8B models measured (our estimate from Table 5, 30 samples; Jev-Omni's size is not stated).
- *Text priors are strong.* With a grey image, the base Qwen3-VL-4B still scores 0.585 on converted GQA against 0.365 chance (Visual Jev Table 1). Counting (TallyQA) stays near 0.35 even after training (Table 2), which matters for Kangaroo counting figures.
- *Adaptation helps only trained task families.* Held-out TextVQA and TallyQA barely move (Visual Jev Table 2).
- *Encoding the image once pays off only with many questions.* At 32 questions per image the time per question falls from 50.7 ms to 5.7 ms; at one question, prefix sharing is slower (82.9 vs 48.1 ms) (Visual Jev Table 3). Kangaroo has one question per figure.
- *Blur hurts most.* Defocus blur is the most damaging corruption; brightness and JPEG do little (DecisionRobust Table A5).
- *CLIP zero-shot is weak.* 0.615–0.655 on binary inspection tasks with 0.5 chance (Beyond CLIP Table 2).
- *Is hosted Jev text-only?* The awesome-jev list says so, but Beyond CLIP sent images to the jev-1.13.0 API and got classifications back (§3.2, Table 2). Unresolved, and irrelevant to the board: hosted Jev is cloud-only either way.

**Negative results and limits.**
- No CPU, ARM or memory numbers for any vision model; Visual Jev's 4B needs 8.4 GiB on a GPU (Table 3).
- No math, diagram-reasoning or chart benchmark apart from DecisionRobust's tiny Geometry3K set.
- No paper measures option-order robustness for the vision models.

**What this means on the UNO Q.**
- Run a blind baseline first: score figure items with the figure removed (text only), as Visual Jev does with a grey image. If accuracy barely drops, the figure is not what limits a 1B model and a vision encoder is not worth the RAM.
- If vision is tried, Intern-Decision-0.8B is the smallest candidate, but llama.cpp support for Qwen3.5 vision via mmproj is unverified. These papers give no evidence that it helps on geometry or pattern figures.
- Feed clean, full-resolution renders of figures, never photos (blur is the main risk).

**Open questions.**
- How much of a 1B model's error on figure items is due to the missing figure? Our blind baseline answers this.
- Does any vision model that fits in 2–4 GB with llama.cpp beat text-only on Kangaroo figure items?

## Papers not covered by any junction

- [[ling2026_jev_in_the_wild_2609.30216.pdf|Jev in the Wild]]: a mining study of 2,170 GitHub projects using Jev in its first week. No accuracy data. Its only useful pattern for us: a decision model picks, a separate small LM writes the text, and the program applies a confidence gate (App. B).

## Links to other folders

- J1 (Gemma 1B format failure that the letter readout addresses): [[torrescamps2026_m3kang_2601.16218.pdf|M3Kang]], [[igualde2025_kangaroo_multilingual_visual_math_2506.07418.pdf|Igualde-Sáez]], and the benchmarks synthesis J3.
- J4 (base model and its language list): [[gemma3_technical_report_2503.19786.pdf|Gemma 3 Technical Report]], [[gonzalezagirre2025_salamandra_technical_report_2502.08489.pdf|Salamandra]].
- J4 (dropping late layers): [[gromov2024_unreasonable_ineffectiveness_deeper_layers_2403.17887.pdf|Unreasonable Ineffectiveness of the Deeper Layers]], [[men2024_shortgpt_2403.03853.pdf|ShortGPT]].
- J4 (LoRA): [[hu2021_lora_2106.09685.pdf|LoRA]].
- J5 (data with figure and text versions): [[torrescamps2026_m3kang_2601.16218.pdf|M3Kang]].
- Dataset: [M3Kang dataset card](https://huggingface.co/datasets/qualcomm/M3Kang).
