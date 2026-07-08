# Chandler Walker Gayton Foundation · Design Tokens Reference

Version 1.1 · 2026-07-08

This document is the reference for the visual system shared by the foundation
homepage (`/index.html`) and the Boots on the Ground event page
(`/event/index.html`). Both pages inline the same token set to stay self
contained; when tokens diverge, this doc is the source of truth.

The system originated as "Boots on the Ground · Design System v1.0" for the
event page, then expanded to v1.1 to add a light "paper" surface for section
level alternation on the homepage.

---

## Color

Two token layers: **foundation palette** (material words) and **semantic
aliases**. Always reference the semantic layer inside components. Use the
foundation layer only when defining new semantic tokens.

### Foundation palette

| Token         | Value      | Purpose                                    |
| ------------- | ---------- | ------------------------------------------ |
| `--forest`    | `#3f4536`  | Structure, depth, secondary ink on paper   |
| `--champagne` | `#be9a71`  | Secondary accent, eyebrow text on dark     |
| `--saddle`    | `#926f54`  | Mid tone, CTA gradient stop                |
| `--rust`      | `#b56a25`  | Primary CTA, dot accents, focus outline    |
| `--midnight`  | `#19100a`  | Card surface on dark, ink on paper         |
| `--base`      | `#0e0905`  | Page background on dark                    |
| `--warm-white`| `#f5ede0`  | Primary text on dark (same hex as paper)   |

### Paper surface (added v1.1)

| Token             | Value                     | Purpose                              |
| ----------------- | ------------------------- | ------------------------------------ |
| `--paper`         | `#f5ede0`                 | Light section background             |
| `--paper-elevated`| `#ece0cf`                 | Elevated card on paper               |
| `--ink`           | `#19100a`                 | Primary text on paper                |
| `--ink-soft`      | `#3f4536`                 | Secondary text on paper              |
| `--ink-muted`     | `rgba(25,16,10, 0.55)`    | Muted text on paper                  |
| `--paper-hairline`| `rgba(63,69,54, 0.20)`    | 1px separators on paper              |
| `--paper-glass`   | `rgba(63,69,54, 0.05)`    | Glass fill on paper                  |

### Glass and glow (dark only)

| Token             | Value                       | Purpose                     |
| ----------------- | --------------------------- | --------------------------- |
| `--glass`         | `rgba(190,154,113, 0.07)`   | Default glass card fill     |
| `--glass-strong`  | `rgba(190,154,113, 0.18)`   | Glass card hover fill       |
| `--glass-dark`    | `rgba(25,16,10, 0.70)`      | Overlay pill / badge fill   |
| `--glow-border`   | `rgba(181,106,37, 0.40)`    | Rust glow border on hover   |
| `--hairline`      | `rgba(190,154,113, 0.18)`   | 1px separators on dark      |

### Purple accent (Chandler / event teaser)

| Token         | Value                     | Purpose                            |
| ------------- | ------------------------- | ---------------------------------- |
| `--plum`      | `#3b1a6e`                 | Deep purple base for In Memoriam   |
| `--violet`    | `#6b21c8`                 | Purple accent                      |
| `--lavender`  | `#b48fe0`                 | Purple highlight (event teaser)    |
| `--glass-purple`| `rgba(107,33,200, 0.10)`| Purple glass overlay               |

### Semantic aliases

Always reference these in components rather than the raw foundation values.
The homepage overrides them inside `.section--light` blocks so the same
component classes work on either surface.

| Token                | Default (dark)    | Overridden by `.section--light` |
| -------------------- | ----------------- | ------------------------------- |
| `--text-primary`     | `--warm-white`    | `--ink`                         |
| `--text-secondary`   | `--champagne`     | `--ink-soft`                    |
| `--text-muted`       | 45% warm white    | `--ink-muted`                   |
| `--bg-glass`         | `--glass`         | `--paper-glass`                 |
| `--bg-surface`       | `--midnight`      | `--paper-elevated`              |
| `--hairline`         | champagne 18%     | forest 20% (`--paper-hairline`) |
| `--accent-primary`   | `--rust`          | (unchanged)                     |
| `--accent-secondary` | `--champagne`     | (unchanged)                     |

