# podman-reveal-js

Containerised [reveal-md](https://github.com/webpro/reveal-md) — run Markdown-based Reveal.js presentations with Podman.
Includes a Python pre-flight script to detect slide overflow before presenting.

## reveal.js vs reveal-md

| | reveal.js | reveal-md |
|---|---|---|
| What it is | Core JS presentation library | CLI wrapper around reveal.js |
| Input | Hand-written HTML (`<section>` tags) | Plain Markdown (`.md` files) |
| Default port | `8000` | `1948` |
| Setup | Install library, write HTML boilerplate | Point at a `.md` file, done |
| Use case | Full custom presentations | Markdown-first, content-focused |

**We use reveal-md** — you write Markdown, it handles the HTML/JS. Port `1948` is correct.

## Build

```bash
podman build -t reveal-js:latest .

# Pin to a specific reveal-md version
podman build --build-arg REVEAL_MD_VERSION=6.1.4 -t reveal-js:6.1.4 .
```

## Serve

All three forms work — the entrypoint passes anything that isn't `preflight` or `serve` straight to reveal-md:

```bash
# Explicit
podman run --rm -p 1948:1948 -v ${PWD}:/slides:Z reveal-js:latest \
  serve /slides/slides.md --host 0.0.0.0

# Short form (backwards compatible)
podman run --rm -p 1948:1948 -v ${PWD}:/slides:Z reveal-js:latest \
  /slides/slides.md --host 0.0.0.0

# Open → http://127.0.0.1:1948
```

## Pre-flight check

Run before presenting to detect slides that will overflow.

```bash
# Basic — shows only overflowing and tight slides
podman run --rm -v ${PWD}:/slides:Z reveal-js:latest \
  preflight /slides/slides.md

# Show all slides (including OK ones)
podman run --rm -v ${PWD}:/slides:Z reveal-js:latest \
  preflight /slides/slides.md --verbose

# Override font-size (if not auto-detected from CSS)
podman run --rm -v ${PWD}:/slides:Z reveal-js:latest \
  preflight /slides/slides.md --font-size 28

# Override all dimensions (e.g. for a 4K screen)
podman run --rm -v ${PWD}:/slides:Z reveal-js:latest \
  preflight /slides/slides.md --width 1920 --height 1080 --margin 0.05
```

### Exit codes

| Code | Meaning |
|---|---|
| `0` | All slides within bounds |
| `1` | One or more slides will overflow |
| `2` | File not found |

### Output example

```
──────────────────────────────────────────────────────────────────────
  Slide Preflight Check
──────────────────────────────────────────────────────────────────────
  File        : /slides/slides.md
  Dimensions  : 1280 × 720 px  |  margin 0.04
  Font size   : 28 px  (CSS detected)
  Available   : ~622 px per slide  |  warn at 529 px (85%)
──────────────────────────────────────────────────────────────────────
  ⚠ OVERFLOW  #    7  [████████████████████] 112%  Amazon Web Services (cont.)
  △ TIGHT     #   12  [█████████████████░░░]  88%  VMware Automation
──────────────────────────────────────────────────────────────────────
  ⚠  1 slide(s) will overflow  →  split with  --  in slides.md
  △  1 slide(s) are tight (>85%)  →  consider splitting
──────────────────────────────────────────────────────────────────────
```

## Build static HTML (CDN / GitHub Pages)

```bash
podman run --rm -v ${PWD}:/slides:Z reveal-js:latest \
  /slides/slides.md --static /slides/dist --host 0.0.0.0
```

## Themes

Set in the frontmatter of your `slides.md`:

```yaml
theme: black
```

Built-in reveal.js themes:

| Theme | Style |
|---|---|
| `black` | Dark background, white text |
| `white` | Light background, dark text |
| `moon` | Dark blue, muted |
| `night` | Dark, high contrast |
| `sky` | Light blue |
| `league` | Dark grey, bold |
| `serif` | Light, editorial |
| `solarized` | Warm light |

Change the value and hard-refresh the browser — no rebuild needed.

## Upgrade reveal-md

Edit `ARG REVEAL_MD_VERSION` in Containerfile and rebuild.
Releases: https://github.com/webpro/reveal-md/releases

---

## Slide Authoring Reference

Everything below documents the customisations used in the Ansible Use Case Gallery deck. Copy any pattern into your own `slides.md` + `custom.css`.

### Frontmatter

```yaml
---
title: My Presentation
theme: white          # base reveal.js theme
css: custom.css       # your custom stylesheet
revealOptions:
  transition: slide
  transitionSpeed: fast   # default | fast | slow
  center: false           # false = top-aligned slides (recommended with custom CSS)
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

> Set `center: false` when you want content to start from the top. Use the `vcenter` class (see below) to opt individual slides back into vertical centering.

---

### Slide separators

| Syntax | Effect |
|---|---|
| `---` | Next horizontal slide |
| `--` | Next vertical slide (sub-slide, press ↓) |

---

### Section label (small red text above heading)

Write a standalone italic line immediately before a `##` heading:

```markdown
*Section Name*

## Slide Title
```

CSS rule targets `em` that is the **only child** of its `<p>` — so inline italics inside sentences are unaffected.

Renders as a small (`0.6em`) red label above the heading with no italics. Useful for showing which section the audience is in.

---

### Vertical centering (per slide)

By default (`center: false`) all slides are top-aligned. To center a specific slide (e.g. a section divider with only a title):

```markdown
<!-- .slide: class="vcenter" -->
# Section Title
```

All section/divider slides should use `vcenter`. Content slides should not.

---

### Card grid layout

Two-column (default):

```html
<div class="card-grid">
  <div class="card">
    <h4>Card Title</h4>
    <p>Short description of the feature or use case.</p>
  </div>
  <div class="card">
    <h4>Card Title</h4>
    <p>Short description.</p>
  </div>
</div>
```

Three-column (add `three-col` class):

```html
<div class="card-grid three-col">
  <div class="card"> … </div>
  <div class="card"> … </div>
  <div class="card"> … </div>
</div>
```

Cards have a red left border, light background, and a bold `h4` title. Ideal for 4–6 named concepts per slide.

> Use `&amp;` for `&` inside HTML blocks — raw `&` breaks HTML parsing.

---

### White theme (custom.css)

| Element | Style |
|---|---|
| Font | Red Hat Display (Google Fonts) |
| Base font size | `28px` on `.reveal` |
| Background | `#ffffff` |
| Headings | `#1a1a1a`, left-aligned, no uppercase |
| `h1` | `250%`, weight 900 |
| `h2` | `160%`, weight 700 |
| `h3` | `110%`, weight 700, **red** `#EE0000` |
| `**bold**` | Red `#EE0000` — use for key terms |
| Bullet `•` | Red dot via CSS `::before` (no `list-style`) |
| Blockquote | Red left border, light grey background |
| Code inline | Light grey background, dark text |
| Code block | Light grey, red left border |
| Links / controls / progress | Red `#EE0000` |
| Top padding | `1.2em` on all content slides (uniform breathing room) |

---

### Blockquote callout

```markdown
> This renders as a highlighted callout with a red left border.
```

Use for notes, cross-references, or important caveats.

---

### Two-level heading slides (sub-sections with bullets)

For slides that group items under sub-headings, use `**Bold**` for the group label and bullets below:

```markdown
## OS Patching

**Linux**
- **RHEL via Satellite**: Errata-based patching with reboot orchestration.

**Windows**
- **WSUS-Driven Patching**: Category filtering, configurable reboot policies.
```

Avoid cards here — the sub-heading structure is clearer as bullets.
