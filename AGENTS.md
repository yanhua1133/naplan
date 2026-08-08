# Repository Mission

Build high-quality Australian NAPLAN-style practice papers from supplied scan photographs. The current source set is under `y3/orig/`. Produce multiple print-ready PDF papers, each containing a complete student paper followed by an answer-and-explanation appendix.

# Scope

- Work on Year 3 (`y3/`) unless the user explicitly changes scope.
- Treat `y5/` as out of scope until source material is supplied or the user asks for Year 5 work.
- Treat every file in `y3/orig/` as immutable source evidence. Never edit, rename, recompress, rotate in place, or delete an original.
- Use `.agents/skills/build-naplan-practice-papers/` whenever inspecting scans, transcribing content, creating questions, generating PDFs, or validating a paper.

# Non-Negotiable Quality Bar

- Verify every page, question, sentence, word, punctuation mark, number, unit, label, table, diagram, and image.
- Do not tolerate typos, missing content, duplicated content, contradictory instructions, broken references, ambiguous answers, incorrect explanations, or unreasonable layouts.
- Never guess unreadable or uncertain source content. Record the uncertainty, inspect the best available source, and stop for user clarification if it cannot be resolved reliably.
- Do not call a paper complete based only on successful compilation. Completion requires source, semantic, answer, cross-reference, and rendered-page checks.
- Prefer correctness over speed and traceability over convenience.
- Match the source paper's difficulty, exact per-section question counts, approximate per-item length, visual density and total page count. For the current Year 3 source, the final PDF must be exactly 20 pages.
- OCR an unchanged source set once only. Build and manually verify a canonical source cache, record source hashes, and use that cache for all later generation. Do not rerun batch OCR unless the source hash set changes.

# Source Handling

- Determine page order from visible page numbers, headers, question continuity, passage continuity, and front/back relationships. Filenames and capture timestamps are hints only.
- Maintain a manifest that maps each logical source page to its original image filename and records orientation, ordering evidence, and unresolved issues.
- Preserve exact wording when reproducing source material. If intentionally adapting content, mark it as adapted in working records and revalidate the entire resulting question independently.
- Preserve the source's visual hierarchy and test-taking intent. Small layout changes are acceptable only when they improve legibility or solve pagination constraints without changing meaning.

# Content Requirements

- Each output PDF must be a self-contained, complete practice paper.
- Keep directions, passages, questions, options, response areas, page numbers, and appendices internally consistent.
- Give every scored item exactly one defensible answer unless the item explicitly permits multiple answers.
- Write explanations that show why the keyed answer is correct and, when useful, why plausible alternatives are wrong.
- Solve every item independently from the final typeset version; never derive the answer key only from drafts or assumptions.
- Keep vocabulary, cognitive load, response format, and visual density appropriate for the source year level.
- Avoid accidental dependence on colour unless the final PDF is explicitly intended for colour printing.

# Layout and PDF Requirements

- Use consistent page size, margins, typography, spacing, headers, footers, numbering, option markers, and answer styling.
- Keep each question with the material needed to answer it whenever practical.
- Prevent clipping, overflow, orphaned instructions, split answer options, tiny text, distorted images, low-resolution diagrams, and blank or duplicate pages.
- Ensure diagrams remain accurate after scaling and that all labels, legends, axes, units, and answer references remain readable.
- Put the answer-and-explanation appendix after the complete student-facing paper, not interleaved with questions.

# Required Workflow

1. Inventory and order the source scans.
2. Create a page-level source manifest and issue log.
3. Transcribe or model source content with page/question provenance.
4. Design each complete practice paper and its answer appendix.
5. Generate the PDF deterministically from editable source files.
6. Run automated structural and text checks.
7. Render every PDF page to an image and inspect every rendered page visually.
8. Perform a separate final content pass against the source and answer key.
9. Release only when all quality gates pass with no unresolved high-severity issue.

# Working Artifacts

- Keep generated or intermediate files outside `y3/orig/`.
- Prefer clear, stable paths such as `y3/work/` for manifests and editable sources, `y3/build/` for temporary renders, and `y3/output/` for final PDFs.
- Keep enough audit information to trace every final page and question back to its source or documented original design decision.
- Do not commit disposable caches, local IDE state, or temporary render debris unless specifically requested.

# Completion Report

When delivering papers, report:

- output PDF paths and page counts;
- source images used and confirmed page order;
- number of questions and answer entries per paper;
- validation commands or checks performed;
- any intentional departures from the scan layout;
- all unresolved uncertainties or limitations.

If any required verification was not performed, state that clearly and do not describe the output as final or fully validated.
