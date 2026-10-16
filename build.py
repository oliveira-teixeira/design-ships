#!/usr/bin/env python3
"""Builds the lucastexr.com local site in three languages.

Run:  python3 build.py   (writes the pages: English at the root, pt-br/ and es/ beside it)

Copy lives in locales/en.py, locales/pt.py and locales/es.py, one dictionary per language with the
same keys. This file holds the structure: shared parts (head, header, phone menu, footer, badge),
then one function per page. Every page runs the AIDA funnel (Attention, Interest, Desire, Action)
and every section names a tone; as you scroll, the whole page takes that section's colors.
"""
import json
import random
import re
from datetime import date
from html import escape
from pathlib import Path

from badge_paths import BADGE
from logos import LOGOS, WORKED
from marks import IBIS, IBIS_VB, TEXR, TEXR_VB
from locales import en, es, pt

ROOT = Path(__file__).parent
EMAIL = "lucastexr@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/lucastexr/"
CV = "assets/cv/Lucas_Teixeira_Resume.pdf"

# English is the default and lives at the root. Brazil and Latin America get their own folders.
LANGS = [
    {"code": "en", "html": "en", "dir": "", "short": "EN", "name": "English", "region": "US and international", "full": "English (US and international)", "t": en.T},
    {"code": "pt", "html": "pt-BR", "dir": "pt-br/", "short": "PT", "name": "Português", "region": "Brasil", "full": "Português (Brasil)", "t": pt.T},
    {"code": "es", "html": "es-419", "dir": "es/", "short": "ES", "name": "Español", "region": "Latinoamérica", "full": "Español (Latinoamérica)", "t": es.T},
]

NAV = [("work", "work.html"), ("merch", "merch.html"), ("process", "process.html"), ("writing", "writing.html"), ("photography", "photography.html"),
       ("about", "about.html"), ("contact", "contact.html")]

# Nav icons. Outline when the page is not current; filled when it is. Shapes (class s) take the
# fill, details (class d) turn into knockouts in the page color, so a filled icon keeps its drawing.
NAV_ICONS = {
    "work": '<rect class="s" x="4" y="4" width="7" height="7" rx="1.5"/><rect class="s" x="13" y="4" width="7" height="7" rx="1.5"/>'
            '<rect class="s" x="4" y="13" width="7" height="7" rx="1.5"/><rect class="s" x="13" y="13" width="7" height="7" rx="1.5"/>',
    "process": '<rect class="s" x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect class="s" x="13.5" y="13.5" width="7" height="7" rx="1.5"/>'
               '<path d="M7 10.5v3a3 3 0 0 0 3 3h3.5"/>',
    "writing": '<path class="s" d="M6.5 3h7.5l4 4v13.5a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5V3.5a.5.5 0 0 1 .5-.5Z"/>'
               '<path class="d" d="M14 3v4h4M9 11.5h6M9 15h6M9 18.5h3.5"/>',
    "photography": '<path class="s" d="M3.5 8.5A1.5 1.5 0 0 1 5 7h2.2l1.6-2.2h6.4L16.8 7H19a1.5 1.5 0 0 1 1.5 1.5v9A1.5 1.5 0 0 1 19 19H5a1.5 1.5 0 0 1-1.5-1.5Z"/>'
                   '<circle class="d" cx="12" cy="13" r="3.25"/>',
    "about": '<circle class="s" cx="12" cy="8" r="3.75"/><path class="s" d="M4.75 20.25c.7-3.9 3.6-6 7.25-6s6.55 2.1 7.25 6Z"/>',
    "contact": '<rect class="s" x="3" y="5.5" width="18" height="13" rx="2"/><path class="d" d="m3.75 7.5 8.25 5.75 8.25-5.75"/>',
    "merch": '<path class="s" d="M8.5 3.5 4 5.75 2.75 10l3 1.25V20.5h12.5V11.25l3-1.25L20 5.75 15.5 3.5c-.6 1.5-1.9 2.4-3.5 2.4s-2.9-.9-3.5-2.4Z"/>',
}
# The Lucas Teixeira monogram, seven paths, in the order the mark is built.
LOGO_PATHS = [
    "M156.591 161.886H26.2219V81.1981H0V92.9034H14.5166V161.886H0V173.575H156.591V161.886Z",
    "M78.9944 58.9876C85.8171 60.1055 96.4867 62.3742 108.932 66.7637L109.392 66.9281C124.961 72.4027 141.253 75.477 157.792 76.0688V123.498H169.497V76.0688C186.068 75.477 202.361 72.4027 217.913 66.9281L218.373 66.7637C230.802 62.3742 241.471 60.1055 248.294 58.9876V72.6657H259.999V45.9342L253.637 46.4603C251.862 46.6247 235.602 48.2687 214.477 55.7325L214 55.8969C197.84 61.5851 180.906 64.4621 163.644 64.4621C146.382 64.4621 129.433 61.5851 113.288 55.8804L112.828 55.716C91.7026 48.2522 75.4434 46.6082 73.635 46.4438L67.3056 45.9178V72.6493H79.0109V58.9712L78.9944 58.9876Z",
    "M169.513 211.962H157.808V266.182H143.291V277.887H184.03V266.182H169.513V211.962Z",
    "M169.513 137.62H157.808V197.824H169.513V137.62Z",
    "M317.096 147.353V161.886H170.713V173.575H328.801V147.353H317.096Z",
    "M245.713 160.521L245.746 160.669H257.665L257.632 160.439C255.955 150.575 250.793 141.533 243.115 134.99C235.339 128.365 225.459 124.731 215.25 124.731H112.072C101.879 124.731 91.9821 128.381 84.2059 134.99C76.5284 141.533 71.3663 150.575 69.6894 160.439L69.6565 160.669H81.5755L81.6084 160.521C84.9622 146.334 97.4895 136.42 112.072 136.42H215.25C229.848 136.42 242.376 146.334 245.713 160.521Z",
    "M245.713 174.956C242.359 189.143 229.832 199.057 215.25 199.057H112.072C97.4731 199.057 84.9457 189.143 81.6084 174.956L81.5755 174.808H69.6565L69.6894 175.038C71.3663 184.902 76.5284 193.944 84.2059 200.487C91.9821 207.112 101.863 210.746 112.072 210.746H215.25C225.442 210.746 235.339 207.096 243.115 200.487C250.793 193.944 255.955 184.902 257.632 175.038L257.665 174.808H245.746L245.713 174.956Z",
]

# Every image the canvas uses. Key = local file under assets/img/, the canvas upload id it replaces.
IMAGES = {
    "fetchly-website.jpg": ("Fetchly Website", "2ac49fef19cb4dba7df11c3f1a4a5c4d"),
    "fetchly-designops-service-page.jpg": ("DesignOps service page", "1ae8eb7ed3671c9006c8961f2aa32e28"),
    "container-alliance.webp": ("Container Alliance", "ef627160428f5026fbdfd39bd5e09793"),
    "tapp-cards.jpg": ("TAPP Cards", "4d5879d1920c8faee28df706ecbbf452"),
    "la-marie-beauty.jpg": ("La Marie Beauty", "cf2daa9be474b17652c1cee059634768"),
    "vintage-cards.jpg": ("Vintage Cards", "ccbae20a02e2a732985ed40c9d1831a0"),
    "yawara.jpg": ("Yawará", "a75d03af0d3ac779cad1dbab6d9178f9"),
    "essay-transition-and-transformation.jpg": ("Transition and Transformation", "f25e7e41739fb4967439e1d8c2e2df9f"),
    "essay-embracing-degrowth.jpg": ("Embracing Degrowth", "53dc641b36d03c14b3caa587880c4160"),
    "photo-nelore-cow.jpg": ("Nelore cow, close up", "3c9598c06cd019c2279b0c4290c1bd8c"),
    "photo-nelore-herd-dusk.jpg": ("Herd under a wide sky", "ec6f302681eaa917edaf942ca2adddd8"),
    "photo-inhotim-gardens.jpg": ("Path through the gardens, Inhotim", "a03dc1b135c4d9e7eee3909fbfb3f08c"),
    "essay-on-thinking-systems.jpg": ("On Thinking Systems", "from the Astro site"),
    "nomad.jpg": ("Nomad", "not on the canvas"),
}

ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>'
DOWN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14"/><path d="m5 12 7 7 7-7"/></svg>'
EXTERNAL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7"/><path d="M8 7h9v9"/></svg>'
PLUS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M5 12h14"/><path d="M12 5v14"/></svg>'
ICON_MAIL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>'
ICON_PIN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>'
ICON_LINK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6Z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg>'
COPY_ICON = ('<svg class="i-copy" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1"/></svg>'
             '<svg class="i-done" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>')
DOWNLOAD_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11"/><path d="m7 10 5 5 5-5"/><path d="M5 20h14"/></svg>'
GITHUB_MARK = ('<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true" focusable="false"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>')

# The colors each tone sets on the page; site.js mirrors them into the theme-color meta.
TONES = {
    "paper": "#FCFCFC", "blush": "#FDF3F6", "mist": "#EFF5FD", "cream": "#FFF8E2",   # pale: black text
    "field": "#2C5846", "berry": "#8C1F50", "cobalt": "#1D4A99",                    # deep: white text
}


# ---------------------------------------------------------------- The work collection (CMS)
# content/work/*.md is the same Decap CMS collection the Astro site uses (src/content/work there):
# one Markdown file per project, front matter fields title, client, year, services, summary, cover,
# order, draft, plus featured and thumbnail for the Home carousel. Image paths are site absolute
# ("/images/work/..."), as Decap writes them; the build makes them relative to each page.

