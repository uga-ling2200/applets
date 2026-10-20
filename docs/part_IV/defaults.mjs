// Explicit object-identity model of the two short Python examples shown on the page.
export function createComparison() {
  return { shared: new Set(), fresh: null, calls: [] };
}
export function callBoth(state, word) {
  if (typeof word !== 'string' || !word.trim()) throw new Error('Enter a word for each call.');
  const value = word.trim();
  state.shared.add(value);
  state.fresh = new Set([value]);
  state.calls.push({ word: value, sharedAtReturn: [...state.shared], fresh: state.fresh });
  return state;
}
export const setRepr = values => {
  const words = [...values].sort();
  return words.length ? '{' + words.map(w => JSON.stringify(w)).join(', ') + '}' : 'set()';
};
