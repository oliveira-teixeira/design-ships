# Ships

The portfolio of Lucas Teixeira, Director of Design at Fetchly Labs, as a working prototype in English, Brazilian Portuguese and Latin American Spanish.

Live: https://oliveira-teixeira.github.io/design-ships/

## Stack

- Static site generator in Python 3 (`build.py`): one template set, copy in `locales/en.py`, `pt.py` and `es.py`, 30 pages
- Content model shared with Decap CMS (`content/work/*.md`, front matter parsed by the build)
- HTML, CSS and vanilla JavaScript, no framework
- Scroll driven color: registered CSS custom properties (`@property`) that blend as each section reaches the middle of the screen
- GSAP 3.12.5 and ScrollTrigger (cdnjs) for the footer badge and the Athos Bulcão tile ribbons
- Inter from Google Fonts
- Data snapshots from the GitHub CLI and Claude Code session logs (`github_snapshot.py`, `claude_snapshot.py`)
- Design system recorded in `DESIGN.md`
- WCAG 2.1 AAA as the target: 7:1 text contrast, 44px targets, reduced motion respected

## Run

```
python3 build.py
```

Exported from a claude.ai artifact on 9 Oct 2026.
