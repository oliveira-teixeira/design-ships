// The tile wall on the About page. Tiles after Athos Bulcão; each one turns in quarter steps.
// The page ships with the wall already spelling LUCAS, so it reads without script.
(() => {
  const wall = document.querySelector('[data-wall]');
  if (!wall) return;
  const tiles = [...wall.querySelectorAll('.tile')];
  const status = document.querySelector('[data-wall-status]');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const MSG = {
    en: { scrambled: 'Scrambled. Turn the tiles back, or spell the name.', spelled: 'The wall spells LUCAS.', byHand: 'You spelled LUCAS by hand.' },
    pt: { scrambled: 'Embaralhado. Gire os azulejos de volta ou escreva o nome.', spelled: 'A parede escreve LUCAS.', byHand: 'Você escreveu LUCAS com as próprias mãos.' },
    es: { scrambled: 'Mezclado. Gira los azulejos de vuelta o escribe el nombre.', spelled: 'El muro escribe LUCAS.', byHand: 'Escribiste LUCAS con tus propias manos.' },
  }[(document.documentElement.lang || 'en').slice(0, 2)] || null;
  const M = MSG || { scrambled: 'Scrambled. Turn the tiles back, or spell the name.', spelled: 'The wall spells LUCAS.', byHand: 'You spelled LUCAS by hand.' };

  // Each tile keeps a running count of quarter turns so it always turns clockwise.
  const states = tiles.map((el) => ({
    el,
    svg: el.querySelector('svg'),
    turns: Number(el.dataset.target),
    target: Number(el.dataset.target),
    period: Number(el.dataset.period), // 4 for arcs and tees, 2 for straights
    letter: el.dataset.letter === '1',
  }));

  const set = (s, turns) => { s.turns = turns; s.svg.style.setProperty('--turns', turns); };
  const isHome = (s) => ((s.turns - s.target) % s.period + s.period) % s.period === 0;
  const spelled = () => states.every((s) => !s.letter || isHome(s));
  const say = (text) => { if (status) status.textContent = text; };

  let manual = false;

  const scramble = (animate = true) => {
    manual = false;
    wall.classList.add('is-scrambled');
    states.forEach((s, i) => {
      const step = 1 + Math.floor(Math.random() * (s.period - 1)) + (s.period === 4 && Math.random() < 0.3 ? 1 : 0);
      const apply = () => set(s, s.turns + Math.min(step, s.period - 1));
      if (animate && !reduce) setTimeout(apply, (i % 16) * 12); else apply();
    });
    say(M.scrambled);
  };

  const spell = () => {
    manual = false;
    wall.classList.remove('is-scrambled');
    states.forEach((s, i) => {
      const col = i % 16;
      const rest = ((s.target - s.turns) % s.period + s.period) % s.period;
      const apply = () => set(s, s.turns + rest);
      if (reduce) apply(); else setTimeout(apply, col * 45 + Math.floor(i / 16) * 20);
    });
    say(M.spelled);
  };

  // Turning single tiles by pointer is offered only where a tile is at least 44px wide (WCAG 2.5.5).
  // Everywhere else the two buttons do the work.
  const sizeCheck = () => {
    const w = tiles[0].getBoundingClientRect().width;
    wall.classList.toggle('can-turn', w >= 44);
    document.querySelector('[data-wall-hint]')?.toggleAttribute('hidden', w < 44);
  };
  sizeCheck();
  addEventListener('resize', sizeCheck, { passive: true });

  wall.addEventListener('click', (e) => {
    if (!wall.classList.contains('can-turn')) return;
    const el = e.target.closest('.tile');
    if (!el) return;
    const s = states[tiles.indexOf(el)];
    manual = true;
    set(s, s.turns + 1);
    if (wall.classList.contains('is-scrambled') && spelled()) {
      wall.classList.remove('is-scrambled');
      say(M.byHand);
    } else if (!wall.classList.contains('is-scrambled') && !spelled()) {
      wall.classList.add('is-scrambled');
      say('');
    }
  });

  document.querySelector('[data-wall-scramble]')?.addEventListener('click', () => scramble(true));
  document.querySelector('[data-wall-spell]')?.addEventListener('click', spell);

  // On arrival: scramble without motion, then let the wall turn itself into the name once.
  if (!reduce) {
    scramble(false);
    say('');
    requestAnimationFrame(() => setTimeout(() => { if (!manual) spell(); }, 650));
  }
})();
