import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {cases,getComparison} from '../docs/part_V/greedy.mjs';
test('all teaching results and spans agree with Python re',()=>{
 const results=JSON.parse(execFileSync('python',['-c',`import json,re,sys
cases=json.load(sys.stdin)
for c in cases.values():
 for mode in ('greedy','lazy'):
  m=re.search('<.'+('*' if mode=='greedy' else '*?')+'>'+c['suffix'],c['text'])
  c[mode]={'match':m.group() if m else None,'span':list(m.span()) if m else None}
print(json.dumps(cases))`],{input:JSON.stringify(cases),encoding:'utf8'}));
 assert.deepEqual(results,cases);assert.throws(()=>getComparison('unknown'),RangeError);
});
test('H5P source, readable content and published runtime agree',()=>{
 const book=JSON.parse(readFileSync(new URL('../docs/part_V/greedy_content.json',import.meta.url)));
 const packed=JSON.parse(execFileSync('python',['-c',"import zipfile,sys;z=zipfile.ZipFile(sys.argv[1]);assert z.testzip() is None;print(z.read('content/content.json').decode())",new URL('../docs/part_V/V_B_Q1_Greedy_Lazy.h5p',import.meta.url).pathname],{encoding:'utf8'}));
 const page=readFileSync(new URL('../docs/part_V/greedy_check.html',import.meta.url),'utf8');
 // Decode the JSON assignment without evaluating the standalone runtime.
 const src=page.slice(page.search(/H5PIntegration\s*=/)).replace(/^H5PIntegration\s*=\s*/,'');let depth=0,quote=false,escaped=false,end=0;
 for(let i=0;i<src.length;i++){const c=src[i];if(quote){if(escaped)escaped=false;else if(c==='\\')escaped=true;else if(c==='"')quote=false;}else if(c==='"')quote=true;else if(c==='{')depth++;else if(c==='}'&&!--depth){end=i+1;break;}}
 const runtime=JSON.parse(Object.values(JSON.parse(src.slice(0,end)).contents)[0].jsonContent);
 assert.deepEqual(book,packed);assert.deepEqual(book,runtime);assert.equal(book.chapters.length,6);
 for(const chapter of book.chapters){const q=chapter.params.content[1].content.params;assert.equal(q.answers.filter(a=>a.correct).length,1);assert.ok(q.answers.every(a=>a.tipsAndFeedback.chosenFeedback));assert.equal(q.behaviour.enableRetry,true);}
});
