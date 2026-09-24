# Locally hosted Python Tutor for Q4

This is Python Tutor's historical visualizer, not a replacement renderer. Philip J. Guo's MIT license is retained in LICENSE.txt. Source snapshot: https://github.com/sineagles/OnlinePythonTutor/tree/526266872a2dc8af671eacd9cb853e08b5bb9fa9 (v5-unity). Bundle contains its original third-party notices.

Pyodide 0.27.7 (CPython 3.12.7) executes the three fixed Q4 snippets in a dedicated Web Worker. The worker accepts only the focus enum and an integer 0–999999; it constructs the code internally. No server executes student-supplied Python. No API keys, accounts, Python Tutor service, AI service or external CDN are needed at runtime. Host this entire directory beside python-tutor-q4.html. First use downloads approximately 14 MB before browser caching.

Local changes:
- pg_logger.py: replace removed imp.new_module with types.ModuleType for Python 3.12 compatibility.
- pytutor-embed.bundle.js: remove replaced/detached visualizers from the resize registry on reload.
- q4-trace.js/css: replace old step controls with labeled native buttons; persistent keyboard focus at endpoints; live step/variable summary; scrollable code keyboard region; text contrast; presentation semantics for visual layout tables; decorative SVG semantics; remove outbound editor/main-site links while retaining attribution/license; show generic Python 3 label instead of upstream's hard-coded 3.6 label.
- trace-worker.js: browser-only execution using the upstream Python Tutor trace generator; validates input, detects execution failure, returns JSON traces.

The worker's use of exec_script_str_local is limited to the isolated browser worker and application-generated snippets. Do not reuse this function as an unrestricted public server execution endpoint.

Pyodide's license and bundled third-party notices are in pyodide/LICENSE. Distributed runtime files are pinned to https://cdn.jsdelivr.net/pyodide/v0.27.7/full/. No optional Pyodide packages are loaded.

Q4 host integration also patches H5P.InteractiveBook 1.11.4 locally to keep navigation and interaction focus indicators visible. This is a local patch, not an upstream release, and requires permission to update the library in the destination H5P host.