def parse_front_matter(text):
    """The small YAML subset Decap writes: scalars, quoted strings, [inline, lists], folded >- blocks.
    Nested lists (the gallery) are skipped; the build does not use them."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    data, lines, i = {}, m.group(1).split("\n"), 0
    while i < len(lines):
        line = lines[i]
        km = re.match(r"^([A-Za-z_]\w*):\s?(.*)$", line)
        i += 1
        if not km:
            continue
        key, val = km.group(1), km.group(2).strip()
        if val in (">-", ">", "|", "|-"):
            block = []
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            data[key] = " ".join(x for x in block if x)
        elif val == "":
            while i < len(lines) and lines[i].startswith((" ", "-")):
                i += 1
            data[key] = None
        elif val.startswith("["):
            data[key] = [x.strip().strip('"').strip("'") for x in val[1:-1].split(",") if x.strip()]
        elif val in ("true", "false"):
            data[key] = val == "true"
        elif re.fullmatch(r"-?\d+", val):
            data[key] = int(val)
        else:
            data[key] = val.strip('"').strip("'")
    return data


def load_work():
    items = []
    for f in sorted((ROOT / "content/work").glob("*.md")):
        d = parse_front_matter(f.read_text(encoding="utf-8"))
        if d.get("draft"):
            continue
        d["slug"] = f.stem
        d.setdefault("order", 99)
        d.setdefault("services", [])
        d["thumbnail"] = d.get("thumbnail") or d["cover"]
        items.append(d)
    return sorted(items, key=lambda d: d["order"])


ALL_WORK = load_work()
# Case studies drive Home, the carousel and the Work grid; presentations (kind: presentation) get their
# own row on Work with a 4:3 thumbnail made for them.
WORK_ITEMS = [x for x in ALL_WORK if x.get("kind") != "presentation"]
DECKS = [x for x in ALL_WORK if x.get("kind") == "presentation"]
CASE_PAGES = {"fetchly-website": "case-fetchly-website.html"}  # projects with their own page


def work_href(item):
    return CASE_PAGES.get(item["slug"], f'work.html#{item["slug"]}')


def work_services(c, item, n=2):
    return ", ".join(c.t["service_terms"].get(x, x) for x in item["services"][:n])


def site_src(c, path):
    return c.R + path.lstrip("/")


def work_img(c, item, field="cover", alt="", eager=False, sizes=None):
    src = site_src(c, item[field])
    loading = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<div class="frame" data-label="{escape(item["title"])}" data-file="{item[field].lstrip("/")}">'
            f'<img src="{src}" alt="{escape(alt)}" {loading}></div>')


def work_card(c, item, tag="h3", size="h3", services=True):
    svc = f'<p class="note">{work_services(c, item)}</p>' if services else ""
    return (f'<article class="card" id="{item["slug"]}"><a href="{work_href(item)}">{work_img(c, item)}'
            f'<div class="card-row"><div><{tag} class="{size}">{item["title"]}</{tag}>{svc}</div>'
            f'<span class="meta year num">{item["year"]}</span></div></a></article>')


def deck_card(c, item):
    who = " · ".join(x for x in (item.get("client") or "", item.get("year") or "") if x)
    note = f'<p class="note">{escape(who)}</p>' if who else ""
    return (f'<article class="card deck" id="{item["slug"]}"><div class="card-body">{work_img(c, item, alt="")}'
            f'<div class="card-row"><div><h3 class="h3">{item["title"]}</h3>{note}</div>'
            f'<span class="meta num">{c.t["deck_slides"].format(n=item["slides"])}</span></div>'
            f'<p class="deck-summary">{item["summary"]}</p></div></article>')


def worked_logos(c):
    """The companies Lucas worked at, as their own marks in the page's ink."""
    out = "".join(
        f'<li style="--lh:{h}px"><svg viewBox="{vb}" fill="currentColor" role="img" aria-label="{escape(name)}" focusable="false">'
        f'<title>{escape(name)}</title>{inner}</svg></li>' for name, vb, inner, h in WORKED)
    out += (f'<li style="--lh:30px"><span class="logo-mask" role="img" aria-label="Future Needs" title="Future Needs" '
            f'style="-webkit-mask-image:url({c.R}assets/img/logos/future-needs.png);mask-image:url({c.R}assets/img/logos/future-needs.png);aspect-ratio:500/286"></span></li>')
    out += '<li><span class="logo-word">SaaSMouth</span></li>'
    return out


# ---------------------------------------------------------------- Home hero: the carousel and the tools
PAUSE_ICON = '<svg class="i-pause" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6.5" y="5" width="3.5" height="14" rx="1"/><rect x="14" y="5" width="3.5" height="14" rx="1"/></svg>'
PLAY_ICON = '<svg class="i-play" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.4-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5Z"/></svg>'


def showcase(c):
    """Three featured projects from the collection, one at a time, each linking to its project.
    The bars under it show which one is up and how long until the next."""
    t = c.t
    items = [x for x in WORK_ITEMS if x.get("featured")][:3]
    total = len(items)
    slides, dots = [], []
    for i, item in enumerate(items):
        label = t["carousel_slide"].format(n=i + 1, total=total)
        slides.append(
            f'<div class="show-slide{" is-active" if i == 0 else ""}" role="group" aria-roledescription="slide" '
            f'aria-label="{label}"{"" if i == 0 else " inert"} data-slide="{i}">'
            f'<a href="{work_href(item)}">{work_img(c, item, "thumbnail", eager=(i == 0))}'
            f'<span class="show-caption"><span class="h3">{item["title"]}</span>'
            f'<span class="note">{work_services(c, item)}</span><span class="meta num">{item["year"]}</span></span></a></div>')
        dots.append(
            f'<button class="show-dot" type="button" data-go="{i}" aria-label="{t["carousel_show"].format(title=item["title"])}"'
            f'{" aria-current=" + chr(34) + "true" + chr(34) if i == 0 else ""}><span></span></button>')
    return f"""<div class="showcase" role="region" aria-roledescription="carousel" aria-label="{t['carousel_label']}" data-showcase>
        <div class="show-slides">{"".join(slides)}</div>
        <div class="show-bar">
          <div class="show-dots" role="group" aria-label="{t['carousel_pick']}">{"".join(dots)}</div>
          <button class="show-toggle" type="button" data-label-pause="{t['carousel_pause']}" data-label-play="{t['carousel_play']}" aria-label="{t['carousel_pause']}">{PAUSE_ICON}{PLAY_ICON}</button>
        </div>
      </div>"""


def tools_marquee(c):
    t = c.t
    def items(hidden):
        return "".join(
            f'<li><svg viewBox="{vb}" fill="currentColor"{"" if hidden else f" role={chr(34)}img{chr(34)} aria-label={chr(34)}{escape(name)}{chr(34)}"}'
            f'{" aria-hidden=" + chr(34) + "true" + chr(34) if hidden else ""} focusable="false"><title>{escape(name)}</title>{inner}</svg></li>'
            for name, vb, inner in LOGOS)
    return f"""<div class="tools">
    <div class="container tools-head"><p class="note">{t['tools_label']}</p>
      <button class="show-toggle tools-toggle" type="button" data-label-pause="{t['tools_pause']}" data-label-play="{t['tools_play']}" aria-label="{t['tools_pause']}">{PAUSE_ICON}{PLAY_ICON}</button></div>
    <div class="marquee" data-marquee>
      <ul class="marquee-track" aria-label="{t['tools_label']}">{items(False)}</ul>
      <ul class="marquee-track" aria-hidden="true">{items(True)}</ul>
    </div>
  </div>"""


class Ctx:
    """One page in one language: its copy, its folder depth and its file name."""

    def __init__(self, lang, file, current):
        self.L = lang
        self.t = lang["t"]
        self.R = "../" if lang["dir"] else ""
        self.file = file
        self.current = current


def fmt_date(t, iso):
    d = date.fromisoformat(iso)
    return t["date"].format(d=d.day, month=t["months"][d.month - 1], y=d.year)


def img(c, file, alt=None, eager=False):
    label = IMAGES[file][0]
    label = c.t["img"].get(label, label)
    alt = label if alt is None else alt
    loading = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<div class="frame" data-label="{escape(label)}" data-file="assets/img/{file}">'
            f'<img src="{c.R}assets/img/{file}" alt="{escape(alt)}" {loading}></div>')


def btn(label, href, solid=False, icon=ARROW, extra=""):
    cls = "btn btn--solid" if solid else "btn"
    return f'<a class="{cls}" href="{href}"{extra}>{label}{icon}</a>'


def cv_btn(c, solid=False):
    cls = "btn btn--solid" if solid else "btn"
    return (f'<a class="{cls}" href="{c.R}{CV}" download="Lucas_Teixeira_Resume.pdf" data-cv>'
            f'{c.t["download_cv"]}{DOWNLOAD_ICON}</a>')


# ---------------------------------------------------------------- shared parts

LANG_SCRIPT = """<script>
(function () {
  var d = document.documentElement, page = "%(code)s", root = "%(root)s", file = "%(file)s";
  var dirs = { en: "", pt: "pt-br/", es: "es/" };
  d.lang = "%(html)s";
  d.classList.add("js");
  d.setAttribute("data-tone", "%(tone)s");
  // A choice made in the switcher is kept and wins from then on.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-lang]");
    if (!a) return;
    try { localStorage.setItem("lt-lang", a.getAttribute("data-lang")); } catch (err) {}
    try { sessionStorage.setItem("lt-lang", a.getAttribute("data-lang")); } catch (err) {}
  });
  var want = null;
  try { want = localStorage.getItem("lt-lang"); } catch (err) {}
  if (!want) { try { want = sessionStorage.getItem("lt-lang"); } catch (err) {} }
  // Without a choice, a visitor arriving on an English page from outside gets their browser's
  // language. A Portuguese or Spanish link someone shares stays in the language it was sent in.
  var inside = false;
  try { inside = !!document.referrer && new URL(document.referrer).origin === location.origin; } catch (err) {}
  if (!want && !inside && page === "en") {
    var list = navigator.languages || [navigator.language || ""];
    for (var i = 0; i < list.length; i++) {
      var l = String(list[i]).toLowerCase().slice(0, 2);
      if (l === "en" || l === "pt" || l === "es") { want = l; break; }
    }
  }
  if (want && want !== page && dirs.hasOwnProperty(want)) location.replace(root + dirs[want] + file + location.hash);
})();
</script>"""


# Share image (designed in Figma, file "lucastexr.com Open Graph", frame 1:2). Social scrapers need an
# absolute address. lucastexr.com is the Netlify site's primary domain, so canonical, og:url, og:image
# and hreflang all point there; the netlify.app and GitHub Pages copies defer to it (16 Oct 2026).
SITE_URL = "https://lucastexr.com/"


# Lucas's marks (marks.py), defined once per page and drawn with <use>: the ibis and the texr wordmark.
SPRITE = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">'
          f'<symbol id="m-ibis" viewBox="{IBIS_VB}">' + "".join(f'<path fill="currentColor" d="{d}"/>' for d in IBIS) + '</symbol>'
          f'<symbol id="m-texr" viewBox="{TEXR_VB}">' + "".join(f'<path fill="currentColor" d="{d}"/>' for d in TEXR) + '</symbol></svg>')


def mark(name, cls):
    vb = IBIS_VB if name == "ibis" else TEXR_VB
    return f'<svg class="{cls}" viewBox="{vb}" aria-hidden="true" focusable="false"><use href="#m-{name}"/></svg>'


OG_LOCALE = {"en": "en_US", "pt": "pt_BR", "es": "es_LA"}   # the forms Facebook and WhatsApp accept
OG_IMAGE = "assets/img/og.jpg?v=3"                          # bump v= when the image changes: WhatsApp caches by URL


def page_url(L, file):
    """Absolute address of a page as Netlify serves it: folders without index.html, pages without .html."""
    return SITE_URL + L["dir"] + ("" if file == "index.html" else file.removesuffix(".html"))


