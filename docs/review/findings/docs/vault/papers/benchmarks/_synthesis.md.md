# Findings: docs/vault/papers/benchmarks/_synthesis.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy. Paper figures were checked for arithmetic and against other notes only: the PDFs are gitignored.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/vault/papers/benchmarks/_synthesis.md | 13-22, 147-151 | 5 broken links | PDF wikilinks | gitignored, excluded, no wikilink support | verified | breaks | - |
| F2 | docs/vault/papers/benchmarks/_synthesis.md | 106-109 | 8 contradictions | "format is the first thing to fix, use a GBNF grammar" | `copilot/llm.py:45-46` already does it | verified | misleading | - |
| F3 | docs/vault/papers/benchmarks/_synthesis.md | 138 | 3 renamed | language slice "eng/cat/spa" | the code is `esp` (`laptop/prepare_m3kang.py:16,40,42`) | verified | misleading | - |
| F4 | docs/vault/papers/benchmarks/_synthesis.md | 12-143 (17 places) | 10 formatting | paragraph runs into a `- ` list with no blank line | Python-Markdown — S3: built page renders 68 raw "- " lines inside paragraphs | verified | cosmetic | - |
| F5 | docs/vault/papers/benchmarks/_synthesis.md | 10, 60, 84 | 7 terminology | "the tutor" | `GLOSSARY.md:7-9` | verified | cosmetic | - |
| F6 | docs/vault/papers/benchmarks/_synthesis.md | 21, 110-111 | 8 contradictions | plan and budget built on Gemma 3 270M/1B | `config.env:12-15` Qwen3.5 0.8B — S3 Q2 (user): the fine-tune base is not chosen yet; say Qwen3.5 0.8B is deployed and Gemma 3 is one option being explored | verified | misleading | - |

## S2 critique (2026-11-14)

Type: explanation, heavy. 17 findings (0 breaks, 3 misleading, 14 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/vault/papers/benchmarks/_synthesis.md | 8 | readability/1 lede | opens with "Changes to the proposed junctions" | the real lede is at 10 | verified | misleading | - |
| C2 | docs/vault/papers/benchmarks/_synthesis.md | 10 | readability/4 sentences | about 45 words, three takeaways | a list | verified | cosmetic | F5 |
| C3 | docs/vault/papers/benchmarks/_synthesis.md | 6, 16-22 | readability/5 jargon | "junction" | defined only in `_junctions.md:8-10` | verified | cosmetic | - |
| C4 | docs/vault/papers/benchmarks/_synthesis.md | 10, 35 | readability/5 jargon | "CoT" | never expanded | verified | cosmetic | - |
| C5 | docs/vault/papers/benchmarks/_synthesis.md | 19-22 | readability/8 form | "Papers" column: same two papers in all rows | no information | verified | cosmetic | F1 |
| C6 | docs/vault/papers/benchmarks/_synthesis.md | 22, 117 | readability/3 headings | J4 has two names | table vs heading | verified | cosmetic | - |
| C7 | docs/vault/papers/benchmarks/_synthesis.md | 14, 51 | readability/5 jargon | "UPV", "SCM" | not expanded | verified | cosmetic | - |
| C8 | docs/vault/papers/benchmarks/_synthesis.md | 32 | readability/5 jargon | chrF++, NLLB, back-translation, LLM-as-judge, Pearson | four terms in one clause | verified | cosmetic | - |
| C9 | docs/vault/papers/benchmarks/_synthesis.md | 45 | readability/4 sentences | "scrambled by the parser" | the PDF parser; 35 uses "parser" for the answer parser | verified | misleading | - |
| C10 | docs/vault/papers/benchmarks/_synthesis.md | 65-71 | readability/5 jargon | "activation steering", MGSM | not explained | verified | cosmetic | - |
| C11 | docs/vault/papers/benchmarks/_synthesis.md | 67 | readability/8 form | 3 models × 4 clusters in prose | a table | verified | cosmetic | - |
| C12 | docs/vault/papers/benchmarks/_synthesis.md | 69 | readability/8 form | 7 ca-vs-es model pairs in one bullet | a table | verified | cosmetic | - |
| C13 | docs/vault/papers/benchmarks/_synthesis.md | 124-125 | readability/8 form | image/no-image pairs in prose | tables | verified | cosmetic | - |
| C14 | docs/vault/papers/benchmarks/_synthesis.md | 83, 107, 110 | readability/5 jargon | control vectors, GBNF, `n_predict` | not defined | verified | cosmetic | F2, F6 |
| C15 | docs/vault/papers/benchmarks/_synthesis.md | 140 | readability/4 sentences | vision server "not supported by these papers" | reads as "does not work" | verified | misleading | - |
| C16 | docs/vault/papers/benchmarks/_synthesis.md | 31, 55, 108, 147 | readability/7 language | "quantisation" vs "quantization"; "organisers" | mixed spellings — S3 Q5 (user): everything in English except the transcript and original sources; US spelling | verified | cosmetic | - |
| C17 | docs/vault/papers/benchmarks/_synthesis.md | 48 | readability/5 jargon | "the laptop harness" | not named (`eval.py`?) — S3: no laptop harness; eval.py runs on the board | verified | cosmetic | - |
