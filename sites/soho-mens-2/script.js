const menu = document.querySelector('#mobile-menu');
const menuButton = document.querySelector('.menu-button');
const closeButton = document.querySelector('.menu-close');

menuButton?.addEventListener('click', () => menu.showModal());
closeButton?.addEventListener('click', () => menu.close());

menu?.addEventListener('click', (event) => {
  if (event.target === menu || event.target.closest('a')) menu.close();
});

const reviewTrack = document.querySelector('.review-track');
document.querySelectorAll('[data-review-direction]').forEach((button) => {
  button.addEventListener('click', () => {
    const card = reviewTrack?.querySelector('.review-card');
    if (!reviewTrack || !card) return;
    const gap = parseFloat(getComputedStyle(reviewTrack).gap) || 0;
    const direction = button.dataset.reviewDirection === 'next' ? 1 : -1;
    const behavior = matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
    reviewTrack.scrollBy({ left: direction * (card.offsetWidth + gap), behavior });
  });
});