def head(c, title, description, tone, css=(), js=(), body_class=""):
    R = c.R
    extra = "".join(f'<link rel="stylesheet" href="{R}{x}">\n' for x in css) + "".join(f'<script src="{R}{x}" defer></script>\n' for x in js)
    alternates = "".join(f'<link rel="alternate" hreflang="{L["html"]}" href="{page_url(L, c.file)}">\n' for L in LANGS)
    alternates += f'<link rel="alternate" hreflang="x-default" href="{page_url(LANGS[0], c.file)}">\n'
    other_locales = "".join(f'<meta property="og:locale:alternate" content="{OG_LOCALE[L["code"]]}">\n' for L in LANGS if L["code"] != c.L["code"])
    script = LANG_SCRIPT % {"code": c.L["code"], "root": R, "file": c.file, "html": c.L["html"], "tone": tone}
    body_attr = f' class="{body_class}"' if body_class else ""
    url = page_url(c.L, c.file)
    # The share tags come first in the head, before any script, so the strictest scrapers (WhatsApp) find them.
    return f"""<!doctype html>
<html lang="{c.L['html']}" data-tone="{tone}" prefix="og: https://ogp.me/ns#">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="Lucas Teixeira">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:locale" content="{OG_LOCALE[c.L['code']]}">
{other_locales}<meta property="og:image" content="{SITE_URL}{OG_IMAGE}">
<meta property="og:image:secure_url" content="{SITE_URL}{OG_IMAGE}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{escape(c.t['og_alt'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="{escape(description)}">
<meta name="twitter:image" content="{SITE_URL}{OG_IMAGE}">
<meta name="theme-color" content="{TONES[tone]}">
{script}
{alternates}<link rel="icon" href="{R}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400..600&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="{R}assets/css/site.css">
<script src="{R}assets/js/site.js" defer></script>
<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
<script src="{R}assets/js/motion.js" defer></script>
{extra}</head>
<body{body_attr}>
{SPRITE}
<div class="noise" aria-hidden="true"></div>
<a class="skip" href="#main">{c.t['skip']}</a>
"""


def nav_icon(key):
    return f'<svg class="ni" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{NAV_ICONS[key]}</svg>'


def lang_links(c, full=False):
    out = []
    for L in LANGS:
        href = c.R + L["dir"] + c.file
        cur = ' aria-current="true"' if L["code"] == c.L["code"] else ""
        text = L["name"] if full else f'{L["short"]}<span class="sr">, {L["full"]}</span>'
        out.append(f'<a href="{href}" hreflang="{L["html"]}" lang="{L["html"]}" data-lang="{L["code"]}"{cur}>{text}</a>')
    return "".join(out)


CHEVRON = '<svg class="lang-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m7 10 5 5 5-5"/></svg>'
CHECK = '<svg class="lp-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>'


def flap(code):
    """A language code as split flap letters: each letter sits on a strip of itself, so it can roll."""
    return "".join(f'<span class="flap" style="--i:{i}"><span>{ch}</span><span>{ch}</span></span>' for i, ch in enumerate(code))


def lang_picker(c):
    """The header language picker. Closed it is one pill with the current code; hover, focus or a tap
    morph it into a panel of the three languages (site.js drives it). Links stay real links."""
    t = c.t
    rows = []
    for r, L in enumerate(LANGS):
        href = c.R + L["dir"] + c.file
        cur = L["code"] == c.L["code"]
        rows.append(
            f'<a class="lp-row" style="--r:{r}" href="{href}" hreflang="{L["html"]}" lang="{L["html"]}" data-lang="{L["code"]}"{" aria-current=" + chr(34) + "true" + chr(34) if cur else ""}>'
            f'<span class="lp-code" aria-hidden="true">{flap(L["short"])}</span>'
            f'<span class="lp-name">{L["name"]}<small>{L["region"]}</small></span>{CHECK}</a>')
    return f"""<div class="lang-picker" data-lang-picker>
        <button class="lang-trigger" type="button" aria-expanded="false" aria-controls="lang-panel" aria-label="{t['lang_label']}: {c.L['name']}. {t['lang_change']}">
          <span class="lp-code" aria-hidden="true">{flap(c.L['short'])}</span>{CHEVRON}
        </button>
        <nav class="lang-panel" id="lang-panel" aria-label="{t['lang_label']}">
          <span class="lp-head" aria-hidden="true">{t['lang_label']}</span><span class="lp-blob" aria-hidden="true"></span>{"".join(rows)}
        </nav>
      </div>"""


def header(c):
    t = c.t
    cur = lambda key: ' aria-current="page"' if key == c.current else ""
    # Icon and word side by side, at the top of the page and after it scrolls (site.css)
    links = "".join(f'<a href="{href}"{cur(key)}>{nav_icon(key)}<span class="nl">{t["nav"][key]}</span></a>' for key, href in NAV)
    menu = "".join(
        f'<li style="--i:{i}"><a href="{href}"{cur(key)}>{nav_icon(key)}<span>{t["nav"][key]}</span></a></li>'
        for i, (key, href) in enumerate(NAV)
    )
    return f"""<header class="site-header">
  <div class="container">
    <a class="brand" href="index.html" aria-label="{t['home_label']}">{mark('ibis', 'brand-ibis')}{mark('texr', 'brand-texr')}</a>
    <nav class="nav" aria-label="{t['nav_label']}">{links}</nav>
    <div class="header-end">
      {lang_picker(c)}
      <button class="menu-button" type="button" aria-expanded="false" aria-controls="menu">{t['menu']}</button>
    </div>
  </div>
</header>
<div class="menu-panel" id="menu" hidden>
  <nav aria-label="{t['nav_label']}"><ul>{menu}</ul></nav>
  <div class="menu-foot">
    <nav class="lang lang--full" aria-label="{t['lang_label']}">{lang_links(c, full=True)}</nav>
    <a class="menu-mail" href="mailto:{EMAIL}">{EMAIL}</a><span class="meta">{t['city']}</span>
  </div>
</div>
"""


def badge(label):
    paths = "".join(
        '<path class="b-%s" d="%s" pathLength="1" style="--d:%s"/>' % (kind, d, delay)
        for kind, delay, d in BADGE
    )
    return f'<svg class="badge" viewBox="0 0 329 317" fill="currentColor" role="img" aria-label="{escape(label)}">{paths}</svg>'


def footer(c):
    # Adapted from the lucastexr.com (Framer) footer, now in Paper: a field with a rounded tab rising
    # into the page, the email line on the tab, the badge centered, name and region in the corners.
    # The footer is the last tone stop: every page ends on Paper (inverted from green on 9 Oct 2026).
    t = c.t
    return f"""<footer class="site-footer" data-tone="paper">
  <div class="footer-tab">
    <p class="footer-ask">{t['footer_ask']} <strong>{t['footer_shoot']}</strong></p>
    <p class="footer-reach"><a class="footer-mail" href="mailto:{EMAIL}">{EMAIL}</a><button class="copy" type="button" data-copy="{EMAIL}">{COPY_ICON}<span class="copy-text">{t['copy']}</span><span class="sr">{t['copy_sr']}</span></button><span class="sr" role="status" data-copy-status></span></p>
  </div>
  <div class="footer-field">
    <div class="badge-wrap">{badge(t['badge_label'])}</div>
    <div class="footer-corners">
      <p>Lucas Teixeira <span class="footer-dim">© 2026</span></p>
      <p>{t['region']} <span class="footer-dim"><time data-clock class="num">{t['local_time']}</time> {t['in_brasilia']}</span></p>
    </div>
  </div>
</footer>
</body>
</html>
"""


def expand_abbr(html, abbr):
    """WCAG 3.1.4 (AAA): the first use of each abbreviation on a page carries its expansion."""
    done = set()

    def text(m):
        chunk = m.group(0)
        for ab, full in abbr.items():
            if ab in done:
                continue
            pat = re.compile(r"(?<![\w-])%s(?![\w-])" % re.escape(ab))
            if pat.search(chunk):
                chunk = pat.sub('<abbr title="%s">%s</abbr>' % (full, ab), chunk, count=1)
                done.add(ab)
        return chunk
    return re.sub(r"(?<=>)[^<]+(?=<)", text, html)


def write_page(c, title, description, main, css=(), js=(), body_class="", tiles=True):
    tone = re.search(r'data-tone="([\w-]+)"', main).group(1)
    ribboned = set()
    if tiles:  # the Bulcão ribbon closes the opening section (Home: the closing one, under the hero's logos)
        i = main.rindex("</section>") if tiles == "close" else main.index("</section>")
        main = main[:i] + f'<div class="container ribbon-wrap">{ribbon(c)}</div>\n' + main[i:]
        if tiles == "close":
            ribboned.add(main[:i].count('<section class="band') - 1)
    main = add_blocos(main, c.file, ribboned)
    main = expand_abbr(main, c.t["abbr"])
    html = head(c, title, description, tone, css, js, body_class) + header(c) + f'<main id="main">\n{main}\n</main>\n' + footer(c)
    out = ROOT / c.L["dir"] / c.file
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def card(c, file, name, services, year, href=None, tag="h3", size="h3"):
    svc = f'<p class="note">{services}</p>' if services else ""
    inner = (f'{img(c, file, alt="")}<div class="card-row"><div><{tag} class="{size}">{name}</{tag}>{svc}</div>'
             f'<span class="meta year num">{year}</span></div>')
    if href:
        return f'<article class="card"><a href="{href}">{inner}</a></article>'
    return f'<article class="card"><div class="card-body">{inner}</div></article>'


def ledger(rows, arrow=" to "):
    def num(n):
        return n.replace(" → ", f'<span aria-hidden="true"> → </span><span class="sr">{arrow}</span>')
    return '<dl class="ledger">' + "".join(f'<div><dt>{num(n)} <small>{u}</small></dt><dd>{d}</dd></div>' for n, u, d in rows) + "</dl>"


def action(c, heading, lead=None, buttons="", shout=False, extra="", tone="field"):
    """The Action stage: a strong close, Field green by default so it runs on into the green footer."""
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""
    cls = "display closing-title is-shout" if shout else "display closing-title"
    return f"""<section class="band closing" data-tone="{tone}" aria-labelledby="close-title">
  <div class="container">
    <h2 class="{cls}" id="close-title">{heading}</h2>
    {lead_html}
    <div class="actions">{buttons}</div>
    <p class="cv-status" data-cv-status aria-live="polite"></p>
    {extra}
  </div>
</section>"""



