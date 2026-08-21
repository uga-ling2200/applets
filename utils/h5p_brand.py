#!/usr/bin/env python3
"""
h5p_brand.py
============

Transforms a raw H5P "Standalone Browser" export (the file H5P itself
produces when you tick "Download as HTML" / export a standalone page)
into the branded, formatted version used on the UGA LING2200 applets
site (uga-ling2200.github.io/applets).

What it does to the raw export
-------------------------------
1. In <head>, right after the opening tag, inserts:
     - Google Fonts preconnects
     - a link to the shared site stylesheet (../style.css)
     - the Bootstrap 5 CSS CDN link
     - the H5P resizer script (so the applet can live in an <iframe>)

2. Right before </head>, inserts two <style> blocks:
     - UGA typography/branding overrides for H5P's own CSS classes
       (fonts, colors, button colors, the .applet-wrapper max-width, etc.)
     - page-level styles for the branded header, the "example" callout,
       and the "Help us improve this applet" feedback card

3. Replaces the bare <body>...<div class="h5p-content" ...></div>...</body>
   wrapper with:
     - a branded header (linking back to the department + the applets
       index) as <body class="pt-3 mt-1">
     - the same h5p-content div, now nested in a .applet-wrapper
     - a "Help us improve this applet" feedback card that deep-links to
       a pre-filled GitHub issue for this specific applet

The huge embedded H5PIntegration <script> blob (the actual interactive
content/JSON/images) and the H5P core CSS block are left completely
untouched -- only the surrounding page chrome changes.

Usage
-----
    python3 h5p_brand.py INPUT.html [-o OUTPUT.html]
                          [--title "I.F While Loops, #1"]
                          [--part part_I]
                          [--dept-name "University of Georgia"]
                          [--dept-url "https://linguistics.uga.edu/"]
                          [--index-name "Quantitative Linguistics Webapps"]
                          [--index-url "https://uga-ling2200.github.io/applets/"]
                          [--repo "uga-ling2200/applets"]
                          [--tutorial-url "https://kaltura.uga.edu/media/t/1_bhor4qfq"]

If --title is omitted, the script tries to auto-detect it from the
H5P.InteractiveBook cover description embedded in the export
(the bold text inside "bookCover":{"coverDescription": ...}).

If --part is omitted, it is derived from the title's leading Roman
numeral (e.g. "I.F While Loops, #1" -> "part_I", "II.B Numbers, Q5"
-> "part_II"). Falls back to "part_I" if nothing can be detected.

The GitHub issue link and the "source-url" query parameter are built to
exactly match the encoding scheme used on the live site: the applet
title is placed in the URL path with spaces (only) written as literal
"%20", and the resulting URL is then percent-encoded once more for use
as a query-string value -- which is why you'll see "%2520" (a doubly
encoded space) but plain "%2C" (a singly encoded comma) in the output.
"""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import quote

# ---------------------------------------------------------------------------
# Static templates (extracted verbatim from a known-good formatted export)
# ---------------------------------------------------------------------------

HEAD_INSERT = """            <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="../style.css">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://h5p.org/sites/all/modules/h5p/library/js/h5p-resizer.js" charset="UTF-8"></script>
"""

BRANDING_STYLE = """    <style>
    body {
        font-family: 'Merriweather Sans', 'Georgia', sans-serif !important;
        background-color: var(--bg);
    }
    /* UGA Typography & Branding Overrides for H5P */
    .h5p-iframe, 
    .h5p-container, 
    .h5p-content, 
    .h5p-interactive-book,
    .h5p-advanced-text,
    .h5p-question-content,
    .h5p-interactive-book-chapter {
        font-family: 'Merriweather Sans', 'Georgia', sans-serif !important;
        background-color: #ffffff;
    }
    html.h5p-iframe, body.h5p-iframe {
    height: 100% !important;
}

    .applet-wrapper{
        max-width: 1200px; /* Limits the width to exactly 600 pixels */
        width: 100%;       /* Allows it to scale down on smaller screens */
        margin: 0 auto;    /* Centers the div horizontally */
    }
    h1, h2, h3, h4, h5, h6, .h5p-interactive-book h2, h5p-multichoice h2 {
        font-family: 'Merriweather', 'Georgia', serif !important;
        color: var(--uga-black);
        font-weight: 800;
        margin: 0;
        letter-spacing: 0.5px;
        text-transform: none;
    }

    
    .h5p-question-introduction {
        font-family: 'Merriweather', 'Georgia', serif !important;
        line-height: 1.5em;
        color: var(--uga-black);
    }

    /* Ensure primary interactive elements match UGA Red */
    .h5p-joubel-simple-rounded-button,
    .joubel-simple-rounded-button,
    .h5p-core-button {
        background-color: #ba0c2f !important;
        border-color: #ba0c2f !important;
        color: #ffffff !important;
    }
      .uga-header{
        text-transform: uppercase;
        text-decoration: none; color: inherit; font-weight: bold;
      }
      .uga-applet-header{
        text-decoration: none; color: inherit; font-weight: bold;
      }
    </style>
"""