---

## Typography

Three families loaded via one Google Fonts request in `<head>`:

- `--font-display` = Playfair Display (400, 500, 600, 700 + italic 400, 500)
- `--font-body`    = Cormorant Garamond (300, 400, 500, 600 + italic 400)
- `--font-ui`      = Lato (300, 400, 700)

### Type scale

| Element  | Rule                                             | Notes                     |
| -------- | ------------------------------------------------ | ------------------------- |
| `body`   | Cormorant Garamond, 300, 18px, 1.6, 0.005em      | Editorial voice on prose  |
| `h1`     | Playfair Display 400, `clamp(48px, 7vw, 92px)`   | Hero only                 |
| `h2`     | Playfair Display 400, `clamp(34px, 4.4vw, 60px)` | Section headings          |
| `h3`     | Playfair Display 500, `clamp(22px, 2.4vw, 30px)` | Card titles               |
| `h4`     | Playfair Display 500, 18-22px                    | Pillar and involve cards  |
| eyebrow  | Lato 400, 11px, 0.22em, uppercase                | Section eyebrows          |
| button   | Lato 700, 12px, 0.18em, uppercase                | All buttons               |

Italic Playfair is used purposefully for emphasized phrase fragments inside
headlines (e.g. "Fund the work Chandler *believed in.*"). Rendered via
`<em>` inside the h2.

---

## Spacing

Base scale is 4 pixels. All spacing tokens are `--space-N` where N is the
step number:

| Token       | Value | Common use                        |
| ----------- | ----- | --------------------------------- |
| `--space-1` | 4px   | icon offsets                      |
| `--space-2` | 8px   | inline gap                        |
| `--space-3` | 12px  | small padding                     |
| `--space-4` | 16px  | card padding, gap                 |
| `--space-5` | 20px  | inner block gap                   |
| `--space-6` | 24px  | card padding, section-head gap    |
| `--space-8` | 32px  | large gap                         |
| `--space-10`| 40px  | hero CTA row bottom               |
| `--space-12`| 48px  | section-head margin               |
| `--space-16`| 64px  | inter-section large gap           |
| `--space-20`| 80px  | reserved                          |
| `--space-24`| 96px  | reserved                          |

Section vertical rhythm: `padding: clamp(72px, 10vw, 128px) 0`.
Container gutter: `--gutter: clamp(20px, 4vw, 48px)`.
Max container width: `--container: 1240px`.

---

## Radii

| Token         | Value | Common use             |
| ------------- | ----- | ---------------------- |
| `--radius-sm` | 6px   | small pills, tags      |
| `--radius-md` | 12px  | icon tiles, notes      |
| `--radius-lg` | 20px  | cards                  |
| `--radius-xl` | 28px  | featured cards, event  |
| pill          | 999px | buttons, badges        |

---

## Shadows

| Token           | Purpose                                       |
| --------------- | --------------------------------------------- |
| `--shadow-card` | Base card lift on dark                        |
| `--shadow-glow` | Rust glow around primary buttons              |
| `--shadow-glass`| Inner highlight plus outer drop on dark cards |
| `--shadow-paper`| Sage-tinted drop for cards on paper (v1.1)    |

---

## Components

Component classes live inline in each page's `<style>` block, sharing the
same tokens. Both pages reuse the same names.

- **`.btn`** with modifiers `.btn-primary`, `.btn-ghost`, `.btn-sm`,
  `.btn-lg`. Pill-shaped, uppercase Lato. Primary uses rust to saddle
  gradient with rust glow shadow. Ghost uses hairline + 4% surface fill.
  `.btn-ghost` gets a paper variant inside `.section--light` (forest fill
  + paper hairline border + ink text).
- **`.eyebrow`** small caps label above every section title with a rust
  dot preface.
