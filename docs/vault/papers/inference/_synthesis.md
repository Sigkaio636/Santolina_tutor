---
tags: [synthesis, inference]
papers: 18
date: 2026-11-14
---
# Inference: synthesis by junction

> Changes to the proposed junctions:
> - **J1 reframed** from "why decode is bandwidth-bound" to **"where the time goes: prefill vs decode"**. The repo's own measurements show that in the `predict.py` contract most of the time is prefill: the board reads about 11–12 tok/s, and the answer is one letter (BOARD_SETUP §5.5, §11.3). Decode matters only for the tutor's generated hints and explanations. FlashAttention 1/2 stay in J1 with a short "skip" verdict. Each later junction is tagged with the phase it can speed up: **[prefill]**, **[decode]** or **[memory]**.
> - **J2 refocused.** With `--parallel 1` and short contexts, the useful lever in the KV-cache papers is **shared-prefix reuse** (vLLM §6.4), not eviction or paging. FlexGen's 4-bit KV result moved here from J4.
> - **J3 kept.** It adds a check the papers assume away: is parallel verification "free" on 4 A53 cores?
> - **J4 kept.** The verdict is mostly "does not transfer". Two lessons do transfer: sparsity disappears in prefill, and paging weights from flash costs 82–89% of decode speed.
> - **J5 narrowed** to low-bit CPU kernels (T-MAC, bitnet.cpp). **MCUNet moved to J6** (engine–model co-design), next to MobileLLM.
> - No junction dropped. All 18 papers are covered.

For the UNO Q tutor, the scored task (one letter A–E) is limited by **prefill**, which on our reading of the repo's tok/s numbers is compute-bound on 4 A53 cores. Decode-side techniques (speculative decoding, activation sparsity, KV eviction, paging, flash offloading) therefore cannot help the contract answer, and on this board even their gain for generated hints is uncertain. The levers that touch prefill are fewer prompt tokens, reuse of a fixed prompt prefix, fewer non-embedding parameters (Gemma 3 270M vs 1B) and faster low-bit kernels, all to be measured with `llama-bench` first; even "fewer bits ⇒ faster decode" is unconfirmed here, with only a hint against it.

## Junctions at a glance

| Junction | Papers | Decision it informs |
|---|---|---|
| J1: Where the time goes: prefill vs decode | [[pope2022_efficiently_scaling_transformer_inference_2211.05102.pdf\|Pope 2022]], [[dao2022_flashattention_2205.14135.pdf\|FlashAttention]], [[dao2023_flashattention2_2307.08691.pdf\|FlashAttention-2]], [[liu2023_deja_vu_2310.17157.pdf\|Deja Vu]] (Table 1), [[wei2024_tmac_lut_cpu_lowbit_2407.00088.pdf\|T-MAC]] (§2.1) | What to optimise first for the 60 s budget; whether to touch attention kernels; how to read tok/s on the board |
| J2: KV cache: size, reuse, eviction, quantization | [[kwon2023_pagedattention_vllm_2309.06180.pdf\|PagedAttention]], [[zhang2023_h2o_heavy_hitter_2306.14048.pdf\|H2O]], [[xiao2023_streamingllm_2309.17453.pdf\|StreamingLLM]], [[liu2024_kivi_2402.02750.pdf\|KIVI]], [[sheng2023_flexgen_2303.06865.pdf\|FlexGen]] (§5), Pope (§3.3) | `--cache-ram`, prompt layout for prefix reuse, KV cache type, how to handle multi-turn tutoring history |
| J3: Speculative decoding on a CPU | [[leviathan2022_speculative_decoding_2211.17192.pdf\|Leviathan 2022]], [[chen2023_speculative_sampling_2302.01318.pdf\|Chen 2023]], [[alizadeh2023_llm_in_a_flash_2312.11514.pdf\|LLM in a flash]] (§5.2), [[song2023_powerinfer_2312.12456.pdf\|PowerInfer]] (§8.2) | Whether a 270M draft + 1B target (or an n-gram draft) can speed up hint generation on the board |
| J4: Activation sparsity and offloading | Deja Vu, PowerInfer, [[xue2024_powerinfer2_2406.06282.pdf\|PowerInfer-2]], LLM in a flash, FlexGen | Whether any sparse or offloading engine is worth it for a model that already fits in RAM |
| J5: Low-bit CPU kernels without dot-product instructions | T-MAC, [[wang2024_bitnet_cpp_1bit_infra_2410.16144.pdf\|bitnet.cpp]], Pope (§3.6) | Which GGUF quant type to benchmark; whether a LUT kernel or a ternary model is worth leaving pinned llama.cpp for |
| J6: Architecture and engine–model co-design for small devices | [[liu2024_mobilellm_2402.14905.pdf\|MobileLLM]], [[lin2020_mcunet_2007.10319.pdf\|MCUNet]] | How to read Gemma 3 270M/1B shapes for speed; what not to try (pretraining a custom shape) |