PAGE_STYLE = """        <style>
      * { box-sizing: border-box; }
      .uga-bar { height: 9px; background: #ba0c2f; }
      header h1,
      main h2,
      .applet-feedback-card h2 { font-family: Georgia, serif; }
      header h1 { margin: 0; font-size: clamp(2rem, 5vw, 3.4rem); }
      main {
        max-width: 1100px;
        min-height: 360px;
        margin: 0 auto;
        padding: 42px 24px;
      }
      main h2 { margin-top: 0; font-size: 1.8rem; }
      .example {
        max-width: 760px;
        padding: 22px;
        border-left: 4px solid #ba0c2f;
        background: #f7f7f7;
        font-size: 1.05rem;
        line-height: 1.65;
      }
      .review-note {
        max-width: 1100px;
        margin: 0 auto;
        padding: 0 24px;
        color: #6b6259;
        font-size: .9rem;
      }
      .applet-feedback-card {
        max-width: 1100px;
        margin: 32px auto 96px;
        padding: 24px;
        border: 1px solid #d6d2ce;
        border-left: 6px solid #ba0c2f;
        border-radius: 8px;
        background: #f7f7f7;
      }
      .applet-feedback-card__content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
      }
      .applet-feedback-card h2 {
        margin: 0 0 8px;
        color: #000;
        font-size: 1.3rem;
        line-height: 1.3;
      }
      .applet-feedback-card p {
        max-width: 720px;
        margin: 0;
        color: #554f47;
        font-size: 1rem;
        line-height: 1.55;
      }
      .applet-feedback-card__tutorial {
        display: inline-block;
        margin-top: 10px;
        color: #7f0a22;
        font-size: .92rem;
        font-weight: 700;
        text-decoration: underline;
        text-underline-offset: 3px;
      }
      .applet-feedback-card__tutorial::before {
        content: "\\25B7";
        display: inline-block;
        margin-right: 7px;
        font-size: .75rem;
      }
      .applet-feedback-card__button {
        flex: 0 0 auto;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 44px;
        padding: 11px 18px;
        border: 2px solid #ba0c2f;
        border-radius: 6px;
        background: #ba0c2f;
        color: #fff;
        font-size: .95rem;
        font-weight: 700;
        line-height: 1.2;
        text-align: center;
        text-decoration: none;
      }
      .applet-feedback-card__button:hover {
        border-color: #8f0a25;
        background: #8f0a25;
      }
      a:focus-visible { outline: 3px solid #f9a825; outline-offset: 3px; }
      @media (max-width: 720px) {
        .applet-feedback-card { margin: 24px 16px 72px; padding: 20px; }
        .applet-feedback-card__content { align-items: stretch; flex-direction: column; }
        .applet-feedback-card__button { width: 100%; }
      }
    </style>
"""

BODY_TEMPLATE = """    </head>
    <body class="pt-3 mt-1">
    <div class="text-center mb-4">
        <h1 style="font-size: 1.4rem;"><a class="uga-header" href="{dept_url}">{dept_name}</a></h1>
        <h2 class="text-muted small"><a class="uga-applet-header" href="{index_url}">{index_name}</a></h2>
    </div>
    <div class="applet-wrapper">
        <div style="margin: 0px 0px;" >
            <div
                style=""
                class="h5p-content lag" data-content-id="{content_id}"></div>        
        </div>       
        </div>
            <section class="applet-feedback-card" aria-labelledby="applet-feedback-heading">
      <div class="applet-feedback-card__content">
        <div>
          <h2 id="applet-feedback-heading">Help us improve this applet</h2>
          <p>Report a problem or share a suggestion.</p>
          <a
            class="applet-feedback-card__tutorial"
            href="{tutorial_url}"
            target="_blank"
            rel="noopener noreferrer"
          >New to GitHub? Watch the one-minute account setup guide</a>
        </div>
        <a
          class="applet-feedback-card__button"
          href="{issue_url}"
          target="_blank"
          rel="noopener noreferrer"
        >Report a problem or give feedback</a>
      </div>
    </section>
    </body>
</html>"""

# ---------------------------------------------------------------------------
# Regexes
# ---------------------------------------------------------------------------

# Matches the raw export's bare body wrapper, from the closing </style> of
# the H5P core CSS block through to the end of the document. Whitespace is
# treated loosely since it is entirely replaced.
TAIL_RE = re.compile(
    r"""</style>\s*
        </head>\s*
        <body>\s*
        <div\ style="margin:\ 0px\ 0px;">\s*
        <div\s*
            style=""\s*
            class="h5p-content\ lag"\s*data-content-id="(?P<cid>\d+)"></div>\s*
        </div>\s*
        </body>\s*
        </html>\s*$""",
    re.VERBOSE,
)

CID_RE = re.compile(r'data-content-id="(\d+)"')
COVER_TITLE_RE = re.compile(r'coverDescription[^{]*?<strong>([^<]+)</strong>')
ROMAN_PREFIX_RE = re.compile(r'^\s*([IVXLC]+)\.')


