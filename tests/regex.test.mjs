import {test} from 'node:test';import assert from 'node:assert/strict';import {cases,trace,search} from '../docs/part_V/regex.mjs';
for(const [name,expected] of Object.entries({basic:['apple','banana'],repeat:['pear','pear'],none:[],empty:[],zero:['fig','apple','']}))test(name,()=>assert.deepEqual(trace(cases[name]).at(-1)?.result??[],expected));
test('zero-length success is distinct from no match',()=>{assert.deepEqual(search('a*','fig'),{start:0,text:''});assert.equal(search('a','fig'),null);});
