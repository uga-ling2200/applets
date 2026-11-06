import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../docs/h5p-embed.js', import.meta.url), 'utf8');

function practice() {
  let contentHeight = 630;
  let fullscreen = false;
  let selected = false;
  let hint;
  let fullscreenHint;
  let focused = false;
  const events = new Map();
  const callbacks = [];
  const observers = [];
  const root = {
    getBoundingClientRect: () => ({ height: contentHeight, bottom: contentHeight }),
    requestFullscreen: () => Promise.reject(new Error('not granted')),
    append(node) { fullscreenHint = node; },
  };
  const question = {
    querySelector(selector) {
      if (selector === '.practice-answer-hint') return hint;
      if (selector.includes('aria-checked')) return selected ? {} : null;
      if (selector.includes('role=')) return { focus() { focused = true; } };
    },
    append(node) { hint = node; },
  };
  const child = {
    body: {},
    head: { append() {} },
    documentElement: { classList: { toggle() {} } },
    getElementById: () => null,
    get fullscreenElement() { return fullscreen ? root : null; },
    defaultView: { scrollY: 0, addEventListener() {}, removeEventListener() {} },
    querySelector(selector) {
      if (selector === '.h5p-content') return root;
      if (selector === '.practice-fullscreen-hint') return fullscreenHint;
      if (selector.includes('fullscreen')) return fullscreen ? {} : null;
      return null;
    },
    querySelectorAll: () => [],
    addEventListener(name, callback, capture) { events.set(name + !!capture, callback); },
    removeEventListener() {},
    createElement() {
      return { style: {}, setAttribute() {}, remove() { hint = undefined; } };
    },
  };
  const frame = {
    contentDocument: child,
    dataset: {},
    style: { height: '1050px' },
    getBoundingClientRect() { return { height: Number.parseFloat(this.style.height) }; },
    addEventListener() {},
  };
  class Observer {
    constructor(callback) { observers.push(callback); }
    observe() {}
    disconnect() {}
  }
  vm.runInNewContext(source, {
    document: { querySelectorAll: () => [frame] },
    ResizeObserver: Observer,
    MutationObserver: Observer,
    requestAnimationFrame(callback) { callbacks.push(callback); return callbacks.length; },
    cancelAnimationFrame() {},
  });
  function flush() {
    for (let i = 0; callbacks.length && i < 20; i++) callbacks.shift()();
    assert.equal(callbacks.length, 0, 'resize must settle instead of growing forever');
  }
  function resize(height) { contentHeight = height; observers.forEach(callback => callback()); flush(); }
  flush();
  return {
    frame, resize, flush,
    setFullscreen(value) { fullscreen = value; },
    setSelected(value) { selected = value; },
    get hint() { return hint; },
    get focused() { return focused; },
    async denyFullscreen() {
      let stopped = false;
      events.get('clicktrue')({
        target: { closest: () => ({}) },
        preventDefault() {},
        stopImmediatePropagation() { stopped = true; },
      });
      await new Promise(setImmediate);
      flush();
      return { stopped, message: fullscreenHint?.textContent };
    },
    check() {
      const result = { prevented: false, stopped: false };
      events.get('clicktrue')({
        target: { closest: selector => selector.includes('fullscreen') ? null : ({ closest: () => question }) },
        preventDefault() { result.prevented = true; },
        stopImmediatePropagation() { result.stopped = true; },
      });
      flush();
      return result;
    },
    answerEvent(name) {
      events.get(name + 'false')({ target: { closest: () => question } });
      flush();
    },
  };
}

test('practice grows for feedback and shrinks on short pages without a viewport-height floor', () => {
  const page = practice();
  assert.equal(page.frame.style.height, '640px');
  page.resize(960);
  assert.equal(page.frame.style.height, '970px');
  page.resize(420);
  assert.equal(page.frame.style.height, '430px');
  for (let i = 0; i < 10; i++) page.resize(420);
  assert.equal(page.frame.style.height, '430px');
});

test('fullscreen measurements do not overwrite the embedded height', () => {
  const page = practice();
  page.setFullscreen(true);
  page.resize(1200);
  assert.equal(page.frame.style.height, '640px');
  page.setFullscreen(false);
  page.resize(500);
  assert.equal(page.frame.style.height, '510px');
});

test('empty submission stays unscored and editable; tab alone does not dismiss the hint', () => {
  const page = practice();
  assert.deepEqual(page.check(), { prevented: true, stopped: true });
  assert.match(page.hint.textContent, /Choose an answer/);
  assert.equal(page.focused, true);
  page.answerEvent('keydown');
  assert.ok(page.hint, 'keep the reminder until an answer is actually chosen');
  page.setSelected(true);
  page.answerEvent('click');
  assert.equal(page.hint, undefined, 'remove the hint and its empty margins');
  assert.deepEqual(page.check(), { prevented: false, stopped: false });
});

test('denied fullscreen requests leave the practice intact and explain how to continue', async () => {
  const page = practice();
  const result = await page.denyFullscreen();
  assert.equal(result.stopped, true, 'do not call the legacy clipping handler');
  assert.match(result.message, /continue using the practice/);
  assert.equal(page.frame.style.height, '640px');
});