# The home page's Action ends on Lucas's card, set like the résumé sheet on About: white paper,
# tilted over a deeper green, straightening when you reach for it. It knows the time in Brasília and
# draws where the sun (or the moon) is over the city, so a visitor in another time zone can see
# whether it is morning or evening there before writing.
SKY = ('<svg class="sky" viewBox="0 0 120 52" aria-hidden="true" focusable="false">'
       '<path class="sky-arc" d="M10 44 A50 36 0 0 1 110 44"/><path class="sky-line" d="M4 44H116"/>'
       '<g data-sun style="--x:60px;--y:8px"><circle class="halo" r="10.5"/><circle class="sun" r="6.5"/>'
       '<path class="moon" d="M2.4-7.6A7.8 7.8 0 1 0 7.8 2.9 6.1 6.1 0 0 1 2.4-7.6Z"/></g></svg>')


def business_card(c):
    t = c.t
    return f"""<div class="card-stack">
        <div class="biz" role="group" aria-label="{t['card_label']}">
          <div class="biz-top">{mark('ibis', 'biz-ibis')}{SKY}</div>
          <p class="biz-name">Lucas Teixeira</p>
          <p class="biz-role">{t['card_role']}</p>
          <p class="biz-time"><time data-clock class="num">{t['local_time']}</time><span data-daypart>{t['in_brasilia']}</span></p>
          <p class="biz-mail"><a href="mailto:{EMAIL}">{EMAIL}</a><button class="copy copy--ink" type="button" data-copy="{EMAIL}">{COPY_ICON}<span class="copy-text">{t['copy']}</span><span class="sr">{t['copy_sr']}</span></button><span class="sr" role="status" data-copy-status></span></p>
        </div>
      </div>"""

# ---------------------------------------------------------------- Home

def home(c):
    t = c.t
    services = "".join(
        f'<section><h3>{name}</h3><ul>{"".join(f"<li>{i}</li>" for i in items)}</ul></section>'
        for name, items in t["services"]
    )
    facts = "".join(f'<li><strong>{n}</strong> {label}</li>' for n, label in t["home_facts"])
    voices = "".join(f'<div class="voice"><p>{a}</p><cite>{b}</cite></div>' for a, b in t["about_voices"])
    checks = "".join(f"<li>{x}</li>" for x in t["about_checks"])
    main = f"""<section class="band hero" data-tone="field">
  <div class="container hero-grid">
    <div class="hero-copy">
      <h1 class="display">{t['home_h1']}</h1>
      <p class="lead">{t['home_lead']}</p>
      <div class="actions">
        {btn(t['see_work'], 'work.html', solid=True)}
        <a class="btn" href="contact.html">{t['get_in_touch']}</a>
      </div>
      <div class="hero-facts">
        <ul class="facts-items" aria-label="{t['home_glance']}">{facts}</ul>
        <div class="worked"><ul class="worked-logos" aria-label="{t['home_worked']}">{worked_logos(c)}</ul></div>
      </div>
    </div>
    {showcase(c)}
  </div>
  {tools_marquee(c)}
</section>

<section class="band" data-tone="mist" aria-labelledby="cases-title">
  <div class="container">
    <h2 class="h2 cases-title" id="cases-title">{t['home_cases']}</h2>
    <article class="feature">
      <a href="{work_href(WORK_ITEMS[0])}">
        {work_img(c, WORK_ITEMS[0])}
        <div class="card-row"><div><h3 class="h3-l">{WORK_ITEMS[0]['title']}</h3><p class="note">{work_services(c, WORK_ITEMS[0], 3)}</p></div><span class="meta year num">{WORK_ITEMS[0]['year']}</span></div>
      </a>
    </article>
    <div class="grid-2">{"".join(work_card(c, x, services=False) for x in WORK_ITEMS[1:5])}</div>
    <div class="more">{btn(t['all_work'], 'work.html')}</div>
  </div>
</section>

<section class="band" data-tone="cream" aria-labelledby="do-title">
  <div class="container">
    <div class="intro-grid">
      <h2 class="h2" id="do-title">{t['home_do']}</h2>
      <div class="intro-side">
        <p class="big">{t['home_do_lead']}</p>
        <div class="actions">{btn(t['how_i_work'], 'process.html')}</div>
      </div>
    </div>
    <div class="services">{services}</div>
  </div>
</section>

<section class="band" data-tone="blush" aria-labelledby="changed-title">
  <div class="container">
    <h2 class="h2" id="changed-title">{t['home_changed']}</h2>
    {ledger(t['results'], t['arrow_sr'])}
    <div class="voices voices--pair" role="group" aria-label="{t['home_voices_label']}">{voices}</div>
  </div>
</section>

<section class="band action" data-tone="field" aria-labelledby="close-title">
  <div class="container">
    <div class="action-grid">
      <div>
        <h2 class="display action-title" id="close-title">{t['home_close']}</h2>
        <p class="lead">{t['contact_lead']}</p>
        <div class="actions">
          {btn(t['get_in_touch'], 'contact.html', solid=True)}
          {btn(t['see_cv'], 'about.html#resume')}
        </div>
        <ul class="checks">{checks}</ul>
      </div>
      {business_card(c)}
    </div>
  </div>
</section>"""
    write_page(c, t["home_title"], t["home_desc"], main, tiles="close")


# ---------------------------------------------------------------- Work

def work(c):
    t = c.t
    cards = "".join(work_card(c, x, tag="h2") for x in WORK_ITEMS)
    decks = "".join(deck_card(c, x) for x in DECKS)
    outcomes = "".join(
        f'<li><h3 class="h3">{name}</h3><p>{text}</p></li>'
        for name, text in zip(["Container Alliance", "Fetchly Website", "Nomad"], t["work_outcomes"])
    )
    main = f"""<section class="band page-head" data-tone="mist">
  <div class="container">
    <h1 class="display">{t['work_h1']}</h1>
    <p class="lead">{t['work_lead']}</p>
    <div class="row"><p class="meta">{t['work_count'].format(n=len(WORK_ITEMS))}</p><p class="note">{t['work_kinds']}</p></div>
  </div>
</section>
<section class="band" data-tone="paper">
  <div class="container grid-2">{cards}</div>
</section>
<section class="band" data-tone="paper" id="presentations" aria-labelledby="decks-title">
  <div class="container">
    <div class="intro-grid"><h2 class="h2" id="decks-title">{t['work_decks_h']}</h2><p class="big">{t['work_decks_lead']}</p></div>
    <div class="grid-2 decks">{decks}</div>
  </div>
</section>
{artifact_browser(c)}
<section class="band" data-tone="blush" aria-labelledby="outcomes-title">
  <div class="container">
    <h2 class="h2" id="outcomes-title">{t['work_changed']}</h2>
    <ul class="trio">{outcomes}</ul>
  </div>
</section>
{action(c, t['work_close'], t['work_close_lead'], btn(t['get_in_touch'], 'contact.html', solid=True) + cv_btn(c))}"""
    write_page(c, t["work_title"], t["work_desc"], main)


# ---------------------------------------------------------------- Case study

def case(c):
    t = c.t
    facts = "".join(f'<div><dt>{a}</dt><dd{" class=" + chr(34) + "num" + chr(34) if b.isdigit() else ""}>{b}</dd></div>' for a, b in t["case_facts"])
    overview = "".join(f"<p>{p}</p>" for p in t["case_overview_p"])
    stats = "".join(f'<div><dt>{n}</dt><dd>{label}</dd></div>' for n, label in t["case_stats"])
    nxt = (f'<nav class="next" aria-label="{t["case_next"]}"><p class="meta">{t["case_next"]}</p>'
           f'<a href="work.html#container-alliance">Container Alliance{ARROW}</a></nav>')
    main = f"""<section class="band page-head case-head" data-tone="cream">
  <div class="container">
    <p class="meta client">Fetchly Labs</p>
    <h1 class="display">Fetchly Website</h1>
    <p class="lead-l">{t['case_lead']}</p>
  </div>
</section>
<section class="band" data-tone="paper">
  <div class="container">
    <div class="cover">{img(c, "fetchly-website.jpg", alt=t['case_cover_alt'], eager=True)}</div>
    <div class="split">
      <aside>
        <dl class="facts-list">
          {facts}
          <div class="wide"><dt>{t['case_services_label']}</dt><dd>{"<br>".join(t['case_services'])}</dd></div>
          <div class="wide"><dt>{t['case_live']}</dt><dd><a href="https://fetch.ly" rel="noopener">{t['case_visit']}{EXTERNAL}</a></dd></div>
        </dl>
        <div class="aside-actions"><a class="btn" href="work.html">{t['all_work']}</a></div>
      </aside>
      <div class="prose">
        <h2>{t['case_overview']}</h2>
        {overview}
        <h2>{t['case_challenge']}</h2>
        <p>{t['case_challenge_p']}</p>
      </div>
    </div>
    <figure class="figure">{img(c, "fetchly-designops-service-page.jpg", alt=t['case_figure_alt'])}<figcaption class="note">{t['case_figcaption']}</figcaption></figure>
  </div>
</section>
<section class="band" data-tone="mist" aria-labelledby="result-title">
  <div class="container statement">
    <h2 class="h2" id="result-title">{t['case_result_h']}</h2>
    <p class="big">{t['case_result']}</p>
    <dl class="figures">{stats}</dl>
  </div>
</section>
{action(c, t['case_close'], buttons=btn(t['get_in_touch'], 'contact.html', solid=True), extra=nxt)}"""
    write_page(c, t["case_title"], t["case_desc"], main)



# ---------------------------------------------------------------- Process
# The documents the team works from, told as a funnel: why write it down (blush), the three documents
# with a step rail that follows the scroll (paper, it reads like a document), the rules (blush),
# what it changes (rose), and the green close.

