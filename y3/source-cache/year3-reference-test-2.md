---
cache_status: verified
cache_version: 1
source_directory: y3/orig
source_hashes: y3/source-cache/source-hashes.json
raw_ocr_cache: y3/work/ocr
ocr_runs_allowed_when_hashes_match: 0
reference_page_count: 20
target_year: 3
---

# Year 3 Reference Test 2 — Canonical Source Cache

This file is the human-verifiable, machine-readable source of truth for future paper generation. It was created from the one-time OCR pass already stored under `y3/work/ocr/` and corrected against the supplied scans. Future generation must validate `source-hashes.json`, read this cache, and must not rerun batch OCR while the hashes match.

## Locked Paper Constraints

- Total pages: **20 exactly**.
- Conventions of Language: **50 questions**.
- Reading: **30 questions** across five texts, six questions per text.
- Writing: **one narrative task**.
- Numeracy: **30 questions**.
- Overall level: Year 3 advanced practice; multi-step reasoning, inference, punctuation control and visual interpretation must remain represented.
- Visual style: pale aqua section bars, compact rounded panels, approximately two-column workbook density, small but normal print text, and concise answer explanations.
- Item-length rule: map new items to the reference item positions and review stem/option word-count differences above approximately 20%.

## Verified Page Map

| Reference page | Source file | Section | Item range / role | Verified layout and difficulty notes |
|---:|---|---|---|---|
| 21 | `IMG_9320.jpg` | Conventions of Language | 1-9 | Advanced grammar and word choice; nine compact multiple-choice items. |
| 22 | `IMG_9321.jpg` | Conventions of Language | 10-18 | Pronouns, agreement, tense and punctuation; nine compact items. |
| 23 | `IMG_9322.jpg` | Conventions of Language | 19-25 | Commas, apostrophes, question marks, speech and sentence correctness; seven items. |
| 24 | `IMG_9323.jpg` | Conventions of Language | 26-50 | Twenty-five spelling-response items with short answer boxes. |
| 25 | `IMG_9324.jpg` | Reading | 1-6 | Information text about forces and friction; vocabulary, literal and inferred meaning. |
| 26 | `IMG_9325.jpg` | Reading | 7-12 | Procedure/experiment text; purpose, sequence, materials and inference. |
| 27 | `IMG_9326.jpg` | Reading | 13-18 | Health information text; vocabulary, summary and inference. |
| 28 | `IMG_9327.jpg` | Reading | 19-24 | Sports table and graph; cross-reference and interpretation. |
| 29 | `IMG_9328.jpg` | Reading | 25-30 | Nursery rhyme; explicit detail, sequence, text type and purpose. |
| 30 | `IMG_9329.jpg` | Reading answers | 1-15 approximately | Dense two-column concise explanations. |
| 31 | `IMG_9330.jpg` | Reading answers | remaining answers | Dense two-column concise explanations. |
| 32 | `IMG_9331.jpg` | Writing | narrative task | Illustration-led imaginative prompt, planning guidance and writing lines. |
| 33 | `IMG_9332.jpg` | Numeracy | 1-4 | Number sequence, place value and grouped-object reasoning. |
| 34 | `IMG_9333.jpg` | Numeracy | 5-8 | Probability, top view, multiplication and data interpretation. |
| 35 | `IMG_9334.jpg` | Numeracy | 9-12 | Shape properties, elapsed time, page totals and money table. |
| 36 | `IMG_9335.jpg` | Numeracy | 13-16 | Time, fractions, transformations and money value. |
| 37 | `IMG_9336.jpg` | Numeracy | 17-21 | 3D construction, mass, number properties and difference. |
| 38 | `IMG_9337.jpg` | Numeracy | 22-25 | Volume/capacity, transport division, temperature change and cost. |
| 39 | `IMG_9338.jpg` | Numeracy | 26-29 | Number line, pattern, similarity and equal grouping. |
| 40 | `IMG_9339.jpg` | Numeracy | 30 and data items | Bar graph, probability spinner and money combinations. |

## Reference Language Profile

### Questions 1-25

- Predominantly four-option multiple choice.
- Usually one short sentence or a two-sentence context.
- Skills include noun/verb/adverb identification, tense, pronouns, agreement, conjunctions, categories, commas, apostrophes, question marks, speech punctuation and correct sentence selection.
- Distractors are grammatically plausible and often differ by one controlled feature.

### Questions 26-50

- One deliberately misspelt word per item.
- Student supplies the complete corrected spelling.
- Short sentence contexts; answer boxes are compact.
- Includes common and less regular spelling patterns, prefixes, doubled consonants and unstressed vowels.

## Reference Reading Profile

- Five texts with six questions each.
- Texts include information, procedure/experiment, health information, table/graph material and rhyme/poetry.
- Each page combines the text and its questions at compact workbook density.
- Questions mix literal retrieval, vocabulary in context, reference words, purpose, sequence, inference, summary and visual-data interpretation.
- New passages should remain close in length to their mapped reference text and retain a similar balance of explicit and inferred answers.

## Reference Writing Profile

- One imaginative narrative prompt supported by a simple illustration.
- Guidance asks for characters, setting, events, complication and ending.
- The page reserves substantial space for planning or writing rather than explanatory prose.

## Reference Numeracy Profile

- Thirty questions covering number, operations, patterns, fractions, money, time, measurement, geometry, spatial reasoning, data and chance.
- Visual items are frequent and essential rather than decorative.
- Difficulty includes more than routine recall: several items require interpreting a diagram, combining two facts, converting units, finding a difference or applying a pattern.
- New questions must preserve this mix and avoid making most items single-step facts.

## Cached Representative Transcriptions

These verified examples anchor wording length and difficulty. They are reference excerpts, not templates to copy into new papers.

- Language: “Which sentence is correctly punctuated?” followed by four comma placements in the same sentence.
- Language: “Circle the letter to show where the missing apostrophe should go.”
- Reading: “Friction is a force that opposes motion: it slows or stops a moving object.”
- Reading procedure: aim, basic materials, different textured materials, method and interpretation questions.
- Writing: narrative prompt about a toy coming to life, with reminders to plan characters, setting, complication and ending.
- Numeracy: number sequences, grouped counters, top-view solids, school arrival time, fraction of an hour, cube construction, bus capacity, temperature difference, bar graphs and probability spinners.

## Cache Use Protocol

1. Hash all files in `y3/orig/` without OCR.
2. Compare the result with `source-hashes.json`.
3. If hashes match, use this Markdown cache and the structured page map. Do not run OCR.
4. Open individual scans only for targeted visual verification when the cache lacks a required diagram detail.
5. If hashes differ, mark the cache invalid, document the changed file, then perform a new one-time OCR and manual verification cycle.

