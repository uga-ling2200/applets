'use strict';
importScripts('./pyodide/pyodide.js');
const ready = (async () => {
  const py = await loadPyodide({indexURL: new URL('./pyodide/', self.location.href).href});
  await Promise.all(['pg_logger.py', 'pg_encoder.py'].map(async name => {
    const response = await fetch(new URL(name, self.location.href));
    if (!response.ok) throw new Error('Could not load Python trace support.');
    py.FS.writeFile('/home/pyodide/' + name, await response.text());
  }));
  py.runPython('import pg_logger, json');
  return py;
})();
self.onmessage = async ({data}) => {
  const {id, number, focus} = data;
  try {
    if (!Number.isInteger(number) || number < 0 || number > 999999 || !['parts','condition','string'].includes(focus)) throw new Error('Invalid trace request.');
    const py = await ready;
    py.globals.set('q4_number', number); py.globals.set('q4_focus', focus);
    const result = py.runPython(`
q4_code = 'number = ' + str(q4_number) + '\\n'
if q4_focus == 'string':
    tail = q4_number % 100
    suffix = 'th' if 11 <= tail <= 13 else {1:'st', 2:'nd', 3:'rd'}.get(q4_number % 10, 'th')
    q4_code += 'suffix = ' + json.dumps(suffix) + '\\nnumber_text = str(number)\\nordinal = number_text + suffix\\n'
else:
    q4_code += 'units = number % 10\\nlast_two = number % 100\\n'
    if q4_focus == 'condition':
        q4_code += 'is_teen_ending = (last_two == 11 or last_two == 12 or last_two == 13)\\n'
pg_logger.exec_script_str_local(q4_code, None, False, False, lambda code, trace: json.dumps({'code': code, 'trace': trace}))
`);
    const trace = JSON.parse(result);
    if (trace.trace.at(-1)?.event !== 'return') throw new Error('Python execution did not finish.');
    self.postMessage({id,trace});
  } catch (error) { self.postMessage({id,error: String(error.message || error)}); }
};
