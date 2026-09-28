"""Compare the JavaScript practice model with Python's actual slice semantics.
Usage: python3 utils/part_iii_ef/test_slices.py [node-executable]
"""
import itertools
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
bounds = [None, -12, -5, -1, 0, 1, 4, 12]
cases = [[n, a, b, s, list(range(n))[slice(a, b, s)]]
         for n, a, b, s in itertools.product(range(8), bounds, bounds, [-3, -1, 1, 2, 4])]
script = """
const fs = require('node:fs');
const {positions} = require(process.argv[1]);
const cases = JSON.parse(fs.readFileSync(0, 'utf8'));
for (const [n,a,b,s,expected] of cases) {
  const actual = positions(n,a,b,s);
  if (JSON.stringify(actual) !== JSON.stringify(expected)) throw Error(JSON.stringify({n,a,b,s,expected,actual}));
}
let rejected=false;
try { positions(5,null,null,0); } catch { rejected=true; }
if(!rejected)throw Error('Zero step must fail');
console.log(`${cases.length} Python comparisons passed; zero step rejected.`);
"""
subprocess.run([sys.argv[1] if len(sys.argv)>1 else 'node', '-e', script,
                str(root/'docs/part_III/sequence-lab.js')], input=json.dumps(cases), text=True, check=True)
