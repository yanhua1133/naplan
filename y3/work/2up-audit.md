# A4 Landscape Two-Up Audit

- Status: `passed` for all 50 files.
- Output: `y3/output/2up/p01.pdf` through `p50.pdf`.
- Format: A4 landscape, two logical source pages per sheet; 13 sheets per PDF.
- Page size: A4 landscape only; obsolete A3 and alternate two-up directories are removed before every rebuild.
- Content source: the verified generated-paper model is reused; no OCR and no new question authoring occurs during imposition.
- Typography: fixed hierarchy, minimum effective essential text 6.85 pt and minimum per-paper median 7.63 pt after imposition; hidden fitting below 99.9% is rejected.
- Spelling sheet: all 50 sheet-2 right halves preserve the source-locked 15 dictation / 5 underlined correction / 5 locate-and-correct structure.
- Underline rule: every `correct_underlined` item has one visible underlined error; `locate_error` items have none; dictated answers are absent from student pages.
- Geometry rule: text from each logical page must survive in the correct half, no prompt or response box may overflow or use hidden scaling, and every external diagram label must pass an explicit non-overlap and minimum-gap check.
- Diagram containment: 1000 diagram regions passed with 1450 label-gap checks and 0 vector boundary crossings.
- Machine-readable evidence: `y3/work/2up-validation.json`. This Markdown file is generated from that same report and must never be maintained as a stale hand-written summary.
