'use strict';
(async () => {
  const byId = id => document.getElementById(id);
  const mode = new URLSearchParams(location.search).get('mode') === 'even' ? 'even' : 'all';
  let index = 0, trace;
  function render() {
    const step = trace.steps[index];
    [...byId('code').children].forEach((line, i) => {
      if (step.line === i + 1) line.setAttribute('aria-current', 'step');
      else line.removeAttribute('aria-current');
    });
    byId('variables').replaceChildren();
    for (const [name, value] of Object.entries(step.values)) {
      const dt = document.createElement('dt'), dd = document.createElement('dd');
      dt.textContent = name; dd.textContent = String(value); byId('variables').append(dt, dd);
    }
    const values = Object.entries(step.values).map(([k, v]) => k + ' = ' + v).join('; ') || 'No variables assigned yet';
    byId('step-status').textContent = 'Step ' + index + ' of ' + (trace.steps.length - 1) + '. ' +
      (step.line ? 'Next: line ' + step.line + ', ' + trace.code.split('\n')[step.line - 1].trim() + '. ' : 'Execution finished. ') + values + '.';
    byId('previous').setAttribute('aria-disabled', String(index === 0));
    byId('next').setAttribute('aria-disabled', String(index === trace.steps.length - 1));
  }
  for (const [id, move] of Object.entries({previous: () => index - 1, next: () => index + 1, restart: () => 0, finish: () => trace.steps.length - 1})) {
    byId(id).addEventListener('click', () => {if (!trace) return; index = Math.max(0, Math.min(trace.steps.length - 1, move())); render();});
  }
  try {
    const response = await fetch('accumulator-' + mode + '.json');
    if (!response.ok) throw Error('Trace unavailable');
    trace = await response.json();
    document.title = trace.title + ': code trace'; byId('trace-title').textContent = trace.title;
    trace.code.trimEnd().split('\n').forEach(text => {const li = document.createElement('li');li.textContent = text;byId('code').append(li);});
    render();
  } catch (_) {byId('step-status').textContent = 'The trace could not load. Reload this page or run the example in your course notebook.';}
})();
