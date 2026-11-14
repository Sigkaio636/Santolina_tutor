---
name: academic-paper-summarizer
description: "Summarize academic papers with structured extraction of key elements"
metadata:
  openclaw:
    emoji: "📋"
    category: "literature"
    subcategory: "metadata"
    keywords: ["paper summary", "structured extraction", "abstract", "key findings", "research synthesis", "literature review"]
    source: "https://github.com/lifan0127/ai-research-assistant"
---

# Academic Paper Summarizer

## Overview

Academic papers are dense, technical documents that require significant time to read and understand fully. The Academic Paper Summarizer skill provides a systematic framework for extracting the essential elements from research papers into structured, reusable summaries.

This skill is designed for researchers who need to rapidly process large volumes of literature—whether during a systematic review, when onboarding into a new field, or when preparing a literature review section for their own manuscripts. Rather than producing generic summaries, it enforces a structured template that captures the components most relevant to downstream academic work: research questions, methodology, key findings, limitations, and contributions to the field.

The skill works with any academic paper format (PDF, HTML, plain text) and can be adapted across disciplines from biomedical sciences to social sciences, engineering, and humanities. It emphasizes fidelity to the original text while organizing information into a consistent schema that facilitates comparison across papers.

## Structured Extraction Framework

The core of this skill is a multi-section extraction template. When summarizing a paper, populate each of the following fields:

**Bibliographic Metadata:**
- Title, authors, journal/conference, year, DOI
- Paper type (empirical, review, theoretical, methodological, case study)

**Research Context:**
- What gap in the literature does this paper address?
- What is the stated research question or hypothesis?
- How does the paper position itself relative to prior work?

**Methodology Summary:**
- Study design (experimental, observational, computational, qualitative, mixed)
- Data sources, sample size, and key variables
- Analytical methods and tools used
- Any novel methodological contributions

**Key Findings:**
- Primary results stated in 3-5 bullet points
- Statistical significance or effect sizes where reported
- Figures and tables worth revisiting (note figure/table numbers)

**Critical Assessment:**
- Strengths of the study design and execution
- Limitations acknowledged by authors and any additional limitations you identify
- Potential biases or confounding factors
- Generalizability of findings

**Relevance and Connections:**
- How does this paper connect to your current research?
- Which references cited in this paper should you follow up on?
- Does this paper support, contradict, or extend existing findings in your collection?

## Batch Processing Workflow

When processing multiple papers (e.g., during a literature review), follow this workflow for efficiency:

1. **Triage pass**: Read title, abstract, and conclusions of each paper. Assign a relevance score (1-5) and decide whether to perform full extraction.
2. **Full extraction**: For papers scoring 3+, apply the complete structured extraction template above.
3. **Cross-paper synthesis**: After extracting 5-10 papers on a related subtopic, create a synthesis note that identifies common findings, methodological trends, and open questions.
4. **Gap identification**: Compare your extraction set against your research questions to identify what evidence is still missing.

**Example extraction prompt:**

```
Read this paper and extract the following in structured format:
1. Bibliographic info (title, authors, year, journal, DOI)
2. Research question / hypothesis
3. Methodology (design, data, sample, analysis)
4. Key findings (3-5 bullets with effect sizes)
5. Limitations and biases
6. Relevance to [your topic]
7. Key references to follow up
```

## Long Papers (MinerU)

*Local addition to the upstream skill.* For a paper longer than about 15 pages, or one whose tables, equations or figures matter, convert the PDF to Markdown first. Reading the raw PDF in page chunks loses equations and table structure.

1. Check that MinerU is installed: `[ -x .venv/bin/mineru ] || command -v mineru`.
2. If it is, run the script with the paper as argument, then read the Markdown it prints by headings, one section at a time, and fill the extraction template from it:
   ```bash
   bash .claude/skills/academic-paper-summarizer/scripts/mineru_parse.sh docs/vault/papers/pruning/paper.pdf
   ```
   The script accepts several PDFs and prints one `.md` path per paper on stdout (MinerU logs go to stderr). It writes to `<pdf dir>/parsed/<name>/` (override with `PAPER_OUT`) and skips papers that are already converted. With MinerU 3.x the file ends up at `parsed/<name>/<name>/auto/<name>.md`, so use the printed path, not a guessed one.
   Checked on a 14-page paper (GPU, about 45 s): headings come out as `#`/`##` (subsections are also `##`), equations as `$$ ... $$` LaTeX, tables as HTML `<table>`, figures as `![](images/...)` files next to the `.md`. Read the `.md` in sections (`grep -n '^#'` for the outline, then `Read` with offset/limit). Open an image only when a figure matters.
3. If MinerU is not installed, say so. Offer `scripts/install_mineru.sh` (runs `uv sync --group ocr`, several GB) and wait for the user's yes. Meanwhile, read the PDF with `Read` in chunks of at most 20 pages.
4. If the script exits with code 1, report the failure and use the `Read` fallback. Do not retry in a loop.

## Tips for High-Quality Summaries

- **Preserve author voice for claims**: When summarizing findings, note whether the authors use hedging language ("suggests", "may indicate") versus strong claims ("demonstrates", "proves"). This matters for synthesis.
- **Note negative results**: Papers often bury non-significant findings. Explicitly extract these, as they are crucial for meta-analyses and for avoiding publication bias in your review.
- **Tag with your own keywords**: Beyond the authors' keywords, add your own tags that connect the paper to your research framework. This makes retrieval easier later.
- **Record page numbers**: When noting key findings or quotes, record the page number so you can return to the source quickly.
- **Update summaries**: If you re-read a paper later with new context, update the summary rather than creating a duplicate.

## Output Formats

Summaries can be exported in several formats depending on your workflow:

- **Markdown**: For integration with note-taking tools (Obsidian, Notion, Logseq)
- **BibTeX annotation**: Append the summary as an `annote` field in your BibTeX entry
- **CSV row**: For spreadsheet-based literature tracking with one row per paper
- **JSON**: For programmatic processing or import into reference managers

## References

- Keshav, S. (2007). "How to Read a Paper." ACM SIGCOMM Computer Communication Review.
- Pautasso, M. (2013). "Ten Simple Rules for Writing a Literature Review." PLOS Computational Biology.
- AI Research Assistant: https://github.com/lifan0127/ai-research-assistant
