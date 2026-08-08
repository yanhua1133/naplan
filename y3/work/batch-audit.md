# Year 3 Practice Papers 01–20 Batch Audit

## Outputs

- PDFs: `y3/output/year3-naplan-style-practice-paper-01.pdf` through `y3/output/year3-naplan-style-practice-paper-20.pdf`.
- Each PDF contains exactly 20 student-facing A4 pages followed by 6 readable answer-and-explanation pages, for 26 pages total.
- Each paper contains 50 Conventions of Language questions, 30 Reading questions, one Writing task, and 30 Numeracy questions.
- Batch total: 400 student-facing pages plus 120 appendix pages, for 520 pages overall; 2,200 scored questions and 20 Writing tasks.

## Source Basis

- Immutable source set: all 20 images in `y3/orig/`, ordered by `y3/work/source-manifest.json`.
- Canonical verified cache: `y3/source-cache/year3-reference-test-2.md`.
- Source hash record: `y3/source-cache/source-hashes.json`.
- The validator confirmed all 20 source hashes and did not rerun OCR.

## Fidelity and Uniqueness

- All papers retain the reference section order, question counts, item types, response burden, page density, typographic hierarchy, and exact 20-page student-paper length before the appendix.
- All 2,200 literal and structurally normalized question prompts are unique after removing names, places, dates, and numbers.
- Maximum mean similarity for corresponding question positions is 0.8864, below the enforced 0.90 threshold.
- All 100 reading passages and all 20 writing prompts are unique.
- All 20 PDF hashes and all 520 rendered-page hashes are unique.
- All 600 Numeracy answers were independently recalculated from final generated parameters.
- Minimum layout scale across the batch is 0.9865; no emergency shrinking or sub-minimum font size was used.
- Minimum requested sizes are 7.4pt for student body text, 6.8pt for essential diagram labels, and 7.4pt for appendix entries.

## Validation Performed

- Generated all papers and rendered all pages with `python3 y3/work/render_paper.py --all`.
- Ran structural, semantic, source-hash, answer, uniqueness, length-band, PDF-text, and rendered-page checks with `python3 y3/work/validate_all.py`.
- Visually inspected contact sheets covering every page of all 20 PDFs for clipping, overlap, blank or duplicate pages, visual branch failures, diagram placement, writing illustrations, and appendix density.
- Machine-readable result: `y3/work/batch-validation.json` with status `passed`.

## Intentional Layout Departures

- The source visual hierarchy and page density are preserved, but newly authored passages, contexts, names, and diagrams use deterministic vector layouts rather than reproducing scan artefacts.
- Answer explanations are typeset in a readable six-page appendix after the student paper.

## Open Issues

- None at release-gate severity. No unresolved Critical, Major, or accepted Minor issue remains in the current batch.
