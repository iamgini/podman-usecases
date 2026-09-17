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

Patterns and customisations for `slides.md` + `custom.css` + `plugins.js`.

---

### Frontmatter

```yaml
---
title: My Presentation
theme: white            # base reveal.js theme
css: custom.css         # your custom stylesheet
scripts:
  - plugin/search/search.js   # enables Ctrl+Shift+F search (built into reveal.js)
  - plugins.js                # footer injection + search registration
revealOptions:
  transition: slide
  transitionSpeed: fast       # default | fast | slow
  center: false               # top-aligned slides; use vcenter class to opt back in per slide
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

---

### Slide separators

| Syntax | Effect |
|---|---|
| `---` | Next horizontal slide |
| `--` | Next vertical slide (press ↓) |

---

### Section label (small red text above heading)

Standalone italic line immediately before a `##` heading:

```markdown
*Section Name*

## Slide Title
```

CSS targets `em` that is the **only child** of its `<p>` — inline italics in sentences are unaffected.
Renders as a small red label (`0.6em`, no italics). Shows the audience which section they're in.

---

### Vertical centering per slide

`center: false` makes all slides top-aligned. To centre a specific slide (section dividers, title slides):

```markdown
<!-- .slide: class="vcenter" -->
# Section Title
```

The `vcenter` CSS rule uses `top: 50%; transform: translateY(-50%)` and clears `padding-top`.

---

### Slide IDs and anchor links (for agenda navigation)

Add an `id` to any slide and link to it from your agenda:

```markdown
<!-- .slide: class="vcenter" id="cloud" -->
# Cloud Automation
```

In the agenda:
```markdown
- [Cloud Automation](#/cloud)
- [Security & Compliance](#/security)
```

reveal.js resolves `#/<id>` to the matching slide — clicking jumps directly to it.

---

### Layout quick-reference

| Layout | Class / Trigger | Best for |
|---|---|---|
| Card grid 2-col | `.card-grid` | 4–6 named concepts with short descriptions |
| Card grid 3-col | `.card-grid.three-col` | 6–9 short concepts |
| Numbered pillars | `.pillar-grid` | 6 ordered rules/principles — numbered emphasis |
| Split layout | `.split-layout` | Big label left + dense content list right |
| Stat row | `.stat-row` | 3 key metrics or percentages |
| Two-column list | `.two-col-list` | 5–8 items too long for cards but short enough to split |
| Checklist | `.checklist` | Do/don't lists — ✓ green or ✗ red prefix |
| Process steps | `.process-steps` | 3–5 sequential phases with arrows |
| Highlight band | `.highlight-band` | Full-width callout bar mid-slide |
| Full-bleed red | `bg-red` + `data-background-color` | High-impact section transitions |
| Full-bleed dark | `bg-dark` + `data-background-color` | Closing slides, premium/serious tone |
| Two-col with headers | `.col-layout` + `.col-header` | Before/After, Benefits/Risks comparisons |
| Alternating table | (automatic on all tables) | Data-heavy slides with 5+ rows |

---

### Layout 1 — Card grid

**2-column** (ideal for 4 items — 2×2):

```html
<div class="card-grid">
  <div class="card">
    <h4>Card Title</h4>
    <p>Description — aim for 2 lines max.</p>
  </div>
  <div class="card">
    <h4>Card Title</h4>
    <p>Description.</p>
  </div>
</div>
```

**3-column** (ideal for 6 or 9 items):

```html
<div class="card-grid three-col">
  <div class="card"> … </div>
  <div class="card"> … </div>
  <div class="card"> … </div>
</div>
```

Cards have a red left border, light background, bold `h4` title, small `p` text (`0.8em`).

> Use `&amp;` for `&` inside HTML blocks — raw `&` breaks HTML parsing.

---

### Layout 2 — Numbered pillars

Big red number prefix (`01`, `02`…) + title + description. 2-column grid.
Use when the ordering or count matters, or when cards feel too boxy.

```html
<div class="pillar-grid">
  <div class="pillar">
    <span class="pillar-num">01</span>
    <div>
      <div class="pillar-title">Rule Title</div>
      <div class="pillar-desc">Short description — 1–2 lines.</div>
    </div>
  </div>
  <div class="pillar">
    <span class="pillar-num">02</span>
    <div>
      <div class="pillar-title">Rule Title</div>
      <div class="pillar-desc">Short description.</div>
    </div>
  </div>
</div>
```

---

