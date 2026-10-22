document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.nav-links');
  if (toggle && nav) toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  document.querySelectorAll('.flash-close').forEach(button => button.addEventListener('click', () => button.closest('.flash')?.remove()));
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', () => {
      const button = form.querySelector('button[type="submit"]');
      if (button && !button.disabled) { button.dataset.originalText = button.textContent; button.disabled = true; button.textContent = 'Please wait…'; }
    });
  });
  // Re-enable after browser back/forward cache restores a page.
  window.addEventListener('pageshow', () => document.querySelectorAll('button[data-original-text]').forEach(button => { button.disabled = false; button.textContent = button.dataset.originalText; }));
});
