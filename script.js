const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('.primary-nav');
const header = document.querySelector('.site-header');
const servicesMenu = document.querySelector('.nav-services');
const servicesButton = document.querySelector('.nav-services-toggle');

function updateHeader() {
  header.classList.toggle('is-scrolled', window.scrollY > 40);
}

window.addEventListener('scroll', updateHeader, { passive: true });
updateHeader();

function closeMenu() {
  menuButton.setAttribute('aria-expanded', 'false');
  menuButton.setAttribute('aria-label', 'Open menu');
  navigation.classList.remove('open');
  document.body.classList.remove('menu-open');
  closeServicesMenu();
}

function closeServicesMenu() {
  servicesMenu.classList.remove('open');
  servicesButton.setAttribute('aria-expanded', 'false');
  servicesButton.setAttribute('aria-label', 'Show service links');
}

function openServicesMenu() {
  servicesMenu.classList.add('open');
  servicesButton.setAttribute('aria-expanded', 'true');
  servicesButton.setAttribute('aria-label', 'Hide service links');
}

servicesButton.addEventListener('click', () => {
  if (window.matchMedia('(min-width: 761px)').matches) {
    openServicesMenu();
    return;
  }
  if (servicesMenu.classList.contains('open')) closeServicesMenu();
  else openServicesMenu();
});

servicesMenu.addEventListener('mouseenter', () => {
  if (window.matchMedia('(min-width: 761px)').matches) openServicesMenu();
});
servicesMenu.addEventListener('mouseleave', () => {
  if (window.matchMedia('(min-width: 761px)').matches && !servicesMenu.contains(document.activeElement)) closeServicesMenu();
});
servicesMenu.addEventListener('focusin', () => {
  if (window.matchMedia('(min-width: 761px)').matches) openServicesMenu();
});
servicesMenu.addEventListener('focusout', () => {
  window.setTimeout(() => {
    if (!servicesMenu.contains(document.activeElement) && !servicesMenu.matches(':hover')) closeServicesMenu();
  }, 0);
});
document.addEventListener('pointerdown', event => {
  if (!servicesMenu.contains(event.target)) closeServicesMenu();
});

menuButton.addEventListener('click', () => {
  const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-expanded', String(!isOpen));
  menuButton.setAttribute('aria-label', isOpen ? 'Open menu' : 'Close menu');
  navigation.classList.toggle('open', !isOpen);
  document.body.classList.toggle('menu-open', !isOpen);
});

navigation.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') {
    const wasOpen = servicesMenu.classList.contains('open');
    closeMenu();
    if (wasOpen) {
      servicesButton.focus({ preventScroll: true });
      closeServicesMenu();
    }
  }
});

document.querySelector('#year').textContent = new Date().getFullYear();

const numbersCard = document.querySelector('.tga-numbers-card');
if (numbersCard && 'IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const counters = [...numbersCard.querySelectorAll('[data-count]')];
  const observer = new IntersectionObserver(entries => {
    if (!entries.some(entry => entry.intersectionRatio >= 0.8)) return;
    observer.disconnect();

    const start = performance.now();
    const duration = 1200;
    const update = now => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      counters.forEach(counter => {
        const target = Number(counter.dataset.count);
        const suffix = progress === 1 ? (counter.dataset.suffix || '') : '';
        counter.textContent = Math.round(target * eased) + suffix;
      });
      if (progress < 1) requestAnimationFrame(update);
    };

    counters.forEach(counter => { counter.textContent = '0'; });
    requestAnimationFrame(update);
  }, { threshold: 0.8 });
  observer.observe(numbersCard);
}

// Reveal content as it enters view without hiding it when motion is reduced.
if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const textBlocks = [...document.querySelectorAll('main h1, main h2, main h3, main h4, main p, main li, main blockquote, main dt, main dd, main figcaption')]
    .filter(element => element.getClientRects().length && !element.closest('details:not([open])'));
  const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      revealObserver.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.01 });

  textBlocks.forEach(element => {
    if (element.getBoundingClientRect().top < window.innerHeight * 0.92) return;
    element.classList.add('scroll-reveal');
    revealObserver.observe(element);
  });
  document.documentElement.classList.add('reveal-ready');
}
