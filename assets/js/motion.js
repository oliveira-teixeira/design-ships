// lucastexr.com: the two authored motions, both on GSAP (loaded from cdnjs before this file).
//  1. The footer badge assembles as it scrolls into view, then answers a hover.
//  2. A ribbon of Athos Bulcão tiles at the foot of each page's opening section, and the tile
//     blocos at the end of other sections: a small extra, not the main thing. Tiles settle into
//     their pattern on arrival, turn under the pointer, ripple on a tap, and drift back home.
// Without GSAP, or with reduced motion, both show finished and still. Nothing here is needed
// to read or use the page.
(() => {
  const gsap = window.gsap;
  if (!gsap) return;
  if (window.ScrollTrigger) gsap.registerPlugin(window.ScrollTrigger);
  const mm = gsap.matchMedia();

  // ---------------------------------------------------------------- 1. Footer badge
  const badge = document.querySelector('.badge');
  if (badge && window.ScrollTrigger) {
    mm.add('(prefers-reduced-motion: no-preference)', () => {
      const strokes = [...badge.querySelectorAll('.b-s')];   // the monogram and the 95
      const letters = [...badge.querySelectorAll('.b-l')];   // LATIN AMERICA, AUTHENTIC DESIGNS
      const byDelay = (a, b) => parseFloat(a.style.getPropertyValue('--d')) - parseFloat(b.style.getPropertyValue('--d'));
      strokes.sort(byDelay);
      letters.sort(byDelay);

      gsap.set(strokes, {
        attr: { 'stroke-dasharray': 1, 'stroke-dashoffset': 1, 'vector-effect': 'non-scaling-stroke' },
        stroke: 'currentColor', strokeWidth: 1.25, fillOpacity: 0,
      });
      gsap.set(letters, { opacity: 0, y: 10, scale: 0.9, transformOrigin: '50% 50%' });

      const tl = gsap.timeline({
        defaults: { ease: 'none' },
        scrollTrigger: { trigger: badge, start: 'top 95%', end: 'bottom 96%', scrub: 0.8 },
      });
      tl.to(strokes, { attr: { 'stroke-dashoffset': 0 }, duration: 1, stagger: 0.12, ease: 'power2.inOut' })
        .to(strokes, { fillOpacity: 1, strokeOpacity: 0, duration: 0.5, stagger: 0.06, ease: 'power1.out' }, '-=0.45')
        .to(letters, { opacity: 1, y: 0, scale: 1, duration: 0.5, stagger: { each: 0.03, from: 'center' }, ease: 'back.out(2)' }, '-=0.6');

      // Once it is built, the badge answers a hover: the lettering lifts in a wave.
      let busy = false;
      const wave = () => {
        if (busy || tl.progress() < 0.999) return;
        busy = true;
        gsap.timeline({ onComplete: () => { busy = false; } })
          .to(letters, { y: -5, duration: 0.22, ease: 'power2.out', stagger: { each: 0.018, from: 'start' } })
          .to(letters, { y: 0, duration: 0.5, ease: 'elastic.out(1, 0.45)', stagger: { each: 0.018, from: 'start' } }, 0.16);
      };
      badge.addEventListener('pointerenter', wave);
      return () => badge.removeEventListener('pointerenter', wave);
    });
  }

  // ---------------------------------------------------------------- 2. Tile ribbons
  document.querySelectorAll('[data-ribbon]').forEach((ribbon) => {
    const tiles = [...ribbon.querySelectorAll('.rt')].map((el) => ({
      el,
      svg: el.querySelector('svg'),
      home: Number(el.dataset.home),          // quarter turns that make the pattern
      turns: Number(el.dataset.home),
      row: Number(el.dataset.row),
      col: Number(el.dataset.col),
      hot: false,
    }));
    const at = new Map(tiles.map((t) => [`${t.row}:${t.col}`, t]));
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const D = reduce ? 0 : 1;

    tiles.forEach((t) => gsap.set(t.svg, { rotation: t.turns * 90, transformOrigin: '50% 50%' }));

    const turn = (t, by = 1, delay = 0) => {
      t.turns += by;
      t.el.classList.add('is-hot');
      gsap.to(t.svg, { rotation: t.turns * 90, duration: 0.55 * D, delay: delay * D, ease: 'back.out(1.7)', overwrite: 'auto' });
    };
    // Home is the nearest clockwise turn that restores the pattern, so tiles never spin backwards.
    const settle = (stagger = 0.018) => {
      tiles.forEach((t) => {
        const rest = ((t.home - t.turns) % 4 + 4) % 4;
        t.turns += rest;
        gsap.to(t.svg, {
          rotation: t.turns * 90, duration: 0.7 * D, delay: t.col * stagger * D, ease: 'power3.inOut', overwrite: 'auto',
          onComplete: () => t.el.classList.remove('is-hot'),
        });
      });
    };
    let idle;
    const restLater = (ms = 1800) => { clearTimeout(idle); idle = setTimeout(() => settle(), ms); };

    // Arrival: the ribbon comes in scrambled and turns itself into the pattern, once.
    if (!reduce && 'IntersectionObserver' in window) {
      tiles.forEach((t) => { t.turns = t.home + 1 + Math.floor(Math.random() * 3); gsap.set(t.svg, { rotation: t.turns * 90 }); });
      const io = new IntersectionObserver((entries) => {
        if (!entries.some((e) => e.isIntersecting)) return;
        io.disconnect();
        setTimeout(() => settle(0.028), 200);
      }, { threshold: 0.6 });
      io.observe(ribbon);
    }

    // Pointer: the tile under a mouse turns, its neighbours follow a beat later.
    let last = null;
    ribbon.addEventListener('pointermove', (e) => {
      if (e.pointerType !== 'mouse') return;
      const el = e.target.closest('.rt');
      if (!el || el === last) return;
      last = el;
      const t = tiles.find((x) => x.el === el);
      turn(t);
      [[0, -1], [0, 1], [-1, 0], [1, 0]].forEach(([dr, dc], i) => {
        const n = at.get(`${t.row + dr}:${t.col + dc}`);
        if (n && Math.random() < 0.5) turn(n, 1, 0.07 + i * 0.02);
      });
      restLater();
    });
    ribbon.addEventListener('pointerleave', () => { last = null; restLater(900); });

    // Tap or click: a ripple runs out from the tile in both directions, then everything goes home.
    ribbon.addEventListener('click', (e) => {
      const el = e.target.closest('.rt');
      if (!el) return;
      const t0 = tiles.find((x) => x.el === el);
      tiles.forEach((t) => turn(t, 1, (Math.abs(t.col - t0.col) + Math.abs(t.row - t0.row)) * 0.035));
      restLater(2400);
    });
  });

})();
