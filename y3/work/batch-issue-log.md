# Batch Convergence Issue Log

All issues below were found during generation or validation, fixed, and followed by a complete batch regeneration and validation pass.

| Issue | Risk | Resolution | Prevention added to skill |
| --- | --- | --- | --- |
| Unsupported drawing helper used by one visual branch | A later paper could fail although Paper 01 rendered | Replaced it with supported primitive lines and exercised all branches | Validate the complete batch and require visual branch coverage |
| Spinner values produced a tied probability outcome | More than one defensible answer | Changed generated sector data and added uniqueness checks | Reject tied single-answer outcomes |
| Several generated items contained duplicate options | Ambiguous or invalid multiple choice | Rebuilt distractors and asserted option uniqueness | Reject duplicate options across every paper |
| Some normalized prompts repeated across papers | Papers differed only superficially | Added deterministic context variation and cross-paper prompt checks | Enforce normalized batch uniqueness |
| Early reading passages were shorter than the reference bands | Material difficulty and response burden drifted | Expanded each passage family to reference-like lengths | Enforce length bands per passage and paper |
| Spelling replacement was case-sensitive | The intended misspelling was not always underlined | Used case-insensitive one-time replacement and exact-error assertions | Require exactly one verified underlined error |
| Dynamic `<` comparison text was interpreted as markup | Options or answers could disappear from PDFs | HTML-escaped plain dynamic values before typesetting | Escape dynamic text and separate markup from content |
| Validator removed text between `<` and `>` as if it were an HTML tag | A real PDF defect could be hidden by validation | Narrowed markup normalization to known tags only | Use separate safe normalization for markup and PDF text |
| Some writing illustration variants lacked renderer branches | Generic or missing prompt art in later papers | Added every generated illustration variant and inspected all 20 writing pages | Require complete illustration branch coverage |
| The 20-page requirement incorrectly included the appendix | Student papers were only 17 pages | Rebuilt every paper as 20 student pages plus a separately counted 3-page appendix | State explicitly that appendix pages begin after student page 20 and never count toward it |
| Templates requested fonts as small as 4.0–6.7pt | Some options and diagram labels looked inexplicably tiny even though layout scale was 1.0 | Raised section-wide minimum sizes and expanded the appendix from 3 to 6 pages | Audit requested font size as well as scale; enforce minimum body, diagram, and appendix sizes |
| Literal prompts were unique but 73.6% belonged to repeated parameter-swapped templates | Papers reused the same tested sentence or mathematics structure with only names, places or numbers changed | Rebuilt language core sentences and options, added distinct project contexts and 20 phrasing structures, then enforced 2,200 structurally unique prompts and a maximum mean same-position similarity below 0.90 | Treat parameter swaps and wrapper-only changes as duplicates; require structural normalization and near-duplicate checks |
