"""Synchronize the canonical Lumi H5P source into the retained standalone runtime.
Run after saving V_A_Q2_Regex_Basics.h5p in Lumi. This never overwrites that source.
The retained runtime already includes the course branding and accessibility repairs.
"""
import argparse,json,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PART=ROOT/'docs/part_V'
parser=argparse.ArgumentParser(description=__doc__)
args=parser.parse_args()
with zipfile.ZipFile(PART/'V_A_Q2_Regex_Basics.h5p') as z:
 assert z.testzip() is None
 book=json.loads(z.read('content/content.json'))
page=(PART/'regex_check.html').read_text()
m=re.search(r'H5PIntegration\s*=\s*',page);start=m.end()
d,consumed=json.JSONDecoder().raw_decode(page[start:])
v=next(iter(d['contents'].values()));v['jsonContent']=json.dumps(book)
v['metadata']['title']='Regex filtering: check your reasoning'
page=page[:start]+json.dumps(d).replace('</','<\\/')+page[start+consumed:]
page=page.replace('.flow','.h5p-advanced-text ol')
page=page.replace('</head>','<style>.h5p-alternative-inner{font-weight:400!important;font-size:1rem!important}</style></head>') if 'id="regex-answer-style"' not in page else page
page=page.replace('<style>.h5p-alternative-inner{','<style id="regex-answer-style">.h5p-alternative-inner{')
(PART/'regex_check.html').write_text(page)
(PART/'regex_content.json').write_text(json.dumps(book,indent=2))
print('Synchronized',len(book['chapters']),'chapters;',sum(len(c['params']['content'])-1 for c in book['chapters']),'questions. Lumi source unchanged.')
