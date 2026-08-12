# ACARA Year 3 Released-Paper Coverage Blueprint (2012–2016)

Status: manually reviewed supplementary reference. This file records item structures and assessment demands only; it does not reproduce the released papers. It complements the scan-verified local blueprint in `year3-reference-blueprint.md` and does not invalidate or rerun the local OCR cache.

Official index reviewed: `https://www.acara.edu.au/assessment/naplan/naplan-2012-2016-test-papers`

## Purpose

The supplied 20-page scan controls the generated paper's section counts, student-page count, density and Year 3 difficulty. The ACARA 2012–2016 Year 3 releases broaden the batch-level item-family pool so that 50 papers do not repeat one sample's exact response pattern at every display position.

Every generated paper still contains exactly:

- 50 Conventions of Language questions;
- 39 Reading questions across seven texts;
- one Writing task;
- 36 Numeracy questions;
- 20 student-facing pages before the answer appendix.

## Conventions of Language Coverage

The 50-paper batch must cover all of these Year 3 response structures:

- choose the grammatically correct word, phrase, sentence or punctuation;
- identify a word in a sentence;
- complete a short cloze using a supplied word bank;
- supply a short written grammar or punctuation answer;
- identify the misspelt word in a sentence and connect it to the correct spelling;
- choose the correctly spelt word from plausible variants;
- correct one visibly underlined misspelling;
- write a dictated word without exposing the answer on the student page.

The language skill pool must include articles, verbs, tense, adverbs, pronouns, conjunctions, subject–verb agreement, sentence boundaries, capitals, commas, apostrophes, contractions, questions, quotation marks and possession.

## Reading Coverage

Across the batch, Reading must include at least these independently authored archetypes:

- information report, scientific explanation and paired information texts;
- public notice, rules/sign, personal message or letter;
- timetable/program, map/directions, labelled form or incident report;
- recipe/procedure, poem, review, narrative and opinion/exposition;
- table, tally, graph or other data-based stimulus.

The skill matrix must include literal retrieval, sequence, vocabulary in context, inference, cause and effect, character motive, main idea, purpose, audience, title or text-feature function, comparison, cross-referencing, spatial reasoning and data interpretation. Multiple choice, short written response, true/false, ordering, matching, cloze and select-two must all occur across the batch.

Question order may vary within a text, but every question must remain attached to the text and visual information needed to answer it.

## Writing Coverage

The batch must include both major Year 3 writing purposes:

- narrative prompts with a setting, characters, complication and ending;
- persuasive prompts requiring a clear position, organised reasons, supporting examples and a conclusion.

Prompts must remain comparable in reading burden and age appropriateness, and every prompt must be unique across the batch.

## Numeracy Coverage

The batch must cover Number and Algebra, Measurement and Geometry, and Statistics and Probability through a balanced mix of:

- missing-number equations, addition, subtraction, multiplication, grouping, remainder and money;
- increasing and decreasing patterns, digit constraints and place value;
- fractions and equal-area models;
- time, temperature, mass, distance and unit-rate reasoning;
- maps, direction, symmetry, top views and composite solids;
- tables, pictographs, bar graphs, number lines, spinners and probability;
- multiple choice, short constructed response and select-two formats.

Diagrams are part of the question, not decoration. Labels, keys, units, scales, shaded regions and answer options must agree with the keyed answer after rendering.

## Batch Coverage Rules

- Do not use a fixed set of seven Reading modules across all papers.
- Every one of the seven Reading positions must see at least 10 genuine passage archetypes across 50 papers.
- No passage archetype may appear in all 50 papers, and no topic label may be a permanent section.
- Names, numbers, objects, places, option order and question order do not create a new archetype.
- Rotating a template to another display position does not create a new archetype.
- Record genre, passage archetype, assessed skill and response kind separately in `y3/work/coverage-report.json`.
- Preserve the local Year 3 source spelling blueprint exactly in every paper: 15 dictation items, 5 underlined-word written corrections, then 5 find-and-write written corrections; do not substitute correct-choice or identification-only formats.
- Exercise narrative and persuasive Writing.
- Preserve all non-MCQ response branches: circle, cloze, true/false, ordering, matching, select-two and open response.
- Record observed response-kind counts, spelling-mode counts, writing-mode counts, unique template families and per-position template coverage in `y3/work/coverage-report.json`.
- Reject duplicate complete questions, duplicate passages, duplicate writing prompts, ambiguous answers, answer leakage and any generated item whose final answer cannot be independently recalculated.
