# LING2200 Part III Q7 guided activities

## Live entry point

https://uga-ling2200.github.io/applets/part_III/

- III.A Q7: `count_names()` — two tuple fields, word units rather than characters, independent singular/plural choices, and a printed message.
- III.B Q7: `extract_tens_digit()` — indexing an indexable representation, missing-position guard returning integer 0, type conversion, and a returned integer. Signed inputs are a magnitude-based extension; floats are optional and explicitly ignore the fractional part rather than round.

## Source and teaching design

Exercise requirements checked against the teacher's `uga-ling2200/prep` notebooks, `classnotes/week07/III.A_Tuples.ipynb` and `III.B_Indexing.ipynb`. The user explicitly chose Q7 for both; the earlier activity-plan reference to III.B Q1 is not implemented. Folder placement in the source notebook does not establish a scheduled teaching week.

Meeting guidance is implemented as partner prediction, paper diagrams/tables, local checks, explanatory feedback, retry, and a final independent notebook task. No complete solution function is displayed. Each activity has five chapters. III.A contains nine scored questions; III.B contains ten.

## Unified 2200 format

HTML uses the repository's `utils/h5p_brand.py` and `docs/style.css` as fetched at `a020597` (September 23, 2026). H5P InteractiveBook, Column, AdvancedText and MultiChoice follow the existing II.Dg Q2 architecture. UGA headers, Merriweather typography, red action buttons, feedback card and accurate source URL are preserved. Added accessibility refinements include banner/main landmarks, UTF-8 metadata, focus outlines, heading/list semantics, and normal answer-label weight. `.h5p` files are editable authoring packages; HTML files are the deployed standalone activities.

## Accessibility and functional verification — September 26, 2026

Used the user's Chrome **axe DevTools Pro**, axe-core 4.13.0, with **advanced rules enabled** and Best Practices ON. Automatic core and advanced scans reached **Total Issues: 0**, with no ignored issues, for the two activities and Part III entry page. Every activity chapter was scanned before and after checking answers; wrong-answer and retry states were also exercised. Initial findings (header landmark and advanced heading markup findings) were repaired and rescanned.

Checked all 19 scored questions, correct/incorrect feedback, retry, chapter navigation, and disabled solution buttons. Keyboard Space selects a radio option and Enter submits Check. Both activities were checked at a 390px viewport with document width equal to scroll width (no horizontal document overflow).

The 0 result describes the scanned states and tool configuration; it is not a claim that automated scanning alone proves every WCAG criterion. Local screenshots and the scan-state history are retained in the delivery outputs. Advanced AI checks are nondeterministic; future content edits should be rescanned.

## Wording and challenge review

### September 30 scaffolding update

All four published Part III activities now connect each of their five pages to
the preceding reasoning step and briefly explain why that step matters. The
III.B Q7 check for input `100` explicitly asks for the integer tens digit;
the III.E Q1 slice check explicitly asks for the type of the returned slice,
not the contained item. Question answers and scoring are unchanged.

The editable H5P packages and standalone HTML pages carry the same text.
After changing III.A or III.B source content, run
`python3 -B utils/part_iii_scaffolding.py`; after changing III.E or III.F,
run `python3 -B utils/part_iii_ef/build.py`. The latter builder imports the
shared page notes from `utils/part_iii_scaffolding.py`.

Rechecked the original III.A Q7 and III.B Q7 notebook prompts against the meeting guidance. Simplified surrounding prose while retaining Python terms and the print/return distinction. Students still predict, compare inputs, draw index diagrams, justify a rule and write their own function.

Removed an opening example that gave away a later tens-digit answer. Randomized answer order and revised distractors to reflect plausible mistakes. Comparison prompts now ask students to discover what changes rather than stating the observation first. Loaded the Merriweather and Merriweather Sans fonts already specified by the shared 2200 template.

All ten chapters were reviewed with axe DevTools Pro (core and advanced rules), before and after answering; final scans showed 0 issues with no ignored issues. AI heading suggestions on normal paragraphs/links were checked against their actual semantics; no incorrect heading roles were added. The AI results are nondeterministic. The latest complete full-page scans were taken from the chapter top.
