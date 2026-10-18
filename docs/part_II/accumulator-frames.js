'use strict';
(() => {
  function nameFrames() {
    document.querySelectorAll('iframe').forEach(frame => {
      if (!frame.src.includes('accumulator-trace.html')) return;
      frame.title = frame.src.includes('mode=even') ? 'Accumulator trace: sum of even numbers from 0 to 100' : 'Accumulator trace: sum of 0 to 4';
    });
  }
  nameFrames();
  new MutationObserver(nameFrames).observe(document.body, {childList:true, subtree:true});
})();
