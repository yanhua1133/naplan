# A4 Two-Up Audit

- Output: `y3/output/2up/p01.pdf` through `p20.pdf`.
- Format: A4 landscape, two logical pages per sheet, 13 sheets per PDF.
- No A3 output exists.
- Existing question data reused; no OCR and no new question generation.
- General prompts enlarged 30%, options enlarged 28%, passages and answer explanations enlarged 25% before A4 imposition.
- The spelling page matches the verified source structure: questions 26–40 are 15 blank dictation lines, questions 41–45 contain one visibly underlined misspelling each, and questions 46–50 contain one unmarked misspelling each.
- Dense spelling prompts use a dedicated 12% enlargement and compact line height. The generator rejects spelling layouts when text scales below 99% of its requested size.
- All 20 final PDFs were opened directly and their sheet-2 right halves were rendered from the released files, not from a cached build directory.
- Visual inspection confirmed all 15/5/5 groups, all five required underlines, answer boxes, line spacing and page boundaries; no clipping, overlap, neighbouring-item collision, leaked dictation answer, missing content or blank region was found.
- Machine-readable result: `y3/work/2up-validation.json` with status `passed`.
