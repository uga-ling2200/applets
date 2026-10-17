import {fileLines,fileTrace} from './core.mjs';
const $=id=>document.getElementById(id);let steps=[],at=0,lines=[],ready=false;
const codes={head:`def head(filepath, n):
    with open(filepath, encoding="utf-8") as in_file:
        for i in range(n):
            line = next(in_file).strip()
            print(line)`,skip:`with open(filepath, encoding="utf-8") as in_file:
    next(in_file)  # consume, discard
    line = next(in_file)
    print(line.strip())`,loop:`with open(filepath, encoding="utf-8") as in_file:
    print(next(in_file).strip())
    for line in in_file:
        print(line.strip())`};
function render(){let s=steps[at];if(!s)return;$('lines').replaceChildren();lines.forEach((line,i)=>{const li=document.createElement('li');const active=i===s.position&&!s.closed;li.textContent=(line.replace(/\n$/,'')||'(blank line)')+(line.endsWith('\n')?' ↵':'')+(active?' ← next unread':'');li.className=i<s.position?'consumed':active?'next-line':'';$('lines').append(li);});$('variables').textContent=`File: ${s.closed?'closed':'open'}. Consumed: ${s.position}/${lines.length}. `+(s.line!==null?`line = ${JSON.stringify(s.line)}. `:'')+(s.i!==undefined?`i = ${s.i}.`:'');$('output').textContent=s.output.join('\n')+(s.output.length?'\n':'');$('status').textContent=`Step ${at+1}/${steps.length}: ${s.action}`;$('error').textContent=s.error?'StopIteration. The requested line does not exist. The with statement will still close the file.':'';$('step').disabled=!ready||at===steps.length-1;$('run').disabled=!ready||at===steps.length-1;}
function prepare(){const n=Number($('n').value);if(!$('n').value.trim()||!Number.isInteger(n)||n<0||n>100){$('error').textContent='Choose an integer n from 0 to 100.';return;}lines=fileLines($('filetext').value);steps=fileTrace($('filetext').value,n,$('program').value);at=0;ready=true;$('code').textContent=codes[$('program').value];render();}
$('prepare').onclick=prepare;$('step').onclick=()=>{at++;render();};$('run').onclick=()=>{const err=steps.findIndex((s,i)=>i>at&&s.error);at=err>=0?err:steps.length-1;render();};for(const id of ['filetext','n','program'])$(id).addEventListener('input',()=>{ready=false;$('step').disabled=true;$('run').disabled=true;$('status').textContent='Inputs changed. Reopen the file to start again.';});prepare();
