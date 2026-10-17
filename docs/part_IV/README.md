# Part IV interactive simulations

The two buildless activities follow the course notebook exercises IV.A Q2 and IV.C Q1. They run explicit simulations of the displayed Python, not arbitrary student code. The main catalog links to both pages.

## Keyword arguments

`IV_A_Q2_Keyword_Arguments.html` follows `extract_and_filter_words(string, words_to_include=None)` from the reference solution. Omitted, empty and nonempty sets are separate call modes. In the reference, both None and an empty set lead to no filtering; repeated words and their original order are preserved. The helper lowercases and strips word-external punctuation using the same specified punctuation set as the reference.

The exercise wording could imply that explicitly supplying an empty set should return no matches. The activity explicitly teaches the reference implementation's behavior and asks students to discuss the alternative. This version follows the reference solution and records the wording discrepancy for instructor review.

## Text files

`IV_C_Q1_Text_Files.html` traces head(filepath, n), skipping a line with next(), and a for loop continuing after next(). Blank lines count; a terminal newline does not create an additional line. Input CRLF is normalized to LF. The reference head() strips surrounding whitespace, and requesting more lines than exist raises StopIteration; the next step still shows the with statement closing the file.

Run `node --test tests/part-iv.test.mjs` from the repository root. The two pages share `part_IV/lab.css` and `core.mjs`, reuse the existing course stylesheet and feedback card styles, and use the shared reflection-notes download component adapted from the LING2150 repository. No existing H5P bundle is modified.