def process(c):
    t = c.t
    chips = "".join(f'<li><span class="meta">{a}</span>{n}</li>' for a, n, *_ in t["process_docs"])
    peak = 100
    bars = "".join(
        f'<li style="--v:{float(v.rstrip("×")) / peak:.3f};--i:{i}"><span class="cost-bar" aria-hidden="true"></span>'
        f'<strong class="num">{v}</strong><span>{label}</span></li>'
        for i, (v, label) in enumerate(t["process_cost"]))
    steps = "".join(
        f'<li><a href="#doc-{a.lower()}" data-step><span class="num">0{i + 1}</span><span class="step-abbr">{a}</span>'
        f'<span class="step-name">{n}</span><span class="step-fill" aria-hidden="true"></span></a></li>'
        for i, (a, n, *_) in enumerate(t["process_docs"]))
    docs = ""
    for a, name, q, body, readers, contents, done, ref in t["process_docs"]:
        k = a.lower()
        items = "".join(f"<li>{x}</li>" for x in contents)
        docs += f"""<article class="doc" id="doc-{k}" aria-labelledby="doc-{k}-title" data-doc>
          <p class="doc-abbr" aria-hidden="true">{a}</p>
          <h3 class="h3-l" id="doc-{k}-title">{name}</h3>
          <p class="doc-q">{q}</p>
          <p class="doc-body">{body}</p>
          <div class="doc-grid">
            <div><h4 class="meta">{t['process_contents']}</h4><ul class="checks">{items}</ul></div>
            <dl class="doc-facts"><div><dt class="meta">{t['process_readers']}</dt><dd>{readers}</dd></div><div><dt class="meta">{t['process_done']}</dt><dd>{done}</dd></div></dl>
          </div>
          <p class="note doc-ref">{ref}</p>
        </article>"""
    rules = "".join(f'<li><h3 class="h3">{a}</h3><p>{b}</p></li>' for a, b in t["process_rules"])
    team = "".join(f'<li><h3 class="h3">{a}</h3><p>{b}</p></li>' for a, b in t["process_team"])
    main = f"""<section class="band page-head" data-tone="cobalt">
  <div class="container">
    <h1 class="display process-title">{t['process_h1']}</h1>
    <p class="lead">{t['process_lead']}</p>
    <ul class="doc-chips" aria-label="{t['process_steps_label']}">{chips}</ul>
    <div class="actions">
      {btn(t['process_see_docs'], '#documents', solid=True, icon=DOWN)}
      <a class="btn" href="contact.html">{t['get_in_touch']}</a>
    </div>
  </div>
</section>

<section class="band" data-tone="mist" aria-labelledby="why-title">
  <div class="container">
    <h2 class="h2" id="why-title">{t['process_why_h']}</h2>
    <div class="why-grid">
      <figure class="why-quote"><blockquote><p class="big">{t['process_quote']}</p></blockquote><figcaption class="note">{t['process_quote_cite']}</figcaption></figure>
      <figure class="cost" data-rise>
        <figcaption class="cost-label">{t['process_cost_label']}</figcaption>
        <ol class="cost-bars">{bars}</ol>
        <p class="note">{t['process_cost_note']}</p>
      </figure>
    </div>
    <p class="architect">{t['process_architect']}</p>
  </div>
</section>

<section class="band" data-tone="paper" id="documents" aria-labelledby="docs-title">
  <div class="container">
    <div class="intro-grid">
      <h2 class="h2" id="docs-title">{t['process_docs_h']}</h2>
      <div class="intro-side"><p class="big">{t['process_docs_lead']}</p></div>
    </div>
    <div class="docs">
      <nav class="doc-steps" aria-label="{t['process_steps_label']}"><ol>{steps}</ol></nav>
      <div class="doc-list">{docs}</div>
    </div>
  </div>
</section>

<section class="band" data-tone="cream" aria-labelledby="practice-title">
  <div class="container">
    <div class="intro-grid">
      <h2 class="h2" id="practice-title">{t['process_practice_h']}</h2>
      <div class="intro-side"><p class="big">{t['process_practice_lead']}</p></div>
    </div>
    <ul class="trio rules">{rules}</ul>
  </div>
</section>

<section class="band" data-tone="blush" aria-labelledby="changes-title">
  <div class="container">
    <h2 class="h2" id="changes-title">{t['process_changes_h']}</h2>
    {ledger(t['process_ledger'], t['arrow_sr'])}
    <ul class="trio">{team}</ul>
  </div>
</section>

{action(c, t['process_close'], t['process_close_lead'], btn(t['get_in_touch'], 'contact.html', solid=True) + btn(t['see_work'], 'work.html'))}"""
    write_page(c, t["process_title"], t["process_desc"], main)


# ---------------------------------------------------------------- Writing

def writing(c):
    t = c.t
    covers = ["essay-transition-and-transformation.jpg", "essay-embracing-degrowth.jpg", "essay-on-thinking-systems.jpg"]
    essays = ""
    for i, ((title, body), cover) in enumerate(zip(t["essays"], covers)):
        alt = title if i == 2 else None
        more = f'<div class="actions">{btn(t["read_essay"], "essay-on-thinking-systems.html")}</div>' if i == 2 else ""
        essays += f'<article class="essay-card">{img(c, cover, alt=alt)}<div><h2 class="h3-l">{title}</h2><p>{body}</p>{more}</div></article>'
    research = "".join(f'<li><h3 class="h3">{a}</h3><p>{b}</p></li>' for a, b in t["writing_research_items"])
    main = f"""<section class="band page-head" data-tone="cream">
  <div class="container">
    <h1 class="display">{t['writing_h1']}</h1>
    <p class="lead">{t['writing_lead']}</p>
    <div class="row"><p class="note">{t['writing_topics']}</p><p class="meta">{t['writing_count']}</p></div>
  </div>
</section>
<section class="band" data-tone="paper">
  <div class="container essays">{essays}</div>
</section>
<section class="band" data-tone="blush" aria-labelledby="research-title">
  <div class="container">
    <h2 class="h2" id="research-title">{t['writing_research']}</h2>
    <ul class="trio">{research}</ul>
  </div>
</section>
{action(c, t['writing_close'], buttons=btn(t['get_in_touch'], 'contact.html', solid=True), tone="berry")}"""
    write_page(c, t["writing_title"], t["writing_desc"], main)


# ---------------------------------------------------------------- Essay

def essay(c):
    t = c.t
    facts = "".join(f'<div class="wide"><dt>{a}</dt><dd>{b}</dd></div>' for a, b in t["essay_facts"])
    paras = "".join(f"<p>{p}</p>" for p in t["essay_p"])
    main = f"""<section class="band page-head" data-tone="blush">
  <div class="container"><h1 class="display essay-title">{t['essay_h1']}</h1></div>
</section>
<section class="band" data-tone="paper">
  <div class="container split">
    <aside>
      <dl class="facts-list">
        {facts}
        <div class="wide"><dt>{t['essay_origin']}</dt><dd class="todo-text">{t['essay_origin_todo']}</dd></div>
      </dl>
      <div class="aside-actions"><a class="btn" href="writing.html">{t['all_writing']}</a></div>
    </aside>
    <article class="prose">
      {img(c, "essay-on-thinking-systems.jpg", alt=t['essay_h1'], eager=True)}
      <p class="standfirst">{t['essay_standfirst']}</p>
      {paras}
      <blockquote><p>{t['essay_quote']}</p><cite class="meta">Heisenberg, 1958</cite></blockquote>
    </article>
  </div>
</section>
{action(c, t['essay_close'], buttons=btn(t['get_in_touch'], 'contact.html', solid=True) + btn(t['all_writing'], 'writing.html'))}"""
    write_page(c, t["essay_title"], t["essay_desc"], main)


# ---------------------------------------------------------------- Photography

def photography(c):
    t = c.t
    plates = "".join(
        f'<figure>{img(c, f)}<figcaption>{c.t["img"].get(IMAGES[f][0], IMAGES[f][0])}</figcaption></figure>'
        for f in ("photo-nelore-cow.jpg", "photo-nelore-herd-dusk.jpg", "photo-inhotim-gardens.jpg")
    )
    main = f"""<section class="band page-head" data-tone="mist">
  <div class="container">
    <h1 class="display">{t['photo_h1']}</h1>
    <div class="row"><p class="note">{t['photo_lead']}</p><p class="meta">{t['photo_count']}</p></div>
  </div>
</section>
<section class="band series" data-tone="paper">
  <div class="container">
    <div class="series-head"><h2 class="h3-l">God's given</h2><span class="meta num">{t['photo_frames']}</span></div>
    <div class="plates">{plates}</div>
  </div>
</section>
<section class="band" data-tone="cream" aria-labelledby="eye-title">
  <div class="container statement">
    <h2 class="h2" id="eye-title">{t['photo_eye']}</h2>
    <p class="big">{t['photo_eye_p']}</p>
    <div class="actions">{btn(t['photo_eye_cta'], 'work.html')}</div>
  </div>
</section>
{action(c, t['photo_close'], buttons=btn(t['get_in_touch'], 'contact.html', solid=True), tone="cobalt")}"""
    write_page(c, t["photo_title"], t["photo_desc"], main)


# ---------------------------------------------------------------- About
# The recruiter funnel: Attention (green, the tile wall spells LUCAS), Interest (blush),
# Desire (rose), Action (green, the résumé), then the questions (blush) and the green footer.
# Every figure comes from the verified career document (~/Documents/lucas-teixeira-ats).