### Layout 3 — Split layout

Large red heading on the left (~34%), content list on the right. Inspired by consulting decks.
Use for guardrails, principles, or anything with a strong rhetorical label.

```html
<div class="split-layout">
  <div class="split-left">
    <div class="split-headline">Big Label<br>Here</div>
    <div class="split-sub">Optional subtitle text.</div>
  </div>
  <div class="split-right">
    <div class="rule-list">
      <div class="rule-item"><strong>Bold Term</strong> — Description sentence.</div>
      <div class="rule-item"><strong>Bold Term</strong> — Description sentence.</div>
    </div>
  </div>
</div>
```

`**bold**` renders red (existing theme rule) — use it for the key term in each row.

---

### Layout 4 — Stat row

Three large numbers/metrics in a grey row with dividers between them.
Use for impact slides, survey results, or KPI summaries.

```html
<div class="stat-row">
  <div class="stat-item">
    <span class="stat-number">96%</span>
    <div class="stat-label">Short caption describing the metric.</div>
  </div>
  <div class="stat-item">
    <span class="stat-number">4h</span>
    <div class="stat-label">Another metric caption.</div>
  </div>
  <div class="stat-item">
    <span class="stat-number">3×</span>
    <div class="stat-label">Third metric caption.</div>
  </div>
</div>
```

---

### Layout 5 — Two-column list

Items flow into two columns automatically (CSS `columns: 2`). No boxes — cleaner than cards when content is text-heavy.

```html
<div class="two-col-list">
  <div><strong>Term</strong> — Description of the item.</div>
  <div><strong>Term</strong> — Description of the item.</div>
  <div><strong>Term</strong> — Description of the item.</div>
  <div><strong>Term</strong> — Description of the item.</div>
</div>
```

Items are separated by a light horizontal rule. Use 5–8 items for a clean 2-col balance.

---

### Layout 6 — Checklist

Items prefixed with ✓ (green) or ✗ (red). Use `class="no"` on `<li>` for the ✗ variant.
Works well for do/don't rules, guardrails, or audit checklists.

```html
<ul class="checklist">
  <li>This is a good practice — green tick.</li>
  <li class="no">This is a violation — red cross.</li>
  <li class="no">Another prohibited action.</li>
</ul>
```

Renders in 2 columns automatically. Mix ✓/✗ in the same list.

---

### Layout 7 — Process steps

Horizontal flow of 3–5 steps with red left borders and grey arrow connectors.
Use for engagement phases, workflows, or delivery sequences.

```html
<div class="process-steps">
  <div class="step">
    <span class="step-num">01</span>
    <div class="step-title">Phase Name</div>
    <div class="step-desc">What happens. 1–2 lines.</div>
  </div>
  <div class="step">
    <span class="step-num">02</span>
    <div class="step-title">Phase Name</div>
    <div class="step-desc">What happens.</div>
  </div>
  <div class="step">
    <span class="step-num">03</span>
    <div class="step-title">Phase Name</div>
    <div class="step-desc">What happens.</div>
  </div>
</div>
```

Steps are separated by a `▶` arrow. Last step has no arrow.

---

### Layout 8 — Highlight band

Full-width coloured bar — breaks up a slide visually or introduces a section label inline.

```html
<!-- Red (default) -->
<div class="highlight-band">Key message or callout text goes here.</div>

<!-- Dark background -->
<div class="highlight-band dark">Dark variant.</div>

<!-- Light — red text on grey -->
<div class="highlight-band light">Light variant.</div>
```

Useful above a stat row or between two content blocks on the same slide.

---

### Layout 9 — Full-bleed colored section slides

Solid-color background covering the entire slide. Use for section transitions or closing slides.
Requires two things: a `data-background-color` attribute (handled by reveal.js, truly full-bleed) and a CSS class to flip text colors.

**Red background — white text:**

```markdown
<!-- .slide: class="vcenter bg-red" data-background-color="#EE0000" -->

*Section Label*

# Section Title
## Subtitle — white text on red
```

**Dark background — red heading + light text:**

```markdown
<!-- .slide: class="vcenter bg-dark" data-background-color="#1a1a1a" -->

*Section Label*

# Section Title
## Subtitle in light grey
```

`data-background-color` is a reveal.js native attribute that sets the full-bleed background layer.
The `.bg-red` / `.bg-dark` CSS classes flip heading, body, bullet, and section-label colours to match.

---

### Layout 10 — Two-column with icon+label headers