- **`.section-head`** heading block above each section (760px max width).
- **`.reveal`** IntersectionObserver-driven fade-and-lift on scroll.
- **`.container`** max-width 1240px, clamp gutter.
- **`.visually-hidden`** SR-only utility (proper clip-rect version on the
  homepage, inline style on the event footer heading).

Homepage-specific components:

- **`.pillar`**, **`.pillar-icon`** in the mission section.
- **`.program`**, **`.program-photo`**, **`.program-photo-label`** in
  initiatives (photo placeholders live here).
- **`.team-card`**, **`.team-portrait`** in the team section (photo
  placeholders live here, dashed rust border tells they are placeholders).
- **`.event-card`**, **`.event-details`**, **`.event-visual`** for the
  event teaser (purple accent).
- **`.involve-card`**, **`.involve-icon`** in the get-involved section.
- **`.legal-note`** for the 501(c)(3) pending disclaimer (paper surface,
  rust left border).

Event page components (documented on the event page, retained here for
cross-reference): `.host`, `.host-badge`, `.host-info`, `.advisor`,
`.ad-portrait`, `.ad-meta`, `.pill`, `.timeline-row`, `.mem-*` family,
`.ticker`, `.hero-orb`, `.stats-grid`, `.tickets-grid`, `.ticket`,
`.sponsor-logo`.

---

## Section surface alternation (hybrid light/dark)

The homepage alternates surface tokens at the section level. This gives a
warm, editorial rhythm and lets one design system produce both moods
without a theme toggle.

| Section       | Surface | Rationale                                       |
| ------------- | ------- | ----------------------------------------------- |
| Hero          | dark    | Continuity with the event page hero            |
| Mission       | light   | Legible, editorial, sets tone for the mission  |
| Chandler      | dark    | Reflective, honors the In Memoriam feeling     |
| Initiatives   | light   | Program cards read as clean editorial cards    |
| Team          | dark    | Portrait grid reads well against dark          |
| Event teaser  | dark    | Purple accent pops against dark                |
| Get Involved  | light   | Action grid reads clean on paper               |
| Footer        | dark    | Matches event page footer                      |

`prefers-color-scheme` is honored via the two `theme-color` meta tags in
the head so mobile browser chrome matches the section under the top of the
viewport. The page layout itself does not flip; the alternation IS the
system.

### Why this pattern was chosen over a manual toggle

1. Zero JavaScript for theming, keeps first paint fast.
2. The event page can stay pure dark, homepage gets the alternation, both
   share tokens.
3. Section variety serves editorial pacing on a nonprofit landing page
   more than a single-mode surface does.
4. A future manual toggle is still additive — introduce `[data-theme]`
   overrides on `:root` when the need is real.

---

## Rendering rules

1. Always reference semantic tokens (`--text-primary`, `--bg-glass`,
   `--hairline`) in components, not the raw foundation palette. This keeps
   `.section--light` overrides working.
2. New pages copy the `:root` block from `index.html` (or the event page)
   verbatim. Do not fork the palette.
3. New foundation colors require a semantic alias before they are used in
   a component.
4. When placing a card on light, use `rgba(255,255,255, 0.6)` fill with
   `--paper-hairline` border. On dark, use `--glass` fill with `--hairline`.
5. Font weight 300 is the body baseline. Do not increase without reason.
6. No em dashes or en dashes anywhere in shipped copy. Use comma, period,
   sentence break, or center dot (`·`).
7. Photo placeholders use a dashed rust border and a small Lato label so
   they are visually distinct from real photos.

---

## Files

- `/index.html` · foundation homepage (v1.1 tokens with hybrid surfaces)
- `/event/index.html` · Boots on the Ground event page (v1.0 tokens, dark)
- `/DESIGN_TOKENS.md` · this reference
- `/images/*.svg`, `/images/*.jpg` · logos, portraits, hero, memories

Both HTML files are self-contained (inline CSS + inline JS). This is the
pattern the repository was established with and continues to be the
correct call for a static, single-region site with no build step.
