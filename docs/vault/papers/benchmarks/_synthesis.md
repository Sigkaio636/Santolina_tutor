---
tags: [synthesis, benchmarks]
papers: 2
date: 2026-11-14
---
# Benchmarks: synthesis by junction

> Changes to the proposed junctions: J1 and J2 are kept. J1 now also covers scoring without the Kangaroo penalty, the recitation check, and the "unified pool" design. J2 now opens with a comparability conflict between the two papers. The proposed J3 is split in two. The new J3 covers small models and answer-format failure. The new J4 covers how modality, level and topic confound each other, and which eval slices to report. Both new junctions have evidence from both papers.

Both papers evaluate large vision-language models on Kangaroo multiple-choice problems. Neither fine-tunes a model, and neither scores the explanation. For the UNO Q tutor they give three things: an evaluation protocol to copy (CoT prompt, last-match answer parsing, mean of runs), a warning that a 1B Gemma fails mainly on output format, and evidence that figure problems and language resource level are the two biggest accuracy confounders. The data itself is described on the [M3Kang dataset card](https://huggingface.co/datasets/qualcomm/M3Kang).

Papers:
- [[torrescamps2026_m3kang_2601.16218.pdf|M3Kang]] ([arXiv 2601.16218](https://arxiv.org/abs/2601.16218)). The challenge dataset paper (Qualcomm AI Research).
- [[igualde2025_kangaroo_multilingual_visual_math_2506.07418.pdf|Igualde-Sáez Kangaroo]] ([arXiv 2506.07418](https://arxiv.org/abs/2506.07418)). Multilingual visual Kangaroo benchmark (UPV).

## Junctions at a glance
| Junction | Papers | Decision it informs |
|---|---|---|
| J1: Two Kangaroo benchmarks side by side | [[torrescamps2026_m3kang_2601.16218.pdf\|M3Kang]], [[igualde2025_kangaroo_multilingual_visual_math_2506.07418.pdf\|Igualde-Sáez]] | Which eval protocol we copy: prompt format, answer parsing, number of runs, chance baseline, train/val split |
| J2: Language effects (Catalan, Spanish, English) | [[torrescamps2026_m3kang_2601.16218.pdf\|M3Kang]], [[igualde2025_kangaroo_multilingual_visual_math_2506.07418.pdf\|Igualde-Sáez]] | Which language to prompt and reason in, whether to translate to English first, how to compare languages fairly |
| J3: Small models and answer-format failure | [[torrescamps2026_m3kang_2601.16218.pdf\|M3Kang]], [[igualde2025_kangaroo_multilingual_visual_math_2506.07418.pdf\|Igualde-Sáez]] | Constrained decoding and format fine-tuning for Gemma 3 270M/1B, and the format-failure metric |
| J4: Modality, level and topic confounds; eval slices | [[torrescamps2026_m3kang_2601.16218.pdf\|M3Kang]], [[igualde2025_kangaroo_multilingual_visual_math_2506.07418.pdf\|Igualde-Sáez]] | Which slices to report (text-only vs figure, level, topic, language) and what a text-only model can expect |

## J1: Two Kangaroo benchmarks side by side

**Question.** How were the two benchmarks built and scored? Which parts of their protocol should our eval harness copy?

**How the papers relate.** They compete, and M3Kang follows Igualde-Sáez. M3Kang cites Igualde-Sáez ("Sáez et al. (2025)") as a related Kangaroo dataset. It agrees with Igualde-Sáez's finding that VLMs underuse diagrams. It also criticises Igualde-Sáez: each country selects different problems, so cross-language comparisons on that dataset are unfair (M3Kang §2). M3Kang answers this with a *unified pool*: one problem set translated into every language (Table 1, §3).

**Key evidence.**
- *Source and size.* M3Kang starts from the Societat Catalana de Matemàtiques PDFs, 2007–2024 editions. Each test has 24 or 30 problems (§3). After deduplication, which keeps the copy at the lowest level (§3.1), 1,747 unique problems remain. They exist in 108 languages, 104 of them in Latin script (§1, App. B.1). Igualde-Sáez compiles tests from 2014–2024 in four languages, each from a different organiser: English (Australia), Spanish (Spain), French (France) and Catalan (Comunitat Valenciana) (§3). Each test has 30 questions (§3). §3 gives no total problem count.
- *Translation and quality control (M3Kang only).* Catalan is the original. English is machine-translated, checked by an LLM-as-judge, then reviewed in full by humans. The review removed 42 mistranslations (§3.2, App. B.2). Other languages are filtered with a reference-free back-translation metric: the maximum chrF++ over several NLLB-family back-translators. The threshold is 0.625, and a "high quality" split uses 0.85 (§3.3.1, App. B.3). The metric correlates with human scores at Pearson 0.87 (Spanish), 0.85 (French), 0.73 (Korean) and 0.79 (Basque) (App. B.4, Fig. 11).
- *Inconsistent size figures in M3Kang.* §1 and §6 give 111,198 problems after filtering. Table 4 gives 108,677 (standard split) and 40,617 (high-quality split). The paper does not reconcile these.
- *Format.* Every M3Kang problem comes as both a text version and an image of the full problem. The text version exists so that evaluation measures reasoning, not OCR (§3). Igualde-Sáez stores questions in a CSV with language, options, ground truth, assigned score, grade level and a figure flag. Images are kept in a separate folder (§3).
- *Prompt and parsing.* M3Kang uses a CoT system prompt. The prompt asks for a reasoning section and then an answer line with one of five lettered options. The prompt is translated into each test language. The parser takes the *last* answer string in the output, or "N" if there is none. Accuracy is the mean of three runs (§4, §4.1, App. D). Igualde-Sáez always asks for an explanation before the answer, in the same language as the question (§3). It counts three outcomes: correct, wrong, and no answer (§4). §3–§4 do not describe how it extracts the letter.
- *No Kangaroo penalty for models.* Neither paper uses the contest's wrong-answer penalty to score models. M3Kang prompts models to always choose an option. For humans only, it scores correct answers plus one fifth of blank answers, which is the expected result of random guessing on blanks (App. C.5.1).
- *Human baseline.* Only M3Kang has one: problem-level data from more than 68,000 participants aged 10–18 in the 2024 Catalan Kangaroo, covering 114 problems (§4.5). Model scores become percentile ranks per level (Table 3, Table 9). The App. C.5.1 prose says Gemini-2.5-Pro ranks "(almost) consistently" above 99% of participants but never takes the top spot. Table 9 is weaker: in English, Gemini ranks at 86.7–97.6% on levels 0–2 and at 99.6–99.9% on levels 3–7. Igualde-Sáez states that no model reaches human-level performance (Abstract, §5). The sections read for this note report no human data behind that claim.
- *Recitation check.* Only Igualde-Sáez has one. It evaluated some models on Comunitat Valenciana tests held in the first week of April, after the models were trained. Gemini and GPT-4o scored in line with earlier years. The authors read this as reasoning, not memorisation (§5).
- *Ensembles.* Igualde-Sáez finds that strong models succeed and fail on the same problems. In 13% of cases Gemini 2.0 Flash fails where Qwen-VL 72B succeeds, and in 15% the reverse happens. The authors say this "impl[ies] a limitation" for ensembles (§4, Fig. 3).

**Negative results and limits.**
- M3Kang's translation filter leaves different numbers of problems in each language (§5). Spanish keeps 1,648 problems in the standard split and 1,368 in the high-quality split (Table 4).
- M3Kang could not replicate the human-vs-AI difficulty correlations of Cherian et al. (2024) (§4.5, App. C.5.4, Table 10).
- M3Kang excludes techniques that fine-tune models (§5).
- Igualde-Sáez prints inconsistent numbers. In Table 1, Llama 3.2 90B scores 15.0 (image) and 16.5 (text). The prose gives an overall 20%, which is above both. Pixtral-12B scores 24.5 and 27.8 in Table 1, but the prose gives 23.7%, which is below both (§4). Igualde-Sáez Table 4 (per language) is scrambled by the parser and is not used in this note.

**What this means on the UNO Q.**
- Keep M3Kang's protocol so our numbers stay comparable with Table 2: CoT prompt, last-match parsing of the answer line, "N" when no answer is found, mean over runs. Our `predict.py` contract is deterministic, so run the "three runs" over different seeds or prompt orders only in the laptop harness.
- Report accuracy against the 20% chance level. Five options make 20% the chance rate. This is our arithmetic, not a number from the papers.
- Split train and val by problem, not by row. Each M3Kang problem is the same item in up to 108 languages. A Catalan copy in train and a Spanish copy in val is a leak.
- Igualde-Sáez's GitHub data could serve as a second held-out set. Its Catalan tests come from the Comunitat Valenciana, and their committee is part of SCM (Acknowledgements). The two sets may therefore share problems. Deduplicate against M3Kang before use.
- Do not expect an ensemble of two small models on the board to help much (Igualde-Sáez §4). Each extra model also costs RAM.

**Open questions.**
- Neither paper says whether the challenge scoring penalises wrong answers. If it does, abstaining could matter, and neither paper evaluates that. Check the organisers' rules.
- What did Igualde-Sáez use as its letter-extraction rule? §3–§4 do not say.

## J2: Language effects (Catalan, Spanish, English)

**Question.** How does accuracy change across languages, Catalan and Spanish especially? Should the tutor reason in the user's language or in English?

**How the papers relate.** They partly contradict each other, and they differ in rigour. Igualde-Sáez reports a Catalan-vs-Spanish ordering that depends on the model family. Its own §4 admits that the languages are "not evaluated on the same questions", and M3Kang §2 calls such comparisons unfair. M3Kang compares languages on a shared pool, but it groups results by Internet-resource level and does not give a Catalan-specific number in the text.

**Key evidence.**
- *M3Kang: resource level drives accuracy.* For every model except Gemini-2.5-Pro, accuracy per language correlates strongly with the language's Internet presence. The correlation is stronger in smaller models, which the authors attribute "likely" to limited capacity (§4.2, Fig. 5). Of 16 evaluated languages, 12 are compared. Lingala, Tsonga, Estonian and Lithuanian are dropped because their correctly translated subsets differ significantly from the full set (App. C.3, Fig. 12).
- *Where Catalan and Spanish sit.* Spanish is high-resource at 6.00% web presence. Catalan is mid-resource at 0.102% (Table 7). In M3Kang, Catalan is the untranslated source with all 1,747 problems. English is a human-checked translation. Spanish is machine-translated and filtered (§3, Table 4). The pipeline goes Catalan → English → other languages (§3, stages 1–3), and the App. B.4 captions say "English to Spanish". So M3Kang Spanish is a two-hop translation: a lower Spanish score could reflect translation drift as well as the model.
- *Small open models, by resource cluster (Table 2, English / high / mid / low):* Qwen-2.5-3B scores 30.3 / 25.7 / 25.6 / 19.4. Phi-4 scores 28.8 / 23.7 / 22.9 / 21.3. Qwen-2.5-7B scores 40.0 / 32.1 / 30.1 / 22.0. Mid-resource (Catalan's group) is close to high-resource for these models, and English leads the high-resource average by about 5–8 points.
- *Human-percentile view.* For Kimi-Thinking-2506, going from high- to low-resource languages costs about 40–60 percentile points (§4.5, Table 3).
- *Igualde-Sáez: Catalan vs Spanish depends on model family (§4 prose).* Gemini and Llama score higher in Spanish. Gemini 2.0 Flash: 62.9 vs 61.7. Flash Lite: 53.8 vs 46.9. Llama 11B: 15.9 vs 14.1. Llama 90B: 20.7 vs 14.4. GPT and Qwen score higher in Catalan. GPT-4o: 56.0 vs 50.6. Qwen-VL 7B: 40.1 vs 32.7. Qwen-VL 72B: 59.3 vs 56.4.
- *Translate first (M3Kang §4.3, Fig. 6).* Model Tongue Reasoning (MTR) gives the model both the original question and an NLLB translation into English. It was the best technique tested, and it brought accuracy close to the English level. For Qwen-2.5-3B and Qwen-2.5-7B, it cut the gap between low- and high-resource languages from 7.1% to 2.5% and from 12.3% to 3.1%. The authors say the gains are largest "in smaller models and low-resource languages". A larger translator (600M → 1.3B → 3.3B) helped only modestly, so "smaller translators can be employed". CLSP (MTR in several languages plus a majority vote) did worse than MTR. Activation steering beat the vanilla baseline only on low-resource languages, and only modestly.
- *Steering details (App. C.4).* Steering the image tokens as well as the text hurt performance (Fig. 14). One-way steering, where the model answers in English, gave 24.9% mean accuracy on German MGSM, against 60.9% for two-way steering. Both values are means across the other configuration choices, not single runs (Table 8).

**Negative results and limits.**
- The Igualde-Sáez Catalan/Spanish gaps are confounded by problem set: each language comes from a different organiser and has different questions. Treat the family dependence as a hint, not a finding.
- M3Kang gives Catalan-level accuracy only in a chart (Fig. 5). No number is quoted here.
- M3Kang ran the Gemma family in English only, because Gemma did worse than random (§4.1). So there is **no multilingual Kangaroo evidence for Gemma 3** in either paper.
- In M3Kang's parameter-matched comparisons, MTR's parameter count includes the translator (§4.3). The paper does not report latency.

**What this means on the UNO Q.**
- Evaluate Catalan, Spanish and English on the *same* problem IDs (the intersection), never on per-language pools. The M3Kang design makes this possible for Catalan and English, which have all problems, and for most of Spanish.
- Expect a few points of loss in Catalan/Spanish against English for a small model (Table 2 pattern). Measure the loss before you design around it.
- MTR is the only multilingual technique here with a strong result. On the board it needs a translator that runs offline and fits in RAM next to the reasoner. The smallest translator tested is NLLB 600M. **Verify** that a translator of that size can run on the board, and in which runtime. Do not assume llama.cpp supports it. A cheaper variant is untested in both papers: the base model writes its own English paraphrase before it reasons.
- Activation steering maps onto llama.cpp control vectors. M3Kang's gains were modest and limited to low-resource languages, and Catalan and Spanish are not low-resource. Skip it at first.
- The tutor must *explain* in the student's language. MTR as tested only adds an English copy to the input. The papers do not say which language the reasoning output was in under MTR, so check the explanation language in our harness.

**Open questions.**
- How does accuracy compare for Catalan and Spanish on the same problems for Gemma 3 1B / 270M after format fine-tuning?
- Does putting both versions (original + English) in the prompt fit our context and time budget on the board?

## J3: Small models and answer-format failure

**Question.** How do the smallest evaluated models do? Is their failure about reasoning or about output format?

**How the papers relate.** They extend each other. M3Kang has the smallest models in either paper, including `google/gemma-3-1b-it` (Table 6), and it shows that format non-compliance decides Gemma's score. Igualde-Sáez shows the same failure mode in mid-size open models: they return "No answer" or pick at random.

**Key evidence.**
- *Gemma 3 is below chance.* In English, Gemma-1B scores 15.3 ± 0.8, Gemma-4B scores 18.8 ± 0.7 and Gemma-12B scores 18.8 ± 0.7 (Table 2). MoonDream (1.9B) scores 8.9 ± 0.7 (Table 2, Table 6). The authors attribute this to the models "not adhering to the required output format" (§4.1). The conclusion adds "likely due to limited reasoning training" (§6). Gemma-4B and Gemma-12B have identical values in Table 2, which may be a copying error in the paper.
- *Small models that follow the format beat chance.* Qwen-2.5-3B (3.8B in Table 6) scores 30.3 in English. Phi-4 multimodal (5.6B) scores 28.8 (Table 2, Table 6). Apart from Gemma and MoonDream, open-model accuracy grows with size (§6).
- *Format mismatch in Igualde-Sáez.* When a reasoned result matches none of the options, Pixtral and Llama often return "No answer". When they do not reason, they tend to pick an option at random (§5). Overall, Llama 3.2 11B Vision scores 15.7% (§4) and Llama 3.2 90B Vision scores 15.0 on image questions and 16.5 on text questions (Table 1). Both are near or below chance despite their size.
- *Prior text-only work by the same group.* Reasoner models beat non-reasoners on text-only Kangaroo problems, and some non-reasoners scored like a random-guessing student (Igualde-Sáez §1, citing their ref. [14] on Catalan). That paper is not in the vault.

**Negative results and limits.**
- Neither paper evaluates anything as small as 270M parameters. Neither tries constrained decoding or a format fine-tune, so the "format, not reasoning" claim for Gemma is the authors' diagnosis, not a measured ablation.
- The sections read for this note do not say how `gemma-3-1b-it` was given figure problems. See the Gemma 3 report for its input modalities.

**What this means on the UNO Q.**
- Format is the first thing to fix, before any compression work. Use a llama.cpp GBNF grammar: it allows a bounded reasoning section and then forces a final `Answer: [A-E]` line. Alternatively, generate the explanation first, then run a second, grammar-constrained call that emits only the letter. Either way, `predict.py` never emits "N" through a format failure.
- Report the **format-failure rate** ("N" or unparseable output) as its own metric, next to accuracy. Track it after every quantisation or pruning step. A drop in accuracy caused by format failures says nothing about reasoning.
- Include output-format compliance in the fine-tuning data (a reasoning section, then the letter), so the model does not depend on the grammar alone.
- Time budget: `predict.py` allows 60 s per problem. Gemma 3 1B decodes at about 5 tok/s on the board (`docs/CHALLENGE_CONTEXT.md` §2). That leaves roughly 300 generated tokens, before prompt processing, for the CoT and the letter. Cap `n_predict` to match, so a long chain never times out without a letter.
- Realistic target: the Table 2 numbers come from far larger VLMs. A 1B text-only model that clearly beats 20% on the text-only slice would already be a result. Compare against the `predict.py` baseline, not against Gemini.

**Open questions.**
- How much of the gap between Gemma-1B and the 20% chance level is format alone? Re-run on the val split with grammar-constrained answers to find out.
- Does a 270M model beat chance at all on text-only problems after a format fine-tune?

## J4: Modality, level and topic confounds; which slices to report

**Question.** How do figures, difficulty level and topic interact? What can a text-only model hope for, and how should we slice the eval?

**How the papers relate.** They agree, and M3Kang refines the result. Both see accuracy *not* falling as the level rises, and both link this to fewer figures at higher levels. Igualde-Sáez offers that link as a possible explanation (§4). M3Kang separates the two effects.

**Key evidence.**
- *Figures cost accuracy.* In M3Kang, every model above the English chance level does substantially better on text-only problems than on figure problems, overall and at every level (§4.4, Fig. 7). Humans in the 2024 subset show the opposite: they find figure problems easier (§4.4, Fig. 7 left). In Igualde-Sáez (Table 1, image / no image), Gemini 2.0 Flash scores 45.4 / 75.9, Qwen-VL 72B 43.5 / 70.6, GPT-4o 40.2 / 65.3 and Qwen-VL 7B 32.5 / 47.3. Weak models barely change between modalities, for example Llama 3.2 11B at 14.0 / 15.8. The authors read this as "underutilization of diagrammatic information" (Abstract, §4).
- *Composition of M3Kang.* About half the problems have a figure: 932 figure and 815 text-only (Table 11, App. C.5.2). Lower levels have a larger share of figure problems (Fig. 15). Geometry is mostly figure problems (513 of 603). Logic is split (277 of 496 have figures). Algebra (154 of 178) and Arithmetic (199 of 234) are mostly text-only (Table 11).
- *The level effect, separated (M3Kang).* On text-only problems, accuracy tends to fall as level rises (Fig. 16). On figure problems, it *rises* with level, most clearly for Gemini-2.5-Pro (Fig. 8). On manual inspection, the authors found that lower-level figure problems test visual understanding, while higher-level ones "embed the image in the text and require more abstract reasoning" (§4.5). Over the full dataset, accuracy rises with level (App. C.5.3, Fig. 17). The abstract states that performance does not scale with grade level.
- *Level effect in Igualde-Sáez.* Accuracy shows "an upward trend" with level. The authors say this "may be linked" to fewer images at higher levels (§4).
- *Topic.* M3Kang uses a VLM to label five categories, checked against human labels on 48 problems (App. C.6). The reported order is Logic ≈ Geometry < Combinatorics & Probability < Arithmetic < Algebra. The authors partly attribute the low Logic and Geometry scores to their share of figure problems (App. C.6, Table 11, Fig. 19). Igualde-Sáez labels only image questions, with five different categories. Visual Logic and Reasoning is the lowest category for every model, and no single model leads in every topic (§4, Fig. 4).
- *Failure types in Igualde-Sáez.* Models misread 3D figures, overlapping shapes, non-right angles, curvature, and measurements read off grids or scales. They do best when the figure only supports information already in the text (§5).

**Negative results and limits.**
- The difficulty levels and the topic labels in the two papers do not map onto each other. Igualde-Sáez uses each country's own levels (Table 2). M3Kang uses levels 0–7 (Table 3).
- M3Kang's topic labels come from a model and were validated on only 48 problems (App. C.6).
- Neither paper evaluates a text-only model on the text version of figure problems as a separate condition. So there is no direct number for "a text-only model on figure problems".

**What this means on the UNO Q.**
- Our model is text-only, and `data/README.md` notes that `options` is empty when OCR cannot read five text options. Expect figure problems and empty-options problems to sit near chance. Report them separately, so that they do not hide progress on the text-only slice.
- Minimum slice set for every run: `text_only` × `level` × `language` (eng/cat/spa on the same IDs), plus topic (M3Kang's five classes) and format-failure rate. Do not compare raw "by level" accuracy across levels unless it is also split by `text_only`. Otherwise the share of figure problems drives the trend.
- Spend fine-tuning and retrieval effort where text-only problems cluster: Algebra, Arithmetic, and the text-only part of Logic and Combinatorics (Table 11). Do not spend board RAM on a vision model for Geometry. Geometry and Logic are the lowest-scoring topics for large VLMs too (M3Kang App. C.6; Igualde-Sáez Fig. 4, where the best Geometry score is 45%).
- The optional vision server (port 8083 in `docs/BOARD_SETUP.md`) is not supported by these papers as a good trade on the UNO Q. The strongest large VLMs score about 25–30 points lower on figure questions than on non-figure questions (Igualde-Sáez Table 1; these are different questions). A small vision model would add RAM and latency.

**Open questions.**
- For figure problems, does a short text description of the figure (written offline, in the training data only) help a text-only model learn the reasoning pattern?
- Does M3Kang's finding that text-only accuracy falls with level (Fig. 16) also hold for a 1B model, or is a 1B model flat near chance at every level?

## Links to other folders
- [[marchisio2024_quantization_multilingual_llms_2407.03211.pdf|Marchisio 2024, quantization and multilingual LLMs]]: J2 (check that quantization does not widen the Catalan/Spanish gap) and J3 (format-failure rate after quantization).
- [[chimoto2026_calibrating_beyond_english_2601.18306.pdf|Chimoto 2026, calibration beyond English]]: J2 (language of the calibration data for the GGUF quant).
- [[jaiswal2023_llm_kick_compressing_llms_truth_2310.01382.pdf|Jaiswal 2023, LLM-KICK]]: J3 and J4 (eval slices after compression).
- [[gonzalezagirre2025_salamandra_technical_report_2502.08489.pdf|Salamandra technical report]]: J2 (base model choice for Catalan/Spanish).
- [[gemma3_technical_report_2503.19786.pdf|Gemma 3 technical report]]: J3 (the base model whose 1B variant scores below chance in M3Kang Table 2).
