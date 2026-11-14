# Findings: docs/vault/papers/inference/_synthesis.md

Open findings of `/docs-review`. Schema: `.claude/skills/doc-authoring/references/findings-schema.md`.

## S1 audit (2026-11-14)

Weight: heavy (explanation). Paper figures were checked for arithmetic and against other notes only: the PDFs are gitignored.

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| F1 | docs/vault/papers/inference/_synthesis.md | 22-27, 279-281 | 5 broken links | `[[<slug>.pdf\|...]]` wikilinks | no wikilink support; PDFs excluded and gitignored | verified | breaks | - |
| F2 | docs/vault/papers/inference/_synthesis.md | 9, 16 | 7 terminology | "the tutor" | `GLOSSARY.md:7-9` | verified | cosmetic | - |
| F3 | docs/vault/papers/inference/_synthesis.md | 51 | 8 contradictions | no SDOT/UDOT/I8MM is "marked VERIFY" in CHALLENGE_CONTEXT | `CHALLENGE_CONTEXT.md:60` "Confirmed on our board" | verified | misleading | - |
| F4 | docs/vault/papers/inference/_synthesis.md | 207, 236 | 6 placeholder | `asimddp` left as VERIFY / open | `UNO_Q_BOARD_REFERENCE.md:309,501-509` measured: absent | verified | misleading | - |
| F5 | docs/vault/papers/inference/_synthesis.md | 71 | 8 contradictions | "board docs suggest" bandwidth-bound decode may not hold | `CHALLENGE_CONTEXT.md:60`, `UNO_Q_BOARD_REFERENCE.md:507-509` say it is bandwidth-bound | verified | misleading | - |
| F6 | docs/vault/papers/inference/_synthesis.md | 16, 74, 76 | 8 contradictions | decode may be compute-bound; "fewer bits ⇒ faster" unconfirmed | other docs assert the opposite; no measurement settles it — S3: S3 Q15 (user): move to "Open questions": not measured on our board | verified | misleading | F5 |
| F7 | docs/vault/papers/inference/_synthesis.md | 76 | 8 contradictions | "Our Q8_0 run gives 5-6 tok/s" | `UNO_Q_BOARD_REFERENCE.md:470,516` 4.8 tok/s measured | verified | cosmetic | - |
| F8 | docs/vault/papers/inference/_synthesis.md | 16, 76, 83, 157, 264 | 1 stale | run `llama-bench` | `board/02_build_llama_cpp.sh:27` builds only llama-server, llama-cli | verified | breaks | - |
| F9 | docs/vault/papers/inference/_synthesis.md | 229 | 5 broken links | "Gemma's QAT Q4_0 (see J1)" | J1 (53-83) never mentions QAT; it is in `surveys/_synthesis.md:89` | verified | cosmetic | - |
| F10 | docs/vault/papers/inference/_synthesis.md | 118-122, 155-157 | 10 formatting | 2-space nested bullets | Python-Markdown needs 4 spaces — S3: same; 114-122 render as raw text | verified | cosmetic | - |
| F11 | docs/vault/papers/inference/_synthesis.md | 117-122, 157, 264 | 11 type-mixing | explanation with step-by-step procedures | - — S3 Q4 (user): no split; the lede states the type and steps go to a final "What to try" section | verified | cosmetic | - |

## S2 critique (2026-11-14)

Type: explanation, heavy. 12 findings (0 breaks, 5 misleading, 7 cosmetic).

| id | file | line | category | claim | evidence | status | severity | depends_on |
|---|---|---|---|---|---|---|---|---|
| C1 | docs/vault/papers/inference/_synthesis.md | 8-14 | readability/1 lede | opens with "Changes to the proposed junctions" | purpose only at 16 | verified | misleading | - |
| C2 | docs/vault/papers/inference/_synthesis.md | 6, 18 | readability/5 jargon | "junction" | defined only in `docs/vault/papers/README.md:10` | verified | misleading | - |
| C3 | docs/vault/papers/inference/_synthesis.md | 9, 16 | readability/5 jargon | "prefill", "decode" carry the lede | defined only at 57 | verified | misleading | - |
| C4 | docs/vault/papers/inference/_synthesis.md | 16 | readability/4 sentences | about 50 words joined by ";" | rule 4 | verified | cosmetic | - |
| C5 | docs/vault/papers/inference/_synthesis.md | 16 | readability/4 sentences | 30 words with a nested clause | rule 4 | verified | cosmetic | - |
| C6 | docs/vault/papers/inference/_synthesis.md | 51 | readability/8 form | 5 board facts in one 60-word sentence | a list | verified | cosmetic | - |
| C7 | docs/vault/papers/inference/_synthesis.md | 61, 76, 229, 264, 270 | readability/5 jargon | "MFU", "tg", "pp" | never expanded; the test cannot be acted on | verified | misleading | - |
| C8 | docs/vault/papers/inference/_synthesis.md | 51-195 | readability/5 jargon | SDOT/UDOT/I8MM, NEON, HBM, SRAM, GQA, NPU, eMMC, UFS | no expansion | verified | cosmetic | - |
| C9 | docs/vault/papers/inference/_synthesis.md | 26, 205, 214 | readability/5 jargon | "LUT kernel", "mpGEMM", "mpGEMV" | not expanded | verified | cosmetic | - |
| C10 | docs/vault/papers/inference/_synthesis.md | 10, 23 | readability/5 jargon | "KV cache" | never explained; J2 depends on it | verified | misleading | - |
| C11 | docs/vault/papers/inference/_synthesis.md | 9-154 | readability/9 links | "BOARD_SETUP §5.5", "CHALLENGE_CONTEXT §2" | no path, no link | verified | cosmetic | - |
| C12 | docs/vault/papers/inference/_synthesis.md | 219 | readability/4 sentences | 28 words, 2 ideas | rule 4 | verified | cosmetic | - |
