# V.A Q2 — Regex filtering

The activity follows exercise 2 in `prep/classnotes/week14/V.A_Regex_I.ipynb`
and the activity-plan row “Regex and Conditions / V.A / #2”: guided flowchart
fill-in explaining the logic. Students distinguish a search result from the
complete original string that is added to a result list. No complete notebook
function is displayed. Input order and repeated entries are preserved.

The outer page reuses the current Part IV course shell, shared course CSS,
feedback and downloadable reflection notes. Five H5P Interactive Book pages
contain **11** local scored checks. The trace lab is a bounded simulation of
five Python-verified examples, not a general JavaScript implementation of `re`.
The zero-length-match case is an optional extension.

## Canonical source

`V_A_Q2_Regex_Basics.h5p` was imported, inspected and saved in **Lumi 1.0.3**.
Keep it canonical. After editing and saving in Lumi, run from the repo root:

```
python3 utils/build_regex.py
node --test tests/regex.test.mjs
```

The synchronizer updates `regex_check.html` and readable `regex_content.json`
without overwriting the editable package. The standalone runtime comes from the
existing Part IV Lumi export and retains the course accessibility repairs.
Lumi may strip presentation classes; flow-list styling is applied by the host
runtime, not required for the meaning of the numbered text flow.

## Verification

Core tests cover basic filtering, duplicates, no matches, empty input, and
zero-length success distinguished from failure. All five cases were also
exercised in Chrome. ZIP integrity and identical H5P/HTML question content were
checked after synchronization. Answer order is randomized; each question has
one correct answer and explanatory feedback for each distractor.

Manual browser/Pro verification results are recorded with the delivery report.
Automated checks do not prove all WCAG criteria. Retain labels, landmarks,
visible focus, live status messages and keyboard operability when editing.

## Requirements audit (November 3)

Reviewed all 60 visible Freedcamp tasks, including the expanded accessibility
comments, and the 13 local meeting-record files (the revised August 26 record
supersedes its earlier copy). The original plan row identifies V.A Q2 as
“Regex and Conditions”, with guided flow fill-in and the distinction between
a condition and the value added to a list. The book retains this focus.

The October 28 review asks for selective red emphasis. The introductory and
reflection accents remain; ordinary work panels use neutral borders. The
introductory subheadings use the shared UGA accent and the Part IV title spacing.
Page-specific rules live in `regex.css` rather than an inline style block.

A fresh all-in-one HTML export was made in Lumi 1.0.3 and passed through the
current `utils/h5p_brand.py` during this audit. Its question JSON exactly matches
the canonical package and production runtime. Production keeps its already
verified course runtime and accessibility patches rather than replacing those
patches with an unverified raw export.

The numbered flow is intentionally readable as text; its two branches both
return to the next candidate. Python Tutor is not used: the bounded trace
exposes decisions without publishing the complete notebook solution or linking
to the Python Tutor main site with AI tools.

Publication and automated checks are implementation evidence, not Ryan's
acceptance or a comprehensive WCAG certification. Team review remains separate.

Structure guided testing identified the bottom pagination title as a misused H1.
The synchronizer now renders that repeated footer status as a paragraph while
retaining the top page heading and all navigation controls. This targeted
Interactive Book runtime repair is preserved on future content synchronization.
