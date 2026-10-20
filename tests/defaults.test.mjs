import test from 'node:test';
import assert from 'node:assert/strict';
import {createComparison,callBoth,setRepr} from '../docs/part_IV/defaults.mjs';
test('two omitted calls reuse the first set, while None creates distinct fresh sets',()=>{
 const state=createComparison();const shared=state.shared;
 callBoth(state,'cat');const firstFresh=state.fresh;
 callBoth(state,'dog');
 assert.equal(state.shared,shared);
 assert.deepEqual([...shared],['cat','dog']);
 assert.notEqual(state.fresh,firstFresh);
 assert.deepEqual([...firstFresh],['cat']);
 assert.deepEqual([...state.fresh],['dog']);
 assert.deepEqual(state.calls[0].sharedAtReturn,['cat']);
 assert.deepEqual([...state.calls[0].fresh],['cat']);
});
test('a new definition resets state; repeated identical words still have different identities in B',()=>{
 const a=createComparison();callBoth(a,'cat');callBoth(a,'cat');
 assert.deepEqual([...a.shared],['cat']);
 assert.notEqual(a.calls[0].fresh,a.calls[1].fresh);
 const b=createComparison();assert.equal(b.shared.size,0);assert.notEqual(a.shared,b.shared);
 assert.throws(()=>callBoth(b,'  '));assert.equal(b.calls.length,0);
 assert.equal(setRepr([]),'set()');
});
