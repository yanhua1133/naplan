# Rendered Page Inspection

Status: **passed** after correction and complete reinspection.

## Scope

- Standard PDFs: all 26 logical page positions across all 50 papers, covering 1,300 rendered pages.
- Student paper: all 20 page positions across all 50 papers, covering 1,000 rendered student pages.
- Answer appendix: all 6 page positions across all 50 papers, covering 300 rendered appendix pages.
- A4 landscape two-up: all 13 sheet positions across all 50 papers, covering 650 rendered sheets and 1,300 logical half-pages.
- High-risk spelling region: sheet 2 right half from all 50 two-up PDFs, reinspected in five enlarged groups of ten papers.
- High-risk answer region: standard appendix page 22 and two-up sheet 11 right half from all 50 papers, reinspected in five contact-sheet groups each.

## Checks

- No clipping, overlap, gutter crossing, duplicate page, unintended blank page or missing half-page.
- No unexplained font-size jump, hidden text fitting, unreadable body text or excessively compressed option row.
- Writing page whitespace is intentional response space; no other suspicious empty region was found.
- Diagrams preserve geometry, labels and alignment; filled and unfilled fraction cells use equal-sized vector rectangles.
- Spelling pages preserve blank dictation lines, readable written-correction prompts and response lines, and visible underlining only for `correct_underlined` items.
- Answer pages use a consistent two-column hierarchy without clipped explanations.

## Closed During Inspection

- The first two-up inspection found that the custom true/false table retained `True` and `False` but omitted the `Statement` column heading.
- The heading was restored in `y3/work/impose_2up.py`, all 50 two-up PDFs were rebuilt, and all 1,300 logical half-pages were text-compared again with zero differences.
- Fixed-height two-up spelling rows were replaced with measured per-item height allocation so long written-correction prompts cannot overlap adjacent cards.
- The spelling directions now use the audited body typography; effective non-diagram body text remains at least 7.63pt, while the 6.85pt batch minimum is confined to essential diagram labels.
- After rebuilding all 50 two-up PDFs, the full historical regression passed with zero gutter crossings, and the answer-page contact sheets showed no clipping, overlap, incorrect wrapping, or isolated font-size changes.
- Paper 17 student page 18 had thermometer captions overlapping the bulb area. Captions now sit below the complete tube/bulb/tick union with a mandatory 4pt separation check.
- Complete 50-paper diagram contact sheets exposed clipped single-row coin diagrams and a room-map target that could duplicate `office`; coins now wrap into readable rows and route labels must be unique.
- All 20 diagram kinds were rechecked for both standard and two-up output: 1,000 diagram regions per format, 1,450 explicit label-gap checks, and zero recorded vector boundary crossings.

## Evidence

- Standard renders: `y3/build/paper-01/rendered/` through `y3/build/paper-50/rendered/`.
- Two-up renders: `y3/build/2up-a4/p01/` through `y3/build/2up-a4/p50/`.
- Machine checks: `y3/work/batch-validation.json`, `y3/work/2up-validation.json`, and `y3/work/historical-regression.json`.
- Diagram contact sheets and geometry totals: `y3/work/visual-collision-audit.json` and `y3/build/visual-collision-audit/`.
