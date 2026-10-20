import {createComparison, callBoth, setRepr} from './defaults.mjs?v=20261019-defaults';
const $ = id => document.getElementById(id);
let state;
function render() {
  const count = state.calls.length;
  $('shared-state').textContent = `Stored default → S1\nS1 = ${setRepr(state.shared)}`;
  $('fresh-state').textContent = count
    ? `Stored default → None\nCall ${count} created S${count + 1} = ${setRepr(state.fresh)}`
    : 'Stored default → None\nNo set has been created yet.';
  $('calls').replaceChildren();
  state.calls.forEach((call, i) => {
    const li = document.createElement('li');
    const code = document.createElement('code');
    code.textContent = `remember(${JSON.stringify(call.word)})`;
    const p = document.createElement('p');
    p.textContent = `A returned S1 containing ${setRepr(call.sharedAtReturn)} at that moment. S1 now contains ${setRepr(state.shared)}. B returned S${i + 2}, still containing ${setRepr(call.fresh)}.`;
    li.append(code, p); $('calls').append(li);
  });
  $('step').textContent = count === 0 ? 'Run first call' : count === 1 ? 'Run second call' : 'Both calls complete';
  $('step').disabled = count === 2;
  for (const id of ['first-word', 'second-word']) $(id).disabled = count > 0;
  $('explanation').textContent = count === 2
    ? 'A reused S1: changing it in the second call also changed the object returned by the first call. B created a different set in each call. Only redefining A creates a new default; calling it does not.'
    : '';
  $('prediction-comparison').textContent = count === 2 && $('prediction').value.trim()
    ? 'Your prediction: ' + $('prediction').value.trim() : '';
}
function reset() {
  state = createComparison(); $('error').textContent = '';
  $('status').textContent = 'Both functions defined. A created S1 once; B stored None. Predict before running the calls.';
  render();
}
$('step').addEventListener('click', () => {
  if (state.calls.length >= 2) return;
  if (!$('first-word').value.trim() || !$('second-word').value.trim()) {
    $('error').textContent = 'Enter a word for both calls before starting.';
    (!$('first-word').value.trim() ? $('first-word') : $('second-word')).focus(); return;
  }
  $('error').textContent = '';
  callBoth(state, $(state.calls.length === 0 ? 'first-word' : 'second-word').value);
  render();
  $('status').textContent = state.calls.length === 1
    ? 'First call complete. Both sets contain the first word. Now test the second call.'
    : 'Second call complete. A reused S1; B created S3. Compare the returned objects below.';
  if (state.calls.length === 2) $('reset').focus();
});
$('reset').addEventListener('click', reset);
$('prediction').addEventListener('input', render);
reset();
