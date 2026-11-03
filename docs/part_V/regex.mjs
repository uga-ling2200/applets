export const cases={basic:{pattern:'a',candidates:['apple','banana','cherry','donut']},repeat:{pattern:'a',candidates:['pear','fig','pear']},none:{pattern:'z',candidates:['pear','fig']},empty:{pattern:'a',candidates:[]},zero:{pattern:'a*',candidates:['fig','apple','']}};
export function search(pattern,value){if(pattern==='a*'){const match=/a*/.exec(value);return {start:match.index,text:match[0]};}const i=value.indexOf(pattern);return i<0?null:{start:i,text:pattern};}
export function trace(c){const result=[];return c.candidates.map(candidate=>{const match=search(c.pattern,candidate);if(match!==null)result.push(candidate);return {candidate,match,result:[...result]};});}
if(typeof document!=='undefined'){
const $=id=>document.getElementById(id);let rows=[],position=0;
function reset(message='Predict first, then start the trace.') {rows=[];position=0;$('next').disabled=true;$('start').disabled=false;$('result').textContent='Not started.';$('current').textContent='No candidate inspected.';$('search-result').textContent='';$('history').replaceChildren();$('status').textContent=message;const c=cases[$('example').value];$('inputs').textContent=`Pattern: r${JSON.stringify(c.pattern)}; candidates: ${JSON.stringify(c.candidates)}.`;}
$('example').addEventListener('change',()=>{reset('Practice case changed. The previous trace is cleared; predict the new result.');$('prediction').value='';});$('reset').addEventListener('click',()=>reset('Trace reset. Your written prediction is retained.'));
$('start').addEventListener('click',()=>{rows=trace(cases[$('example').value]);position=0;$('result').textContent='[]';$('history').replaceChildren();$('current').textContent='No candidate inspected.';$('search-result').textContent='';$('start').disabled=true;$('next').disabled=rows.length===0;$('status').textContent=rows.length?'Initialized an empty list. Choose Next candidate.':'Complete: no candidates to inspect. Return [].';(rows.length?$('next'):$('reset')).focus();});
$('next').addEventListener('click',()=>{const row=rows[position++];if(!row)return;$('current').textContent=JSON.stringify(row.candidate);$('search-result').textContent=row.match===null?'Search result: None (falsy). Skip this candidate.':`Search result: Match object (truthy), span (${row.match.start}, ${row.match.start+row.match.text.length}), matched text ${JSON.stringify(row.match.text)}. Add the complete candidate.`;$('result').textContent=JSON.stringify(row.result);const li=document.createElement('li');li.textContent=`${JSON.stringify(row.candidate)} → ${row.match===null?'skip':'keep'} → ${JSON.stringify(row.result)}`;$('history').append(li);const done=position===rows.length;$('next').disabled=done;$('status').textContent=`Candidate ${position} of ${rows.length}: ${row.match===null?'skipped':'kept'}. ${done?'Complete. Return '+JSON.stringify(row.result)+'.':'Continue with the next candidate.'}`;if(done)$('reset').focus();});reset();}

if(typeof document!=="undefined"){
// The Lumi book changes height on navigation, feedback, font load and reflow.
// Observe its content box, not the iframe viewport (which would feed back).
const practiceFrame = document.querySelector('.defaults-check');
let bookObserver;
function fitPractice() {
  bookObserver?.disconnect();
  const content = practiceFrame.contentDocument?.querySelector('.h5p-content');
  if (!content) return;
  const fit = () => {
    const height = Math.ceil(content.getBoundingClientRect().height);
    if (height > 0 && practiceFrame.style.height !== `${height + 2}px`)
      practiceFrame.style.height = `${height + 2}px`;
  };
  bookObserver = new ResizeObserver(fit);
  bookObserver.observe(content);
  fit();
}
practiceFrame.addEventListener('load', fitPractice);
if (practiceFrame.contentDocument?.readyState === 'complete') fitPractice();
// H5P computes chapter heights itself; notify it when the embedding width changes.
// Ignore height-only changes so fitting the iframe cannot create a resize loop.
let previousBookWidth = 0;
new ResizeObserver(([entry]) => {
  const width = Math.round(entry.contentRect.width);
  if (width === previousBookWidth) return;
  previousBookWidth = width;
  practiceFrame.contentWindow?.H5P?.instances?.forEach(book => book.trigger('resize'));
}).observe(practiceFrame);

}
