// lucastexr.com, local build. Small, dependency free, every feature optional.
(() => {
  const EMAIL = 'lucastexr@gmail.com';
  const root = document.documentElement;
  const lang = (root.lang || 'en').slice(0, 2);

  // Interface strings in the three site languages. Page copy lives in the HTML.
  const STRINGS = {
    en: {
      locale: 'en-US', menu: 'Menu', close: 'Close', copied: 'Copied', copy: 'Copy', selectToCopy: 'Select to copy',
      copiedStatus: 'Email address copied.', selectStatus: 'Copy did not work here. The address is selected; press Command or Control and C.',
      daypart: (h) => `${h < 5 ? 'Night' : h < 12 ? 'Morning' : h < 18 ? 'Afternoon' : 'Evening'} in Brasília`,
      name: 'Add your name so I know who is writing.',
      email: 'Add an email I can reply to, like you@company.com.',
      message: 'Tell me a little about the project.',
      subject: (n) => `Project inquiry from ${n}`,
      sent: `Your mail app should open with the message ready. If it does not, write to ${EMAIL}.`,
      cvBlocked: `Downloads are blocked in this view. Write to ${EMAIL} and I will send the résumé.`,
      cvSaved: 'Résumé saved.', cvBusy: 'A save prompt is already open.',
      cvFailed: `The download did not start here. Write to ${EMAIL} and I will send the résumé.`,
    },
    pt: {
      locale: 'pt-BR', menu: 'Menu', close: 'Fechar', copied: 'Copiado', copy: 'Copiar', selectToCopy: 'Selecione para copiar',
      copiedStatus: 'Endereço de email copiado.', selectStatus: 'Não deu para copiar aqui. O endereço está selecionado; use Command ou Control e C.',
      daypart: (h) => `${h < 5 ? 'Madrugada' : h < 12 ? 'Manhã' : h < 18 ? 'Tarde' : 'Noite'} em Brasília`,
      name: 'Coloque o seu nome para eu saber quem está escrevendo.',
      email: 'Coloque um email para a resposta, como voce@empresa.com.',
      message: 'Me conte um pouco sobre o projeto.',
      subject: (n) => `Projeto, mensagem de ${n}`,
      sent: `O seu app de email deve abrir com a mensagem pronta. Se não abrir, escreva para ${EMAIL}.`,
      cvBlocked: `Downloads estão bloqueados nesta visualização. Escreva para ${EMAIL} e eu envio o currículo.`,
      cvSaved: 'Currículo salvo.', cvBusy: 'Já existe uma janela de salvamento aberta.',
      cvFailed: `O download não começou aqui. Escreva para ${EMAIL} e eu envio o currículo.`,
    },
    es: {
      locale: 'es-419', menu: 'Menú', close: 'Cerrar', copied: 'Copiado', copy: 'Copiar', selectToCopy: 'Selecciona para copiar',
      copiedStatus: 'Dirección de correo copiada.', selectStatus: 'No se pudo copiar aquí. La dirección está seleccionada; usa Command o Control y C.',
      daypart: (h) => `${h < 5 ? 'Madrugada' : h < 12 ? 'Mañana' : h < 18 ? 'Tarde' : 'Noche'} en Brasilia`,
      name: 'Agrega tu nombre para saber quién escribe.',
      email: 'Agrega un correo para responderte, como tu@empresa.com.',
      message: 'Cuéntame un poco sobre el proyecto.',
      subject: (n) => `Proyecto, mensaje de ${n}`,
      sent: `Tu app de correo debería abrirse con el mensaje listo. Si no se abre, escribe a ${EMAIL}.`,
      cvBlocked: `Las descargas están bloqueadas en esta vista. Escribe a ${EMAIL} y te envío el currículum.`,
      cvSaved: 'Currículum guardado.', cvBusy: 'Ya hay una ventana de guardado abierta.',
      cvFailed: `La descarga no empezó aquí. Escribe a ${EMAIL} y te envío el currículum.`,
    },
  };
  const S = STRINGS[lang] || STRINGS.en;

  // ---------- Tone: the page takes the colors of the section at the middle of the screen ----------
  // Each section and the footer carry data-tone. The CSS registers the color tokens, so a change of
  // tone is a smooth blend of background, text and lines, not a jump.
  const TONES = {
    paper: '#FCFCFC', blush: '#FDF3F6', mist: '#EFF5FD', cream: '#FFF8E2',
    field: '#2C5846', berry: '#8C1F50', cobalt: '#1D4A99',
  };
  const stops = [...document.querySelectorAll('main [data-tone], footer[data-tone]')];
  const themeMeta = document.querySelector('meta[name="theme-color"]');
  const header = document.querySelector('.site-header');
  const setTone = (tone) => {
    if (!tone || root.dataset.tone === tone) return;
    root.dataset.tone = tone;
    if (themeMeta) themeMeta.content = TONES[tone];
  };
  let ticking = false;
  let current = -1;
  const BAND = 32;   // a dead band either side of the line, so a scroll wobble at a boundary cannot flicker the page
  const update = () => {
    ticking = false;
    // The trigger line starts under the header and slides down to mid screen over the first half
    // screen of scroll, so the first section always owns the top of the page, however short it is.
    const line = Math.min(innerHeight * 0.5, (header ? header.offsetHeight : 0) + scrollY);
    const tops = stops.map((el) => el.getBoundingClientRect().top);
    const lastAbove = (y) => { let i = 0; tops.forEach((t, k) => { if (t <= y) i = k; }); return i; };
    if (current < 0) current = lastAbove(line);
    else {
      const down = lastAbove(line - BAND);
      const up = lastAbove(line + BAND);
      if (down > current) current = down;
      else if (up < current) current = up;
    }
    setTone(stops[current].dataset.tone);
    header?.classList.toggle('is-scrolled', scrollY > 8);   // the ibis settles, the nav turns from icons to words
  };
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };
  if (stops.length) {
    update();
    // Only after the first tone is in place does the blend switch on, so arriving mid page does not animate.
    requestAnimationFrame(() => requestAnimationFrame(() => root.classList.add('tone-ready')));
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll, { passive: true });
  }

  // ---------- Language picker: a pill that opens into a panel ----------
  // Hover (mouse), focus or a tap opens it. The highlight springs to the row under the pointer or the
  // focused row, codes roll like split flaps, and a choice folds the panel back into the trigger
  // before the page changes. Escape closes and returns focus; arrows move between languages.
  const picker = document.querySelector('[data-lang-picker]');
  if (picker) {
    const trigger = picker.querySelector('.lang-trigger');
    const panel = picker.querySelector('.lang-panel');
    const blob = picker.querySelector('.lp-blob');
    const rows = [...panel.querySelectorAll('.lp-row')];
    const current = rows.find((r) => r.hasAttribute('aria-current')) || rows[0];
    const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
    let shutTimer = 0;
    let byClick = false;
    panel.inert = true;
    const roll = (el) => { el.classList.remove('is-flapping'); void el.offsetWidth; el.classList.add('is-flapping'); };
    const settle = (el) => setTimeout(() => el.classList.remove('is-flapping'), 650);
    const spring = (row) => {
      if (!row) return;
      blob.style.setProperty('--y', `${row.offsetTop}px`);
      blob.style.setProperty('--h', `${row.offsetHeight}px`);
      blob.classList.add('is-on');
    };
    const open = (how) => {
      clearTimeout(shutTimer);
      if (picker.classList.contains('is-open')) return;
      byClick = how === 'click';
      picker.classList.add('is-open');
      trigger.setAttribute('aria-expanded', 'true');
      panel.inert = false;
      spring(current);
      roll(trigger); settle(trigger);
    };
    const close = (refocus) => {
      clearTimeout(shutTimer);
      picker.classList.remove('is-open');
      trigger.setAttribute('aria-expanded', 'false');
      panel.inert = true;
      blob.classList.remove('is-on');
      if (refocus) trigger.focus();
    };
    const closeSoon = () => { clearTimeout(shutTimer); shutTimer = setTimeout(() => close(false), 240); };

    picker.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse') open('hover'); });
    picker.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse' && !byClick && !picker.contains(document.activeElement)) closeSoon(); });
    trigger.addEventListener('click', () => {
      if (!picker.classList.contains('is-open')) open('click');
      else if (byClick) close(false);
      else byClick = true;   // opened by hover, the click pins it open
    });
    rows.forEach((row) => {
      row.addEventListener('pointermove', () => spring(row));
      row.addEventListener('focus', () => spring(row));
      row.addEventListener('click', (e) => {
        if (row === current) { e.preventDefault(); close(true); return; }
        if (still) return;   // the link navigates at once
        e.preventDefault();
        // fold: the trigger rolls to the chosen code, the panel closes into it, then the page changes
        const code = row.querySelector('.lp-code').innerHTML;
        trigger.querySelector('.lp-code').innerHTML = code;
        close(false);
        roll(trigger);
        setTimeout(() => { window.location.href = row.href; }, 360);
      });
    });
    panel.addEventListener('pointerleave', () => spring(current));
    picker.addEventListener('focusin', () => open('focus'));
    picker.addEventListener('focusout', (e) => { if (!picker.contains(e.relatedTarget)) close(false); });
    picker.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && picker.classList.contains('is-open')) { e.preventDefault(); close(true); return; }
      const step = { ArrowDown: 1, ArrowUp: -1 }[e.key];
      if (!step) return;
      e.preventDefault();
      open('focus');
      const i = rows.indexOf(document.activeElement);
      const next = i < 0 ? (step > 0 ? rows.indexOf(current) : rows.length - 1) : (i + step + rows.length) % rows.length;
      rows[next].focus();
    });
    document.addEventListener('pointerdown', (e) => { if (!picker.contains(e.target)) close(false); });
  }

  // Images the canvas uses but this build does not have yet show a labelled slot.
  const markMissing = (img) => img.closest('.frame')?.classList.add('is-missing');
  document.querySelectorAll('.frame img').forEach((img) => {
    if (img.complete && img.naturalWidth === 0) markMissing(img);
    img.addEventListener('error', () => markMissing(img), { once: true });
  });

  // Phone menu
  const button = document.querySelector('.menu-button');
  const panel = document.getElementById('menu');
  if (button && panel) {
    const behind = [document.querySelector('main'), document.querySelector('.site-footer'), document.querySelector('.skip')].filter(Boolean);
    const setOpen = (open) => {
      document.body.classList.toggle('menu-open', open);
      button.setAttribute('aria-expanded', String(open));
      button.textContent = open ? S.close : S.menu;
      panel.hidden = !open;
      behind.forEach((el) => { el.inert = open; });
      if (open) panel.querySelector('a')?.focus();
    };
    setOpen(false);
    button.addEventListener('click', () => setOpen(button.getAttribute('aria-expanded') !== 'true'));
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') { setOpen(false); button.focus(); }
    });
    matchMedia('(min-width: 1081px)').addEventListener('change', (e) => { if (e.matches) setOpen(false); });
  }

  // Copy email: the address lands on the clipboard, the button says so, then settles back.
  document.querySelectorAll('[data-copy]').forEach((btn) => {
    let timer;
    const status = btn.parentElement.querySelector('[data-copy-status]');
    btn.addEventListener('click', async () => {
      const label = btn.querySelector('.copy-text') || btn;
      try {
        await navigator.clipboard.writeText(btn.dataset.copy);
        label.textContent = S.copied;
        if (status) status.textContent = S.copiedStatus;
      } catch {
        label.textContent = S.selectToCopy;
        const mail = btn.parentElement.querySelector('a[href^="mailto:"]');
        if (mail) getSelection().selectAllChildren(mail);
        if (status) status.textContent = S.selectStatus;
      }
      btn.dataset.state = 'done';
      clearTimeout(timer);
      timer = setTimeout(() => {
        label.textContent = S.copy; delete btn.dataset.state;
        if (status) status.textContent = '';
      }, 2600);
    });
  });

  // Live time in Brasília, so a US team can see where Lucas's day is before writing.
  const clocks = document.querySelectorAll('[data-clock]');
  if (clocks.length) {
    const fmt = new Intl.DateTimeFormat(S.locale, { timeZone: 'America/Sao_Paulo', hour: 'numeric', minute: '2-digit' });
    const iso = new Intl.DateTimeFormat('sv-SE', {
      timeZone: 'America/Sao_Paulo', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit',
    });
    const tick = () => {
      const now = new Date();
      clocks.forEach((el) => {
        el.textContent = fmt.format(now);
        el.setAttribute('datetime', iso.format(now).replace(' ', 'T'));
      });
    };
    tick();
    let id = setInterval(tick, 15000);
    document.addEventListener('visibilitychange', () => {
      clearInterval(id);
      if (!document.hidden) { tick(); id = setInterval(tick, 15000); }
    });
  }

  // Lucas's card on Home: the part of the day in Brasília, and the sun or moon on its arc.
  const daypart = document.querySelector('[data-daypart]');
  const sky = document.querySelector('.sky');
  const sun = sky?.querySelector('[data-sun]');
  if (daypart || sun) {
    const hm = new Intl.DateTimeFormat('en-GB', { timeZone: 'America/Sao_Paulo', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' });
    const place = () => {
      const [h, m] = hm.format(new Date()).split(':').map(Number);
      const hours = h + m / 60;
      if (daypart) daypart.textContent = S.daypart(h);
      if (sun) {
        const day = hours >= 6 && hours < 18;
        const f = day ? (hours - 6) / 12 : ((hours + 6) % 24) / 12;   // 0 at rise, 1 at set
        const x = 60 - 50 * Math.cos(Math.PI * f);
        const y = 44 - 36 * Math.sin(Math.PI * f);
        sun.style.setProperty('--x', `${x.toFixed(1)}px`);
        sun.style.setProperty('--y', `${y.toFixed(1)}px`);
        sky.classList.toggle('is-night', !day);
      }
    };
    place();
    setInterval(() => { if (!document.hidden) place(); }, 60000);
  }

  // ---------- Home showcase: three featured projects from the collection ----------
  // Auto advances every 6 seconds; the bar under each project fills while it is up. Hover or
  // keyboard focus holds it, the button pauses it, arrows and swipes move it. With reduced motion
  // it starts paused. Only the visible slide can be reached; the others are inert.
  const show = document.querySelector('[data-showcase]');
  if (show) {
    const slides = [...show.querySelectorAll('.show-slide')];
    const dots = [...show.querySelectorAll('.show-dot')];
    const toggle = show.querySelector('.show-toggle');
    const area = show.querySelector('.show-slides');
    let index = 0;
    let playing = !matchMedia('(prefers-reduced-motion: reduce)').matches;
    const restart = () => {
      show.classList.remove('is-playing');
      void show.offsetWidth;   // restart the fill animation from zero
      show.classList.toggle('is-playing', playing);
      area.setAttribute('aria-live', playing ? 'off' : 'polite');
    };
    const go = (i) => {
      index = (i + slides.length) % slides.length;
      slides.forEach((el, k) => { el.classList.toggle('is-active', k === index); el.inert = k !== index; });
      dots.forEach((d, k) => (k === index ? d.setAttribute('aria-current', 'true') : d.removeAttribute('aria-current')));
      restart();
    };
    const setPlaying = (on) => {
      playing = on;
      toggle.classList.toggle('is-paused', !on);
      toggle.setAttribute('aria-label', on ? toggle.dataset.labelPause : toggle.dataset.labelPlay);
      restart();
    };
    show.addEventListener('animationend', (e) => { if (e.animationName === 'show-fill' && playing) go(index + 1); });
    dots.forEach((d, k) => d.addEventListener('click', () => go(k)));
    show.querySelector('.show-dots').addEventListener('keydown', (e) => {
      const step = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
      if (!step) return;
      e.preventDefault();
      go(index + step);
      dots[index].focus();
    });
    toggle.addEventListener('click', () => setPlaying(!playing));
    const hold = (on) => show.classList.toggle('is-held', on);
    show.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse') hold(true); });
    show.addEventListener('pointerleave', () => { if (!show.contains(document.activeElement)) hold(false); });
    show.addEventListener('focusin', () => hold(true));
    show.addEventListener('focusout', (e) => { if (!show.contains(e.relatedTarget)) hold(false); });
    let x0 = null;
    area.addEventListener('pointerdown', (e) => { if (e.pointerType !== 'mouse') x0 = e.clientX; });
    area.addEventListener('pointerup', (e) => {
      if (x0 === null) return;
      const dx = e.clientX - x0;
      x0 = null;
      if (Math.abs(dx) > 40) go(index + (dx < 0 ? 1 : -1));
    });
    setPlaying(playing);
  }

  // The tools marquee: hover holds it in CSS; this button stops it for good (WCAG 2.2.2).
  document.querySelectorAll('.tools-toggle').forEach((btn) => {
    const strip = btn.closest('.tools')?.querySelector('[data-marquee]');
    btn.addEventListener('click', () => {
      const paused = strip.classList.toggle('is-paused');
      btn.classList.toggle('is-paused', paused);
      btn.setAttribute('aria-label', paused ? btn.dataset.labelPlay : btn.dataset.labelPause);
    });
  });

  // Figures that rise once when they come into view (the cost curve on Process).
  document.querySelectorAll('[data-rise]').forEach((el) => {
    if (!('IntersectionObserver' in window)) { el.classList.add('is-in'); return; }
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) { el.classList.add('is-in'); io.disconnect(); }
    }, { threshold: 0.4 });
    io.observe(el);
  });

  // Process: the step rail follows the reader through the three documents. The current document is
  // marked for assistive tech too (aria-current="step"), and each step's line fills as it is read.
  const steps = [...document.querySelectorAll('[data-step]')];
  const docs = [...document.querySelectorAll('[data-doc]')];
  if (steps.length && docs.length) {
    let tick = false;
    const follow = () => {
      tick = false;
      const line = innerHeight * 0.4;
      let current = -1;
      docs.forEach((doc, i) => {
        const r = doc.getBoundingClientRect();
        const p = Math.min(1, Math.max(0, (line - r.top) / r.height));
        steps[i].style.setProperty('--p', p.toFixed(3));
        if (r.top <= line) current = i;
      });
      steps.forEach((a, i) => (i === current ? a.setAttribute('aria-current', 'step') : a.removeAttribute('aria-current')));
    };
    addEventListener('scroll', () => { if (!tick) { tick = true; requestAnimationFrame(follow); } }, { passive: true });
    addEventListener('resize', follow, { passive: true });
    follow();
  }

  // The GitHub bars rise once, the first time the chart comes into view.
  // The grain: still by default, it flickers like static while the page moves (scrolling) and for a
  // moment after arrival, so nothing moves on its own for more than a few seconds (WCAG 2.2.2).
  const noise = document.querySelector('.noise');
  if (noise && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    let rest = 0;
    const live = (ms) => { noise.classList.add('is-live'); clearTimeout(rest); rest = setTimeout(() => noise.classList.remove('is-live'), ms); };
    live(3000);
    addEventListener('scroll', () => live(420), { passive: true });
  }

  // Blocos pop in tile by tile, like pixels, the first time they come into view.
  document.querySelectorAll('.bloco').forEach((b) => {
    if (!('IntersectionObserver' in window)) { b.classList.add('is-in'); return; }
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) { b.classList.add('is-in'); io.disconnect(); }
    }, { threshold: 0.5 });
    io.observe(b);
  });

  document.querySelectorAll('.gh-chart').forEach((chart) => {
    if (!('IntersectionObserver' in window)) { chart.classList.add('is-in'); return; }
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) { chart.classList.add('is-in'); io.disconnect(); }
    }, { threshold: 0.35 });
    io.observe(chart);
  });

  // Contact form: no backend, so it opens the visitor's mail app with the message filled in.
  const form = document.getElementById('contact-form');
  if (form) {
    const note = form.querySelector('.form-note');
    const fields = { name: form.elements.name, email: form.elements.email, message: form.elements.message };
    const check = (key) => {
      const input = fields[key];
      const error = document.getElementById(`${key}-error`);
      const ok = input.value.trim() !== '' && input.checkValidity();
      input.setAttribute('aria-invalid', String(!ok));
      error.textContent = ok ? '' : S[key];
      return ok;
    };
    Object.keys(fields).forEach((key) => {
      fields[key].addEventListener('blur', () => { if (fields[key].value) check(key); });
      fields[key].addEventListener('input', () => {
        if (fields[key].getAttribute('aria-invalid') === 'true') check(key);
      });
    });
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const results = Object.keys(fields).map(check);
      if (results.includes(false)) {
        Object.values(fields).find((f) => f.getAttribute('aria-invalid') === 'true')?.focus();
        return;
      }
      const subject = S.subject(fields.name.value.trim());
      const body = `${fields.message.value.trim()}\n\n${fields.name.value.trim()}\n${fields.email.value.trim()}`;
      window.location.href = `mailto:${EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      note.dataset.state = 'sent';
      note.textContent = S.sent;
    });
  }

  // Résumé download. A plain link on a normal site. Inside a claude.ai artifact the frame blocks
  // links that download, so the page fetches the PDF and asks the viewer to confirm the save.
  const cvLinks = document.querySelectorAll('[data-cv]');
  const cvStatus = document.querySelector('[data-cv-status]');
  if (cvLinks.length && window.claude?.use) {
    window.claude.use('downloads').then((downloads) => {
      cvLinks.forEach((link) => link.addEventListener('click', async (e) => {
        e.preventDefault();
        if (!downloads) {
          if (cvStatus) cvStatus.textContent = S.cvBlocked;
          return;
        }
        try {
          const blob = await (await fetch(link.getAttribute('href'))).blob();
          await downloads.save({ filename: 'Lucas_Teixeira_Resume.pdf', data: blob });
          if (cvStatus) cvStatus.textContent = S.cvSaved;
        } catch (err) {
          if (!cvStatus) return;
          if (err && err.code === 'declined') cvStatus.textContent = '';
          else if (err && err.code === 'rate_limited') cvStatus.textContent = S.cvBusy;
          else cvStatus.textContent = S.cvFailed;
        }
      }));
    });
  }
})();