# The tile wall. Tiles after Athos Bulcão: a band of constant width that meets every tile edge at its
# middle, so strokes run on from tile to tile. Arc = quarter ring around a corner (round inside,
# octagonal outside, the Bulcão contour). Straight and tee tiles carry the strokes letters need.
TILE_DEFS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<path id="t-arc" d="M39 100 L39 74.73 L74.73 39 L100 39 L100 61 A39 39 0 0 0 61 100 Z" fill="currentColor"/>
<path id="t-straight" d="M39 0 H61 V100 H39 Z" fill="currentColor"/>
<path id="t-tee" d="M39 0 H61 V39 H100 V61 H61 V100 H39 Z" fill="currentColor"/>
</defs></svg>"""

# Each letter is 2 columns by 3 rows. Codes: V/H straight, BR/BL/TL/TR arc around that corner,
# T0 tee with its stub to the right, T180 stub to the left, "." background tile.
GLYPHS = {
    "L": [["V", "."], ["V", "."], ["TR", "H"]],
    "U": [["V", "V"], ["V", "V"], ["TR", "TL"]],
    "C": [["BR", "H"], ["V", "."], ["TR", "H"]],
    "A": [["BR", "BL"], ["T0", "T180"], ["V", "V"]],
    "S": [["BR", "H"], ["TR", "BL"], ["H", "TL"]],
}
ARC_TURNS = {"BR": 0, "BL": 1, "TL": 2, "TR": 3}
FLOWER = {(0, 0): "BR", (0, 1): "BL", (1, 0): "TR", (1, 1): "TL"}  # rings around shared corners


def tile_wall(label, word="LUCAS", cols=16, rows=5):
    grid = [[None] * cols for _ in range(rows)]
    col = 1
    for ch in word:
        for r in range(3):
            for k in range(2):
                grid[1 + r][col + k] = GLYPHS[ch][r][k]
        col += 3
    cells = []
    for r in range(rows):
        for k in range(cols):
            code = grid[r][k]
            letter = code not in (None, ".")
            if not letter:
                kind, turns, period = "arc", ARC_TURNS[FLOWER[(r % 2, k % 2)]], 4
            elif code in ARC_TURNS:
                kind, turns, period = "arc", ARC_TURNS[code], 4
            elif code in ("V", "H"):
                kind, turns, period = "straight", 0 if code == "V" else 1, 2
            else:
                kind, turns, period = "tee", 0 if code == "T0" else 2, 4
            cells.append(
                f'<span class="tile{"" if letter else " is-faint"}" data-target="{turns}" data-period="{period}" '
                f'data-letter="{1 if letter else 0}"><svg viewBox="0 0 100 100" style="--turns:{turns}" aria-hidden="true" '
                f'focusable="false"><use href="#t-{kind}"/></svg></span>'
            )
    return (TILE_DEFS + f'<div class="wall" data-wall role="img" aria-label="{escape(label.format(word=word))}">'
            + "".join(cells) + "</div>")


# A ribbon of Bulcão tiles at the foot of each page's opening section: two rows of the same
# tiles as the About wall, in the page's own ink. Each page turns the pattern its own way, so
# every page has a slightly different wall. Decorative and pointer only (motion.js).
RIBBON_TURN = {"index.html": 0, "process.html": 1, "work.html": 2, "case-fetchly-website.html": 1, "writing.html": 3,
               "essay-on-thinking-systems.html": 2, "photography.html": 1, "contact.html": 3, "merch.html": 2}


def ribbon(c, cols=48):
    offset = RIBBON_TURN.get(c.file, 0)
    rows = []
    for r in range(2):
        cells = "".join(
            f'<span class="rt" data-row="{r}" data-col="{k}" data-home="{(ARC_TURNS[FLOWER[(r % 2, k % 2)]] + offset) % 4}">'
            f'<svg viewBox="0 0 100 100" focusable="false"><use href="#t-arc"/></svg></span>'
            for k in range(cols)
        )
        rows.append(f'<div class="ribbon-row">{cells}</div>')
    return f'<div class="ribbon" data-ribbon aria-hidden="true">{TILE_DEFS}{"".join(rows)}</div>'


# ---------------------------------------------------------------- Blocos: one tile, sometimes exploded
# Lucas's direction (9 Oct 2026): a single tile pattern, in outline, and every so often the same motif
# blown up and cropped behind a section, set on a third or a golden section, at the top or the bottom.
# The tile is Athos Bulcão's dove from the Igrejinha; the big ones alternate the dove and Lucas's ibis.
# Texture, never content: hidden from assistive tech and drawn under the type (motion.js turns tiles).
MOTIF_DEFS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<path id="m-dove" vector-effect="non-scaling-stroke" d="M31 4 Q50 7.5 69 4 C64 15 57.5 26 57.5 36 C57.5 44 59.5 50 63.5 53.5 Q65.5 55 68 53 L95.5 34.5 Q98.5 33.5 97.6 37 C93 51 86.5 62 80.5 69 C74.5 75.5 63 78.5 54.2 81.6 C51.6 82.6 53.8 85.6 54.8 88 C56 91.5 53 94 50 97.5 C47 94 44 91.5 45.2 88 C46.2 85.6 48.4 82.6 45.8 81.6 C37 78.5 25.5 75.5 19.5 69 C13.5 62 7 51 2.4 37 Q1.5 33.5 4.5 34.5 L32 53 Q34.5 55 36.5 53.5 C40.5 50 42.5 44 42.5 36 C42.5 26 36 15 31 4 Z"/>
</defs></svg>"""
# Where a big one sits: horizontally on a third or a golden section, cropped at the top or the bottom.
BURST_X = ("33.333%", "61.8%", "66.667%", "38.2%")
BURST_TONES = {"blush", "mist", "cream", "field", "berry", "cobalt"}   # never on Paper, under photos and forms


def dove_strip(seed, side):
    rng = random.Random(seed)
    rows = []
    for r in range(2):
        rows.append("".join(
            f'<span class="rt bt" data-row="{r}" data-col="{k}" data-home="{0 if (r + k) % 2 == 0 else 2}" style="--n:{rng.randrange(16)}">'
            f'<svg viewBox="0 0 100 100" focusable="false"><use href="#m-dove"/></svg></span>' for k in range(8)))
    body = "".join(f'<div class="ribbon-row">{row}</div>' for row in rows)
    return f'<div class="bloco bloco--{side}"><div class="ribbon bloco-tiles" data-ribbon aria-hidden="true">{body}</div></div>'


def burst(motif, x, edge):
    if motif == "ibis":
        art = f'<svg viewBox="{IBIS_VB}" focusable="false"><use href="#m-ibis"/></svg>'
    else:
        art = '<svg viewBox="0 0 100 100" focusable="false"><use href="#m-dove"/></svg>'
    return f'<div class="burst burst--{motif} burst--{edge}" style="--bx:{x}" aria-hidden="true">{art}</div>'


def add_blocos(main, file, ribboned):
    """A dove strip at the end of most sections; on one or two sections per page (pale or deep tones
    only, never the opening one) a big cropped dove or ibis instead, behind the content."""
    spots = [(m.start(), m.end(), m.group(1), m.group(2)) for m in re.finditer(r'<section class="band([^"]*)" data-tone="([\w-]+)"', main)]
    rng = random.Random("blocos:" + file)
    # never on the opening section, a ribboned one, Paper, or a closing / action band (Lucas: not there)
    eligible = [n for n, (_, _, cls, tone) in enumerate(spots)
                if n > 0 and n not in ribboned and tone in BURST_TONES and "closing" not in cls and "action" not in cls]
    bursts = set(rng.sample(eligible[1:] or eligible, min(2 if len(spots) > 5 else 1, len(eligible[1:] or eligible)))) if eligible else set()
    motif_i = rng.randrange(2)
    edits, side_i = [], 0
    for n, (start, tag_end, cls, tone) in enumerate(spots):
        if n == 0 or n in ribboned:
            continue
        if n in bursts:
            motif = ("dove", "ibis")[motif_i % 2]
            motif_i += 1
            edits.append(("burst", start, tag_end, burst(motif, rng.choice(BURST_X), rng.choice(("top", "bottom")))))
        else:
            side = "end" if side_i % 2 == 0 else "start"
            side_i += 1
            edits.append(("strip", start, tag_end, dove_strip(f"{file}:{start}", side)))
    for kind, start, tag_end, html in reversed(edits):
        if kind == "burst":
            open_tag = main[start:main.index(">", tag_end) + 1]
            new_tag = open_tag.replace('class="band', 'class="band has-burst', 1)
            main = main[:start] + new_tag + "\n" + html + main[start + len(open_tag):]
        else:
            end = main.index("</section>", start)
            main = main[:end] + f'<div class="container bloco-wrap">{html}</div>\n' + main[end:]
    return MOTIF_DEFS + "\n" + main


KEY_MILESTONES = {4, 5}  # DesignOps Lead and Director of Design carry the diamond
PROOF_LINKS = [("container-alliance.webp", "Container Alliance", "work.html#container-alliance"),
               ("fetchly-website.jpg", "Fetchly Website", "case-fetchly-website.html"),
               ("nomad.jpg", "Nomad", "work.html")]


def short_date(t, iso):
    d = date.fromisoformat(iso)
    return f'{d.day} {t["months_short"][d.month - 1]}'


def bars_html(series, key, peak_label, tip_label, t, date_key):
    """Bars for a chart: height relative to the peak, the peak labelled, a title on each bar."""
    peak = max(x[key] for x in series) or 1
    peak_i = max(range(len(series)), key=lambda i: series[i][key])
    side = ' data-side="start"' if peak_i < len(series) * 0.4 else ""
    out = []
    for i, x in enumerate(series):
        n = x[key]
        zero = ' class="is-zero"' if n == 0 else ""
        peak_attr = f' data-peak="{peak_label.format(n=n)}"{side}' if i == peak_i else ""
        out.append(f'<li style="--h:{n / peak:.3f};--i:{i}"{zero} title="{tip_label.format(date=fmt_date(t, x[date_key]), n=n)}"{peak_attr}></li>')
    return "".join(out), peak, peak_i


def claude_mark():
    vb, inner = next((v, i) for n, v, i in LOGOS if n == "Claude")
    return f'<svg viewBox="{vb}" fill="currentColor" aria-hidden="true" focusable="false">{inner}</svg>'


SPLIT_TOP = 3  # tools named in the split; the rest are "Other"
# The page is built with the snapshots in this folder; assets/js/stats.js then swaps in the latest ones
# from main, which scripts/refresh_stats.sh commits twice a day, so the numbers stay current between deploys.
STATS_SRC = "https://raw.githubusercontent.com/oliveira-teixeira/design-ships/main/"
STATS_KEYS = ["date", "months", "months_short", "cc_span", "cc_peak", "cc_day_title", "cc_chart_label",
              "cc_tool_names", "cc_other", "gh_peak", "gh_week_title", "gh_chart_label"]


