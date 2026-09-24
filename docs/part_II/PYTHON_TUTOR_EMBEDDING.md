# Q4 Python Tutor embedding

Q4 uses H5P IFrame Embed → `python-tutor-q4.html` → the official Python Tutor
`iframe-embed.html`. The standalone HTML bundles the existing IFrame Embed
constructor. The H5P archive now includes a local IFrameEmbed 1.0.30 patch
adding a metadata-derived iframe title and enabling scrolling. This is not an
official upstream release. Import requires H5P library update permission.

Deploy the wrapper alongside `II.E_Strings_Q4.html` and `II.E_Strings_Q4.h5p`.
Both artifacts refer to the wrapper's absolute GitHub Pages URL, so the H5P
package can be imported into other hosts. The wrapper takes `focus=parts`,
`focus=condition`, or `focus=string`, and a `number` from 0 through 999999.
The standalone explorer also uses `controls=external` to keep a single set of
input controls. Changing input clears the old trace; loading restarts it.

Do not put the percent-encoded Python Tutor code URL directly into the stock
H5P embedder: it calls `encodeURI` again. The intermediary constructs that URL
itself and avoids double encoding.

## Navigation limitation

The live official embed currently displays an **Edit Code & Get AI Help**
link and a Python Tutor attribution link. The inner iframe deliberately uses
`sandbox="allow-scripts allow-same-origin"`, without popup or top-navigation
permissions. Ordinary clicks on both existing `target="_blank"` links were
blocked in Chrome while Next/Prev continued to work. Attribution remains.

This does not remove the AI link's text, prevent manual URL copying, or prevent
students from independently visiting the website. Cross-origin CSS cannot hide
the internal link. A requirement to remove every AI mention would need an
upstream no-AI embed option or a separately evaluated self-hosted visualizer.
Do not add popup or top-navigation sandbox permissions.

## Validation

Chrome checks: chapter traces for parts (111 → 1 and 11), condition (121 → False,
then 111 → True after reloading), and string construction (23 → "23rd"); Next,
Prev, blocked external links, explorer prediction feedback, input changes,
invalid -1, reset, and a 390px viewport. All 12 multiple-choice questions and
feedback are unchanged; ZIP integrity passed. Course LMS import remains to be
checked. The Codex in-app browser showed an empty third-party frame; Chrome was
used for functional verification.

The visualization requires an internet connection and Python Tutor availability.
Code and a course-notebook/paper fallback remain available in the activity.

## Accessibility audit

Chrome axe DevTools Pro (axe-core 4.13.0, WCAG 2.1 AA, advanced rules enabled)
was run on all four pages and representative answer-feedback states in the
standalone HTML and a separate preview of the actual H5P package. The H5P
frame-title issue is fixed in the local library patch. Upstream Python Tutor
still has low-contrast line numbers/start text and a keyboard-inaccessible code
scroll region in some states. These cross-origin issues remain unresolved;
this is not a claim of complete accessibility compliance. LMS import and a
complete assistive-technology audit remain unverified.
