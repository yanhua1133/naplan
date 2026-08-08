---
cache_status: verified
cache_version: 2
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
- Reading: **39 questions** across seven texts.
- Writing: **one narrative task**.
- Numeracy: **36 questions**.
- Overall level: Year 3 advanced practice; multi-step reasoning, inference, punctuation control and visual interpretation must remain represented.
- Visual style: pale aqua section bars, compact rounded panels, approximately two-column workbook density, small but normal print text, and concise answer explanations.
- Item-length rule: map new items to the reference item positions and review stem/option word-count differences above approximately 20%.

## Verified Page Map

| Reference page | Source file | Section | Item range / role | Verified layout and difficulty notes |
|---:|---|---|---|---|
| 21 | `IMG_9320.jpg` | Conventions of Language | 1-9 | Advanced grammar and word choice; nine compact multiple-choice items. |
| 22 | `IMG_9321.jpg` | Conventions of Language | 10-18 | Pronouns, agreement, tense and punctuation; nine compact items. |
| 23 | `IMG_9322.jpg` | Conventions of Language | 19-25 | Commas, apostrophes, question marks, speech and sentence correctness; seven items. |
| 24 | `IMG_9323.jpg` | Conventions of Language | 26-50 | Mixed spelling page: 15 dictated words, five underlined-error sentences and five unmarked-error sentences. |
| 25 | `IMG_9324.jpg` | Reading | 1-6 | Science information text; literal, inference, true/false and force-diagram interpretation. |
| 26 | `IMG_9325.jpg` | Reading | 7-12 | Related procedure/experiment; sequence, trial count, purpose, substitution and cross-text application. |
| 27 | `IMG_9326.jpg` | Reading | 13-18 | Health information; vocabulary, matching, cloze, inference and summary. |
| 28 | `IMG_9327.jpg` | Reading | 19-24 | Survey description, tally table and bar graph; matching, axes, purpose and cross-text classification. |
| 29 | `IMG_9328.jpg` | Reading | 25-29 | Traditional rhyme; reference, cloze, vocabulary, text type and purpose. |
| 30 | `IMG_9329.jpg` | Reading | 30-34 | Book review; bibliographic retrieval, purpose, two-answer selection, criticism and star rating. |
| 31 | `IMG_9330.jpg` | Reading | 35-39 | Narrative; adjective matching, event order, character inference, cause and title meaning. |
| 32 | `IMG_9331.jpg` | Writing | narrative task | Illustration-led imaginative prompt, planning guidance and writing lines. |
| 33 | `IMG_9332.jpg` | Numeracy | 1-5 | Missing number, subset total, sequence, multiplication equivalence and visual covering. |
| 34 | `IMG_9333.jpg` | Numeracy | 6-9 | Visual pattern, pictograph key, top view and constrained odd number. |
| 35 | `IMG_9334.jpg` | Numeracy | 10-15 | One-third diagram, missing addend, elapsed time, addition, difference and money table. |
| 36 | `IMG_9335.jpg` | Numeracy | 16-19 | Analogue time, spatial map, reflection symmetry and unit rate. |
| 37 | `IMG_9336.jpg` | Numeracy | 20-23 | Equal areas, cube mass, two-answer pattern and digit constraint. |
| 38 | `IMG_9337.jpg` | Numeracy | 24-27 | Composite solid, proportional cost, bus capacity and thermometer decrease. |
| 39 | `IMG_9338.jpg` | Numeracy | 28-33 | Halfway distance, number line, dozens/remainder, scales, backward pattern and table total. |
| 40 | `IMG_9339.jpg` | Numeracy | 34-36 | Bar graph, spinner probability and grouped coin total. |

## Reference Language Profile

### Questions 1-25

- Predominantly four-option multiple choice.
- Usually one short sentence or a two-sentence context.
- Skills include noun/verb/adverb identification, tense, pronouns, agreement, conjunctions, categories, commas, apostrophes, question marks, speech punctuation and correct sentence selection.
- Distractors are grammatically plausible and often differ by one controlled feature.

### Questions 26-50

- Questions 26–40 are dictated-word items. The student page shows only numbered writing lines; a teacher or parent reads each target word aloud.
- Questions 41–45 are short sentences containing exactly one deliberately misspelt and visibly underlined word. The student writes the complete corrected spelling in a compact box.
- Questions 46–50 are short sentences containing exactly one deliberately misspelt word without an underline. The student must identify the incorrect word and write its complete corrected spelling in a compact box.
- The page therefore has an exact `15 dictation / 5 underlined correction / 5 identify-and-correct` distribution.
- Includes common and less regular spelling patterns, prefixes, doubled consonants and unstressed vowels.

## Reference Reading Profile

- Seven texts with question ranges `1–6`, `7–12`, `13–18`, `19–24`, `25–29`, `30–34` and `35–39`.
- Texts include science information, a related procedure/experiment, health information, survey/table/graph material, rhyme/poetry, a book review and a narrative.
- Each page combines the text and its questions at compact workbook density.
- Questions mix literal retrieval, vocabulary in context, reference words, purpose, sequence, inference, summary and visual-data interpretation.
- New passages should remain close in length to their mapped reference text and retain each mapped response form, including true/false, ordering, matching, cloze, visual options, cross-text questions and select-two items.

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
