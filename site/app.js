// Content is visible by default; only hide it for the reveal animation once this script is running.
document.documentElement.classList.add('js-reveal');

document.addEventListener('DOMContentLoaded', () => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.getElementById('year').textContent = new Date().getFullYear();

  // --- Nav: background on scroll, mobile menu, active link ---
  const nav = document.getElementById('nav');
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 10);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  const menuBtn = document.getElementById('menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  const setMenu = (open) => {
    mobileMenu.classList.toggle('hidden', !open);
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.querySelector('span').textContent = open ? 'close' : 'menu';
  };
  menuBtn.addEventListener('click', () => setMenu(mobileMenu.classList.contains('hidden')));
  mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenu(false)));

  const navLinks = document.querySelectorAll('.nav-link');
  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      navLinks.forEach(l => l.classList.toggle('active', l.getAttribute('href') === `#${entry.target.id}`));
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  ['work', 'about', 'services', 'contact'].forEach(id => sectionObserver.observe(document.getElementById(id)));

  // --- Scroll reveal ---
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

  // --- Stat counters ---
  const animateCounter = (el) => {
    const target = Number(el.dataset.target);
    if (reducedMotion) { el.textContent = target; return; }
    const duration = 1400;
    const start = performance.now();
    const tick = (now) => {
      const p = Math.min((now - start) / duration, 1);
      el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        counterObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });
  document.querySelectorAll('.counter').forEach(el => counterObserver.observe(el));

  // --- Project filters ---
  const filterBtns = document.querySelectorAll('.filter-btn');
  const projectCards = document.querySelectorAll('.project-card');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;
      filterBtns.forEach(b => {
        b.classList.toggle('active', b === btn);
        b.setAttribute('aria-pressed', String(b === btn));
      });
      projectCards.forEach(card => {
        const show = filter === 'all' || card.dataset.category === filter;
        card.classList.toggle('hidden-card', !show);
        if (show) card.classList.add('visible');
      });
    });
  });

  // --- Lightbox ---
  const lightbox = document.getElementById('lightbox');
  const lightboxContent = document.getElementById('lightbox-content');
  const lightboxClose = document.getElementById('lightbox-close');
  const lightboxScroll = document.getElementById('lightbox-scroll');
  const lightboxFocusables = [lightboxScroll, lightboxClose];
  const background = [...document.body.children].filter(el => el !== lightbox && el.tagName !== 'SCRIPT');
  let lastFocused = null;

  const setBackgroundInert = (inert) => background.forEach(el => { el.inert = inert; });

  const openLightbox = (phone) => {
    lastFocused = phone;
    const clone = phone.cloneNode(true);
    clone.removeAttribute('role');
    clone.removeAttribute('tabindex');
    clone.removeAttribute('aria-label');
    lightboxContent.replaceChildren(clone);
    lightbox.setAttribute('aria-label', `${phone.dataset.screen} screen preview`);
    lightbox.classList.add('open');
    lightboxScroll.scrollTop = 0;
    document.body.style.overflow = 'hidden';
    setBackgroundInert(true);
    lightboxClose.focus();
  };
  const closeLightbox = () => {
    lightbox.classList.remove('open');
    lightboxContent.replaceChildren();
    document.body.style.overflow = '';
    setBackgroundInert(false);
    if (lastFocused) lastFocused.focus();
  };

  document.querySelectorAll('.phone').forEach(phone => {
    phone.addEventListener('click', () => openLightbox(phone));
    phone.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openLightbox(phone);
      }
    });
  });
  lightboxClose.addEventListener('click', closeLightbox);
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox || e.target === lightboxScroll) closeLightbox();
  });
  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('open')) return;
    if (e.key === 'Escape') {
      closeLightbox();
    } else if (e.key === 'Tab') {
      e.preventDefault();
      const i = lightboxFocusables.indexOf(document.activeElement);
      const next = (i + (e.shiftKey ? -1 : 1) + lightboxFocusables.length) % lightboxFocusables.length;
      lightboxFocusables[i === -1 ? 0 : next].focus();
    }
  });

  // --- Contact form ---
  const form = document.getElementById('contact-form');
  const toast = document.getElementById('toast');
  const toastText = document.getElementById('toast-text');
  let toastTimer;

  const showToast = (msg) => {
    toastText.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 3500);
  };

  const validators = {
    name: v => v.trim().length > 0,
    email: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim()),
    message: v => v.trim().length >= 10,
  };

  // The error is only referenced while shown, so screen readers don't announce it for a valid field.
  const setInvalid = (field, invalid) => {
    field.classList.toggle('invalid', invalid);
    if (invalid) {
      field.setAttribute('aria-invalid', 'true');
      field.setAttribute('aria-describedby', `${field.name}-error`);
    } else {
      field.removeAttribute('aria-invalid');
      field.removeAttribute('aria-describedby');
    }
  };

  form.querySelectorAll('.field').forEach(field => {
    field.addEventListener('input', () => {
      if (field.classList.contains('invalid') && validators[field.name](field.value)) {
        setInvalid(field, false);
      }
    });
  });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    let firstInvalid = null;
    Object.entries(validators).forEach(([name, isValid]) => {
      const field = form.elements[name];
      const ok = isValid(field.value);
      setInvalid(field, !ok);
      if (!ok && !firstInvalid) firstInvalid = field;
    });
    if (firstInvalid) {
      firstInvalid.focus();
      return;
    }
    const firstName = form.elements.name.value.trim().split(/\s+/)[0];
    showToast(`Thanks, ${firstName}! I'll be in touch soon.`);
    form.reset();
  });
});
