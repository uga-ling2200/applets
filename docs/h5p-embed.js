/* Shared host behaviour for the course's same-origin H5P practice frames.
   Measure the content, not scrollHeight (which includes the current iframe
   viewport and cannot reliably shrink). Keep native scrolling as a fallback. */
(function () {
  'use strict';
  for (const frame of document.querySelectorAll('iframe.defaults-check')) {
    let cleanup = () => {};
    function connect() {
      cleanup();
      let doc;
      try { doc = frame.contentDocument; } catch { return; }
      if (!doc?.body) return;
      const view = doc.defaultView;
      // Interactive Book caches a pixel height and absolutely positions each
      // chapter. That cache can clip reflowed text or our validation message.
      // Let the active chapter participate in normal flow at every width.
      if (!doc.getElementById('course-practice-flow')) {
        const style = doc.createElement('style');
        style.id = 'course-practice-flow';
        style.textContent = `
          html.course-embedded-practice .h5p-interactive-book-content {
            height:auto!important; overflow:visible!important;
          }
          html.course-embedded-practice .h5p-interactive-book-chapter {
            position:static!important; transform:none!important;
            top:auto!important; left:auto!important; overflow:visible!important;
          }
          html.course-embedded-practice .h5p-interactive-book-chapter:not(.h5p-interactive-book-current) {
            display:none!important;
          }
          html.course-embedded-practice pre,
          html.course-embedded-practice pre code {
            white-space:pre-wrap!important; overflow-wrap:anywhere!important;
          }
          html.course-embedded-practice .h5p-content:fullscreen {
            width:100%!important; height:100vh!important; max-height:100vh!important;
            overflow:auto!important; background:white;
          }
        `;
        doc.head.append(style);
      }
      let pending = 0;
      let root;
      const resize = new ResizeObserver(schedule);
      function schedule() {
        if (!pending) pending = requestAnimationFrame(fit);
      }
      function fit() {
        pending = 0;
        const fullscreen = Boolean(doc.fullscreenElement);
        doc.documentElement.classList.toggle('course-embedded-practice', true);
        for (const button of doc.querySelectorAll('.h5p-interactive-book-status-fullscreen')) {
          const label = fullscreen ? 'Exit fullscreen' : 'Fullscreen';
          if (button.getAttribute('aria-label') !== label) {
            button.setAttribute('aria-label', label);
            button.setAttribute('title', label);
            button.classList.toggle('h5p-interactive-book-enter-fullscreen', !fullscreen);
            button.classList.toggle('h5p-interactive-book-exit-fullscreen', fullscreen);
          }
        }
        const next = doc.querySelector('.h5p-content');
        if (next !== root) {
          resize.disconnect();
          root = next;
          if (root) resize.observe(root);
        }
        if (!root || !root.getBoundingClientRect().height || fullscreen) return;
        // Leave room for the last control's focus outline and the frame border.
        const height = Math.ceil(root.getBoundingClientRect().bottom + view.scrollY + 10);
        if (Math.abs(frame.getBoundingClientRect().height - height) > 1) {
          frame.style.height = height + 'px';
        }
        frame.dataset.contentSized = 'true';
      }
      function clearHint(question) {
        const hint = question?.querySelector('.practice-answer-hint');
        if (hint) hint.remove();
      }
      function checkAnswer(event) {
        const fullscreenButton = event.target.closest?.('.h5p-interactive-book-status-fullscreen');
        if (fullscreenButton) {
          event.preventDefault();
          event.stopImmediatePropagation();
          // The bundled H5P fullscreen handler sets clipping classes before
          // requesting permission and never rolls them back if the API rejects.
          // Use the native promise directly so denial leaves the lesson usable.
          (async () => {
            try {
              if (doc.fullscreenElement) await doc.exitFullscreen();
              else await doc.querySelector('.h5p-content').requestFullscreen();
              doc.querySelector('.practice-fullscreen-hint')?.remove();
            } catch {
              let hint = doc.querySelector('.practice-fullscreen-hint');
              if (!hint) {
                hint = doc.createElement('p');
                hint.className = 'practice-fullscreen-hint';
                hint.setAttribute('role', 'status');
                doc.querySelector('.h5p-content').append(hint);
              }
              hint.textContent = 'Fullscreen is unavailable. You can continue using the practice here.';
            }
            schedule();
          })();
          return;
        }
        const button = event.target.closest?.('.h5p-question-check-answer');
        const question = button?.closest('.h5p-multichoice');
        if (!question || question.querySelector('[aria-checked="true"], input:checked')) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        let hint = question.querySelector('.practice-answer-hint');
        if (!hint) {
          hint = doc.createElement('p');
          hint.className = 'practice-answer-hint';
          hint.setAttribute('role', 'status');
          hint.style.cssText = 'color:#222;font:1rem/1.5 sans-serif;margin:.75rem 0;';
          question.append(hint);
        }
        hint.textContent = 'Choose an answer before checking. Your score has not changed.';
        question.querySelector('[role="radio"], [role="checkbox"]')?.focus();
        schedule();
      }
      function answerChanged(event) {
        const question = event.target.closest?.('.h5p-question');
        if (question?.querySelector('[aria-checked="true"], input:checked')) clearHint(question);
      }
      doc.addEventListener('click', checkAnswer, true);
      doc.addEventListener('click', answerChanged);
      doc.addEventListener('keydown', answerChanged);
      // H5P handles Space/arrow selection during keydown; inspect the updated
      // selection on keyup as well, after its delegated keyboard handler.
      doc.addEventListener('keyup', answerChanged);
      doc.addEventListener('change', answerChanged);
      doc.addEventListener('fullscreenchange', schedule);
      const mutations = new MutationObserver(schedule);
      mutations.observe(doc.body, { childList: true, subtree: true, attributes: true });
      view.addEventListener('resize', schedule);
      doc.fonts?.ready.then(schedule);
      schedule();
      cleanup = () => {
        cancelAnimationFrame(pending);
        mutations.disconnect();
        resize.disconnect();
        view.removeEventListener('resize', schedule);
        doc.removeEventListener('click', checkAnswer, true);
        doc.removeEventListener('click', answerChanged);
        doc.removeEventListener('keydown', answerChanged);
        doc.removeEventListener('keyup', answerChanged);
        doc.removeEventListener('change', answerChanged);
        doc.removeEventListener('fullscreenchange', schedule);
      };
    }
    frame.addEventListener('load', connect);
    connect();
  }
})();
