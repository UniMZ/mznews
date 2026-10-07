const input = document.querySelector('#query');
const cards = [...document.querySelectorAll('[data-search]')];
const status = document.querySelector('#search-status');
function filter(value) {
  const query = value.trim().toLocaleLowerCase();
  let count = 0;
  cards.forEach(card => {
    const match = card.dataset.search.includes(query);
    card.hidden = !match;
    if (match) count++;
  });
  status.textContent = `${count} ${count === 1 ? 'post' : 'posts'} found`;
}
function restore() { input.value = new URL(location.href).searchParams.get('q') || ''; filter(input.value); }
input.addEventListener('input', () => {
  const url = new URL(location.href);
  if (input.value) url.searchParams.set('q', input.value); else url.searchParams.delete('q');
  history.replaceState(null, '', url);
  filter(input.value);
});
window.addEventListener('popstate', restore);
window.addEventListener('pageshow', restore);
restore();
