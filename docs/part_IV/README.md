# Part IV interactive simulations

The two buildless activities follow the course notebook exercises IV.A Q2 and IV.C Q1. They run explicit simulations of the course operations, not arbitrary student code. Students compare predictions and traces before writing their own notebook functions; no complete notebook function solution is displayed. The main catalog links to both pages.

## Keyword arguments: mutable defaults

Revised against Ryan's October 19 feedback and the IV.A notebook sections on mutability, shared default containers and the `is None` pattern. The main comparison deliberately uses a short `remember` function that calls `add`; it is not the notebook exercise solution. Students predict two omitted calls, inspect stable object labels, see the earlier return value change through aliasing, and compare fresh sets created inside the None branch. Redefining resets the default. Supplying a set still permits mutation of the caller's object.

The course reference filter only reads its set, so the page explicitly avoids claiming that filtering alone accumulates words. `{}` is an empty dictionary and has no `add` method. Four H5P Interactive Book checks cover accumulation, None initialization, dictionary type, and the distinction between sharing and actual mutation. They reuse the existing Part III licensed H5P runtime and Check/Retry behaviour. Scores remain local and are not submitted. The original public URL is retained.

## Text files

`IV_C_Q1_Text_Files.html` traces head(filepath, n), skipping a line with next(), and a for loop continuing after next(). Blank lines count; a terminal newline does not create an additional line. Input CRLF is normalized to LF. The reference head() strips surrounding whitespace, and requesting more lines than exist raises StopIteration; the next step still shows the with statement closing the file.

Run `node --test tests/part-iv.test.mjs` from the repository root. The two pages share `part_IV/lab.css` and `core.mjs`, reuse the existing course stylesheet and feedback card styles, and use the shared reflection-notes download component adapted from the LING2150 repository. No existing H5P bundle is modified.

## Lumi authoring and export

Open `IV_A_Q2_Keyword_Arguments.h5p` in Lumi to edit the four-page Interactive Book. The package includes the same library/editor dependencies as the existing Part III packages. Keep this source alongside the published HTML, as in Part III. `utils/defaults_content.json` is its readable content. Run `python3 utils/build_defaults_check.py` to regenerate both the package and embedded standalone HTML from the current content builder; after edits in Lumi, export HTML and apply the repository UGA/accessibility formatting before replacing the published check. The surrounding editable-word comparison uses `kwargs.mjs` / `defaults.mjs` and is independent of the H5P score.
