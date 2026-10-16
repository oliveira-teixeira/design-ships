// About: the Claude Code and GitHub cards. The page ships with the snapshots it was built with; this
// swaps in the latest ones from the repository (refreshed twice a day by scripts/refresh_stats.sh),
// so the numbers stay current between deploys. It mirrors stats_pair() in build.py. If the fetch
// fails, or nothing changed, the built numbers stay as they are.
(() => {
  const pair = document.querySelector('[data-stats]');
  if (!pair || !window.fetch) return;
  let cfg;
  try { cfg = JSON.parse(pair.dataset.stats); } catch (err) { return; }
  const t = cfg.t;

  const fill = (tpl, vals) => tpl.replace(/\{(\w+)\}/g, (m, k) => (k in vals ? vals[k] : m));
  const parts = (iso) => iso.split('-').map(Number);
  const fmtDate = (iso) => { const [y, m, d] = parts(iso); return fill(t.date, { d, month: t.months[m - 1], y }); };
  const shortDate = (iso) => { const [, m, d] = parts(iso); return `${d} ${t.months_short[m - 1]}`; };
  const monthYear = (iso) => { const [y, m] = parts(iso); return `${t.months_short[m - 1]} ${y}`; };
  const num = (n) => Number(n).toLocaleString('en-US').replace(/,/g, cfg.sep);
  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');

  // Bars relative to the peak, the peak labelled on the side with room, a title on each bar
  const bars = (ol, series, key, dateKey, peakTpl, tipTpl) => {
    const peak = Math.max(...series.map((x) => x[key])) || 1;
    const peakI = series.findIndex((x) => x[key] === peak);
    const side = peakI < series.length * 0.4 ? ' data-side="start"' : '';
    ol.style.setProperty('--n', series.length);
    ol.innerHTML = series.map((x, i) => {
      const n = x[key];
      const zero = n === 0 ? ' class="is-zero"' : '';
      const peakAttr = i === peakI ? ` data-peak="${esc(fill(peakTpl, { n }))}"${side}` : '';
      return `<li style="--h:${(n / peak).toFixed(3)};--i:${i}"${zero} title="${esc(fill(tipTpl, { date: fmtDate(x[dateKey]), n }))}"${peakAttr}></li>`;
    }).join('');
    return { peak, peakI };
  };
  const figs = (card, values) => card.querySelectorAll('.sc-figs dt').forEach((dt, i) => { if (i < values.length) dt.textContent = values[i]; });
  const axis = (card, a, b) => { const s = card.querySelectorAll('.sc-axis span'); if (s.length === 2) { s[0].textContent = a; s[1].textContent = b; } };

  const claude = (cc) => {
    const card = pair.querySelector('.sc--cc');
    if (!card || !cc.daily || !cc.daily.length) return;
    figs(card, [num(cc.actions), cc.sessions, cc.active_days]);
    const span = card.querySelector('.sc-span');
    if (span) span.textContent = fill(t.cc_span, { start: shortDate(cc.from) });
    const ol = card.querySelector('.gh-bars');
    const { peak, peakI } = bars(ol, cc.daily, 'actions', 'date', t.cc_peak, t.cc_day_title);
    ol.setAttribute('aria-label', fill(t.cc_chart_label, { start: fmtDate(cc.from), end: fmtDate(cc.to), peak_day: fmtDate(cc.daily[peakI].date), peak }));
    axis(card, shortDate(cc.from), shortDate(cc.to));
    const named = cc.tools.slice(0, cfg.top).map((x) => [t.cc_tool_names[x.name] || x.name, x.actions]);
    named.push([t.cc_other, cc.actions - cc.tools.slice(0, cfg.top).reduce((a, x) => a + x.actions, 0)]);
    const bar = card.querySelector('.sc-split-bar');
    const list = card.querySelector('.sc-split ol');
    if (bar) bar.innerHTML = named.map(([, n], k) => `<span style="--w:${(n / cc.actions).toFixed(4)}" data-k="${k}"></span>`).join('');
    if (list) list.innerHTML = named.map(([name, n], k) => `<li style="--w:${(n / cc.actions).toFixed(4)}" data-k="${k}"><span class="sc-key" aria-hidden="true"></span>${esc(name)} <span class="num">${Math.round((100 * n) / cc.actions)}%</span></li>`).join('');
    const when = pair.parentNode.querySelector('[data-stats-date]');
    if (when) { when.textContent = fmtDate(cc.to); when.setAttribute('datetime', cc.to); }
  };

  const github = (gh) => {
    const card = pair.querySelector('.sc--gh');
    if (!card || !gh.weeks || !gh.weeks.length) return;
    figs(card, [num(gh.commits), num(gh.pull_requests)]);
    const ol = card.querySelector('.gh-bars');
    const { peak, peakI } = bars(ol, gh.weeks, 'commits', 'start', t.gh_peak, t.gh_week_title);
    ol.setAttribute('aria-label', fill(t.gh_chart_label, { start: fmtDate(gh.from), end: fmtDate(gh.to), peak_week: fmtDate(gh.weeks[peakI].start), peak }));
    axis(card, monthYear(gh.from), monthYear(gh.to));
  };

  const load = (url) => fetch(url, { cache: 'no-cache' }).then((r) => (r.ok ? r.json() : null)).catch(() => null);
  // Only a later snapshot replaces the built one, so a page built ahead of main never steps back
  const fresh = (snap, built, total) => snap && (snap.to > built[0] || (snap.to === built[0] && snap[total] !== built[1]));
  load(cfg.src.cc).then((cc) => { if (fresh(cc, cfg.built.cc, 'actions')) claude(cc); });
  load(cfg.src.gh).then((gh) => { if (fresh(gh, cfg.built.gh, 'commits')) github(gh); });
})();