Two equal columns each with a red underlined label at the top — useful for Before/After, Benefits/Risks, or any comparison that needs clear column identity.

```html
<div class="col-layout">
  <div class="col">
    <span class="col-header">⚡ Before — Manual</span>
    <ul>
      <li>Ticket-based, 3–5 day lead time</li>
      <li>Scripts owned by individuals</li>
    </ul>
  </div>
  <div class="col">
    <span class="col-header">🚀 After — Automated</span>
    <ul>
      <li>Self-service in minutes</li>
      <li>Version-controlled, shared playbooks</li>
    </ul>
  </div>
</div>
```

The `.col-header` span renders as bold red text with a 2px red underline. Emoji icons in the label add visual identity without needing image files.

---

### Layout 11 — Alternating-row table

All Markdown tables get dark header rows and alternating even-row shading automatically — no extra markup needed.

```markdown
| Column A | Column B | Column C |
|---|---|---|
| Row 1 data | Value | Notes |
| Row 2 data | Value | Notes |
| Row 3 data | Value | Notes |
```

- Header row: dark (`#1a1a1a`) background, white text
- Even rows: light grey (`#f7f7f7`)
- Hover: very light red tint (`#fff5f5`)
- Font size: `0.82em` (fits more rows per slide)

---

### Table layout (for many items)

When cards would be too small or items have unequal descriptions:

```markdown
| Use Case | What It Does |
|---|---|
| Item One | Short description |
| Item Two | Short description |
```

Good for 6–10 items. Keep descriptions terse — one line per cell.

---

### Blockquote callout

```markdown
> Important note or cross-reference — red left border, light grey background.
```

---

### Sub-section grouping (bullets with bold labels)

For items grouped under headings (e.g. Linux / Windows):

```markdown
## OS Patching

**Linux**
- **RHEL via Satellite**: Errata-based patching with reboot orchestration.

**Windows**
- **WSUS-Driven Patching**: Category filtering, configurable reboot policies.
```

---

### Global footer (fixed position trick)

Add a footer that persists across every slide without touching each `<section>`:

In `plugins.js`:
```js
var LAST_UPDATED = '2026-09-17';   // ← update this when deck changes

window.addEventListener('load', function () {
  var footer = document.createElement('div');
  footer.className = 'global-footer';
  footer.textContent = 'Last updated: ' + LAST_UPDATED;
  document.body.appendChild(footer);
});
```

In `custom.css`:
```css
.global-footer {
  position: fixed;
  top: 0.6em;
  right: 1em;
  font-size: 12px;
  color: #bbb;
  z-index: 9999;
  pointer-events: none;
}
```

**Why it works:** `position: fixed` on a `body` child sits outside reveal.js's slide system entirely — one element, always visible, no per-slide injection needed. `pointer-events: none` lets clicks pass through to slides.

---

### Search plugin (Ctrl+Shift+F)

reveal.js ships `RevealSearch` but reveal-md doesn't load it by default.
Wire it up via `scripts` in frontmatter + a registration call in `plugins.js`:

```yaml
scripts:
  - plugin/search/search.js   # reveal-md serves reveal.js statics at /plugin/
  - plugins.js
```

```js
// in plugins.js
window.addEventListener('load', function () {
  if (window.RevealSearch && window.Reveal) {
    Reveal.registerPlugin(RevealSearch);
  }
});
```

---

### Keyboard shortcuts

| Key | Action |
|---|---|
| `→` / `Space` | Next slide |
| `←` | Previous slide |
| `↓` | Next vertical slide |
| `O` or `Esc` | Overview mode — thumbnail grid of all slides |
| `F` | Fullscreen |
| `S` | Speaker notes |
| `Ctrl+Shift+F` | Search (requires search plugin above) |

---

### White theme (custom.css) — summary

| Element | Value |
|---|---|
| Font | Red Hat Display (Google Fonts) |
| Base font size | `28px` |
| Background | `#ffffff` |
| Accent colour | `#EE0000` |
| `h1` | `250%`, weight 900 |
| `h2` | `160%`, weight 700 |
| `h3` | `110%`, weight 700, red |
| `**bold**` | Red — use for key terms |
| Bullets | Red `•` via CSS `::before` |
| Blockquote | Red left border, `#f9f9f9` background |
| Code block | `#f5f5f5` background, red left border |
| Top padding | `1.2em` on all content slides |
| `vcenter` slides | No padding; `top:50% + translateY(-50%)` |