def extract_content_id(html: str) -> str:
    m = CID_RE.search(html)
    if not m:
        raise ValueError("Could not find a data-content-id in the input file.")
    return m.group(1)


def extract_title(html: str) -> str:
    """Best-effort auto-detection of the applet title from the embedded
    H5P.InteractiveBook cover description, e.g. '<strong>I.F While Loops,
    #1</strong>' -> 'I.F While Loops, #1'. Returns '' if not found."""
    m = COVER_TITLE_RE.search(html)
    return m.group(1).strip() if m else ""


def derive_part_dir(title: str) -> str:
    m = ROMAN_PREFIX_RE.match(title)
    return f"part_{m.group(1)}" if m else "part_I"


def build_issue_url(repo: str, part_dir: str, title: str) -> str:
    """Reproduces the exact (slightly quirky) double-encoding scheme used
    on the live site: only spaces in the title get pre-encoded as literal
    '%20' before the whole source URL is percent-encoded once more."""
    title_path = title.replace(" ", "%20")
    source_url = f"https://uga-ling2200.github.io/applets/{part_dir}/{title_path}.html"
    source_url_q = quote(source_url, safe="")

    issue_title = quote(f"[Applet feedback] {title}: ", safe="")
    applet_q = quote(title, safe="")

    return (
        f"https://github.com/{repo}/issues/new?template=applet-feedback.yml"
        f"&amp;title={issue_title}"
        f"&amp;applet={applet_q}"
        f"&amp;source-url={source_url_q}"
    )


def transform(
    html: str,
    *,
    title: str = "",
    part_dir: str = "",
    dept_name: str = "University of Georgia",
    dept_url: str = "https://linguistics.uga.edu/",
    index_name: str = "Quantitative Linguistics Webapps",
    index_url: str = "https://uga-ling2200.github.io/applets/",
    repo: str = "uga-ling2200/applets",
    tutorial_url: str = "https://kaltura.uga.edu/media/t/1_bhor4qfq",
) -> str:
    if "<head>" not in html:
        raise ValueError("Input does not look like an H5P standalone export (no <head> found).")

    content_id = extract_content_id(html)

    if not title:
        title = extract_title(html)
        if not title:
            raise ValueError(
                "Could not auto-detect the applet title from the export. "
                "Pass --title explicitly."
            )

    if not part_dir:
        part_dir = derive_part_dir(title)

    issue_url = build_issue_url(repo, part_dir, title)

    # 1. Insert the head links/scripts right after <head>
    html = html.replace("<head>\n", "<head>\n" + HEAD_INSERT, 1)

    # 2. Replace the tail (core-css-close -> </html>) with the branded
    #    styles + branded body + feedback card.
    new_tail = (
        "</style>\n        "
        + BRANDING_STYLE
        + PAGE_STYLE
        + BODY_TEMPLATE.format(
            dept_name=dept_name,
            dept_url=dept_url,
            index_name=index_name,
            index_url=index_url,
            content_id=content_id,
            tutorial_url=tutorial_url,
            issue_url=issue_url,
        )
    )

    new_html, n = TAIL_RE.subn(lambda m: new_tail, html)
    if n != 1:
        raise ValueError(
            "Could not locate the expected end-of-document wrapper in the "
            "input file -- is this a raw (unformatted) H5P standalone "
            "export? The script only transforms files matching that shape."
        )

    return new_html


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Brand/format a raw H5P standalone export for the UGA LING2200 applets site."
    )
    parser.add_argument("input", type=Path, help="Path to the raw H5P export HTML file")
    parser.add_argument("-o", "--output", type=Path, help="Output path (default: <input>_formatted.html)")
    parser.add_argument("--title", default="", help="Applet title, e.g. 'I.F While Loops, #1' (auto-detected if omitted)")
    parser.add_argument("--part", default="", dest="part_dir", help="Part directory, e.g. 'part_I' (derived from title if omitted)")
    parser.add_argument("--dept-name", default="University of Georgia")
    parser.add_argument("--dept-url", default="https://linguistics.uga.edu/")
    parser.add_argument("--index-name", default="Quantitative Linguistics Webapps")
    parser.add_argument("--index-url", default="https://uga-ling2200.github.io/applets/")
    parser.add_argument("--repo", default="uga-ling2200/applets", help="GitHub repo (owner/name) for the feedback issue link")
    parser.add_argument("--tutorial-url", default="https://kaltura.uga.edu/media/t/1_bhor4qfq")
    args = parser.parse_args(argv)

    html = args.input.read_text(encoding="utf-8")

    try:
        result = transform(
            html,
            title=args.title,
            part_dir=args.part_dir,
            dept_name=args.dept_name,
            dept_url=args.dept_url,
            index_name=args.index_name,
            index_url=args.index_url,
            repo=args.repo,
            tutorial_url=args.tutorial_url,
        )
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    output = args.output or args.input.with_name(args.input.stem + "_formatted.html")
    output.write_text(result, encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
