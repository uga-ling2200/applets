"""Rebuild the two fixed accumulator examples from CPython line events."""
import json
from pathlib import Path
import sys

EXAMPLES = {
    'all': ('Sum of 0 to 4', 'sum = 0\nfor i in range(5):\n    sum += i\nsum\n'),
    'even': ('Sum of even numbers from 0 to 100', 'sum = 0\nfor i in range(101):\n    if i % 2 == 0:\n        sum += i\nsum\n'),
}
root = Path(__file__).resolve().parents[1] / 'docs' / 'part_II'
for key, (title, code) in EXAMPLES.items():
    steps = []
    def record(frame, event, arg):
        if frame.f_code.co_filename == '<accumulator>' and event in ('line', 'return'):
            steps.append({'line': frame.f_lineno if event == 'line' else None,
                          'values': {k: frame.f_globals[k] for k in ('sum', 'i') if k in frame.f_globals}})
        return record
    sys.settrace(record)
    try:
        exec(compile(code, '<accumulator>', 'exec'), {})
    finally:
        sys.settrace(None)
    (root / ('accumulator-' + key + '.json')).write_text(json.dumps({'title': title, 'code': code, 'steps': steps}, indent=2) + '\n')
