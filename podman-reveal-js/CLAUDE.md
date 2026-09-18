# CLAUDE.md — podman-reveal-js

Containerised reveal-md for authoring Markdown-based presentations.
All slide projects reference this container. Full authoring reference is in `README.md`.

## Container

```bash
# Build (one-time or on update)
podman build -t reveal-js:latest .

# Pin a specific reveal-md version
podman build --build-arg REVEAL_MD_VERSION=6.1.4 -t reveal-js:6.1.4 .
```

## Running a Deck

```bash
cd /path/to/deck/folder
podman run --rm -p 1948:1948 -v ${PWD}:/slides:Z reveal-js:latest \
  /slides/slides.md --host 0.0.0.0
# → http://127.0.0.1:1948
```

## Pre-flight Overflow Check

```bash
podman run --rm -v ${PWD}:/slides:Z reveal-js:latest preflight /slides/slides.md
```

## Sample Slides (Design Reference)

`sample-slides/` — a live demo deck showing every available layout pattern.
Use this as a copy-paste library when building new decks.

```bash
cd sample-slides
podman run --rm -p 1948:1948 -v ${PWD}:/slides:Z reveal-js:latest \
  /slides/slides.md --host 0.0.0.0
```

Font: Plus Jakarta Sans (Google Fonts) — closest public match to Google Sans.
Accent colour: `#1a73e8` (Google blue).

## Active Slide Decks

- `~/workarea/slides/ansible-use-cases/` — Ansible Automation Use Case Gallery
  - Theme: white + `#EE0000` (red accent)
  - Hosted on Cloudflare Pages (`npm run build` in `~/workarea/slides/`)
- `~/ansible/automation-consutling-services/consulting-service-helper/` — Consulting helper deck
  - Same red theme, private use

## Deck File Structure

Every deck is a folder with:
```
my-deck/
├── slides.md     # Markdown content (reveal-md format)
├── custom.css    # Theme + layout patterns
└── plugins.js    # Footer injection (date or label)
```

## Frontmatter Template

```yaml
---
title: Deck Title
theme: white
css: custom.css
scripts:
  - plugins.js
revealOptions:
  transition: slide
  transitionSpeed: fast
  center: false
  slideNumber: true
  controls: true
  progress: true
  width: 1280
  height: 720
  margin: 0.04
  minScale: 0.2
  maxScale: 2.0
---
```

## Layout Patterns (all in custom.css)

| # | Name | Class(es) | Ideal for |
|---|---|---|---|
| 1 | Card grid 2-col | `.card-grid` | 4–6 named concepts with short descriptions |
| 2 | Card grid 3-col | `.card-grid.three-col` | 6–9 short concepts |
| 3 | Numbered pillars | `.pillar-grid` + `.pillar` | Ordered rules/principles — numbered emphasis |
| 4 | Split layout | `.split-layout` + `.split-headline` + `.rule-list` | Big label left, dense list right |
| 5 | Stat row | `.stat-row` + `.stat-item` + `.stat-number` | 3 key metrics or percentages |
| 6 | Two-column list | `.two-col-list` | 5–8 text-heavy items, cleaner than cards |
| 7 | Checklist | `.checklist` + `li.no` | Do/don't — ✓ green or ✗ red prefix |
| 8 | Process steps | `.process-steps` + `.step` | 3–5 sequential phases with arrows |
| 9 | Highlight band | `.highlight-band` / `.dark` / `.light` | Full-width callout bar mid-slide |
| 10 | Full-bleed blue/dark | `bg-blue` / `bg-dark` + `data-background-color` | Section transitions, closing slides |
| 11 | Two-col with headers | `.col-layout` + `.col-header` | Before/After, Benefits/Risks |
| 12 | Alternating table | automatic on all Markdown tables | Data-heavy slides, 5+ rows |

## Key Authoring Patterns

**Section label** (small accent text above heading):
```markdown
*Section Name*

## Slide Title
```

**Section divider with ID** (for agenda links):
```markdown
<!-- .slide: class="vcenter" id="my-section" -->
# Section Title
```

**Full-bleed colored slide:**
```markdown
<!-- .slide: class="vcenter bg-blue" data-background-color="#1a73e8" -->
# White Text on Blue
```

**Vertical slides** (↓ navigation):
```markdown
## Parent Slide

--

## Child Slide 1

--

## Child Slide 2
```

**Agenda with anchor links:**
```markdown
- [Section Name](#/section-id)
```

## plugins.js — Footer

```js
window.addEventListener('load', function () {
  var footer = document.createElement('div');
  footer.className = 'global-footer';
  footer.textContent = 'Last updated: 2026-09-17';
  document.body.appendChild(footer);
});
```

Update the date string when the deck changes. `position: fixed` on `body` means one element persists across all slides.

## Speaker Notes

Add notes to any slide with the `Note:` keyword — only visible in the speaker window, never on the slide:

```markdown
## Slide Title

Content here.

Note:
This text only appears in the speaker notes window.
Write as much as you want — talking points, reminders, context.
```

Press `S` to open the speaker notes popup — shows current slide, next slide preview, notes, and a timer.

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `→` / `Space` | Next slide |
| `←` | Previous slide |
| `↓` | Next vertical slide |
| `O` or `Esc` | Overview mode (thumbnail grid) |
| `F` | Fullscreen |
| `S` | Speaker notes window |

## Full Authoring Reference

See `README.md` in this directory — detailed code examples for every layout pattern.
