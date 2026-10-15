// A progressively enhanced disclosure: navigation remains visible without JS.
document.documentElement.classList.add('js');
const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('#navigation');
function setMenu(open, returnFocus = false) {
  toggle.setAttribute('aria-expanded', String(open));
  toggle.querySelector('.menu-label').textContent = open ? 'Close' : 'Menu';
  toggle.querySelector('.menu-icon').textContent = open ? '×' : '☰';
  nav.classList.toggle('open', open);
  if (returnFocus) toggle.focus();
}
toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
nav.addEventListener('click', event => { if (event.target.closest('a')) setMenu(false); });
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') setMenu(false, true);
});
document.addEventListener('click', event => {
  if (!event.target.closest('.header')) setMenu(false);
});
matchMedia('(min-width: 761px)').addEventListener('change', () => setMenu(false));
