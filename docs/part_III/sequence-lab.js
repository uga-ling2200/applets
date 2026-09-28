/* Shared, deterministic practice labs. No learner code is evaluated. */
(function(){
'use strict';
function positions(n,start,stop,step){
 if(!Number.isSafeInteger(step)||step===0)throw Error('Step must be a nonzero whole number.');
 const norm=(x,lo,hi)=>Math.max(lo,Math.min(hi,x<0?x+n:x));
 const a=start===null?(step>0?0:n-1):norm(start,step>0?0:-1,step>0?n:n-1);
 const b=stop===null?(step>0?n:-1):norm(stop,step>0?0:-1,step>0?n:n-1);
 const out=[];for(let i=a;step>0?i<b:i>b;i+=step)out.push(i);return out;
}
if(typeof module!=='undefined')module.exports={positions};
if(typeof document==='undefined')return;
const root=document.querySelector('[data-sequence-lab]');if(!root)return;
const el=id=>document.getElementById(id), mode=root.dataset.sequenceLab;
const status=el('lab-status'), result=el('lab-result'), prediction=el('lab-prediction');
const say=s=>{status.textContent=s;};
function chars(s){return Array.from(s);}
function display(items,kind){let a=items.map(x=>typeof x==='string'?JSON.stringify(x):String(x));return kind==='string'?JSON.stringify(items.join('')):kind==='tuple'?'('+a.join(', ')+(a.length===1?',':'')+')':'['+a.join(', ')+']';}
function diagram(items,selected=[]){
 const list=el('lab-positions');list.replaceChildren();
 items.forEach((x,i)=>{const li=document.createElement('li');li.textContent=`${JSON.stringify(x)} — index ${i}, negative index ${i-items.length}`;if(selected.includes(i)){li.className='lab-selected';li.textContent+=' — selected';}list.append(li);});
}
function clear(){result.textContent='';prediction.value='';say('Make a prediction before checking.');}
if(mode==='slice'){
 const presets={word:{items:chars('plant'),kind:'string'},tuple:{items:[3,8,2,5],kind:'tuple'},list:{items:['red','blue','green'],kind:'list'},empty:{items:[],kind:'list'},single:{items:['oak'],kind:'tuple'}};
 const input=el('lab-example');let example=presets[input.value];
 const number=id=>{const raw=el(id).value.trim();if(raw==='')return null;if(!/^-?\d+$/.test(raw)||!Number.isSafeInteger(Number(raw)))throw Error('Use whole numbers for the slice fields, or leave a field blank.');return Number(raw);};
 function update(){example=presets[input.value];clear();el('lab-original').textContent=display(example.items,example.kind);diagram(example.items);}
 input.addEventListener('change',update);
 ['lab-start','lab-stop','lab-step'].forEach(id=>el(id).addEventListener('input',()=>{result.textContent='';diagram(example.items);say('The slice changed. Update your prediction, then check again.');}));
 el('lab-form').addEventListener('submit',e=>{e.preventDefault();try{if(!prediction.value.trim())throw Error('Write your predicted result, or write empty or error.');let a=number('lab-start'),b=number('lab-stop'),s=number('lab-step')??1;let indices=positions(example.items.length,a,b,s);diagram(example.items,indices);result.textContent=`Visited indices: ${indices.length?indices.join(', '):'none'}. Result (${example.kind}): ${display(indices.map(i=>example.items[i]),example.kind)}. The original sequence is unchanged.`;say('Result shown. Compare it with your prediction and explain any difference.');}catch(err){result.textContent='';say(err.message);}});
 el('lab-reset').addEventListener('click',()=>{input.value='word';el('lab-start').value='1';el('lab-stop').value='4';el('lab-step').value='1';update();});update();
}else{
 const examples=['A (x) B (y) C','We (quietly) left','(maybe) We can go','We left (quietly)','(aside)'];let current=examples[0],pending=null;
 function update(){el('lab-original').textContent=JSON.stringify(current);diagram(chars(current));el('lab-apply').disabled=true;pending=null;}
 el('lab-example').addEventListener('change',()=>{current=examples[Number(el('lab-example').value)];clear();update();});
 el('lab-clean').addEventListener('change',()=>{result.textContent='';pending=null;el('lab-apply').disabled=true;say('The joining option changed. Update your prediction and check again.');});
 el('lab-form').addEventListener('submit',e=>{e.preventDefault();if(!prediction.value.trim()){say('Write your predicted next string, or write empty.');return;}let a=current.indexOf('('),b=current.indexOf(')',a+1);if(a<0){result.textContent='No opening parenthesis remains. Current string: '+JSON.stringify(current);say('There is no next pair to remove.');return;}let left=current.slice(0,a),right=current.slice(b+1);pending=el('lab-clean').checked?[left.trimEnd(),right.trimStart()].filter(Boolean).join(' '):left+right;diagram(chars(current),Array.from({length:b-a+1},(_,i)=>a+i));result.textContent=`Opening index: ${a}; closing index: ${b}. Left piece: ${JSON.stringify(left)}. Right piece: ${JSON.stringify(right)}. Next string: ${JSON.stringify(pending)}.`;el('lab-apply').disabled=false;say('One edit previewed. Compare the spaces, then apply the edit to continue.');});
 el('lab-apply').addEventListener('click',()=>{if(pending===null)return;current=pending;clear();update();say(current.includes('(')?'Edit applied. Positions have changed. Predict the next edit.':'Edit applied. No opening parenthesis remains.');});
 el('lab-reset').addEventListener('click',()=>{current=examples[Number(el('lab-example').value)];el('lab-clean').checked=false;clear();update();});update();
}
})();
