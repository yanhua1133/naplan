# NAPLAN-Style Paper Quality Gates

Use this checklist for every paper. Record `pass`, `fail`, or `blocked` with evidence. A mandatory `fail` or `blocked` prevents final release.

## 1. Source Gate

- [ ] Every file in the scoped source directory appears exactly once in the inventory.
- [ ] Every image has been directly inspected at usable resolution.
- [ ] Orientation is confirmed for every image.
- [ ] Logical page order is confirmed using visible content, not filename order alone.
- [ ] Page-order evidence is recorded in the source manifest.
- [ ] Duplicates, gaps, front/back relationships, cropped edges, glare, blur, and unreadable areas are logged.
- [ ] No unresolved uncertainty has been silently guessed.
- [ ] Original source files are unchanged.

## 2. Transcription Gate

- [ ] Every heading, direction, sentence, word, number, unit, punctuation mark, symbol, option, and label is checked against the source.
- [ ] Paragraph order and question associations match the source.
- [ ] Capitalisation, spelling, apostrophes, quotation marks, hyphens, dashes, and mathematical symbols are intentional and consistent.
- [ ] OCR output, if used, has been manually corrected against the image.
- [ ] Source-faithful and adapted content are clearly distinguished in working records.
- [ ] Every source-derived element has page/question provenance.
- [ ] A second comparison pass has been completed after initial transcription.

## 3. Question Gate

- [ ] The student has all information needed to answer each question.
- [ ] Directions specify the required response clearly.
- [ ] Question numbering is unique, sequential, and consistent everywhere.
- [ ] Each single-answer item has exactly one defensible answer.
- [ ] Distractors are plausible but not arguably correct.
- [ ] No answer is revealed accidentally by nearby text, formatting, grammar, or another question.
- [ ] Difficulty, vocabulary, context, and expected knowledge suit the target year level.
- [ ] Names, quantities, dates, units, diagrams, and scenarios remain internally consistent.
- [ ] Questions do not depend unintentionally on colour, external knowledge, missing pages, or ambiguous visual detail.
- [ ] Newly authored or adapted items have been reviewed independently of their draft answer key.

## 4. Answer and Explanation Gate

- [ ] Every scored question has exactly one corresponding appendix entry.
- [ ] No appendix entry refers to a nonexistent or superseded question.
- [ ] Answers were solved independently from the final paper.
- [ ] Calculations and units are correct and reproducible.
- [ ] Passage-based answers cite the correct evidence or reasoning.
- [ ] Visual questions use the final diagram, labels, scale, legend, and orientation.
- [ ] Explanations address the final wording and final option order.
- [ ] Explanations contain no contradiction, typo, unsupported claim, or circular reasoning.
- [ ] Multiple valid methods or answers are acknowledged when the item permits them.

## 5. Cross-Reference Gate

- [ ] Contents, section headings, question ranges, page references, and appendix references agree.
- [ ] “See above/below/next page” references remain correct after pagination.
- [ ] Passage titles and question references use identical wording.
- [ ] Tables, figures, and diagrams are paired with the correct questions.
- [ ] Option labels in the appendix match the student paper exactly.
- [ ] Headers, footers, paper identifiers, and page numbers identify the correct paper.
- [ ] Each PDF is self-contained and does not rely on another paper's assets or answers.

## 6. Visual and Layout Gate

- [ ] Every final PDF page has been rendered and visually inspected; no sampling is allowed.
- [ ] Page size, orientation, margins, and printable area are consistent.
- [ ] No text, rule, image, or answer area is clipped or outside the printable region.
- [ ] No content overlaps, overflows, disappears, or becomes too small to read.
- [ ] No unintended blank page or duplicate page exists.
- [ ] Instructions, passages, questions, options, and answer spaces have a clear hierarchy.
- [ ] Page breaks do not separate a question from essential options, data, or diagrams without a clear continuation treatment.
- [ ] Widows, orphans, stranded headings, and awkwardly split options have been resolved where they affect readability.
- [ ] Spacing, indentation, alignment, bullets, option markers, line weights, and borders are consistent.
- [ ] Images are sharp enough for print and are not stretched, skewed, or unintentionally cropped.
- [ ] Every diagram label, axis, scale, legend, unit, arrow, shape, and data value is readable and correct.
- [ ] Greyscale printing preserves distinctions needed to answer the questions.
- [ ] Student response areas are appropriately sized and do not contain answer content.
- [ ] The answer appendix begins only after the complete student paper.

## 7. PDF Technical Gate

- [ ] The PDF opens without repair warnings.
- [ ] Page count matches the expected count.
- [ ] All required fonts and images render on a clean viewer.
- [ ] Extracted text contains no Unicode replacement characters or obvious encoding corruption.
- [ ] Automated checks find no numbering gaps, duplicated question IDs, or missing answer IDs.
- [ ] File name, metadata where used, and visible paper title identify the same year level and paper number.
- [ ] Temporary files, debug marks, crop marks, comments, and hidden answer layers are absent from the student pages.

## 8. Final Read-Through Gate

- [ ] A fresh pass starts at page 1 of the final PDF, not the source document.
- [ ] Every page, question, sentence, word, punctuation mark, number, and visual is reviewed.
- [ ] Every question is re-solved using only the final student-facing PDF.
- [ ] Every answer and explanation is checked against that fresh solution.
- [ ] All earlier corrections appear in the final rendered PDF.
- [ ] No critical or major issue remains open.
- [ ] Intentional deviations from the scan layout are documented and do not change meaning or difficulty.

## Severity and Release Decision

- **Critical:** wrong or ambiguous answer, missing question/page, unreadable required content, materially incorrect transcription, mismatched appendix, or corrupted PDF. Release is prohibited.
- **Major:** misleading wording, significant layout defect, incorrect reference, unsuitable difficulty, or visual defect that could affect a response. Release is prohibited.
- **Minor:** cosmetic inconsistency that cannot change interpretation or response. Fix before release whenever practical; document any accepted exception.

Release as final only when all mandatory checks pass, no critical or major issue remains, and every accepted minor exception is documented.
