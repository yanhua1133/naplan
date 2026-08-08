# A4 Two-Up Audit

- Output: `y3/output/2up/p01.pdf` through `p20.pdf`.
- Format: A4 landscape, two logical pages per sheet, 13 sheets per PDF.
- No A3 output exists.
- Existing question data reused; no OCR and no new question generation.
- General prompts enlarged 30%, options enlarged 28%, passages and answer explanations enlarged 25% before A4 imposition.
- Dense spelling prompts use a dedicated 12% enlargement and compact line height so every prompt remains above its answer box.
- The generator rejects spelling layouts when prompt and answer rectangles have less than a 2pt source-page gap or when spelling text scales below 99% of its requested size.
- All 20 sheet-2 right halves were inspected at full rendered height after the fix; no clipping, prompt/answer overlap, neighbouring-item collision, missing content, or blank region was found.
- Unchanged sheets were compared against the previous committed PDFs at pixel level; all 240 unchanged full sheets and all 20 unchanged sheet-2 left halves matched exactly.
