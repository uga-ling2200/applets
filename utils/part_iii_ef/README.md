# III.E Q1 and III.F Q4

## Source and scope

Reviewed on September 27–28, 2026:

- [III.E Q1](https://github.com/uga-ling2200/prep/blob/master/classnotes/week08/III.E_Slicing.ipynb): implement `reverse(group)` for strings, tuples and lists, returning the same sequence type in reverse order.
- [III.F Q4](https://github.com/uga-ling2200/prep/blob/master/classnotes/week08/III.F_Strings_III.ipynb): implement `remove_parentheticals(string)`, remove parentheses and their contents, retain a single space at surviving joins, and extend to multiple parentheticals. The question assumes at least one parenthetical.
- Course source revision: `16ef77e`; applet infrastructure baseline: `3f1c34e`.
- The activity plan emphasizes tracing negative slice boundaries by hand and explaining why repeated-character/string-edit attempts produce unexpected results.
- September meeting guidance: guided partner discovery, a testable draft, shared infrastructure and interaction patterns. Learners still implement their own functions in the notebook.

The slicing notebook's internal heading says III.D although its filename is III.E. Two nearby prose descriptions reverse the slice direction/empty-slice condition. These activities use the task/file identifier III.E and Python's executable semantics, without changing Q1's function contract. Nested and unmatched parentheses are not specified by F Q4; its practice lab explicitly uses separate matched pairs.

## Shared course infrastructure

The latest reviewed [2150 conventions](https://github.com/uga-ling2150/applets/blob/main/conventions.md), its official template and shared stylesheet were used as references (2150 revision `3c093a8`). The 2200 repository does not contain its own `conventions.md` at the reviewed revision. These are 2200 activities: they retain the existing III.A/III.B H5P InteractiveBook, Column and MultiChoice structure, teacher `utils/h5p_brand.py`, `docs/style.css`, branding, navigation and feedback card.

`sequence-lab.css` and `sequence-lab.js` are shared by E and F and contain only the new practice component and focused accessibility/responsive corrections. The full function solutions are not displayed. Copy uses short instructions and accurate terms; explanations follow submitted choices, and two advance hints that disclosed results were removed during review.

## Build and maintenance

Run from the repository root:

```sh
python3 utils/part_iii_ef/build.py
python3 utils/part_iii_ef/test_slices.py
```

The builder uses the existing III.A HTML/H5P as the installed runtime and applies the teacher formatter. Content IDs are stable. It emits the HTML pages, editable H5P packages, and readable content JSON. The HTML pages include the shared practice lab; the H5P packages contain the five guided book chapters. Keep the shared lab files with the published HTML.

The builder also corrects the bundled InteractiveBook 1.11 `l10n.exitFullScreen` typo to `l10n.exitFullscreen`, so the exit button has a meaningful accessible name. This correction is applied to both standalone HTML and H5P library code.

## Verification

- 22 MultiChoice checks: correct answers, feedback and scores verified in Chrome; incorrect-answer/retry paths checked in both activities.
- Practice models: string, tuple, list, empty list and one-item tuple; omitted/negative boundaries; zero-step rejection; reset. JavaScript slicing matches 2,560 cases evaluated by CPython.
- F practice: raw versus cleaned join, repeated edits and updated positions, beginning/end parentheticals, empty result, disabled/apply/reset transitions.
- Keyboard activation, previous/next pages, menu and section navigation, fullscreen enter/exit; 390px layout checked without page overflow. The mobile chapter label no longer overlaps the page counter.
- Paid axe DevTools Pro, axe-core 4.13.0, WCAG 2.1 AA, Best Practices and advanced rules enabled: all ten chapters scanned before/after answers, plus lab/error/mobile/fullscreen states. Real focus issues were fixed and rescanned. Final tested states returned Total Issues: 0, without ignored issues or disabled rules.
- Advanced AI occasionally classified ordinary answer/list text as headings; semantic markup and font weight were inspected. Focus scans were repeated from a neutral page focus to avoid comparing an already-focused control with itself. These findings and subsequent results are retained in the local audit history. Automatic scans are supplemented by the interaction/keyboard checks above; they are not a WCAG certification.
