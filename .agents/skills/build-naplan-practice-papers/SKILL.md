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
- Match the source question count exactly for every section and the complete paper. For the current Year 3 reference, require 50 Conventions of Language questions, 39 Reading questions, one Writing task, and 36 Numeracy questions.
- Keep each new question's stem, options, passage dependency, reasoning steps, and visual footprint close to its corresponding source item. Treat a word-count difference greater than roughly 20% as a review trigger unless the source item is primarily visual.
- Match the source test's section sequence, page density, column structure, question grouping, response-space proportions, and typographic hierarchy.
- Require exactly 20 student-facing pages for the current Year 3 paper. The answer-and-explanation appendix is additional and must begin after page 20; appendix pages must never be counted toward the 20-page student-paper requirement.
- Use font sizes and spacing comparable to the scans. Do not create oversized sparse pages or compress content into unreasonably small text. If content does not fit at reference-like density, revise the content or layout rather than silently changing the page count.
- For the current Year 3 format, require at least 7.4pt for student prompts, options, passages, and writing guidance; at least 6.8pt for essential diagram labels; and at least 7.4pt for appendix answers and explanations. Headers, footers, page numbers, and circular question numbers may be smaller only when they remain clearly legible.
- Record the requested font size for every rendered text box and validate minimum actual scale separately. A scale value of 1.0 does not prove readability when the template's requested font size is already too small.
- If the answer appendix cannot fit at the minimum readable size, add appendix pages. Never shrink answers or explanations merely to preserve an arbitrary appendix page count.

## Batch Generation and Convergence Rules

- Generate and validate the complete requested batch before release. Passing one representative paper does not prove that every content or drawing branch works.
- Build an official-source-derived Year 3 coverage matrix before generating a large batch. Cover genres, assessed skills, response forms, diagram families and writing purposes observed across multiple released papers, not only the local scan.
- Never count changed names, nouns, numbers, option order, question order or display position as a new task family. These are parameter variants, not genuine coverage.
- Never use one fixed Reading module in every paper. Across 50 papers, every Reading position must cycle through multiple genuine genres and assessment archetypes; no survey or named passage family may occupy the same slot in all papers.
- Report passage genre and question skill separately. One timetable should not stand in for timetable retrieval, elapsed time, cross-referencing and text-feature navigation as if they were the same demand.
- Language and Numeracy also require independently authored stem and representation variants. A template that merely substitutes a child, place, object or number remains one template.
- Produce a structural-reuse report that separates exact duplicates, parameter-only variants and genuinely different task families. Reject diversity claims supported only by rotations or substitutions.
- For 50 Year 3 papers, require at least 12 Reading passage archetypes, at least 10 Reading skills, all supported response kinds, and at least 10 passage archetypes at every one of the seven passage positions unless the user approves a narrower blueprint.
- No Reading passage archetype may appear in all 50 papers, and no single topic such as favourite sports may be a permanent section.
- Enforce normalized cross-paper uniqueness for question prompts, reading passages, writing prompts, and final PDF hashes. Reject accidental repeats even when names or numbers differ superficially.
- Reject duplicated answer options, tied probability outcomes, and distractors that create more than one defensible answer.
- Exercise every passage, diagram, chart, and writing-illustration variant. Missing template branch coverage is a release-blocking defect.
- Escape dynamic plain text, options, labels, answers, and explanations before inserting them into HTML or XML. Keep intentional markup separate from plain content.
- For spelling items, require exactly one intentional underlined error, perform case-insensitive replacement, and verify that the keyed correction restores the sentence.
- For locate-the-misspelling items, require every answer option to appear as a complete visible word in the final sentence; the keyed option must be the only misspelling and its recorded correction must restore a valid word.
- Prevent spelling-answer leakage against the complete visible student page, including headings, directions, other questions and options. Compare complete words rather than raw substrings, and exclude any dictated target that appears visibly elsewhere on that page.
- Every item must state exactly what the student must do. Reject vague fragments such as `Error: ...`, unexplained wrong words, generic filler such as `task:`, and contrived scaffolds such as `X wrote <misspelling> neatly` that do not form a meaningful question.
- Intentional spelling or punctuation errors are permitted only when the prompt explicitly identifies the editing task. The surrounding sentence must remain natural enough for a Year 3 student to understand what is being corrected.
- A generated misspelling must not be another correctly spelt English word. Prefer a mechanically reversible one-character duplication typo, validate that deleting exactly one duplicated character restores the keyed word, and reject deletion/substitution variants such as `patent` for `patient` that remain valid words without sentence context.
- Never insert option letters A/B/C/D into a sentence to mark punctuation positions. Show one complete readable sentence, then use descriptive options such as `after gate` or `between n and t in cant`.
- Verify that every option answers the exact question asked. Reject unrelated word lists, incomplete location labels, options that depend on hidden formatting, and any item whose task cannot be explained in one clear sentence.
- Add semantic rejection tests at both structured-content and final-PDF text levels for known malformed patterns. A visually fitting card is still a release blocker when its wording is awkward, ambiguous, nonsensical, or incomplete.
- Use separate normalization rules for editable markup and extracted PDF text. Never apply a broad HTML-tag regex to mathematical comparison text because it can delete content between `<` and `>` symbols.
- Recalculate every generated mathematics answer independently from the final parameters and verify the final option order, diagram data, units, and explanation.
- Treat convergence as a loop: generate all, validate all, render all, inspect all, fix, then rerun every affected gate. A shared-generator fix requires a full-batch rerun.
- Enforce fidelity per paper, not only as a batch average. Every Year 3 PDF must individually contain the exact section counts, reference-like item lengths and density, exactly 20 student-facing pages, and a separately counted appendix after page 20.
- Reject unexplained font-size changes between otherwise equivalent questions, options, labels, or answer entries. Typography must follow a deliberate section-wide hierarchy rather than item-specific fitting.

