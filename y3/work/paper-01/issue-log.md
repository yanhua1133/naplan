# Practice Paper 01 Issue Log

| ID | Severity | Status | Description | Resolution |
|---|---|---|---|---|
| SRC-01 | Minor | Resolved | Source photos 11-20 were captured in landscape orientation. | Used rotated working copies only; all originals remain unchanged. |
| SRC-02 | Minor | Accepted | Source pages contain fingers, curvature and mild perspective distortion. | Used the scans as evidence without reproducing photographic defects. |
| CACHE-01 | Major | Resolved | Repeated OCR would be slow and could introduce inconsistent transcriptions. | Stored one-time OCR plus the verified canonical Markdown cache and locked reuse to matching source hashes. |
| GEN-01 | Critical | Resolved | The earlier draft expanded to 39 pages and did not preserve the reference counts. | Rebuilt the paper as exactly 20 A4 pages with 50 Language, 30 Reading, 1 Writing and 30 Numeracy items. |
| QA-01 | Major | Resolved | The earlier validator expected 90 questions and a 28/11 page split. | Replaced it with hard checks for 110 scored items, a 17/3 split, cache integrity, length bands and 20 unique rendered pages. |
| QA-02 | Minor | Resolved | A speech-punctuation distractor contained malformed quotation marks. | Replaced it with a controlled, readable incorrect option and regenerated the PDF. |
| QA-03 | Minor | Resolved | Punctuation-only option differences were incorrectly flagged as duplicate text by the validator. | Duplicate detection now preserves punctuation while extraction matching still uses normalized text. |
