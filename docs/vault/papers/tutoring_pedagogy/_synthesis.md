---
tags: [synthesis, tutoring_pedagogy]
papers: 5
date: 2026-11-14
---
# Tutoring pedagogy: synthesis by junction

This note is an explanation for the team members who design how the copilot teaches. It sums up five papers on tutoring models: what data exists, how to make a model teach instead of answer, and how to measure that. It is organized by junction: one question that several papers answer together (see the [glossary](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md)).

The copilot's deployed language model is Qwen3.5 0.8B Q8_0 ([`config.env`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/config.env)). The fine-tune base is not chosen yet. Gemma 3 is one option being explored. Where this note names Gemma 3 270M or 1B, it plans for that option.

Three tutoring corpora exist: MathDial and Bridge in English, and SocraticMATH in Chinese. None is in Catalan or Spanish. Prompting, supervised fine-tuning (SFT) and reinforcement learning (RL) each improve tutoring. Only MathDial reported results for models under 1B parameters. Bridge fine-tuned Flan-T5 and GODEL, but reported no numbers. In MathDial, a fine-tuned 780M model told students the answer far less often than prompted ChatGPT.

Every paper that measured grounding found that a tutoring model does better when it gets the reference solution. Our copilot has no such solution at inference time. The cheapest useful metric is a solution-leak rate scored by an LLM judge. Track it next to accuracy on the M3Kang validation set, and check that fine-tuning did not hurt reasoning.

## Junctions at a glance

