// Bounded teaching cases. Results and spans are generated and checked with Python re.
export const cases = {
 multiple:{label:'Two bracketed pieces',text:'A <red> and <blue> balloon.',suffix:'',greedy:{match:'<red> and <blue>',span:[2,18]},lazy:{match:'<red>',span:[2,7]},why:'Both searches start at the first <. Greedy .* tries more repetitions before the closing >; lazy .*? can finish at the first >.'},
 single:{label:'One bracketed piece',text:'A <red> balloon.',suffix:'',greedy:{match:'<red>',span:[2,7]},lazy:{match:'<red>',span:[2,7]},why:'Only one closing > is available. The two quantifiers have different preferences but produce the same match here.'},
 missing:{label:'Missing closing bracket',text:'A <red balloon.',suffix:'',greedy:{match:null,span:null},lazy:{match:null,span:null},why:'Both complete patterns require a closing >. Changing the quantifier cannot supply a missing required character.'},
 empty:{label:'Empty bracketed piece',text:'A <> and <blue> balloon.',suffix:'',greedy:{match:'<> and <blue>',span:[2,15]},lazy:{match:'<>',span:[2,4]},why:'Both * and *? allow zero repetitions. Lazy .*? can match zero characters between < and >; the complete match <> is not empty.'},
 suffix:{label:'Optional: required words after the bracket',text:'A <red> and <blue> balloon.',suffix:' balloon',greedy:{match:'<red> and <blue> balloon',span:[2,26]},lazy:{match:'<red> and <blue> balloon',span:[2,26]},why:'At the first >, the required text " balloon" does not follow. Lazy .*? must expand until the entire pattern succeeds. Lazy does not choose a globally shortest match from a later starting point.'}
};
export function getComparison(key){if(!Object.hasOwn(cases,key))throw new RangeError('Unknown practice case');return cases[key];}
if(typeof document!=='undefined'){
 const $=id=>document.getElementById(id);const select=$('case');let revealed=false;
 function panel(mode,c){
  $('pattern-'+mode).textContent='r"<.'+(mode==='greedy'?'*':'*?')+'>'+c.suffix+'"';
  const node=$('text-'+mode);node.replaceChildren();const result=c[mode];
  if(!revealed||!result.span){node.textContent=c.text;}else{
   const [a,b]=result.span;const mark=document.createElement('mark');mark.textContent=c.text.slice(a,b);node.append(document.createTextNode(c.text.slice(0,a)),mark,document.createTextNode(c.text.slice(b)));
  }
  $('result-'+mode).textContent=!revealed?'Result hidden. Predict before revealing.':result.match===null?'re.search() returns None. No match.':'Matched text: '+JSON.stringify(result.match)+'. Span: ('+result.span.join(', ')+').';
 }
 function render(){const c=getComparison(select.value);panel('greedy',c);panel('lazy',c);$('explanation').textContent=revealed?c.why:'The panels show the same input and search operation. Only the quantifier changes.';$('status').textContent=revealed?'Results revealed for '+c.label+'. Read the matched text and explanation below.':'Results hidden for '+c.label+'. Write a prediction, then reveal.';}
 select.addEventListener('change',()=>{revealed=false;$('prediction').value='';render();});
 $('reveal').addEventListener('click',()=>{revealed=true;render();});
 $('reset').addEventListener('click',()=>{revealed=false;render();});render();
}
