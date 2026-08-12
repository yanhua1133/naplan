# Historical Regression Closure

Status: **passed**. All previously reported critical and major defect classes are covered by current repeatable checks.

## Verified

- 50 standard PDFs: exactly 20 student pages plus 6 appendix pages, with 125 scored questions and matching explanations per paper.
- 50 concise `pNN.pdf` A4-landscape files: 13 sheets each, 1300 logical halves text-matched to the standard PDFs, zero gutter-crossing text spans.
- No A3 output, obsolete two-up directory, hidden text scaling, undersized required text, missing render, blank student page, duplicate PDF, or duplicate rendered page/sheet.
- No known malformed prompt fragments, leaked dictation words, missing required underline, stray underline in locate-error items, duplicated complete question, passage or writing prompt.
- All 1,300 standard rendered pages and all 650 two-up rendered sheets were visually reviewed by logical position; the separate enlarged spelling-page review covered every sheet-2 right half.
- All 20 diagram kinds were inspected in complete 50-paper standard and two-up contact sheets; 1,000 regions per format passed with zero vector boundary crossings.
- Structural diversity: minimum 4 Language variants and 5 Numeracy variants per template; every paper preserves the source-locked 15 dictation / 5 underlined correction / 5 locate-and-correct spelling blueprint.
- Source cache: 20 immutable scans hash-verified; OCR was not rerun.

## Evidence

- `y3/work/historical-regression.json`
- `y3/work/batch-validation.json`
- `y3/work/coverage-report.json`
- `y3/work/2up-validation.json`
- `y3/work/2up-audit.md`
- `y3/work/rendered-page-inspection.md`
