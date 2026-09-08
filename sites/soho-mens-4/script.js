(() => {
  const menuButton = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.primary-nav');

  if (menuButton && nav) {
    const closeMenu = () => {
      menuButton.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('menu-open');
    };

    menuButton.addEventListener('click', () => {
      const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
      menuButton.setAttribute('aria-expanded', String(!isOpen));
      document.body.classList.toggle('menu-open', !isOpen);
      if (!isOpen) nav.querySelector('a')?.focus();
    });

    nav.addEventListener('click', event => {
      if (event.target.closest('a')) closeMenu();
    });

    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') {
        closeMenu();
        menuButton.focus();
      }
    });
  }

  const concierge = document.querySelector('#concierge-form');
  if (concierge) {
    const select = concierge.querySelector('select');
    const message = concierge.querySelector('.field-message');
    const button = concierge.querySelector('button[type="submit"]');
    const defaultLabel = button.innerHTML;

    select.addEventListener('change', () => {
      select.removeAttribute('aria-invalid');
      message.textContent = '';
    });

    concierge.addEventListener('submit', event => {
      event.preventDefault();
      if (!select.value) {
        select.setAttribute('aria-invalid', 'true');
        message.textContent = 'Please choose a Manhattan location.';
        select.focus();
        return;
      }

      button.disabled = true;
      button.textContent = 'Opening the appointment request…';
      window.setTimeout(() => {
        window.location.href = 'https://sohomenshealth.com/appointments/';
        button.disabled = false;
        button.innerHTML = defaultLabel;
      }, 550);
    });
  }

  const search = document.querySelector('#service-search');
  const directory = document.querySelector('#service-directory');
  if (search && directory) {
    const rooms = [...directory.querySelectorAll('.directory-room')];
    const chips = [...document.querySelectorAll('.filter-chip')];
    const count = document.querySelector('#result-count');
    const empty = document.querySelector('#empty-state');
    const clear = document.querySelector('#clear-search');
    const reset = document.querySelector('#reset-directory');
    let activeFilter = 'all';

    const update = () => {
      const query = search.value.trim().toLowerCase();
      let visibleRooms = 0;
      let visibleServices = 0;

      rooms.forEach(room => {
        const inCategory = activeFilter === 'all' || room.dataset.category === activeFilter;
        const items = [...room.querySelectorAll('li')];
        let roomMatches = false;

        items.forEach(item => {
          const matches = !query || item.textContent.toLowerCase().includes(query);
          item.hidden = query ? !matches : false;
          if (matches) {
            roomMatches = true;
            visibleServices += inCategory ? 1 : 0;
          }
        });

        if (!items.length) roomMatches = !query || room.textContent.toLowerCase().includes(query);
        const show = inCategory && roomMatches;
        room.hidden = !show;
        if (show) visibleRooms += 1;
      });

      empty.hidden = visibleRooms > 0;
      count.textContent = query || activeFilter !== 'all'
        ? `${visibleServices || visibleRooms} matching ${visibleServices === 1 ? 'service' : 'services'}`
        : 'Showing all services';
    };

    chips.forEach(chip => chip.addEventListener('click', () => {
      activeFilter = chip.dataset.filter;
      chips.forEach(item => {
        const active = item === chip;
        item.classList.toggle('is-active', active);
        item.setAttribute('aria-pressed', String(active));
      });
      update();
    }));

    search.addEventListener('input', update);
    clear.addEventListener('click', () => { search.value = ''; search.focus(); update(); });
    reset.addEventListener('click', () => {
      search.value = '';
      activeFilter = 'all';
      chips.forEach((chip, index) => { chip.classList.toggle('is-active', index === 0); chip.setAttribute('aria-pressed', String(index === 0)); });
      update();
      search.focus();
    });
  }

  const year = document.querySelector('#year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
