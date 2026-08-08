# Practice Paper 01 Final Audit

## Output

- PDF: `y3/output/year3-naplan-style-practice-paper-01.pdf`
- Total pages: 20 A4 pages, matching the 20-page reference constraint exactly.
- Student paper: pages 1-17.
- Answer-and-explanation appendix: pages 18-20.
- Scored questions: 110 — Language 50, Reading 30 and Numeracy 30.
- Writing tasks: 1 narrative task.

## Cached Source Review

- All 20 immutable files in `y3/orig/` are mapped in `y3/work/source-manifest.json`.
- Confirmed order: `IMG_9320.jpg` through `IMG_9339.jpg`, corresponding to visible reference pages 21-40.
- SHA-256 and byte-size checks passed for all 20 files against `y3/source-cache/source-hashes.json`.
- The canonical, human-verifiable source is `y3/source-cache/year3-reference-test-2.md`.
- No OCR was rerun. The renderer and validator use the verified cache whenever source hashes match.

## Fidelity Review

- Reference counts are preserved exactly: 50 Language, 30 Reading, 1 Writing and 30 Numeracy.
- Language preserves the 25 grammar/punctuation plus 25 contextual spelling structure.
- Reading preserves five texts with six questions each and a similar literal, vocabulary, inference, purpose and visual-data mix.
- Numeracy preserves number, operations, patterns, money, time, measurement, geometry, fractions, data, chance and diagram interpretation.
- Question and passage length proxies are recorded in `y3/work/paper-01/fidelity-report.json`; no item falls outside the approved Year 3 compact-workbook bands.
- Every scored item was independently checked against its final wording, options, diagram and explanation. Each has exactly one defensible answer.

## Page-by-Page Visual Inspection

| Pages | Content | Status |
|---|---|---|
| 1-3 | Language questions 1-25 | Checked: wording, punctuation marks, option order, numbering, spacing and page boundaries. |
| 4 | Spelling questions 26-50 | Checked: every deliberate misspelling, response box, two-column alignment and answer mapping. |
| 5-9 | Five reading texts and questions 1-30 | Checked: every paragraph, table/poem line, question, option, text reference and page layout. |
| 10 | Narrative writing task | Checked: illustration, prompt, planning guidance, writing lines and review reminders. |
| 11-17 | Numeracy questions 1-30 | Checked: every number, unit, option, grid, fraction bar, square, cube, map, graph and spinner. |
| 18 | Language answers 1-50 | Checked at full-page resolution: all entries readable, complete and correctly aligned. |
| 19 | Reading answers 1-30 | Checked: every key and explanation matches the final passage and option order. |
| 20 | Numeracy answers 1-30 and writing review | Checked: all calculations, units, visual answers and review text. |

No clipping, overlap, overflow, duplicate page, unintended blank page, broken glyph, distorted diagram or low-resolution raster element was found. Minimum layout text scale is 1.0000; no content was shrunk by the layout engine.

## Automated Validation

Run:

```bash
PYTHONPYCACHEPREFIX=/tmp/naplan-pycache python3 y3/work/paper-01/render_pdf.py
PYTHONPYCACHEPREFIX=/tmp/naplan-pycache python3 y3/work/paper-01/validate.py
```

The validator checks source hashes, the one-time OCR policy, exact question IDs and counts, question/passage length bands, 20 A4 pages, 17/3 student-to-appendix split, non-empty pages, Unicode extraction, all 110 prompts and explanations, inventory alignment, layout scaling and unique rendered-page hashes.

## Intentional Layout Differences

- The generated paper uses clean vector shapes and text rather than reproducing photographic page curvature, fingers or perspective distortion.
- The original pale-aqua hierarchy and compact workbook density are retained, with limited spacing adjustments for legibility.
- The appendix is compressed into three dense but readable pages so the complete output remains exactly 20 pages.

## Release Decision

No critical or major issue remains open. Practice Paper 01 passes the defined source, content, answer, cross-reference, layout, rendered-page and cache gates.