## Two-Up Imposition Rules

- Treat A4 landscape two-up as a separate typesetting target, not as a blind 70.7% reduction of the standard pages. Reflow within each logical half-page when needed, while preserving every word, item, answer area, diagram, page order, and question number.
- Maximise readable type within each text box. Require at least 7.4pt effective size after imposition for prompts, options, passages, writing guidance, and appendix text, and at least 6.8pt for essential diagram labels. Reject any hidden HTML/PDF text scaling below 1.0.
- Large unused regions beside small text are a release blocker unless the region is deliberately reserved for a student response, working, planning, or writing. Measure content needs, shrink genuinely over-tall passage or instruction boxes, and return that space to questions before considering smaller type.
- Determine prompt, response, and passage heights from measured final content rather than fixed guessed heights. Validate the most crowded item of every response kind and rerun the complete batch after a shared layout change.
- Preflight every generated dense card at the exact final typography before starting a long batch render. For a 50-paper Year 3 batch, measure all 1,250 spelling cards, not only one representative form.
- Preflight every generated Conventions of Language card at the exact two-up dimensions and fixed typography, including all 1,250 grammar/punctuation cards and all 1,250 spelling cards. Do not discover an over-height insertion or editing prompt only after batch imposition begins.
- Choose spelling-option column counts from rendered word length and available width. Short options may use four columns; long variants must reflow to two columns. Reject joined markers or words such as `cupboardB`, even when text extraction still succeeds.
- Draw scored grids, fraction bars, area models, number-line nodes, coins, and similar symbols with vector geometry. Never use mixed Unicode filled/empty square or circle glyphs as diagram cells; filled and unfilled cells must share identical dimensions, stroke widths, alignment, and spacing.
- Any chart used for a numerical calculation must expose the required scale or exact values in the student-facing rendering. Hidden model values do not count; reject an unlabelled bar chart that asks for a numerical difference.
- Inspect line breaks after final two-up imposition. Reject orphaned option markers, isolated punctuation, unnatural one-word fragments, prompt text entering a diagram, labels colliding with axes or shapes, and answer lines crossing text.
- Render and inspect all two-up sheets, with explicit high-risk checks for the spelling page, longest reading questions, data displays, densely labelled numeracy visuals, filled-versus-empty shapes, and the final numeracy page.

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