def stats_pair(c):
    """Two charts side by side with their logos: Claude Code (the wider one, it has more to show)
    and GitHub. Numbers come from claude_snapshot.py and github_snapshot.py; totals only."""
    t = c.t
    sep = "," if c.L["code"] == "en" else "."
    cc = json.loads((ROOT / "claude_snapshot.json").read_text())
    gh = json.loads((ROOT / "github_snapshot.json").read_text())

    def figs(pairs):
        return "".join(f'<div><dt class="num">{n}</dt><dd>{label}</dd></div>' for n, label in pairs)

    # Claude Code: actions per day, then the same actions split by tool
    daily = cc["daily"]
    cc_bars, cc_peak, cc_pi = bars_html(daily, "actions", t["cc_peak"], t["cc_day_title"], t, "date")
    cc_label = t["cc_chart_label"].format(start=fmt_date(t, cc["from"]), end=fmt_date(t, cc["to"]),
                                          peak_day=fmt_date(t, daily[cc_pi]["date"]), peak=cc_peak)
    f = t["cc_figs"]
    cc_figs = figs([(f'{cc["actions"]:,}'.replace(",", sep), f[0]), (cc["sessions"], f[1]), (cc["active_days"], f[2])])
    named = cc["tools"][:SPLIT_TOP]
    parts = [(t["cc_tool_names"].get(x["name"], x["name"]), x["actions"]) for x in named]
    parts.append((t["cc_other"], cc["actions"] - sum(x["actions"] for x in named)))
    split = "".join(
        f'<li style="--w:{n / cc["actions"]:.4f}" data-k="{k}"><span class="sc-key" aria-hidden="true"></span>'
        f'{name} <span class="num">{round(100 * n / cc["actions"])}%</span></li>'
        for k, (name, n) in enumerate(parts))
    split_bar = "".join(f'<span style="--w:{n / cc["actions"]:.4f}" data-k="{k}"></span>' for k, (_, n) in enumerate(parts))

    # GitHub: commits per week over twelve months
    weeks = gh["weeks"]
    gh_bars, gh_peak, gh_pi = bars_html(weeks, "commits", t["gh_peak"], t["gh_week_title"], t, "start")
    gh_label = t["gh_chart_label"].format(start=fmt_date(t, gh["from"]), end=fmt_date(t, gh["to"]),
                                          peak_week=fmt_date(t, weeks[gh_pi]["start"]), peak=gh_peak)
    g = t["gh_figs"]
    gh_figs = figs([(f'{gh["commits"]:,}'.replace(",", sep), g[0]), (f'{gh["pull_requests"]:,}'.replace(",", sep), g[1])])
    gh_from = date.fromisoformat(gh["from"])
    gh_to = date.fromisoformat(gh["to"])

    public = f'<a href="{gh["public_repo"]["url"]}" rel="noopener">{t["gh_public"]}{EXTERNAL}</a>'
    note = t["stats_note"].format(date=f'<time datetime="{cc["to"]}" data-stats-date>{fmt_date(t, cc["to"])}</time>', public=public)
    live = {"src": {"cc": STATS_SRC + "claude_snapshot.json", "gh": STATS_SRC + "github_snapshot.json"},
            "built": {"cc": [cc["to"], cc["actions"]], "gh": [gh["to"], gh["commits"]]},
            "sep": sep, "top": SPLIT_TOP, "t": {k: t[k] for k in STATS_KEYS}}
    return f"""<div class="stats-pair" data-stats="{escape(json.dumps(live, ensure_ascii=False))}">
      <section class="sc sc--cc" aria-labelledby="sc-cc">
        <header class="sc-head"><span class="sc-mark sc-mark--claude">{claude_mark()}</span><h3 class="sc-name" id="sc-cc">Claude Code</h3><span class="sc-span">{t['cc_span'].format(start=short_date(t, cc['from']))}</span></header>
        <dl class="sc-figs">{cc_figs}</dl>
        <figure class="gh-chart">
          <ol class="gh-bars" style="--n:{len(daily)}" role="img" aria-label="{escape(cc_label)}">{cc_bars}</ol>
          <div class="sc-axis" aria-hidden="true"><span>{short_date(t, cc['from'])}</span><span>{short_date(t, cc['to'])}</span></div>
        </figure>
        <div class="sc-split"><div class="sc-split-bar" aria-hidden="true">{split_bar}</div><ol aria-label="{t['cc_split_h']}">{split}</ol></div>
      </section>
      <section class="sc sc--gh" aria-labelledby="sc-gh">
        <header class="sc-head"><span class="sc-mark">{GITHUB_MARK}</span><h3 class="sc-name" id="sc-gh">GitHub</h3><span class="sc-span">{t['gh_span']}</span></header>
        <dl class="sc-figs">{gh_figs}</dl>
        <figure class="gh-chart">
          <ol class="gh-bars" style="--n:{len(weeks)}" role="img" aria-label="{escape(gh_label)}">{gh_bars}</ol>
          <div class="sc-axis" aria-hidden="true"><span>{t['months_short'][gh_from.month - 1]} {gh_from.year}</span><span>{t['months_short'][gh_to.month - 1]} {gh_to.year}</span></div>
        </figure>
        <a class="sc-link" href="{gh['url']}" rel="noopener">github.com/{gh['login']}{ARROW}</a>
      </section>
    </div>
    <p class="stats-note">{note}</p>"""


def about(c):
    t = c.t
    meta = "".join(f"<span>{m}</span>" for m in t["about_meta"])
    who = "".join(f'<p{" class=" + chr(34) + "big" + chr(34) if i == 0 else ""}>{p}</p>' for i, p in enumerate(t["about_who_p"]))
    principles = "".join(f'<li><h3 class="h3">{a}</h3><p>{b}</p></li>' for a, b in t["about_principles"])
    milestones = "".join(
        '<li%s><p class="when">%s</p><div><h3 class="h3">%s</h3><p>%s</p></div></li>'
        % (' class="is-key"' if i in KEY_MILESTONES else "", when, what, body)
        for i, (when, what, body) in enumerate(t["about_milestones"])
    )
    proofs = "".join(
        f'<article class="proof">{img(c, f)}<h3 class="h3-l">{name}</h3><p class="role">{role}</p><p class="what">{what}</p>'
        f'<p class="result">{result}</p><a class="more-link" href="{href}">{label}{ARROW}</a></article>'
        for (f, name, href), (role, what, result, label) in zip(PROOF_LINKS, t["about_proofs"])
    )
    practices = "".join(f"<li><strong>{a}</strong><span>{b}</span></li>" for a, b in t["about_practices"])
    voices = "".join(f'<div class="voice"><p>{a}</p><cite>{b}</cite></div>' for a, b in t["about_voices"])
    checks = "".join(f"<li>{x}</li>" for x in t["about_checks"])
    faq = "".join(f"<li><details><summary>{q}{PLUS}</summary><p class=\"answer\">{a}</p></details></li>" for q, a in t["about_faq"])
    R = c.R
    main = f"""<section class="band hero-a" data-tone="berry" aria-labelledby="about-title">
  <div class="container">
    <h1 class="display" id="about-title">{t['about_h1']}</h1>
    <p class="lead">{t['about_lead']}</p>
    <p class="hero-meta">{meta}</p>
    <div class="actions"><a class="btn" href="#resume">{t['about_jump']}{DOWN}</a></div>
    <div class="wall-wrap">{tile_wall(t['wall_label'])}</div>
    <div class="wall-bar">
      <p class="wall-note">{t['wall_note']} <span data-wall-hint hidden>{t['wall_hint']}</span></p>
      <div class="actions"><button class="btn" type="button" data-wall-scramble>{t['wall_scramble']}</button><button class="btn btn--solid" type="button" data-wall-spell>{t['wall_spell']}</button></div>
      <p class="wall-status" data-wall-status aria-live="polite"></p>
    </div>
  </div>
</section>

<section class="band" data-tone="blush" aria-labelledby="who-title">
  <div class="container">
    <div class="intro-grid">
      <h2 class="h2" id="who-title">{t['about_who']}</h2>
      <div class="prose">{who}</div>
    </div>
    <ul class="trio principles">{principles}</ul>
  </div>
</section>

<section class="band" data-tone="blush" aria-labelledby="milestones-title">
  <div class="container">
    <h2 class="h2" id="milestones-title">{t['about_milestones_h']}</h2>
    <ol class="milestones">{milestones}</ol>
  </div>
</section>

<section class="band" data-tone="mist" aria-labelledby="proof-title">
  <div class="container">
    <h2 class="h2" id="proof-title">{t['about_proof_h']}</h2>
    <div class="proof-grid">{proofs}</div>
  </div>
</section>

<section class="band" data-tone="mist" aria-labelledby="impact-title">
  <div class="container">
    <h2 class="h2" id="impact-title">{t['about_impact_h']}</h2>
    {ledger(t['about_ledger'], t['arrow_sr'])}
    <p class="ledger-note">{t['about_ledger_note']}</p>
    {stats_pair(c)}
  </div>
</section>

<section class="band" data-tone="cream" aria-labelledby="lead-title">
  <div class="container">
    <h2 class="h2" id="lead-title">{t['about_lead_h']}</h2>
    <div class="lead-grid">
      <ul class="practices">{practices}</ul>
      <div class="unique">
        <p class="big">{t['about_unique_big']}</p>
        <p>{t['about_unique_p']}</p>
        <div class="voices">{voices}</div>
      </div>
    </div>
  </div>
</section>

<section class="band action" data-tone="field" id="resume" aria-labelledby="resume-title">
  <div class="container">
    <div class="action-grid">
      <div>
        <h2 class="h2" id="resume-title">{t['about_resume_h']}</h2>
        <p class="lead">{t['about_resume_lead']}</p>
        <div class="actions">
          {cv_btn(c, solid=True)}
          {btn(t['get_in_touch'], 'contact.html')}
        </div>
        <p class="file-note">{t['about_file_note']}</p>
        <p class="cv-status" data-cv-status aria-live="polite"></p>
        <ul class="checks">{checks}</ul>
      </div>
      <div class="resume-stack">
        <a class="resume-sheet" href="{R}{CV}" download="Lucas_Teixeira_Resume.pdf" data-cv aria-label="{t['about_cv_label']}">
          <img src="{R}assets/cv/resume-page-1.jpg" alt="{t['about_cv_alt']}" width="1082" height="1400" loading="lazy" decoding="async">
          <span class="badge-pdf">PDF</span>
        </a>
      </div>
    </div>
  </div>
</section>

<section class="band faq-a" data-tone="blush" aria-labelledby="faq-title">
  <div class="container">
    <h2 class="h2" id="faq-title">{t['about_faq_h']}</h2>
    <ul class="faq">{faq}</ul>
  </div>
</section>"""
    write_page(c, t["about_title"], t["about_desc"], main, css=("assets/css/about.css",), js=("assets/js/tiles.js", "assets/js/stats.js"), body_class="page-about", tiles=False)


# ---------------------------------------------------------------- Contact

def contact(c):
    t = c.t
    steps = "".join(f'<li><span class="num">0{i + 1}</span><h3 class="h3">{a}</h3><p>{b}</p></li>' for i, (a, b) in enumerate(t["contact_steps"]))
    voice = t["about_voices"][0]
    faq = "".join(
        f'<li><details><summary>{q}{PLUS}</summary>'
        f'<p class="answer{" todo" if a is None else ""}">{a if a else t["contact_faq_todo"]}</p></details></li>'
        for q, a in t["contact_faq"]
    )
    clock = f'<time data-clock class="num">{t["local_time"]}</time>'
    main = f"""<section class="band page-head" data-tone="blush">
  <div class="container">
    <h1 class="display">{t['contact_h1']}</h1>
    <p class="lead">{t['contact_lead']}</p>
    <div class="actions">
      {btn(t['contact_write_btn'], '#write', solid=True, icon=DOWN)}
      <a class="btn" href="mailto:{EMAIL}">{EMAIL}</a>
    </div>
  </div>
</section>
<section class="band" data-tone="mist" aria-labelledby="steps-title">
  <div class="container">
    <h2 class="h2" id="steps-title">{t['contact_steps_h']}</h2>
    <ol class="steps">{steps}</ol>
  </div>
</section>
<section class="band" data-tone="cream" aria-labelledby="proof-title">
  <div class="container">
    <h2 class="h2" id="proof-title">{t['contact_proof_h']}</h2>
    {ledger(t['results'], t['arrow_sr'])}
    <div class="voice voice--wide"><p>{voice[0]}</p><cite>{voice[1]}</cite></div>
  </div>
</section>
<section class="band" data-tone="paper" id="write" aria-labelledby="write-title">
  <div class="container contact-grid">
    <div>
      <h2 class="h2" id="write-title">{t['contact_write_h']}</h2>
      <dl class="contact-facts">
        <div>{ICON_MAIL}<dt>{t['contact_email']}</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
        <div>{ICON_PIN}<dt>{t['contact_based']}</dt><dd>{t['contact_based_dd'].format(clock=clock)}</dd></div>
        <div>{ICON_LINK}<dt>{t['contact_linkedin']}</dt><dd><a href="{LINKEDIN}" rel="noopener">linkedin.com/in/lucastexr{EXTERNAL}</a></dd></div>
      </dl>
    </div>
    <form class="form" id="contact-form" novalidate>
      <div class="field"><label for="name">{t['form_name']}</label><input id="name" name="name" autocomplete="name" placeholder="{t['form_name_ph']}" required aria-describedby="name-error"><p class="error" id="name-error" aria-live="polite"></p></div>
      <div class="field"><label for="email">{t['form_email']}</label><input id="email" name="email" type="email" autocomplete="email" placeholder="you@company.com" required aria-describedby="email-error"><p class="error" id="email-error" aria-live="polite"></p></div>
      <div class="field"><label for="message">{t['form_message']}</label><textarea id="message" name="message" placeholder="{t['form_message_ph']}" required aria-describedby="message-error"></textarea><p class="error" id="message-error" aria-live="polite"></p></div>
      <div class="actions"><button class="btn btn--solid" type="submit">{t['form_send']}{ARROW}</button></div>
      <p class="form-note" aria-live="polite">{t['form_note']}</p>
    </form>
  </div>
</section>
<section class="band" data-tone="paper" aria-labelledby="faq-title">
  <div class="container">
    <h2 class="h2" id="faq-title">{t['contact_faq_h']}</h2>
    <ul class="faq">{faq}</ul>
  </div>
</section>"""
    write_page(c, t["contact_title"], t["contact_desc"], main)


