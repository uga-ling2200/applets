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
