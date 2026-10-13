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