# ---------------------------------------------------------------- Build

# ---------------------------------------------------------------- Merch
# A Fetchly merch line, from the brand book out (assets Lucas sent on 9 Oct 2026, resized into
# images/merch/). Paper under the images, pales for the reading stops.
MERCH_BOOK = ["book-cover", "book-color", "book-neutrals", "book-maps"]
MERCH_MAT = ["mat-steel", "mat-paper", "mat-concrete", "mat-stained"]
MERCH_LINE = ["line-beanie", "line-cap", "line-cardigan", "line-zip-hoodie", "line-wind-vest", "line-training-tee", "line-tote", "line-duffel",
              "line-crossbody", "line-bottle", "line-notebook", "line-pen", "line-keyboard", "line-mouse-pad", "line-socks", "line-stickers"]
MERCH_PAIRS = [("notebook", "v1-notebook", "line-notebook"), ("towel", "v1-towel", "final-towel"), ("cards", "v1-cards", "final-cards")]
MERCH_CAMPAIGN = [("shot-01-hero", "is-wide"), ("shot-02-stone-cardigan", ""), ("shot-03-silver", ""), ("shot-05-duo", "is-wide"),
                  ("shot-04-silk-claw", ""), ("shot-08-wind-vest", ""), ("shot-10-hands", ""), ("shot-09-desk", "is-wide"),
                  ("shot-12-vest-detail", ""), ("shot-11-departure", "is-full")]


def merch_fig(c, slug, cap, cls=""):
    klass = f"m-fig {cls}".strip()
    return (f'<figure class="{klass}"><div class="frame"><img src="{c.R}images/merch/{slug}.jpg" alt="{escape(cap)}" loading="lazy" decoding="async"></div>'
            f'<figcaption class="note">{cap}</figcaption></figure>')


def merch(c):
    t = c.t
    def intro(key, hid):
        return f'<div class="intro-grid"><h2 class="h2" id="{hid}">{t[key + "_h"]}</h2><p class="big">{t[key + "_p"]}</p></div>'
    book = "".join(merch_fig(c, s, cap) for s, cap in zip(MERCH_BOOK, t["merch_book_caps"]))
    mats = "".join(merch_fig(c, s, cap) for s, cap in zip(MERCH_MAT, t["merch_mat_caps"]))
    line = "".join(merch_fig(c, s, t["merch_items"][s]) for s in MERCH_LINE)
    pairs = "".join(
        f'<div class="m-pair"><h3 class="h3">{t["merch_iter_caps"][k]}</h3><div class="m-pair-row">'
        f'{merch_fig(c, a, t["merch_first"])}{merch_fig(c, b, t["merch_final"])}</div></div>' for k, a, b in MERCH_PAIRS)
    camp = "".join(merch_fig(c, s, t["merch_camp_caps"][s], cls) for s, cls in MERCH_CAMPAIGN)
    main = f"""<section class="band page-head" data-tone="cream">
  <div class="container">
    <h1 class="display">{t['merch_h1']}</h1>
    <p class="lead">{t['merch_lead']}</p>
    <div class="row"><p class="meta">{t['merch_count']}</p><p class="note">{t['merch_kinds']}</p></div>
  </div>
</section>
<section class="band" data-tone="paper" aria-labelledby="book-title">
  <div class="container">{intro('merch_book', 'book-title')}<div class="m-book">{book}</div></div>
</section>
<section class="band" data-tone="mist" aria-labelledby="mat-title">
  <div class="container">{intro('merch_mat', 'mat-title')}<div class="m-mat">{mats}</div></div>
</section>
<section class="band" data-tone="paper" aria-labelledby="line-title">
  <div class="container">{intro('merch_line', 'line-title')}<div class="m-line">{line}</div></div>
</section>
<section class="band" data-tone="cream" aria-labelledby="iter-title">
  <div class="container">{intro('merch_iter', 'iter-title')}<div class="m-pairs">{pairs}</div></div>
</section>
<section class="band" data-tone="paper" aria-labelledby="camp-title">
  <div class="container">{intro('merch_camp', 'camp-title')}<div class="m-mosaic m-campaign">{camp}</div></div>
</section>
{action(c, t['merch_close'], t['merch_close_lead'], btn(t['get_in_touch'], 'contact.html', solid=True) + btn(t['see_work'], 'work.html'))}"""
    write_page(c, t["merch_title"], t["merch_desc"], main)


# ---------------------------------------------------------------- Artifacts
# Every claude.ai artifact Lucas built, each exported to its own public repo (design-<name>) and served
# with GitHub Pages; artifacts.json holds the list. They sit on the Work page, after the presentations
# (Lucas, 16 Oct 2026): listed by group with their stack, the chosen one opens in an iframe; without
# JavaScript each entry is a plain link to the live page. This portfolio is not one of them.
ART_GROUPS = ["portfolio", "showcase", "client", "internal"]


def load_artifacts():
    f = ROOT / "artifacts.json"
    return json.loads(f.read_text()) if f.exists() else []


def artifact_browser(c):
    t = c.t
    items = load_artifacts()
    if not items:
        return ""
    code = c.L["code"]
    groups = []
    for g in ART_GROUPS:
        rows = [x for x in items if x["group"] == g]
        if not rows:
            continue
        lis = "".join(
            f'<li><a class="art-item" href="{x["pages_url"]}" target="_blank" rel="noopener" data-art="{x["pages_url"]}" '
            f'data-repo="{x["repo_url"]}" data-title="{escape(x["title"])}">'
            f'<span class="art-name">{escape(x["title"])}</span>'
            f'<span class="art-desc">{escape(x["description"].get(code) or x["description"]["en"])}</span>'
            f'<span class="art-stack">{"".join(f"<span>{escape(s)}</span>" for s in x["stack"])}</span></a></li>'
            for x in rows)
        groups.append(f'<div class="art-group"><h3 class="meta">{t["art_groups"][g]}</h3><ul>{lis}</ul></div>')
    first = items[0]
    viewer = (f'<div class="art-viewer" data-art-viewer data-frame-label="{escape(t["art_frame_label"])}">'
              f'<div class="art-bar"><p class="art-now" data-art-now>{escape(first["title"])}</p>'
              f'<div class="art-links"><a class="btn" data-art-open href="{first["pages_url"]}" target="_blank" rel="noopener">{t["art_open"]}{EXTERNAL}</a>'
              f'<a class="btn" data-art-repo href="{first["repo_url"]}" target="_blank" rel="noopener">{t["art_repo"]}{EXTERNAL}</a></div></div>'
              f'<div class="art-frame"><iframe data-art-frame title="{escape(t["art_frame_label"].format(title=first["title"]))}" '
              f'src="{first["pages_url"]}" loading="lazy" referrerpolicy="no-referrer"></iframe></div>'
              f'<p class="note art-note">{t["art_note"]}</p></div>')
    return f"""<section class="band" data-tone="paper" id="artifacts" aria-labelledby="art-title">
  <div class="container">
    <div class="intro-grid"><h2 class="h2" id="art-title">{t['art_h']}</h2><p class="big">{t['art_lead']}</p></div>
    <p class="meta art-count">{t['art_count'].format(n=len(items))}</p>
    <div class="art-layout"><nav class="art-list" aria-label="{t['art_list_h']}">{"".join(groups)}</nav>{viewer}</div>
  </div>
</section>"""


def artifacts(c):
    """The old Artifacts address forwards to the section on the Work page, so shared links keep working."""
    target = "work.html#artifacts"
    html = f"""<!doctype html>
<html lang="{c.L['html']}">
<head>
<meta charset="utf-8">
<title>{escape(c.t['art_h'])}, Lucas Teixeira</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{page_url(c.L, 'work.html')}">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace("{target}");</script>
</head>
<body><a href="{target}">{escape(c.t['art_h'])}</a></body>
</html>
"""
    out = ROOT / c.L["dir"] / c.file
    out.write_text(html, encoding="utf-8")


PAGES = [
    ("index.html", "home", home),
    ("work.html", "work", work),
    ("merch.html", "merch", merch),
    ("artifacts.html", "artifacts", artifacts),
    ("case-fetchly-website.html", "work", case),
    ("process.html", "process", process),
    ("writing.html", "writing", writing),
    ("essay-on-thinking-systems.html", "writing", essay),
    ("photography.html", "photography", photography),
    ("about.html", "about", about),
    ("contact.html", "contact", contact),
]


def check_locales():
    base = set(en.T)
    for L in LANGS[1:]:
        missing, extra = base - set(L["t"]), set(L["t"]) - base
        assert not missing and not extra, f'{L["code"]}: missing {sorted(missing)}, extra {sorted(extra)}'
        for k, v in en.T.items():
            if isinstance(v, (list, dict)):
                assert len(v) == len(L["t"][k]), f'{L["code"]}: {k} has {len(L["t"][k])} items, English has {len(v)}'


if __name__ == "__main__":
    check_locales()
    for L in LANGS:
        for file, current, build in PAGES:
            build(Ctx(L, file, current))
    # Favicon: the ibis on Field
    (ROOT / "assets/img/favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-60 -40 620 620"><rect x="-60" y="-40" width="620" height="620" rx="120" fill="#2C5846"/>'
        '<g transform="translate(40 40) scale(0.9)">' + "".join(f'<path fill="#FCFCFC" d="{d}"/>' for d in IBIS) + "</g></svg>", encoding="utf-8")
    print("Built", len(PAGES) * len(LANGS), "pages:", ", ".join(L["dir"] or "/" for L in LANGS))
