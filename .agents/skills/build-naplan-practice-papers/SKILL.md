---
name: build-naplan-practice-papers
description: Build, typeset, and rigorously validate Australian NAPLAN-style practice-paper PDFs from photographed or scanned source pages. Use when Codex needs to order source scans, transcribe or adapt Year 3 test material, create complete mock papers, add answer-and-explanation appendices, reproduce diagrams and page layouts, audit question correctness, or perform page-by-page and word-by-word PDF quality assurance in this repository.
---

# Build NAPLAN Practice Papers

## Overview

Create traceable, print-ready practice papers from imperfect scan photographs without sacrificing textual, mathematical, visual, or layout correctness. Treat validation as part of generation: no PDF is final until every source page, final page, question, answer, explanation, and visual element has passed the required checks.

Read `references/quality-gates.md` before creating or approving any paper. Apply every relevant gate and retain evidence in the repository's working artifacts.

## Operating Rules

- Treat `y3/orig/` as immutable evidence and `y5/` as out of scope unless explicitly requested.
- OCR each unchanged source set only once. Store the result in a canonical, human-verifiable source cache such as `y3/source-cache/reference.md` plus structured metadata. Never rerun batch OCR during later paper generation when the cache is valid.
- Record source image hashes in the cache. Rerun OCR only when files are added, removed, replaced, or their hashes change; document the invalidation reason.
- Use OCR only to bootstrap the cache. Manually compare and correct the cached source against every scan before marking it verified. Later work must read the verified cache first and use scans only for targeted visual spot-checks or unresolved details.
- Resolve ordering from visible evidence. Never assume lexical filename order is correct without checking page content.
- Preserve exact source wording for reproduced content. Track every intentional adaptation.
- Stop and surface blockers when an image is unreadable, cropped, contradictory, or missing continuation content.
- Keep editable generation sources and audit records; a PDF-only workflow is insufficient.
- Never claim exact NAPLAN affiliation or official status. Describe outputs as NAPLAN-style practice materials.

## Mandatory Fidelity Constraints

- Match the reference paper's difficulty distribution. Do not make the paper materially easier or harder overall, and do not replace advanced source items with routine one-step items.
- Match the source question count exactly for every section and the complete paper. For the current Year 3 reference, require 50 Conventions of Language questions, 30 Reading questions, one Writing task, and 30 Numeracy questions.
- Keep each new question's stem, options, passage dependency, reasoning steps, and visual footprint close to its corresponding source item. Treat a word-count difference greater than roughly 20% as a review trigger unless the source item is primarily visual.
- Match the source test's section sequence, page density, column structure, question grouping, response-space proportions, and typographic hierarchy.
- Require exactly 20 pages for the current Year 3 paper, including the answer-and-explanation appendix. Any other page count is a release-blocking error.
- Use font sizes and spacing comparable to the scans. Do not create oversized sparse pages or compress content into unreasonably small text. If content does not fit at reference-like density, revise the content or layout rather than silently changing the page count.

## Workflow

### 1. Inventory the source

- Enumerate every source image and record dimensions, orientation, and legibility.
- Inspect every image and infer logical page order from page numbers, headings, passage/question continuation, and front/back relationships.
- Create a manifest containing at least `logical_page`, `source_file`, `orientation`, `ordering_evidence`, `content_summary`, and `issues`.
- Record gaps, duplicates, uncertain ordering, cropped edges, glare, blur, and unreadable details before transcription.

### 2. Build the content model

- Transcribe directions, passages, questions, options, labels, numbers, punctuation, and visible formatting hierarchy.
- Attach provenance to each source-derived element: source filename, logical page, and location or question number.
- Separate source-faithful content from newly authored or adapted content.
- Represent question IDs, answer choices, assets, answer keys, and explanations in structured data when practical so consistency checks can be automated.
- Perform a line-by-line comparison against the scan after transcription. Do not rely on a single OCR or reading pass.

### 3. Design complete papers

- Define the paper structure before typesetting: front matter, sections, passages, question ranges, response formats, and appendix.
- Make each PDF self-contained and ensure question numbering is unique, sequential, and stable.
- Match the source's visual language and student experience while allowing limited changes for clear pagination and reliable printing.
- Keep difficulty, vocabulary, expected knowledge, and response burden appropriate for Year 3 unless the user requests another level.
- For newly authored questions, check that all required information is present and that distractors are plausible but unambiguously wrong.

### 4. Create answers and explanations

- Solve every final question independently before accepting its keyed answer.
- Verify calculations, units, spelling, grammar, factual claims, diagram readings, and passage evidence.
- Require exactly one defensible answer for single-answer items.
- Write concise explanations at an adult-review level while remaining clear enough to support a student or parent.
- Cross-check that every scored question has one matching appendix entry and that the entry refers to the final wording and final option order.

### 5. Generate the PDF

- Generate from editable, deterministic source rather than manually assembling final pages.
- Embed or package required fonts and assets where the chosen toolchain permits.
- Use print-safe contrast, legible type sizes, consistent margins, and sufficient response space.
- Preserve image aspect ratios and redraw diagrams only when the redraw can be checked point-for-point against the source intent.
- Put answers and explanations after the full student paper.

### 6. Validate structure and semantics

- Confirm the PDF opens, has the intended page size and count, contains no blank or duplicate pages, and has no missing assets.
- Extract text from the PDF and check for replacement characters, unexpected omissions, duplicated paragraphs, numbering gaps, and answer-key coverage.
- Compare final text against the approved content model, not only against the typesetting source.
- Re-solve questions from the final PDF because layout or option-order changes can invalidate an earlier key.

### 7. Inspect every rendered page

- Render every page at a resolution high enough to inspect body text, punctuation, thin lines, and image labels.
- Inspect 100% of rendered pages in logical order. Do not sample.
- Check clipping, overflow, spacing, page breaks, alignment, contrast, visual hierarchy, answer areas, diagrams, and page references.
- Compare all source-derived visuals and layouts against the corresponding scans.
- Correct defects, regenerate, and repeat all affected checks.

### 8. Run the final independent pass

- Review the final PDF from page 1 without trusting earlier notes.
- Read every sentence and option, inspect every image, and verify every answer reference.
- Apply the release gate in `references/quality-gates.md`.
- Report unresolved uncertainties. If any critical or major issue remains, label the output as a draft and do not release it as final.

## Required Audit Artifacts

- Source manifest with confirmed page order.
- Issue log with status and resolution.
- Structured question/answer inventory or equivalent traceable record.
- Rendered-page inspection checklist covering every final page.
- Final release summary with PDF path, page count, question count, validation performed, intentional layout deviations, and remaining limitations.

Keep these artifacts under `y3/work/` or another clearly documented non-original path. Put temporary rendered pages under `y3/build/` and final PDFs under `y3/output/` unless the project later establishes different conventions.

## Release Language

Use “final” or “fully validated” only when every mandatory quality gate passes. Otherwise use “draft,” name the missing checks, and state what remains to be resolved.
