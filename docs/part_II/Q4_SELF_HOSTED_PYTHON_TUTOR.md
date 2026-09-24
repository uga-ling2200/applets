# Q4 self-hosted Python Tutor

Q4 embeds a locally maintained MIT-licensed historical Python Tutor renderer and upstream trace generator. Python runs locally with Pyodide 0.27.7; the app does not send students to the Python Tutor website. See python-tutor-assets/README.md for pinned provenance, licenses, and local modifications.

Deploy II.E_Strings_Q4.html, python-tutor-q4.html and the entire python-tutor-assets directory together. The H5P package references the production wrapper URL. Initial runtime downloads are approximately 14 MB.

Local H5P patches: IFrameEmbed 1.0.30 adds iframe titles and scrolling; InteractiveBook 1.11.4 strengthens visible focus. These are local patches, not official upstream releases. Destination LMS administrators must permit library updates; test the imported package in the destination LMS.

Validation: 87 runtime cases, each of 12 questions and all three answer options in both HTML and H5P, Chrome axe DevTools Pro 4.137.0 / axe-core 4.13.0 (WCAG 2.1 AA, best practices), keyboard controls, visible focus, invalid input, runtime-load recovery, and 320 CSS-pixel layout. Core rules reported no issues in the retained final Pro scans. Raw advanced heuristic flags were retained and manually reviewed: existing form labels, status text, a question prompt and a legend are not missing headings; visible keyboard outlines were independently verified where a pre-focused control was flagged.

This describes tested scope, not universal WCAG certification. Independent screen-reader user testing, every guided test, and the actual course LMS import were not performed. Recheck after changes to content, libraries or hosting.
