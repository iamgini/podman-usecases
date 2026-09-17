---
title: Layout Showcase — All Patterns
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

<!-- .slide: class="vcenter bg-blue" data-background-color="#1a73e8" id="title" -->

# Layout Showcase
## Every pattern, one deck — lorem ipsum dummy content

*2026 Edition*

---

<!-- .slide: id="agenda" -->

## What's Inside

- [Section Dividers](#/dividers) — plain white, full-bleed blue, full-bleed dark
- [Text & Labels](#/text) — section labels, blockquotes, grouped bullets
- [Card Grids](#/cards) — 2-column and 3-column
- [List Layouts](#/lists) — numbered pillars, two-col list, checklist
- [Split Layout](#/split) — big label left + content right
- [Data & Metrics](#/data) — stat row, process steps, alternating table
- [Special Elements](#/special) — two-col with headers, highlight bands, vertical slides

---

<!-- .slide: class="vcenter" id="dividers" -->

*Section 01*

# Section Dividers

Three variants — navigate down ↓

--

<!-- .slide: class="vcenter" -->

*Plain White*

# Standard Section Divider
## Dark heading on white — the default

--

<!-- .slide: class="vcenter bg-blue" data-background-color="#1a73e8" -->

*Full-Bleed Blue*

# High-Impact Section Divider
## White text — use for major transitions

--

<!-- .slide: class="vcenter bg-dark" data-background-color="#1a1a1a" -->

*Full-Bleed Dark*

# Premium Section Divider
## Blue heading, light body — closing or serious tone

---

<!-- .slide: id="text" -->

*Section 02*

## Text Layouts — Labels, Blockquotes, Grouped Bullets

*Standalone italic line* above a heading renders as a small uppercase accent label (that one above).

> **Blockquote callout** — use for important notes, warnings, or pull quotes. Blue left border with a tinted background. Lorem ipsum dolor sit amet, consectetur adipiscing elit.

**Group Alpha**
- **Lorem Ipsum**: Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque.
- **Dolor Sit**: Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit.

**Group Beta**
- **Consectetur**: At vero eos et accusamus et iusto odio dignissimos ducimus blanditiis.
- **Adipiscing**: Nam libero tempore cum soluta nobis est eligendi optio cumque nihil impedit.

---

<!-- .slide: id="cards" -->

*Section 03*

## Card Grid — 2 Column

<div class="card-grid">
  <div class="card">
    <h4>Scalability</h4>
    <p>Scale each service independently based on demand without touching adjacent components.</p>
  </div>
  <div class="card">
    <h4>Resilience</h4>
    <p>Isolated failures stay contained. One component going down doesn't cascade to others.</p>
  </div>
  <div class="card">
    <h4>Deployability</h4>
    <p>Release individual services on their own cycle — no full-system release trains required.</p>
  </div>
  <div class="card">
    <h4>Observability</h4>
    <p>Per-service metrics, traces, and structured logs provide fine-grained visibility.</p>
  </div>
</div>

---

## Card Grid — 3 Column

<div class="card-grid three-col">
  <div class="card">
    <h4>Compute</h4>
    <p>Auto-scale instances and containers across availability zones on demand.</p>
  </div>
  <div class="card">
    <h4>Storage</h4>
    <p>Object, block, and file tiers matched to each workload's access pattern.</p>
  </div>
  <div class="card">
    <h4>Networking</h4>
    <p>Software-defined networking with micro-segmentation and policy enforcement.</p>
  </div>
  <div class="card">
    <h4>Security</h4>
    <p>Zero-trust identity, secrets management, and runtime threat detection built in.</p>
  </div>
  <div class="card">
    <h4>Monitoring</h4>
    <p>Unified dashboards, alert routing, and on-call runbook integration out of the box.</p>
  </div>
  <div class="card">
    <h4>Automation</h4>
    <p>Infrastructure as code, GitOps pipelines, and self-healing workflow orchestration.</p>
  </div>
</div>

---

<!-- .slide: id="lists" -->

*Section 04*

## Numbered Pillars

<div class="pillar-grid">
  <div class="pillar">
    <span class="pillar-num">01</span>
    <div><div class="pillar-title">Design for Failure</div><div class="pillar-desc">Assume any component can fail at any time. Build retries, fallbacks, and circuit breakers in from day one.</div></div>
  </div>
  <div class="pillar">
    <span class="pillar-num">02</span>
    <div><div class="pillar-title">Automate Everything</div><div class="pillar-desc">If you did it twice manually, it belongs in a pipeline. No snowflake environments, ever.</div></div>
  </div>
  <div class="pillar">
    <span class="pillar-num">03</span>
    <div><div class="pillar-title">Shift Security Left</div><div class="pillar-desc">Scan dependencies, secrets, and images in CI — not after the artefact has already shipped.</div></div>
  </div>
  <div class="pillar">
    <span class="pillar-num">04</span>
    <div><div class="pillar-title">Measure Outcomes</div><div class="pillar-desc">DORA metrics, SLO error budgets, and mean time to restore over vanity metrics and velocity points.</div></div>
  </div>
  <div class="pillar">
    <span class="pillar-num">05</span>
    <div><div class="pillar-title">Ship Small</div><div class="pillar-desc">Smaller changesets reduce blast radius, speed up reviews, and make rollbacks trivially simple.</div></div>
  </div>
  <div class="pillar">
    <span class="pillar-num">06</span>
    <div><div class="pillar-title">Own the Full Stack</div><div class="pillar-desc">Teams own build, deploy, run, and on-call. No throwing code over the fence to a separate ops team.</div></div>
  </div>
</div>

---

## Two-Column List

<div class="two-col-list">
  <div><strong>API Gateway</strong> — Single ingress for routing, rate limiting, and auth enforcement.</div>
  <div><strong>Service Mesh</strong> — mTLS, retries, and observability between internal services.</div>
  <div><strong>Event Bus</strong> — Decoupled async communication between producers and consumers.</div>
  <div><strong>Config Store</strong> — Centralised, versioned configuration with live reload support.</div>
  <div><strong>Secrets Vault</strong> — Encrypted, audited secret storage with short-lived dynamic leases.</div>
  <div><strong>Artifact Registry</strong> — Scanned, signed container image and package store.</div>
</div>

---

## Checklist — ✓ / ✗

<ul class="checklist">
  <li>Containers built from a hardened, minimal base image</li>
  <li>Secrets injected at runtime — never baked into images or source</li>
  <li>Every service exposes <code>/health</code> and <code>/metrics</code> endpoints</li>
  <li>Readiness and liveness probes configured in all deployments</li>
  <li class="no">Running as root inside containers — use non-root UID 1000+</li>
  <li class="no">Hardcoded credentials in source code, configs, or Dockerfiles</li>
  <li class="no">Skipping vulnerability scans in CI/CD pipelines</li>
  <li class="no">Using <code>latest</code> tags in production manifests</li>
</ul>

---

<!-- .slide: id="split" -->

*Section 05*

## Split Layout — Big Label Left + Content Right

<div class="split-layout">
  <div class="split-left">
    <div class="split-headline">Why It<br>Matters</div>
    <div class="split-sub">Developer productivity at scale.</div>
  </div>
  <div class="split-right">
    <div class="rule-list">
      <div class="rule-item"><strong>Reduce cognitive load</strong> — Developers focus on product logic, not infrastructure plumbing and undifferentiated heavy lifting.</div>
      <div class="rule-item"><strong>Standardise the golden path</strong> — One opinionated, supported way to ship to production consistently across all teams.</div>
      <div class="rule-item"><strong>Enforce policy by default</strong> — Security and compliance baked into templates, not bolted on during audits.</div>
      <div class="rule-item"><strong>Accelerate onboarding</strong> — New engineers ship on day one using self-service scaffolding without waiting for setup tickets.</div>
      <div class="rule-item"><strong>Reduce mean time to restore</strong> — Consistent tooling means anyone can debug any service, not just its original author.</div>
    </div>
  </div>
</div>

---

<!-- .slide: id="data" -->

*Section 06*

## Stat Row — Key Metrics

<div class="highlight-band">What high-performing engineering organisations consistently deliver</div>

<div class="stat-row">
  <div class="stat-item">
    <span class="stat-number">4×</span>
    <div class="stat-label">Faster deployment frequency vs. industry median</div>
  </div>
  <div class="stat-item">
    <span class="stat-number">24h</span>
    <div class="stat-label">Mean time to restore after a production incident</div>
  </div>
  <div class="stat-item">
    <span class="stat-number">15%</span>
    <div class="stat-label">Change failure rate — one-third of the industry average</div>
  </div>
</div>

---

## Process Steps — Horizontal Flow

<div class="process-steps">
  <div class="step">
    <span class="step-num">01</span>
    <div class="step-title">Discover</div>
    <div class="step-desc">Map current state. Identify gaps, bottlenecks, and high-value quick wins.</div>
  </div>
  <div class="step">
    <span class="step-num">02</span>
    <div class="step-title">Design</div>
    <div class="step-desc">Define target architecture. Prioritise by impact and implementation effort.</div>
  </div>
  <div class="step">
    <span class="step-num">03</span>
    <div class="step-title">Build</div>
    <div class="step-desc">Deliver iteratively in short increments. Validate each change before the next.</div>
  </div>
  <div class="step">
    <span class="step-num">04</span>
    <div class="step-title">Operate</div>
    <div class="step-desc">Monitor outcomes, iterate on runbooks, and hand off sustainable operations.</div>
  </div>
</div>

---

## Alternating-Row Table

| Pattern | Category | When to Use |
|---|---|---|
| Sidecar | Observability | Attach agents to a pod without modifying application code |
| Ambassador | Networking | Proxy outbound calls through a gateway for retry and circuit-break |
| Adapter | Integration | Standardise disparate interfaces behind a single contract |
| Init Container | Bootstrap | Run setup tasks once before the main container starts |
| Leader Election | Coordination | Ensure one replica processes a shared resource at a time |
| Bulkhead | Resilience | Isolate thread pools per downstream to contain slow-caller impact |

---

<!-- .slide: id="special" -->

*Section 07*

## Two-Column with Icon+Label Headers

<div class="col-layout">
  <div class="col">
    <span class="col-header">✅ Do</span>
    <ul>
      <li>Pin base image digests in every Dockerfile</li>
      <li>Lint and test infrastructure code in CI before merge</li>
      <li>Store all state in external stores — not in containers</li>
      <li>Use immutable artifact versions in every manifest</li>
    </ul>
  </div>
  <div class="col">
    <span class="col-header">✗ Don't</span>
    <ul>
      <li>Use <code>latest</code> tags anywhere in production</li>
      <li>Apply YAML by hand — use a GitOps pipeline</li>
      <li>Write stateful logic inside ephemeral containers</li>
      <li>Grant cluster-admin permissions for convenience</li>
    </ul>
  </div>
</div>

---

## Highlight Band — Three Variants

Normal slide content above the band — body text at 28px with the standard theme.

<div class="highlight-band">Blue band — default. Key takeaways, important callouts, or section transitions.</div>

Follow-on body text after the band. Mix with other content freely to break up dense slides.

<div class="highlight-band dark">Dark band — good for quoted facts, emphasis shifts, or end-of-section summaries.</div>

<div class="highlight-band light">Light band — subtle separator with blue text on a pale tint. Softest visual weight.</div>

---

## Vertical Slides Demo — Navigate ↓

Three related slides grouped under one horizontal position. Press ↓ to go deeper.

--

## Vertical Slide 1 of 2

Lorem ipsum dolor sit amet, consectetur adipiscing elit.

> Vertical slides are created with `--` instead of `---`. Use them for sub-topics that belong together but would clutter the main flow.

**When to use vertical slides:**
- Drill-down detail under a summary slide
- Backup or appendix slides you might not always show
- Step-by-step walkthroughs with a parent overview

--

## Vertical Slide 2 of 2

Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam.

<div class="card-grid">
  <div class="card">
    <h4>Tip A</h4>
    <p>Press <strong>Esc</strong> or <strong>O</strong> for overview mode — see all slides as a grid.</p>
  </div>
  <div class="card">
    <h4>Tip B</h4>
    <p>Press <strong>F</strong> for fullscreen. Press <strong>S</strong> to open the speaker notes window.</p>
  </div>
</div>

---

<!-- .slide: class="vcenter bg-dark" data-background-color="#1a1a1a" id="closing" -->

*That's all the layouts*

# End of Showcase

## github.com/your-org/slides
