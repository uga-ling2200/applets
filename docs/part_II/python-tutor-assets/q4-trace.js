'use strict';
(() => {
  const byId = id => document.getElementById(id);
  const params = new URLSearchParams(location.search);
  const focus = ['parts','condition','string'].includes(params.get('focus')) ? params.get('focus') : 'parts';
  if (window.self !== window.top) {
    const heading = document.querySelector('h1');
    const embeddedHeading = document.createElement('h2');
    embeddedHeading.textContent = heading.textContent;
    heading.replaceWith(embeddedHeading);
  }
  const traceName = (params.get('controls') === 'external' ? 'Comparison explorer: ' : '') + ({parts:'Numeric parts',condition:'Exception condition',string:'String construction'}[focus]);
  document.querySelector('main').setAttribute('aria-label','Python Tutor: ' + traceName);
  byId('activity').setAttribute('aria-label',traceName + ': step-by-step execution');
  const input = byId('number');
  let worker, generation = 0, timer, viz, trace;
  input.value = params.get('number') || ({parts:'111',condition:'121',string:'23'}[focus]);
  if (params.get('controls') === 'external') { byId('trace-form').hidden = true; byId('range').hidden = true; }
  function clear() {
    generation++; clearTimeout(timer); byId('activity').hidden = true;
    byId('step-status').textContent = ''; byId('code').textContent = '';
    byId('input-error').textContent = ''; input.removeAttribute('aria-invalid');
  }
  function repair() {
    const root = byId('visualizer');
    const language = root.querySelector('#langDisplayDiv'); if (language) language.textContent = 'Python 3';
    root.querySelectorAll('#navControlsDiv').forEach(el => el.hidden = true); // Replaced by the labeled native controls above.
    root.querySelectorAll('a').forEach(el => el.replaceWith(document.createTextNode(el.textContent)));
    root.querySelectorAll('svg').forEach(el => {el.setAttribute('aria-hidden','true');el.setAttribute('focusable','false');});
    root.querySelectorAll('table').forEach(el => el.setAttribute('role','presentation'));
    const code = root.querySelector('#pyCodeOutputDiv');
    if (code) { code.tabIndex = 0; code.setAttribute('role','region'); code.setAttribute('aria-label',traceName + ': Python source code; use arrow keys to scroll'); }
  }
  const repr = value => typeof value === 'boolean' ? (value ? 'True' : 'False') : JSON.stringify(value);
  function update() {
    const index = viz.curInstr, step = trace.trace[index];
    const total = trace.trace.length - 1;
    const position = index === total ? 'Execution finished.' : 'Next: line ' + step.line + ', ' + trace.code.split('\n')[step.line-1] + '.';
    const values = step.ordered_globals.map(key => key + ' = ' + repr(step.globals[key])).join('; ') || 'No variables assigned yet';
    byId('step-status').textContent = 'Completed ' + index + ' of ' + total + ' steps. ' + position + ' Variables: ' + values + '.';
    byId('previous').setAttribute('aria-disabled',String(index === 0));
    byId('next').setAttribute('aria-disabled',String(index === total));
    repair();
  }
  function fail() {
    clearTimeout(timer); byId('status').textContent = 'The Python runtime could not load. Check your connection and select Load trace here to try again. You can also run the example in your course notebook.';
    if (worker) worker.terminate(); worker = undefined;
    byId('trace-form').hidden = false;
    byId('range').hidden = false;
  }
  function ensureWorker() {
    if (worker) return;
    worker = new Worker('python-tutor-assets/trace-worker.js');
    worker.onerror = fail;
    worker.onmessage = ({data}) => {
      if (data.id !== generation) return;
      clearTimeout(timer);
      if (data.error) {fail(); return;}
      trace = data.trace; byId('activity').hidden = false;
      byId('visualizer').replaceChildren();
      try {
        viz = addVisualizerToPage(trace, 'visualizer', {embeddedMode:true,verticalStack:true,editCodeBaseURL:null,lang:'py3',codeDivWidth:600,codeDivHeight:300});
        viz.add_pytutor_hook('end_updateOutput', () => {update();return [false];});
        byId('code').textContent = trace.code; update();
        byId('status').textContent = 'Trace ready for ' + input.value.trim() + '. Python executed locally in your browser.';
      } catch (error) {byId('activity').hidden=true;fail();}
    };
  }
  function load() {
    clear();
    if (!/^\d{1,6}$/.test(input.value.trim())) {
      input.setAttribute('aria-invalid','true'); byId('input-error').textContent = 'Enter a whole number from 0 to 999999.'; byId('status').textContent=''; return false;
    }
    byId('status').textContent='Loading Python and preparing the trace…';
    try {ensureWorker(); worker.postMessage({id:generation,number:Number(input.value.trim()),focus}); timer=setTimeout(fail,60000);} catch (error) {fail();}
    return true;
  }
  byId('trace-form').addEventListener('submit', event => {event.preventDefault();if (!load()) input.focus();});
  input.addEventListener('input', () => {clear(); byId('status').textContent='Number changed. Predict the result, then load the new trace.';});
  byId('previous').addEventListener('click', () => {if(viz && viz.curInstr>0) viz.renderStep(viz.curInstr-1);});
  byId('next').addEventListener('click', () => {if(viz && viz.curInstr<trace.trace.length-1) viz.renderStep(viz.curInstr+1);});
  byId('restart').addEventListener('click', () => {if(viz) viz.renderStep(0);});
  load();
})();