Papers:
- MCUNet: Lin et al. ([arXiv 2007.10319](https://arxiv.org/abs/2007.10319))
- FlashAttention: Dao et al. ([arXiv 2205.14135](https://arxiv.org/abs/2205.14135))
- Pope 2022: Pope et al., "Efficiently Scaling Transformer Inference" ([arXiv 2211.05102](https://arxiv.org/abs/2211.05102))
- Leviathan 2022: Leviathan et al., "Fast Inference from Transformers via Speculative Decoding" ([arXiv 2211.17192](https://arxiv.org/abs/2211.17192))
- Chen 2023: Chen et al., "Accelerating LLM Decoding with Speculative Sampling" ([arXiv 2302.01318](https://arxiv.org/abs/2302.01318))
- FlexGen: Sheng et al. ([arXiv 2303.06865](https://arxiv.org/abs/2303.06865))
- H2O: Zhang et al., Heavy-Hitter Oracle ([arXiv 2306.14048](https://arxiv.org/abs/2306.14048))
- FlashAttention-2: Dao ([arXiv 2307.08691](https://arxiv.org/abs/2307.08691))
- PagedAttention / vLLM: Kwon et al. ([arXiv 2309.06180](https://arxiv.org/abs/2309.06180))
- StreamingLLM: Xiao et al., attention sinks ([arXiv 2309.17453](https://arxiv.org/abs/2309.17453))
- Deja Vu: Liu et al., contextual sparsity ([arXiv 2310.17157](https://arxiv.org/abs/2310.17157))
- LLM in a flash: Alizadeh et al. ([arXiv 2312.11514](https://arxiv.org/abs/2312.11514))
- PowerInfer: Song et al. ([arXiv 2312.12456](https://arxiv.org/abs/2312.12456))
- KIVI: Liu et al., 2-bit KV cache ([arXiv 2402.02750](https://arxiv.org/abs/2402.02750))
- MobileLLM: Liu et al. ([arXiv 2402.14905](https://arxiv.org/abs/2402.14905))
- PowerInfer-2: Xue et al. ([arXiv 2406.06282](https://arxiv.org/abs/2406.06282))
- T-MAC: Wei et al. ([arXiv 2407.00088](https://arxiv.org/abs/2407.00088))
- bitnet.cpp: Wang et al., "1-bit AI Infra" ([arXiv 2410.16144](https://arxiv.org/abs/2410.16144))

Dataset for our evaluation: [M3Kang dataset card](https://huggingface.co/datasets/qualcomm/M3Kang). No problem text from it appears in this note.

Board facts used below come from the repo, not from the papers: 4× Cortex-A53 @ 2.0 GHz, ARMv8.0-A, "no SDOT/UDOT ... and no I8MM" (CHALLENGE_CONTEXT §2, itself marked VERIFY); 4 GB LPDDR4X, "single rank, 32-bit", about 3.6 GB usable (UNO_Q_BOARD_REFERENCE §3.3); llama.cpp pinned at commit `2cbe0ec`, CPU-only build with `-DGGML_NATIVE=ON` (BOARD_SETUP §3); server flags `--threads 4 --ctx-size 4096 --parallel 1 --cache-ram 0 --ctx-checkpoints 2` (BOARD_SETUP §5.1).

## J1: Where the time goes: prefill vs decode

**Question.** In a 60 s per-problem budget with a one-letter answer, which phase dominates on the board, and what does that mean for which papers to act on? Does FlashAttention matter on a CPU with short contexts?

**How the papers relate.** Pope sets the frame and the others extend it. Pope splits latency into prefill (all input tokens in one parallel pass) and decode (one sequential pass per output token) and analyses them separately (§2, §2.2). At small batch, the decode memory time is dominated by loading weights, and the KV cache dominates only at large batch × long context (§2). Deja Vu (§2.2, Table 1) and T-MAC (§2.1) restate the same split for GPUs and edge CPUs: prefill is matrix–matrix work and compute-heavy, decode is matrix–vector work and memory-heavy. FlashAttention and FlashAttention-2 are a different line. They reduce reads and writes between GPU HBM and on-chip SRAM inside the attention operator. FA2 is FA1 with better GPU work partitioning across thread blocks and warps (FA2 §3.2).

**Key evidence.**
- Pope: an N-parameter decoder needs 2N matmul FLOPs per token. Attention FLOPs "can often be excluded" for large models, but the KV cache can still be a large share of memory traffic (§2).
- Pope: at low batch, int8 weights beat bfloat16 on latency (28.5 vs 36.9 ms/token on PaLM 540B at batch 64), "because low-batch-size cost is dominated by weight loading time" (§4.4). Decode MFU is far below prefill MFU: 14% vs 43% in the low-latency PaLM 540B setup (Table 2).
- Pope: with multiquery attention and short context, "almost all of the time is spent on the feedforward layer". Attention becomes significant only as context grows (§4.2, Figure 8).
- Deja Vu Table 1 (8× A100, theoretical): prompting 128 tokens costs 20.6 ms of I/O, and generating 128 tokens costs 2,600 ms of I/O for the same 44.6 TFLOPs. On a GPU, a whole 128-token prompt costs about one decode step.
- T-MAC §2.1: on edge devices prefill is "compute-intensive matrix-matrix multiplications", and decode is "memory-intensive matrix-vector multiplications".
- FlashAttention: up to 7.6× on the attention computation for GPT-2 (Figure 1), and 2–4× attention speedup on A100 (Appendix E.5). Speedup shrinks on T4, whose SRAM is smaller (Appendix E.5). The authors list as limitations that each variant needs a new CUDA kernel and "may also not be transferrable across GPU architectures" (§5).
- FlashAttention-2: about 2× over FA1, up to 73% of A100 peak in the forward pass (§1, §4.1). Every gain comes from GPU thread-block and warp scheduling (§3.2–§3.3).

**Negative results and limits.**
- None of Pope, FA1 or FA2 measures a CPU. Pope's numbers are TPU v4 at 8B–540B (§4.4).
- FA1 itself says that beyond 1K tokens some approximate methods become faster (§1).
- The "decode is bandwidth-bound" claim is for accelerators with spare compute. The board docs suggest it may not hold cleanly on an A53 (next section).

**What this means on the UNO Q.** Phase tags in later junctions refer to this split.
- *Prefill dominates the contract.* BOARD_SETUP §5.5 measured about 11.3 tok/s reading and 5.9 tok/s writing (Qwen3.5 0.8B Q8_0). §11.3 says an 85-token problem takes about 7 s before the first answer token, and the answer is one token. *Our arithmetic:* on the board, a 128-token prompt costs 128 / 11.3 ≈ 11 s, which is about 66 decode steps at 0.17 s. On the A100 in Deja Vu Table 1, it costs about one decode step. On the A53 prefill is only about 2× cheaper per token than decode, so it is compute-bound, not bandwidth-bound.
- *Decode tok/s ceiling.* The board's memory bandwidth is **not in the repo docs** (the board reference gives only "LPDDR4X, single rank, 32-bit"). **VERIFY**, for example with a STREAM-style test on the board. *Our arithmetic:* 835 MB (Q8_0 file, BOARD_SETUP §4) × 5.9 tok/s ≈ 4.9 GB/s. That is an upper bound on the bandwidth actually used, because not every byte of the file is read per token.
- *"Fewer bits ⇒ faster" is not confirmed here.* The official Arduino run gives Qwen3.5 0.8B **Q4_K_M at 3.6 tok/s** generation. Our Q8_0 run gives 5–6 tok/s (UNO_Q_BOARD_REFERENCE §13.1–13.2). The builds differ, so this is a hint, not a result. T-MAC §5.2 points the same way for llama.cpp on CPUs: no gain from 4-bit to 2-bit, and 15% slower at 3-bit "due to decoding overhead". Hypothesis: without dot-product instructions, the A53 spends enough time unpacking and multiplying that decode is partly compute-bound. **Test first:** `llama-bench` on Q8_0, Q4_0 and Q4_K_M of the same model with the pinned build, at `-t 1,2,3,4`. If tg scales with threads and Q8_0 ≈ Q4_0, decode is compute-bound and bit-width will not buy speed.
- *FlashAttention: skip.* Our prompts are 80–300 tokens (BOARD_SETUP §5.5) in a 4,096 context. Per Pope §4.2, attention is a small share at that length. FA's gains come from GPU SRAM/HBM tiling and warp scheduling, which do not exist on this CPU. Whether pinned llama.cpp `2cbe0ec` has a flash-attention flag for CPU, and whether it changes anything here, is **not in the repo docs: VERIFY**. It is low priority.
- *What to optimise first for the contract:* prompt length (each token costs about 0.09 s), reuse of a fixed prefix (J2), and fewer non-embedding parameters (J6). Decode-side papers matter only for generated tutoring text.

**Open questions.**
- Is decode on the A53 bandwidth-bound or compute-bound? (See the `llama-bench` test above.)
- What is the board's measured DRAM bandwidth?
- In the pinned llama.cpp, are prompt logits computed only for the last token? If so, the LM head does not count towards prefill cost. VERIFY in the code or with `llama-bench -p`.

## J2: KV cache: size, reuse, eviction, quantization

Phase tags: **[memory]**, and **[prefill]** for prefix reuse.

**Question.** For one user with short prompts and multi-turn tutoring chats, does anything in the KV-cache papers help? Which llama.cpp options correspond to these ideas?

**How the papers relate.**
- *Four answers to one problem.* PagedAttention manages KV memory (paging, sharing). H2O and StreamingLLM evict tokens. KIVI and FlexGen §5 quantize the cache. Pope §3.3 shrinks it at the architecture level with multiquery attention.
- *H2O vs StreamingLLM.* They compete, and partly converge. H2O keeps "heavy hitters" plus recent tokens, and notes that many heavy hitters sit at the start of sentences (Appendix B.2). StreamingLLM keeps 4 initial "attention sink" tokens plus a recent window (§1, §4.4). H2O reports lower perplexity than StreamingLLM on streaming input (§5.3 Q1, Figure 5; Appendix C.4).
- *KIVI builds on FlexGen.* It positions itself against the per-token 4-bit KV quantization of FlexGen and H2O (KIVI §1, §3.1).
- *Common target.* All of these target large batches or very long contexts on GPUs.

**Key evidence.**
- *KV size scales with layers × hidden size.* OPT-13B needs 800 KB of KV per token at FP16 (2 × 5,120 × 40 layers × 2 bytes). That is up to 1.6 GB for a 2,048-token request (PagedAttention §3).
- *Fragmentation.* Existing systems store real token states in only 20.4–38.2% of the KV memory they reserve (PagedAttention §1, Fig. 2). PagedAttention's paged kernel costs 20–26% more attention latency than FasterTransformer (§7.1). The authors warn that paging can "rather degrade the performance" where memory is not the bottleneck (§8).
- *Shared prefix.* With a shared few-shot prefix, vLLM gets 1.67× (1 example, 80 tokens) and 3.58× (5 examples, 341 tokens) higher throughput than Orca Oracle (§6.4, Fig. 16). In the chatbot test, vLLM does **not** keep KV between conversation rounds (§6.5).
- *H2O.* With a 20% KV budget, quality is comparable to the full cache on most tasks (§5.1, Table 1). "Local" (recent-only) collapses: OPT-30B COPA drops from 85.00 to 48.00 (Table 2). Heavy hitters alone, or local tokens alone, lose 2.85–22.75% (§5.3 Q4).
- *StreamingLLM.* Window attention collapses once the first tokens are evicted. Keeping 4 sink tokens restores it (§1, §4.4). Up to 22.2× faster per token than sliding-window recomputation (§4.5). Bigger caches do not consistently lower perplexity (Table 6).
- *KIVI on math.* Fake 2-bit KV (K per-channel, V per-token) drops Llama-2-7B GSM8K from 13.50 to 5.76. Per-token 4-bit holds at 12.28. KIVI-2 R128, which keeps a recent window in full precision, gets 12.74 (Table 3 for the fake-quantization rows; Appendix C, Table 6 for KIVI-2). Llama-2-13B: 22.67 → 20.77 with KIVI-2 R128 (Appendix C, Table 6). The authors say the full-precision window "is crucial to maintaining accuracy for hard generation tasks such as mathematical reasoning" (§4.2.1).
- *KIVI on MQA models.* Falcon-7B uses multi-query attention, so its cache is "already highly compressed". It needs 4-bit KIVI, and 2-bit "may have a large accuracy drop" (§4.2.2).
- *FlexGen.* 4-bit group-wise compression of both weights and KV is close to FP16 on OPT-30B/175B: Lambada 0.725 → 0.724 on OPT-30B (Table 5). "3-bit compression ... cannot preserve accuracy" (§6.2). On a CPU, the group-wise dequantization overhead "could be very significant" (§5).
- *Multiquery attention.* It shrinks the KV cache by a factor of n_heads (Pope §3.3).

**Negative results and limits.**
- *StreamingLLM:* "does not extend the models' context window or enhance their long-term memory". It is "not suitable for tasks that demand long-term memory" (Appendix A). Evicted turns are gone.
- *H2O* accumulated-score eviction is biased towards old tokens. Averaging the scores instead made it worse (Appendix B.2).
- *KIVI:* 2-bit hurts math first (Table 3). Group size 128 "significantly decreases" accuracy (§4.2.3).
- *Scale and setting:* all evaluations are 6.7B+ models on A100/T4 GPUs with batching. None uses a sub-1B model, a CPU, or batch-1 latency as the main metric.

**What this means on the UNO Q.**
- *Batching does not apply.* With `--parallel 1` (BOARD_SETUP §5.1), PagedAttention's main gain (packing many requests) does not apply, and H2O/KIVI gains are reported as larger batches and throughput (H2O §5.2; KIVI §4.2.4).
- *Our KV cache is small.* Gemma 3 1B uses GQA and 5 local sliding-window layers (1,024-token window) per global layer. See the surveys note (J2, citing the Gemma 3 report) for its KV figures; they are not restated here. At `--ctx-size 4096` the cache is a small part of RAM compared with the weights. The RAM problem the repo actually hit was the **prompt cache**: the default kept up to 8 GB and got the server killed (BOARD_SETUP §5.1).
- *Try first [prefill]: shared-prefix reuse.* This is the vLLM §6.4 idea. Put the fixed instruction and any fixed examples first, and the problem-specific and RAG text after them.
  - Project rule: the `unoq-board` skill says every `llama-server` "must keep `--parallel 1 --cache-ram 0`". Nothing here is permission to drop it.
  - Step 1, no rule change: check whether the single slot already reuses the common prefix at `--cache-ram 0`. Send two requests that share the prefix and compare `prompt_n` and the prompt timings in the `/v1/chat/completions` response.
  - Step 2, only if step 1 shows no reuse: a one-off experiment with a small bounded `--cache-ram`, watching `free -h`. Never make it the service default.
  - **VERIFY** in pinned llama.cpp what `--cache-ram` and `--ctx-checkpoints` actually store, and whether temperature-0 answers stay identical with and without reuse (determinism is a contest rule, BOARD_SETUP §11.1).
  - If prefix reuse works, every token moved into the shared prefix costs about 0.09 s less per problem (our arithmetic from J1).
- *KV quantization: skip for now.* The pinned build's KV cache type options (e.g. `--cache-type-k`) are not in the repo docs (**VERIFY**). If tried, stay at 8-bit or 4-bit and test on math. KIVI and FlexGen agree that 2-bit and 3-bit fail first on hard generation. A GQA model like Gemma 3 may have less headroom, as KIVI found for MQA Falcon (§4.2.2); this is untested.
- *Multi-turn tutoring.* Do not rely on eviction or llama.cpp context shifting (whether the pinned build has it is **VERIFY**). StreamingLLM and H2O keep recent and "important" tokens by attention score, not the problem statement. The app should pin the system prompt and the problem, and summarise or drop old turns itself, inside the 4,096 context.

**Open questions.**
- Does pinned llama.cpp reuse a common prefix across requests with `--parallel 1 --cache-ram 0`, or does that need `--cache-ram > 0`? How much RAM does it cost?
- How many KV heads do Gemma 3 270M and 1B have? (Check `num_key_value_heads` in the HF config.) This sets how much KV quantization headroom there is.

## J3: Speculative decoding on a CPU

Phase tag: **[decode]** only. Speculative decoding does nothing for the one-letter contract answer.

**Question.** Leviathan and Chen get 2–3× with a small draft model. Is a 270M draft + 1B target, or a draft-free n-gram scheme, viable in 2–4 GB on 4 A53 cores, where draft and target compete for the same cores and memory?

**How the papers relate.** Leviathan and Chen are concurrent and independent, with "the core underlying idea ... the same" (Chen, Related Work). Both use a modified rejection sampling step that keeps the target's distribution. Leviathan adds the analysis: the acceptance rate α, the cost ratio c and the walltime formula (§3). Chen adds a distributed 70B case and the effect of draft length K. LLM in a flash (§5.2) and PowerInfer (§8.2, SpecInfer baseline) report it as a side result under memory pressure.

**Key evidence.**
- *Walltime formula.* The improvement is (1 − α^(γ+1)) / ((1 − α)(γc + 1)) (Theorem 3.8). This **assumes** γ+1 parallel target evaluations cost no more walltime than one (§3.3). An improvement exists if α > c (Corollary 3.9).
- *Speedups on TPU.* T5-XXL 11B with T5-small (77M) as draft: 3.4× at temperature 0 (α = 0.75, γ = 7). T5-large (800M) has higher α (0.82) but only 1.7× (Table 2). A draft "around two orders of magnitude smaller" worked best (§3.6). In their setups c "was always less than 0.05" (§3.3).
- *Temperature 0 helps.* α and speedup are higher at temperature 0 than at temperature 1 (§4.1, Table 2).
- *Draft-free options.* A bigram "draft" (c ≈ 0) gives α ≈ 0.2 and 1.25× on EnDe (§3.6, §4.2). Copying tokens from the context "might yield high values of α" for chat-like interfaces (§3.6). The paper gives no measurement for this.
- *Limit stated by the authors.* The method "is not helpful for configurations where additional computation resources are not available" (§6). Total arithmetic grows: for example 1.53× more operations for 1.96× speed at α = 0.6, γ = 2 (Table 1).
- *Chen.* Chinchilla 70B with a 4B draft: 1.92–2.46× (Table 1). The draft ran at 1.8 ms/token vs 14.1 ms/token, so c ≈ 0.13 (Results). Speedup plateaus or regresses with larger K: XSum is best at K = 3, and variance grows with K (Figure 1).
- *Chen on determinism.* Even greedy outputs are not identical to plain sampling, because numerics differ; the distributions match "within hardware numerics" (Evaluation section).
- *Under memory pressure.* LLM in a flash: 1.4× with λ = 4 vs the original 1.58× (§5.2). PowerInfer: SpecInfer barely beats llama.cpp when the target does not fit, because verification swapping takes over 95% of the time (§8.2).

**Negative results and limits.**
- Every speedup is on TPUs (Leviathan, Chen) or GPUs, with spare compute during decode.
- Leviathan tested only drafts with the same architecture and tokenizer as the target (§3.6).

**What this means on the UNO Q.**
- *Parallel verification is not free here.* Per J1, prefill on the board costs about 0.09 s per token vs about 0.17 s per decode step. *Our arithmetic, illustrative:* verifying γ+1 = 5 tokens at prefill speed costs about 5 / 11.3 ≈ 0.44 s, or about 2.6 decode steps, before any draft cost. Draft and target also run on the same 4 cores.
- *Worked example (our estimate, every input VERIFY).* Take a target Gemma 3 1B at about 5 tok/s (CHALLENGE_CONTEXT §2), so T ≈ 0.2 s. Take a draft Gemma 3 270M with c ≈ 0.35 (Q4 file sizes ~0.25–0.3 GB vs ~0.7–0.8 GB, CHALLENGE_CONTEXT §2, if decode time scales with bytes). Take an optimistic α = 0.8 and γ = 4, which give 3.36 tokens per round (Eq. 1).
  - If verification costs 5 prefill tokens (0.45 s): about 4.6 tok/s. That is **slower than plain decode**.
  - If verifying 5 tokens costs about one decode step: about 7.0 tok/s, or about 1.4×.
  - The difference is a measurement: `llama-bench` with `-p 2,4,8` vs `-n` on the 1B model. If a 5-token batch costs close to one decode step, speculation can pay. If it costs close to five prefill tokens, skip it.
- *A 270M draft is not "two orders smaller" than a 1B target.* That size gap is what worked in Leviathan §3.6. Both models must use the same tokenizer and vocabulary. Whether Gemma 3 270M and 1B do is an open question in the surveys note: **VERIFY**.
- *RAM.* Both models at Q4 (~0.3 + ~0.8 GB) plus the embedding server fit in 4 GB on paper (CHALLENGE_CONTEXT §2). On a 2 GB board it is tight.
- *Cheapest thing to try:* a draft-free copy/n-gram scheme (c ≈ 0), since hints often repeat numbers and words from the problem. Whether pinned llama.cpp `2cbe0ec` has lookup or n-gram speculative decoding in `llama-server`, and which flags, is **not in the repo docs: VERIFY**. It still pays the verification cost above.
- *Determinism.* At temperature 0, check that answers with speculation match answers without it, since Chen reports numerics-level differences.

**Open questions.**
- What is the batch-5 verification cost vs one decode step on the A53?
- What is α between a fine-tuned 270M and a fine-tuned 1B on Catalan and Spanish tutoring text? No paper measures α for non-English or sub-1B targets.

## J4: Activation sparsity and offloading

Phase tags: **[decode]** and **[memory]**. None of these help prefill.

**Question.** Deja Vu, PowerInfer 1/2, LLM in a flash and FlexGen get large speedups from skipping inactive neurons or from paging weights. What transfers to a ≤1B model that already fits in RAM, on llama.cpp, CPU only?

**How the papers relate.**
- *Lineage.* Deja Vu introduces contextual sparsity with learned predictors on GPUs. LLM in a flash reuses its low-rank predictor to load only the needed FFN rows from flash (§3.1). PowerInfer adds a hot/cold neuron split between GPU and CPU, as a 4,200-line extension of llama.cpp (§7). PowerInfer-2 ports it to phones with an NPU (§6).
- *Different goal.* FlexGen is throughput-oriented offloading with large batches. It is the opposite of our batch-1 latency case. LLM in a flash and H2O position themselves against it (LLM in a flash §6).

**Key evidence.**
- *Activation function decides sparsity.* MLP sparsity is 96–98% for ReLU OPT models, 70–82% for ReGLU LLaMA2, and 40–53% for SwiGLU models (PowerInfer Table 3). Deja Vu runs BLOOM at only 30% MLP sparsity "due to the difference in activation function" (§5.2). LLM in a flash saw "less sparsity" on Phi-2 and had to raise its memory limit to 65% (§4.2).
- *Gains on non-ReLU models are modest.* PowerInfer gives 1.47–1.7× on SiLU models (§8.4), against up to 11.69× on ReLU models (Abstract). PowerInfer-2 gives 2.4× on SiLU models (§7.2.5).
- *Sparsity vanishes in prefill.* "When aggregating these activations across the batch", the overall sparsity drops, so PowerInfer-2 runs prefill dense (§4.1.1).
- *Flash paging is very costly.* On a OnePlus 12, offloading 50% of FFN weights cuts decode by 89% (PowerInfer) and 82% (LLMFlash) (PowerInfer-2 §2.4, Table 2).
- *Mobile GPU and NPU.* For matrix-vector work the mobile GPU was slower than both CPU and NPU (PowerInfer-2 §2.3.1, Fig. 3a). The NPU did prefill of a 7B INT4 model at 770 tok/s vs 8 tok/s on CPU (§2.3.1).
- *Quantization matters more than the engine for math.* Qwen2 7B GSM8K was 77.43 with llama.cpp (groups of 32), 22.26 with QNN's per-channel INT4, and 75.24 with PowerInfer-2's hybrid (PowerInfer-2 §7.6, Table 7).
- *Deja Vu.* No accuracy drop until 75% sparsity on OPT-175B, and 1.8–2× over FasterTransformer at batch 1 (§5.1, Figures 6–7). Predictor accuracy is over 99% in shallow layers and about 93% in the last layers (§5.2).
- *LLM in a flash.* Runs models up to 2× DRAM size (Abstract). On CPU, OPT 6.7B end-to-end inference latency goes from 3,182 ms to 669 ms vs naive loading (Table 3). The sparse model used more total energy than a dense model of similar size, because it ran longer (§5.3).

**Negative results and limits.**
- Every speedup needs (a) ReLU-family sparsity or fine-tuning to ReLU, (b) predictors trained per model, which "often [take] several hours" (PowerInfer §7) or 4 hours on an A100 (LLM in a flash §3.1), and (c) a custom engine.
- LLM in a flash is "limited to single-batch inference", and prompt processing is left for future work (§8).
- The smallest model in any of these papers is 6.7B, except Phi-2 in LLM in a flash (§4.2).

**What this means on the UNO Q.**
- *Skip for the contract.* The time is prefill (J1), and PowerInfer-2 §4.1.1 says sparsity disappears there.
- *Skip for hints too, unless Gemma 3's FFN is ReLU-like.* The activation is not stated in any paper here; check `hidden_activation` in the HF config: **VERIFY**. If it is GELU- or SiLU-gated, the evidence points to at most 1.5–2.4×, and only with predictors, a custom engine and a GPU or NPU to share the dense part. The board has no NPU (CHALLENGE_CONTEXT §2), and the pinned build is CPU-only.
- *Transfer 1: keep the whole model resident.* Never let weights page from eMMC. Flash paging cost 82–89% of decode speed on a phone with UFS 4.0 storage (PowerInfer-2 §2.3.2, Table 2). How the board's eMMC compares is not in the repo docs: **VERIFY**. The 2 GB board variant plus the embedding server is where this could happen by accident. Whether llama.cpp's default memory mapping keeps all pages resident under pressure is **VERIFY** (watch `free -h` and major page faults during `eval.py`).
- *Transfer 2: per-channel INT4 is a trap for math.* If anyone tries Qualcomm's Hexagon tooling instead of llama.cpp, PowerInfer-2 Table 7 shows per-channel INT4 destroying GSM8K. Keep group-wise formats (Q4_0, Q4_K).
- *GPU: no.* PowerInfer-2 §2.3.1 found the phone GPU slower than the CPU for matrix-vector work, and T-MAC Table 7 found llama.cpp on the OnePlus 12's Adreno 750 (named in T-MAC Table 6) far slower than the CPU. How the board's Adreno 702 compares is **VERIFY**. This matches the repo's decision to stay CPU-only (UNO_Q_BOARD_REFERENCE §13.1).

**Open questions.**
- What is Gemma 3's FFN activation? (Settles whether this junction is closed.)
- Does the 2 GB board variant fit Gemma 3 1B Q4 + the embedding model without paging?

## J5: Low-bit CPU kernels without dot-product instructions

Phase tags: **[decode]**, and **[prefill]** for mpGEMM.

**Question.** The A53 is ARMv8.0 with NEON but reportedly no SDOT/UDOT (CHALLENGE_CONTEXT §2, VERIFY with `grep Features /proc/cpuinfo` and look for `asimddp`). Would a LUT kernel (T-MAC) or a ternary model with bitnet.cpp beat llama.cpp's stock kernels here?

**How the papers relate.** T-MAC replaces dequantize-then-multiply with bit-serial table lookups for any weight bit-width (§1, §3.1). bitnet.cpp applies the same LUT idea to ternary BitNet b1.58 models (TL1/TL2 kernels) and adds a plain 2-bit unpack kernel (I2_S) (§2). Both compare against llama.cpp. Pope §3.6 is the accelerator baseline: int8 weights cut weight-loading time, with matmuls still in bfloat16.

**Key evidence.**
- *T-MAC's lookups need only base NEON.* The kernel uses NEON `vqtbl1q_u8` for lookup and `vrhaddq_u8` for aggregation (§4, Table 1). A 4-bit-indexed table (g = 4) fits exactly in one 128-bit NEON register (§4). Neither instruction is a dot-product instruction.
- *llama.cpp gains nothing from 4 → 2 bits.* It is 15% slower at 3 bits "due to decoding overhead". T-MAC speeds up roughly linearly as bits drop (§5.2).
- *Kernel speedups.* Single-thread mpGEMV: up to 11.2×, 5.8×, 4.7× and 3.1× at 1, 2, 3 and 4 bits. Multi-thread is "primarily constrained by memory bandwidth" (§5.2).
- *Prefill-shaped work too.* mpGEMM at sequence length 256 runs up to 4.0× faster on a Raspberry Pi 5 at 2-bit (§5.2).
- *End to end.* BitNet-b1.58-3B reaches 11 tok/s on a Raspberry Pi 5 (Abstract, §5.3). The Pi 5 is Cortex-A76 with 17.1 GB/s (Table 2).
- *Quality.* Llama-2-7B 4-bit on M2-Ultra, single thread: 5.65 tok/s with llama.cpp vs 7.34 with T-MAC, at the same perplexity (5.96 WikiText-2). The optional "fast aggregation" raises speed to 8.97 tok/s but perplexity to 6.38 (§5.6, Table 4).
- *Mobile GPU.* On a OnePlus 12, T-MAC on CPU is 6.4× (4-bit) and 9.7× (2-bit) faster than llama.cpp on the Adreno 750 GPU (§5.7, Table 7).
- *bitnet.cpp.* 1.37×–5.07× over llama.cpp on ARM, with smaller models (125M to 1B) gaining less (§1, §3.1). On M2 Ultra at 1B: 85.60 → 169.45 tok/s (Table 4). The llama.cpp baseline in Figure 1 is labelled fp16, and the Table 4 caption does not state the type. So the speedups are likely against fp16 weights, not the Q4_0 a team would run, and the gap on the board would be smaller than these numbers read.
- *bitnet.cpp "lossless" check.* Its kernels match FP32 output token-for-token on 100% of 1,000 prompts. llama.cpp's own ternary types TQ1_0 and TQ2_0 match on only 1.4% (§3.2, Table 7; tested on a 700M BitNet b1.58).

**Negative results and limits.**
- No A53, and no core without dot-product instructions, is in either paper. T-MAC tests A76, A78AE, Oryon, X4/A720, Intel and Apple (Table 2, Table 6). bitnet.cpp tests only M2 Ultra and an i7-13700H (§3.1).
- The baselines on those cores use their dot-product paths, so how big T-MAC's gain is on an A53 is unknown in either direction.
- T-MAC's large gains are at 1–2 bits. At 4-bit the end-to-end gain is 1.3× single-thread on M2-Ultra (Table 4).
- bitnet.cpp only helps models **trained** ternary. There is no ternary Gemma 3.

**What this means on the UNO Q.**
- *First experiment, inside the rules:* compare stock GGUF types on the pinned build: Q8_0, Q4_0, Q4_K_M, and Gemma's QAT Q4_0 (see J1). Pick by measured tg and pp, not by bits.
- *T-MAC and bitnet.cpp are different engines.* For end-to-end tests, T-MAC's kernels are integrated into llama.cpp as its own build (§5.1). BOARD_SETUP §3.1 pins one llama.cpp commit "so results compare fairly". Whether a team may ship a different build is a **rules question to ask the organisers** before investing time.
- *T-MAC is the one paper here that speeds up prefill-shaped mpGEMM on small ARM cores.* It could matter for the contract, but mainly at 2-bit, where quality on a 1B math model is unproven. Treat it as a stretch experiment.
- *2-bit Gemma: skip* without QAT. The quantization folder covers low-bit quality.
- *bitnet.cpp: skip.* We would need a ternary model trained from scratch in Catalan, Spanish and English with math. BitNet b1.58 2B4T exists (quantization folder), but it is 2B and its multilingual math is untested here.

**Open questions.**
- Does the board's `/proc/cpuinfo` list `asimddp`? (The docs say no, but mark it VERIFY.)
- On an A53, is llama.cpp's Q4_0 path limited by unpacking or by bandwidth? (Same test as J1.)
- Do the contest rules allow a forked inference engine?

## J6: Architecture and engine–model co-design for small devices

Phase tags: **[prefill]**, **[decode]** and **[memory]**, through model shape.

**Question.** We will not pretrain a model. What do MobileLLM's sub-billion design results and MCUNet's co-design lesson tell us about choosing between Gemma 3 270M and 1B, and about where their time goes?

**How the papers relate.** MCUNet (CNNs on microcontrollers) argues that the model and the inference engine must be designed together: a leaner engine leaves memory for a bigger model, and that raises accuracy (§3.2, §4.5). MobileLLM is the LLM-side counterpart for phones, but it designs only the model. Its findings overlap with Gemma 3's design: GQA and tied embeddings (Gemma 3 report, linked only). On depth, it disagrees with depth-pruning work for large models (ShortGPT, linked only).

**Key evidence.**
- *Depth over width at small scale.* For about 125M parameters, 30–42 layers beat 12 layers. "Shallow architectures with fewer than 10 layers perform poorly", and the best depth is "near 30 layers for sub-billion scale models" (§2.2.2, Appendix C).
- *Embedding sharing.* The embeddings are over 20% of a 125M model with a 32k vocabulary (§2.2.3). Tying input and output embeddings saves 16M parameters (11.8%) for a 0.2-point drop, which extra depth recovers (Table 1).
- *GQA.* Going from 16 to 4 KV heads is "comparable" at 125M and costs 0.2 points at 350M, for almost 10% smaller size (§2.2.4).
- *Block-wise weight sharing (MobileLLM-LS).* It adds 0.7/0.8 points at 125M/350M (Abstract). It costs 2.6% more execution time on iPhone 13. A 60-layer model without sharing costs 86% more execution time (§3.6, Table 7). The speed argument assumes the shared block stays in an SRAM "typically limited to around 20MB" (§2.3).
- *Quantization and distillation.* W8A8 post-training quantization loses under 0.5 points (§3.4, Appendix F). Knowledge distillation from LLaMA-v2 7B slowed training 2.6–3.2× and gave "comparable or inferior accuracy" (§3.5).
- *MCUNet.* The engine (TinyEngine) cuts peak memory 3.4× and is 1.7–3.3× faster than TF-Lite Micro and CMSIS-NN (Abstract). Generating code at compile time instead of interpreting saves memory and time (§3.2).

**Negative results and limits.**
- MobileLLM's results are zero-shot common-sense, chat and API-calling tasks on models it pretrained itself. There is no math, no non-English evaluation, and no CPU profiling; on-device latency is iPhone GPU (MPS) only (§3.6).
- MCUNet is about CNNs on a Cortex-M7 with 320 kB SRAM (Table 1). The board's STM32U585 MCU plays no role in the LLM (CHALLENGE_CONTEXT §2).

**What this means on the UNO Q.**
- *Gemma 3 270M is embedding-heavy.* About 170M of its 270M parameters are embeddings (CHALLENGE_CONTEXT §3). For Gemma 3 1B, 302M of 1B are embeddings (surveys note J2, citing the Gemma 3 report).
  - *Our inference:* in prefill, the input embedding is a lookup, and the matmul FLOPs come from the non-embedding parameters (Pope §2's 2N rule). So the 270M model could prefill several times faster than the 1B. That is the lever J1 says matters for the contract.
  - If the output layer is tied to the input embedding (MobileLLM §2.2.3 explains the mechanism), each decode step still multiplies by the whole 256k-row matrix. So the 270M model's decode is dominated by its vocabulary, and vocabulary trimming (pruning folder note, J6) would mostly speed up decode.
  - **VERIFY all of this with `llama-bench` pp and tg on 270M vs 1B.**
- *Do not pretrain a custom deep-thin or layer-shared model.* MobileLLM-LS needs training from scratch. Its speed argument assumes a ~20 MB SRAM holding a block; the A53's L2 size is not in the repo docs (**VERIFY**). Whether GGUF and llama.cpp can store a repeated block once, without duplicating weights, is also **VERIFY**.
- *Do not count on distillation from a large teacher at this size.* MobileLLM §3.5 found it slower and not better for pretraining. This is a pretraining result, and it does not test task-specific distillation for tutoring. The fine-tuning folder covers that.
- *MCUNet's lesson:* tune the engine settings (threads, context size, cache flags, quant type) together with the model choice, under the RAM budget. The repo already did this when it found that the default prompt cache causes out-of-memory kills (BOARD_SETUP §5.1).

**Open questions.**
- Measured pp and tg for Gemma 3 270M vs 1B at Q4_0 on the board.
- Does Gemma 3 270M tie its input and output embeddings in the GGUF?

## Papers not covered by any junction

None. MCUNet sits in J6 only as the co-design lesson. Its methods (NAS for CNNs, in-place depth-wise convolution) do not apply to the LLM.

## Links to other folders

- J5 (ternary models for bitnet.cpp): [[wang2023_bitnet_2310.11453.pdf|BitNet]], [[ma2024_bitnet_b158_2402.17764.pdf|BitNet b1.58]], [[ma2025_bitnet_b158_2b4t_2504.12285.pdf|BitNet b1.58 2B4T]] (quantization folder).
- J2, J6 (Gemma 3's GQA, local:global attention, embedding share, QAT Q4_0): [[gemma3_technical_report_2503.19786.pdf|Gemma 3 report]] (surveys folder).
- J6 (depth redundancy in large models vs MobileLLM's depth-first result for small ones): [[men2024_shortgpt_2403.03853.pdf|ShortGPT]] (pruning folder).
