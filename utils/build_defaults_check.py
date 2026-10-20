"""Publish the H5P book edited in Lumi, keeping its .h5p package canonical.

After Save in Lumi and Export > All-in-one HTML file:
  python3 utils/build_defaults_check.py --export /path/to/lumi-export.html
Without --export, synchronize content from the saved .h5p into the existing
standalone runtime. Never overwrite the Lumi source from generated questions.
"""
import argparse
import json
import re
import zipfile
from pathlib import Path
from h5p_accessibility import repair_runtime
from h5p_brand import BRANDING_STYLE

ROOT = Path(__file__).resolve().parents[1]
PART = ROOT / 'docs/part_IV'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--export', type=Path)
args = parser.parse_args()
with zipfile.ZipFile(PART / 'IV_A_Q2_Keyword_Arguments.h5p') as archive:
    book = json.loads(archive.read('content/content.json'))
    assert archive.testzip() is None

output = PART / 'defaults_check.html'
page = (args.export or output).read_text()
match = re.search(r'H5PIntegration\s*=\s*', page)
assert match
start = match.end()
integration, consumed = json.JSONDecoder().raw_decode(page[start:])
entry = next(iter(integration['contents'].values()))
entry['jsonContent'] = json.dumps(book)
entry['metadata']['title'] = 'Mutable defaults: check your reasoning'
entry['displayOptions'].update(frame=False, embed=False, export=False, copyright=False)
entry['url'] = entry['exportUrl'] = ''
page = page[:start] + json.dumps(integration).replace('</', '<\\/') + page[start + consumed:]
page = repair_runtime(page).replace('l10n.exitFullScreen', 'l10n.exitFullscreen')
if args.export:
    page = page.replace('<html class=', '<html lang="en" class=', 1)
    head_end = page.rfind('</head>')
    assert head_end > 0
    styles = '''<title>Mutable defaults: practice checks</title>
<link rel="stylesheet" href="../style.css">
<link rel="stylesheet" href="../h5p-accessibility.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700;800&amp;family=Merriweather+Sans:wght@400;600;700&amp;display=swap">
'''+BRANDING_STYLE+'''
<style>
html.h5p-iframe,html.h5p-iframe body{min-height:0!important;height:auto!important;margin:0!important;padding:0!important}
a:focus-visible,button:focus-visible,[tabindex]:focus-visible{outline:3px solid #0055a4!important;outline-offset:3px!important}
.h5p-alternative-inner p{font-weight:400!important;font-size:1rem!important}
code{overflow-wrap:anywhere}
</style>
'''
    page = page[:head_end] + styles + page[head_end:]
    # Name the main content without changing the Lumi runtime.
    body = list(re.finditer(r'<body[^>]*>', page))[-1]
    close = page.rfind('</body>')
    page = page[:body.end()]+'<main aria-label="Mutable defaults practice">'+page[body.end():close]+'</main>'+page[close:]
page = re.sub(r'[ \t]+(?=\n)', '', page)
output.write_text(page)
(ROOT / 'utils/defaults_content.json').write_text(json.dumps(book, indent=2))