| Junction | Papers | Decision it informs |
|---|---|---|
| J1: Tutoring datasets and their formats | [MathDial](https://arxiv.org/abs/2305.14536), [Bridge](https://arxiv.org/abs/2310.10648), [SocraticMATH](https://arxiv.org/abs/2407.17349), [Dinucu-Jianu RL](https://arxiv.org/abs/2505.15607) | Which corpus to translate or imitate for SFT, and in what record format |
| J2: Inducing pedagogical behaviour: prompting vs SFT vs RL | [LearnLM](https://arxiv.org/abs/2412.16429), Bridge, MathDial, SocraticMATH, Dinucu-Jianu RL | What to try on a 270M–1B model trained on a laptop GPU, and what to skip |
| J3: Grounding: what the tutor sees | MathDial, SocraticMATH, Dinucu-Jianu RL, Bridge, LearnLM | Whether the copilot solves first and then tutors, and what goes in the prompt |
| J4: Evaluating a tutor | MathDial, Dinucu-Jianu RL, Bridge, SocraticMATH, LearnLM | Which metrics to add to the eval harness ([CHALLENGE_CONTEXT §7](../../../CHALLENGE_CONTEXT.md#7-evaluation)) |

Papers:

- MathDial: Macina et al. 2023 ([arXiv 2305.14536](https://arxiv.org/abs/2305.14536))
- Bridge: Wang et al. 2023 ([arXiv 2310.10648](https://arxiv.org/abs/2310.10648))
- SocraticMATH / SocraticLLM: Ding et al. 2024 ([arXiv 2407.17349](https://arxiv.org/abs/2407.17349)). SocraticMATH is the dataset; SocraticLLM is the model trained on it.
- LearnLM: LearnLM Team 2024 ([arXiv 2412.16429](https://arxiv.org/abs/2412.16429))
- Dinucu-Jianu et al. 2025 ([arXiv 2505.15607](https://arxiv.org/abs/2505.15607))

## J1: Tutoring datasets and their formats

**Question.** Which public tutoring corpus can we use as SFT data for a small model that speaks Catalan and Spanish? What format should our own records follow?

**How the papers relate.**

- **They compete on how the data was made.**
    - MathDial: real teachers talk to an LLM that plays the student.
    - Bridge: real tutoring chats, annotated by experts.
    - SocraticMATH: GPT-4 writes the dialogues, then humans revise them.
- **Bridge criticizes MathDial.** It says synthetic sources give responses of "lower pedagogical quality" (Bridge §2.4).
- **SocraticMATH criticizes MathDial.** It says MathDial is not Socratic and "mainly focuses on answering students' questions" (SocraticMATH §3.2).
- **Same group.** Dinucu-Jianu comes from the same ETH group as MathDial. It drops static corpora for on-policy synthetic dialogues.
- **LearnLM releases no data.** It co-trains on Gemini's internal post-training mixture (§2).

**Key evidence.**

| | MathDial | Bridge | SocraticMATH |
|---|---|---|---|
| Size | 2,861 dialogues, 14,197 dialogic pairs (Table 1) | 700 examples, 2 expert responses each (§4.3) | 6,846 conversations (Table 2) |
| Split | 80/20 train/test, published (§5.1) | 420/70/210 (§4.3) | 5,476/685/685 (Table 2) |
| How it was made | Teachers paired with an LLM student (§3.2–3.3) | Real tutoring chats, annotated by experts (§3, §4.1) | GPT-4 drafts, revised by experts (§3.1) |
| Language | English (not stated in the paper) | English (not stated in the paper) | Chinese (Table 1) |
| Grade level | Grade-school word problems (GSM8k). The simulated student is a sixth grader (§4.1) | Grades 1–5, 120 lesson topics (§1, §4.3) | Chinese primary-school exams, 513 knowledge points (§3.1, Table 2) |
| Labels | Teacher move per turn (Table 2), solution, confusion step, resolved flag (§3) | Error type (7 options), strategy (11), intention (11) (§4.2) | Knowledge points, difficulty, solution and answer (§3.2) |
| Turn length | 17.3 words per utterance (Table 1) | Not reported | 86.45 words per utterance, about 5 turns per conversation (Table 2) |
| License | Not stated. Check [eth-nlped/mathdial](https://github.com/eth-nlped/mathdial) | Not stated. Check [rosewang2008/bridge](https://github.com/rosewang2008/bridge) | Not stated. Check [ECNU-ICALK/SocraticMath](https://github.com/ECNU-ICALK/SocraticMath) |

Details behind the table:

- **How MathDial was made.** Teachers with teaching experience were recruited on Prolific, a paid platform for research participants. Each was paired with an InstructGPT student. Student confusions are the most frequent wrong ChatGPT answer out of 50 samples per GSM8k problem (§3.2–3.3).
- **How Bridge was made.** Real chat transcripts from a US tutoring provider. 4 expert teachers built the decision model and annotated the data (§3, §4.1). The source data is used under a Data Use Agreement with FERPA constraints (§3, App. C.1). FERPA is the US student-privacy law.
- **How SocraticMATH was made.** GPT-4 pre-annotated 8,935 questions. Three experts deleted more than 23% of the dialogues and changed more than 18% (§3.1).
- **Language.** MathDial is listed as EN in SocraticMATH Table 1; the MathDial paper does not state it. Bridge raters were screened for fluent English (App. E); the paper does not state the transcript language.
- **MathDial labels.** The teacher moves are Focus, Probing, Telling and Generic (Table 2). Each record also has the solution, the step where confusion starts, and a resolved flag (§3).

- **MathDial record format.** Each record pairs a dialogue history, grounding (the problem, a step-by-step solution, the student's attempt) and a teacher move with the next teacher turn (§5.1). It maps directly to one chat-format SFT example per teacher turn.
- **MathDial data quality.** Teachers say they resolved the confusion in almost 89% of conversations: about 75% mainly with scaffolding and about 14% by revealing most of the answer (§4.3). Annotators rated about 80% of confusions as conceptual errors, not arithmetic slips (§4.1).
- **MathDial teacher-move labels are noisy.** Agreement on the four moves is κ = 0.60 between two annotators. κ (kappa) is an agreement score: 1 is perfect agreement, 0 is chance level. Merging Focus and Probing into one class raises it to κ = 0.67–0.75 (§4.2).
- **Dinucu-Jianu as a data recipe.** Their SFT baseline uses about 14k judge-accepted conversations. These came from 8 rollouts per problem on 30% of the 10k Big-Math training problems (App. A.3). The data is generated, not released as a corpus.

**Negative results and limits.**

- **MathDial:**
    - The LLM student may under- or over-represent some kinds of confusion.
    - Teachers may have acted differently once they knew the student was simulated (§8).
- **Bridge:**
    - The math question is sometimes missing from the transcript, because it was on a shared whiteboard (§9).
    - The experts are all US-based (§9).
- **SocraticMATH:**
    - The dataset is built from GPT-4 output. The authors say this is why GPT-4 beats their model on METEOR, a score of word overlap with a reference answer (§5.2).
    - This is a 6-page short paper, and it has no limitations section.

**What this means on the UNO Q.**

- **MathDial is the best fit for the SFT format.**
    - Its turns are short (17.3 words). At about 5 tok/s on the board ([CHALLENGE_CONTEXT §6](../../../CHALLENGE_CONTEXT.md#6-fine-tuning)), a turn costs a few seconds.
    - It has per-turn move labels.
    - It is the only corpus with a published sub-1B result (J2).
    - It must be translated to Catalan and Spanish. Small models are fragile at language-switching ([CHALLENGE_CONTEXT §6](../../../CHALLENGE_CONTEXT.md#6-fine-tuning)).
- **SocraticMATH: reuse the structure, not the turns.** At about 86 words per utterance, a turn likely takes too long to generate on the board. That count is on Chinese text, so the length after translation is unknown. The data is also in Chinese. Its review → guide → rectify → summarize structure is the part worth copying (§4).
- **Bridge: use the labels, not the size.** It is too small for SFT on its own (420 training examples). Its error/strategy/intention taxonomy is a good label set for our synthetic data.
- **M3Kang problems stay out of every file we commit.** We can generate MathDial-format dialogues on our own M3Kang training split, but the problem text must never enter Git. See the [M3Kang dataset card](https://huggingface.co/datasets/qualcomm/M3Kang).

**Open questions.**

- What are the licences of the three repos?
- Does translating dialogue with an LLM keep the scaffolding style, or does it drift toward telling the answer?
- Do 270M–1B models need MathDial's grade level (around sixth grade) or something closer to the Kangaroo levels?

## J2: Inducing pedagogical behaviour: prompting vs SFT vs RL

**Question.** Which method makes a model teach instead of answer, and which ones fit a 270M–1B model trained on a laptop GPU?

**How the papers relate.** The five papers sit along one axis, from prompting to RL.

- **Prompting with a decision template.** Bridge.
- **System instruction plus SFT.** SocraticMATH (prompt plus LoRA SFT) and MathDial (SFT conditioned on a move label).
- **SFT plus RL from human feedback (RLHF) on pedagogical system instructions.** LearnLM.
- **Online multi-turn RL with no human labels.** Dinucu-Jianu.

Dinucu-Jianu compares against several of the others directly: LearnLM, an SFT baseline built in the MathDial style, and SocraticLM. SocraticLM (Liu et al. 2024) is a different system from SocraticLLM (Ding et al. 2024), and it is not in the vault.

**Key evidence.**

- **Fine-tuned small models can beat prompted large models.**
    - Correctness: Flan-T5 780M scores 0.89 vs ChatGPT 0.43 (MathDial Table 5).
    - Equitable tutoring (3-point scale): 2.19 vs 1.43 (MathDial Table 5).
    - Scale was "not directly reflected in improved metrics" (automatic metrics, §6.1, Table 3). Tested models range from 125M to 3B. T5 and Flan-T5 at 780M beat their 250M versions on sBLEU, a score of word overlap with the reference response (9.0 vs 7.2, 9.7 vs 8.2), but Flan-T5 3B drops to 7.8. In human evaluation, Flan-T5 3B rates about the same as 780M (Table 5).
    - ChatGPT asked to tutor reveals the solution 66% of the time and gives incorrect feedback 59% of the time (§1, §6.3).
- **A decision template, tested only on large models** (Bridge Table 1, overall scores on −2..2, vs the novice tutor's response).
    - GPT-4: no decision 0.51, expert decisions 0.83, self-made decisions 0.84, random decisions 0.26.
    - GPT-3.5 with self-made decisions drops to 0.16, below no decision (0.28). The paper blames poor decisions: GPT-3.5 "overwhelmingly corrects" the student (§7.1, Fig. 2).
    - The paper's percentages contradict each other. For random decisions, the abstract says −97% and the introduction says −67%. Cite the Table 1 values instead.
    - Table 1 also conflicts with §7.1. The text says the overall gain from expert decisions is significant for all models. Table 1 shows Llama-2 at 0.49 with expert decisions vs 0.53 with none.
- **Prompt and grounding both help a 7B SFT model.** SocraticLLM is Qwen1.5-7B with LoRA (rank 64). Removing the Socratic prompt or the extra knowledge lowers human and GPT-4 scores (Table 3, ablation rows; see J3).
- **LearnLM: specific system instructions, then RLHF.**
    - Each SFT conversation starts with a different system instruction that describes the pedagogy present in that conversation.
    - "More general or vague instructions are counterproductive", because the model learns to ignore them (§2.2).
    - SFT "seems to improve pedagogical instruction following somewhat". RL is "significantly more effective" (§2.2). No ablation numbers are given.
    - Expert preference over Gemini 1.5 Pro, the base model: +13%. Over GPT-4o: +31%. Over Claude 3.5 Sonnet: +11% (abstract, Fig. 1).
- **Dinucu-Jianu: GRPO with a penalty λ** (Table 2). GRPO (Group Relative Policy Optimization) is an RL algorithm.
    - The tutor is Qwen2.5-7B, the student is Llama-3.1-8B, and the judge is Qwen2.5-14B. The reward is the student's solve rate minus λ when any judge rejects the conversation (§4.1, §5.3–5.4).
    - Δ solve is the gain in the simulated student's solve rate after the dialogue. Leak is the share of dialogues where a judge says the tutor gave away the solution (§5.2; see J4).
    - λ = 0: Δ solve 36.2%, leak 89.5%.
    - λ = 0.75: Δ solve 25.3%, leak 10.6%.
    - λ = 1.5: Δ solve 21.2%, leak 5.4%.
    - Baselines: their SFT gets Δ solve 8.9%, leak 36.0%. MDPO (multi-turn DPO, Direct Preference Optimization) gets 16.4%, 35.6%. LearnLM 2.0 Flash gets 4.3%, 0.9%.
    - The abstract says the model reaches "similar performance to LearnLM". Against the two LearnLM versions (Table 2, §6.1), RL at λ = 1.5:
        - nearly matches on leakage: 5.4% vs 2.6% and 0.9%.
        - exceeds on Δ solve: 21.2% vs 1.5% and 4.3%.
        - trails on Ped-RM micro: 4.4 (4.9 with thinking tags) vs 5.9 and 6.8. Ped-RM is the score of MathTutorBench's learned Pedagogical Reward Model; higher is better.
- **SFT can hurt reasoning; RL did not.** Dinucu-Jianu Table 3:
    - Their SFT baseline: GSM8K −7.5 (86.8 → 79.5) and MATH500 −9.4 (75.4 → 66.0).
    - RL-hard λ = 1.0: −0.7 and −1.8.
    - SocraticLM: −4.9 on GSM8K against its own base model.
- **Thinking tags give mixed results** (Table 2). The tutor plans in hidden `<think>` text.
    - At λ = 1.5, adding them lowers Δ solve from 21.2 to 17.0 but raises Ped-RM micro from 4.4 to 4.9.
    - At hard λ = 1.0, they raise Δ solve from 12.6 to 20.5.
    - The authors call the overall effect "slightly improved performance" (§6.1).

**Negative results and limits.**

- **Bridge §5.1 small-model failure.** The authors fine-tuned Flan-T5 (large) and GODEL. The responses were "very poor" on inspection, so the results were left out of the paper.
- **MathDial generalization gap.** Every fine-tuned model scores much lower on unseen problems than on seen ones (§6.1).
- **MathDial's small models get the teacher move as input.** The fine-tuned models are conditioned on the gold teacher move A (§5.1). So the sub-1B results in Tables 3 and 5 assume a perfect move selector. No paper here tests a small model that picks its own move.
- **Dinucu-Jianu cost and stability.**
    - Each RL run took 4×A100 80GB for about 48 h, about $400. That covered only about 20% of the training data and about 300 policy updates (App. A.1).
    - The authors say training can be unstable and sample-inefficient (Limitations).
    - Rewards come only from a single simulated student and LLM judges. Nothing is validated with real students (Limitations).
- **LearnLM's case against per-application fine-tuning.** LearnLM argues that post-hoc fine-tuning for each application is "impractical" and that prompting will likely stay the main control (§1). This applies to people building products on a large hosted model, not to our on-device case.

**What this means on the UNO Q.**

- **Try first: LoRA SFT on short, move-labeled dialogues.** The steps are in [What to try](#what-to-try).
- **Pick the teacher move with a rule, not the model.**
    - In MathDial, teachers start with Focus and Probing, and Telling rises later in the conversation (§4.2, Fig. 4). A rule based on the turn index can copy that.
    - Bridge shows that weak models make poor decisions (GPT-3.5 self-decision) and that random decisions hurt. A 270M model should not choose its own strategy.
- **Check reasoning after SFT.** Measure accuracy on the M3Kang validation set before and after fine-tuning, because SFT cost 7.5–9.4 points on math benchmarks at 7B (Dinucu-Jianu Table 3).
- **Skip online RL on the laptop.** It needs simultaneous tutor, student and judge models, and multi-GPU-days at 7B.
    - A cheap substitute: generate dialogues offline with a large model, filter them with a leak judge, then SFT. This is close to the Dinucu-Jianu SFT baseline, which is the weakest of their tuned models on leakage (36.0%). Expect less than RL gives.
- **Thinking tags: probably skip on the board.** At about 5 tok/s, every hidden token adds latency the student waits for. The evidence for them is mixed (Table 2).

**Open questions.**

- Does SFT at 270M–1B learn to withhold answers at all? The only sub-1B evidence is MathDial (Flan-T5 780M, BART, T5, OPT), with a different architecture and in English.
- Does Q4 quantization erase the pedagogical behavior that SFT adds? None of these papers tests it.
- Can DPO-style offline preference tuning on judge-labeled pairs fit on a laptop? The Dinucu-Jianu MDPO baseline did not reduce leakage compared with SFT (35.6% vs 36.0%).

## J3: Grounding: what the tutor sees

**Question.** Should a tutoring model get a reference solution in its prompt? On the board, the copilot has none for a new problem. What should it do instead?

**How the papers relate.** The papers agree that grounding helps. They differ on where the solution comes from.

- **Gold solution in the prompt.** MathDial and SocraticMATH.
- **Tutor solves the problem itself, privately.** Dinucu-Jianu.
- **Grounding material from the scenario.** LearnLM.
- **Lesson topic and the last five messages only.** Bridge.

**Key evidence.**

- **MathDial grounding ablation** (Flan-T5 780M, Table 4).
    - Adding the ground-truth step-by-step solution gives the largest gain: sBLEU 8.0 → 9.5, BERTScore 53.0 → 55.0. BERTScore measures how close a response is in meaning to the reference.
    - Adding everything gives 9.7 and 55.0.
    - The authors: "the step-by-step solution is crucial for the model" (§6.2).
- **SocraticMATH "− Knowledge" ablation** (Table 3).
    - Removing the solution and answer from the input lowers human reliability from 7.119 to 6.643 and human Socratic score from 7.190 to 6.692, on a 1–10 scale.
    - The authors add the knowledge "to reduce the hallucination" and so the model can "check and rectify the errors since the model tends to trust the users" (§4, §5.2).
    - The human evaluation found that ChatGPT tends to "believe the users' responses without a doubt" (§5.2).
- **Dinucu-Jianu tutor input.** Each rollout starts from "only problem P as input" (App. A.2). The tutor can use thinking tags to solve the problem before it guides the student (§5.1, §6.1, Fig. 7).
- **Bridge missing context.** Some examples lack the question, because it was on a whiteboard. The authors list this as a limitation (§9).
- **LearnLM context.** Every scenario passes grounding material (e.g. a homework problem) and system instructions to the model (Fig. 1, §3.2).

**Negative results and limits.**

- **MathDial's metric is not a pedagogy measure.** Its ablation uses sBLEU and BERTScore, which the authors themselves question as tutor metrics (§5.1, §6.1). The paper also notes that overlap with the grounding can mean more telling (§5.1).
- **No paper tests a tutor grounded in a wrong self-generated solution.** That is exactly the risk for a 270M–1B model.

**What this means on the UNO Q.**

- **Solve first, then tutor.** The copilot has to produce its own solution first: the `predict.py` letter plus a short derivation. Then it tutors conditioned on that solution.
    - Two `llama-server` model services already run on the board (ports 8081/8082, [CHALLENGE_CONTEXT §8](../../../CHALLENGE_CONTEXT.md#8-recommended-pipeline-synthesis)). Port 8082 serves the embedding model, not a second language model ([`config.env`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/config.env)). A separate solver model would need its own model service. RAM limits whether two 1B Q4 language models fit; measure it.
- **Self-grounding is weak.** A wrong self-solution then becomes confident wrong feedback, the failure MathDial measured for ChatGPT (59% incorrect feedback). Gate tutoring on solver confidence; for example, majority vote over a few samples if latency allows.
- **Train with gold grounding, deploy with self-generated grounding.** For SFT on our M3Kang training split, put the gold solution in the grounding field, as MathDial and SocraticMATH do. At inference, the model's own solution goes in that field. Expect a train/test mismatch.

**Open questions.**

- How much does tutoring quality drop when the gold solution is replaced by a 1B model's own solution?
- Should the copilot stay silent on correctness when the solver is unsure?

## J4: Evaluating a tutor

**Question.** Which metrics measure "teaches, not just answers", and which can we compute cheaply next to the harness in [CHALLENGE_CONTEXT §7](../../../CHALLENGE_CONTEXT.md#7-evaluation)?

**How the papers relate.**

- **MathDial and Dinucu-Jianu measure the same two things** (same ETH group):
    - MathDial: Success@k and Telling@k.
    - Dinucu-Jianu: Δ solve rate and leaked-solution %, plus the MathTutorBench Ped-RM.
- **Bridge, SocraticMATH and LearnLM use human rubrics.** Each paper uses its own rubric; none is shared between them.
- **Two papers say reference-overlap metrics are unreliable for tutors.** MathDial §6.1 and SocraticMATH §5.2 independently say BLEU, ROUGE and similar metrics do not capture tutoring quality.

**Key evidence.**

- **MathDial interactive metrics** (§5.1).
    - Success@k: share of conversations where the simulated student reaches the answer within k turns.
    - Telling@k: share where the teacher tells the answer first.
    - Every model does worse on problems that need more than 2 steps (Fig. 6).
    - The results are in the table below.

**MathDial results** (§6.4, Fig. 5 table):

| Tutor | Success@10 | Telling@10 |
|---|---|---|
| Flan-T5 780M | 39% | 4% |
| ChatGPT | 53% | 32% |
| Ground truth | 82% | 4% |
| "What is the next step?" baseline | 25% | 0% |

- **MathDial human evaluation** (§6.3). Three criteria: coherence, correctness, equitable tutoring. Three expert annotators rated 50 responses each. Agreement was κ = 0.29, 0.69 and 0.34.
- **Dinucu-Jianu metrics** (§5.2).
    - Δ solve: the student's solve rate after the dialogue minus before, with 8 student samples.
    - Leak %: an LLM judge (Gemma3-27B at test time, a different family from the training judge) decides whether the tutor gave away the solution.
    - Ped-RM: scored on MathTutorBench, out of domain.
    - Regression check: MMLU, GSM8K and MATH500 (§5.2, Table 3).
    - MathTutorBench has nine tasks under three headings: math expertise, student understanding and pedagogy (Table 4). Our `.md` parse of Table 4 is column-shifted, so no numbers are quoted here.
- **Bridge.** Pairwise human comparisons against the original novice tutor response: prefer, useful, care, and "not robot" (human-soundingness). Each is a 5-point Likert (rating) scale mapped to −2..2. There were 40 pairs per model and 3 teacher raters each (§6.1).
- **SocraticMATH.** Human (three experts) and GPT-4 scores on 150 test samples, 1–10, for reliability and Socratic quality (§5.2).
- **LearnLM.**
    - Scenario-guided, multi-turn expert evaluation: 49 scenarios, conversations of at least 10 turns, a 29-item 7-point rubric, comparative preferences, and Bayesian hierarchical models (§3, App. B.6).
    - In total: 2,360 conversations and 10,192 expert assessments (§4).
    - The paper reports two participant counts for each pool, in the table below.

**LearnLM participant counts:**

| Pool | §3 | Later sections |
|---|---|---|
| Role-players | N = 186 | N = 168 (§3.2) |
| Assessors | N = 248 | N = 228 (§3.3) |

- **Length and quality.** LearnLM found "no clear relationship between length and perceived quality". LearnLM averaged 174 words per turn (§4, Fig. 3).

**Negative results and limits.**

- **Low agreement on fine-grained labels.** MathDial human eval reached only κ = 0.29 on coherence and 0.34 on equitable tutoring (§6.3).
- **Simulated students, not real learners.** MathDial §8 and Dinucu-Jianu (Limitations) both say a student simulator does not show long-term learning or transfer.
- **No outcome evidence.** LearnLM says it is unclear how rubric scores translate into learning outcomes, and calls for extrinsic evaluation (§5).
- **No evaluation in Catalan or Spanish in any of the five papers.**
- **The Telling and leak judges answer different questions.** MathDial's Telling@k counts telling before the student reaches the answer. Dinucu-Jianu's leak judge asks whether the tutor gave away the solution at all. Do not compare the numbers directly.

**What this means on the UNO Q.**

[CHALLENGE_CONTEXT §7](../../../CHALLENGE_CONTEXT.md#7-evaluation) lists MathTutorBench and MRBench as candidate benchmarks.

- **MathTutorBench** is the only one used in this folder (Dinucu-Jianu), and its Ped-RM is a learned reward model. Run it on the laptop against the merged FP16 model and the GGUF, not on the board.
- **MRBench** is not used by any paper here.

- **Cheapest metrics first.** The list is in [What to try](#what-to-try).

**Open questions.**

- Which judge model, run locally on the laptop, agrees well enough with humans on leakage in Catalan?
- Does the MathTutorBench Ped-RM score Catalan or Spanish responses meaningfully? It was not trained for them, as far as these papers say.

## Papers not covered by any junction

None. All five papers feed at least two junctions.

## What to try

### Fine-tune on short, move-labeled dialogues

These steps come from [J2](#j2-inducing-pedagogical-behaviour-prompting-vs-sft-vs-rl).

1. Use the MathDial format, translated or synthesized in Catalan and Spanish, on Gemma 3 270M/1B.
2. Start each example with a specific system instruction, LearnLM-style. Example: "do not reveal the final option letter; ask one guiding question".
3. Merge the adapter, convert to GGUF and quantize ([CHALLENGE_CONTEXT §6](../../../CHALLENGE_CONTEXT.md#6-fine-tuning), [§8](../../../CHALLENGE_CONTEXT.md#8-recommended-pipeline-synthesis)).

### Add tutoring metrics, cheapest first

These metrics come from [J4](#j4-evaluating-a-tutor).

1. **Leak rate, single turn.** For each validation-set problem, generate the copilot's first turn in tutoring mode. A laptop LLM judge then marks whether it reveals the option letter or the final value, in the style of the Dinucu-Jianu leak judge. One generation per problem, so it can also run on the board. Keep the problem text out of every committed result file.
2. **Accuracy on the M3Kang validation set**, already in the harness. Run it before and after SFT, as a regression check in the spirit of Dinucu-Jianu Table 3.
3. **Words per copilot turn and seconds per turn on the board.** This is a latency budget, not a quality score.
4. **Success@k / Telling@k with a simulated student.** Use a larger model on the laptop as the student. This is expensive, so run it only on a small sample for final comparisons.

Open tension: the `predict.py` contract asks for the letter A–E ([CHALLENGE_CONTEXT §1](../../../CHALLENGE_CONTEXT.md#1-the-challenge-what-we-know)). Measure leak rate only in the tutoring mode, never on the answer channel.

## Links to other folders

- J1, J2 (synthetic data for small models): [TinyGSM](https://arxiv.org/abs/2312.09241), [Small models struggle to learn from strong reasoners](https://arxiv.org/abs/2502.12143)
- J2 (LoRA SFT on a laptop GPU): [LoRA](https://arxiv.org/abs/2106.09685)
- J1, J4 (M3Kang data, validation set, levels and languages): [M3Kang](https://arxiv.org/abs/2601.16218)
