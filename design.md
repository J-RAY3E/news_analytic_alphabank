---
version: alpha
name: Alfa-Radar-design
description: A design system for Alfa Radar, the News → Impact → Action service embedded in the Alfa-Business internet bank. Structure and typography follow a Stripe-inspired analysis; the palette is taken from alfabank.ru (Alfa red primary, near-black surfaces, cyan / blue / lilac tile accents). It keeps the thin editorial display type and an atmospheric gradient mesh, and adds what a decision tool needs on top - three typed claim labels (Fact, Bank View, AI Inference), relevance score and reason chips, source chips, and a dark Agent Trace panel that plays the role of the brand's composited IDE mockup. UI language is Russian.

colors:
  primary: "#ef3124"
  primary-press: "#c4271c"
  surface-dark: "#121212"
  surface-dark-raised: "#212124"
  surface-dark-button: "#2c2c2e"
  hairline-on-dark: "#3a3a3d"
  on-dark-mute: "#a0a3ab"
  ink: "#121212"
  ink-secondary: "#2c2c2e"
  ink-mute: "#6d7078"
  on-primary: "#ffffff"
  canvas: "#ffffff"
  canvas-soft: "#f3f4f5"
  canvas-track: "#edeef0"
  canvas-grey: "#e8ecee"
  hairline: "#e3e5e8"
  hairline-input: "#c9cdd2"
  cyan: "#01d2f1"
  cyan-soft: "#6ae9ed"
  blue: "#266fff"
  blue-deep: "#0a3fb5"
  blue-bg: "#e3edff"
  lilac: "#dfbfff"
  lilac-soft: "#f1e4ff"
  lilac-deep: "#9b5de5"
  success: "#108c3d"
  success-bg: "#e3f5e8"
  risk-bg: "#ffe5e2"
  danger: "#c4271c"

typography:
  display-lg:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: 32px
    fontWeight: 300
    lineHeight: 1.15
    letterSpacing: -0.64px
  display-md:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: 26px
    fontWeight: 300
    lineHeight: 1.2
    letterSpacing: -0.26px
  heading-lg:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: 22px
    fontWeight: 300
    lineHeight: 1.25
    letterSpacing: -0.22px
  heading-md:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: 20px
    fontWeight: 300
    lineHeight: 1.4
    letterSpacing: -0.2px
  heading-sm:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: 0
  body-lg:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0
  body-md:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0
  body-tabular:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: -0.14px
    fontFeature: tnum
  number-score:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: 28px
    fontWeight: 300
    lineHeight: 1.0
    letterSpacing: -0.56px
    fontFeature: tnum
  button-md:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.0
    letterSpacing: 0
  button-sm:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.0
    letterSpacing: 0
  caption:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: -0.13px
    fontFeature: tnum
  label-claim:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: 11px
    fontWeight: 500
    lineHeight: 1.15
    letterSpacing: 0.4px
  micro:
    fontFamily: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: 11px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: 0
  mono-trace:
    fontFamily: "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0

rounded:
  xs: 4px
  sm: 6px
  md: 8px
  lg: 12px
  xl: 16px
  pill: 9999px

spacing:
  xxs: 2px
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  xxl: 32px
  huge: 64px

components:
  button-primary-pill:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button-md}"
    rounded: "{rounded.pill}"
    padding: 8px 16px
  button-primary-pill-pressed:
    backgroundColor: "{colors.primary-press}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button-md}"
    rounded: "{rounded.pill}"
    padding: 8px 16px
  button-secondary:
    backgroundColor: "{colors.surface-dark-button}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button-md}"
    rounded: "{rounded.pill}"
    padding: 8px 16px
  button-on-dark:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.button-md}"
    rounded: "{rounded.pill}"
    padding: 8px 16px
  text-input:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.sm}"
    padding: 8px 12px
  text-input-focused:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.sm}"
    padding: 8px 12px
  news-test-input:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.lg}"
    padding: 16px
  nav-bar:
    backgroundColor: "{colors.surface-dark}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.xs}"
    padding: 16px 24px
  radar-widget:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.heading-lg}"
    rounded: "{rounded.xl}"
    padding: 24px
  client-role-switcher:
    backgroundColor: "{colors.canvas-track}"
    textColor: "{colors.ink-secondary}"
    typography: "{typography.button-sm}"
    rounded: "{rounded.pill}"
    padding: 8px 12px
  client-role-switcher-active:
    backgroundColor: "{colors.surface-dark-raised}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button-sm}"
    rounded: "{rounded.pill}"
    padding: 8px 12px
  feed-card:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.lg}"
    padding: 24px
  feed-card-selected:
    backgroundColor: "{colors.canvas-soft}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.lg}"
    padding: 24px
  score-badge:
    backgroundColor: "{colors.blue-bg}"
    textColor: "{colors.blue-deep}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: 4px 8px
  reason-chip:
    backgroundColor: "{colors.canvas-soft}"
    textColor: "{colors.ink-secondary}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: 4px 8px
  risk-chip:
    backgroundColor: "{colors.risk-bg}"
    textColor: "{colors.ink}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: 4px 8px
  opportunity-chip:
    backgroundColor: "{colors.success-bg}"
    textColor: "{colors.ink}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: 4px 8px
  insight-section-card:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-lg}"
    rounded: "{rounded.lg}"
    padding: 32px
  claim-block:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: 12px 16px
  claim-label-fact:
    backgroundColor: "{colors.success-bg}"
    textColor: "{colors.ink}"
    typography: "{typography.label-claim}"
    rounded: "{rounded.pill}"
    padding: 2px 8px
  claim-label-bank-view:
    backgroundColor: "{colors.blue-bg}"
    textColor: "{colors.blue-deep}"
    typography: "{typography.label-claim}"
    rounded: "{rounded.pill}"
    padding: 2px 8px
  claim-label-ai-inference:
    backgroundColor: "{colors.lilac-soft}"
    textColor: "{colors.ink}"
    typography: "{typography.label-claim}"
    rounded: "{rounded.pill}"
    padding: 2px 8px
  source-chip:
    backgroundColor: "{colors.canvas-soft}"
    textColor: "{colors.blue-deep}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: 4px 8px
  trace-panel:
    backgroundColor: "{colors.surface-dark}"
    textColor: "{colors.on-primary}"
    typography: "{typography.mono-trace}"
    rounded: "{rounded.xl}"
    padding: 24px
  trace-step:
    backgroundColor: "{colors.surface-dark-raised}"
    textColor: "{colors.on-dark-mute}"
    typography: "{typography.mono-trace}"
    rounded: "{rounded.md}"
    padding: 8px 12px
  critic-badge-pass:
    backgroundColor: "{colors.success}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-claim}"
    rounded: "{rounded.pill}"
    padding: 2px 8px
  critic-badge-fail:
    backgroundColor: "{colors.danger}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-claim}"
    rounded: "{rounded.pill}"
    padding: 2px 8px
  chat-bubble-user:
    backgroundColor: "{colors.surface-dark-raised}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.lg}"
    padding: 12px 16px
  chat-bubble-agent:
    backgroundColor: "{colors.canvas-soft}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.lg}"
    padding: 12px 16px
  feedback-button:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink-secondary}"
    typography: "{typography.button-sm}"
    rounded: "{rounded.pill}"
    padding: 8px 12px
  budget-meter:
    backgroundColor: "{colors.canvas-soft}"
    textColor: "{colors.ink-secondary}"
    typography: "{typography.caption}"
    rounded: "{rounded.md}"
    padding: 12px
  footer-light:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink-mute}"
    typography: "{typography.caption}"
    rounded: "{rounded.xs}"
    padding: 32px 24px
---

## Overview

Alfa Radar is a decision tool for executives of large companies. It answers six questions about every event: what happened, why it matters for this company, what consequences are possible, which actions are relevant, how Alfa-Bank assesses it, and what the conclusion is based on. The design language therefore has two jobs: look like a calm, trustworthy piece of financial infrastructure, and make the **origin of every sentence visible**.

The system keeps the Stripe-inspired structure and typography, with the palette taken from the Alfa-Bank website (alfabank.ru):

- **Gradient mesh** as the atmospheric backdrop of the entry points (Radar widget on the home screen and the Radar landing header). It is never placed behind dense text.
- **Near-black ink** (`{colors.ink}`) as the universal text color and **Alfa red** (`{colors.primary}`) as the single CTA color, one filled red button per band. Dark chrome (`{colors.surface-dark}`) frames the app, white and soft grey carry the content, as on the bank's own site.
- **Thin display type** (weight 300) with negative tracking; body copy goes to weight 400 for readability of dense Russian text.
- **Dark IDE-style panel** (`{colors.surface-dark}`) is repurposed as the **Agent Trace panel**, the visual proof of real agentic behavior (criteria 11 and 12).
- **Tabular figures** for relevance scores, percentages, key rate values and RUB amounts.

What this version adds for the PRD:

- Three typed claim labels (Fact, Bank View, AI Inference) with distinct color, icon and text, never color alone.
- A feed card that always shows a relevance score and the top reasons for the rank (FR-4, FR-17).
- Source chips that open the original source (FR-18, FR-20a).
- A mocked Alfa-Business home-screen shell with a prominent, always visible Radar entry widget (FR-16, criterion 09).

**Key Characteristics:**
- Three-panel workspace: feed, interpretation, Agent Trace.
- Every claim is a block with a label, source chips and, optionally, the company features that drove it.
- Light surfaces for reading and judging, one dark surface for machine behavior. The polarity flip tells the user "this is what the system did", not "this is what the bank says".
- Pill buttons, 12-16px cards, hairline borders, very light shadows. The bank's site uses larger card radii (about 24-32px); raise `{rounded.lg}` to 24px if you want a closer match.
- Russian UI copy; layouts tolerate strings 20-30% longer than English.

## Colors

### Source
Values were sampled from two screenshots of alfabank.ru (home hero and the "Выбирайте лучшее" product grid). Tokens marked *derived* were not on screen and were chosen to pair with the sampled ones.

### Brand & Accent
- **Alfa Red** (`{colors.primary}` - `#ef3124`): sampled from the "Войти" and "Заказать карту" buttons and the logo. Filled CTA only; one per band.
- **Red Press** (`{colors.primary-press}` - `#c4271c`, *derived*): pressed state and the Critic "fail" badge (`{colors.danger}` has the same value).
- **Cyan** (`{colors.cyan}` - `#01d2f1`) and **Cyan Soft** (`{colors.cyan-soft}` - `#6ae9ed`): sampled from the hero and tile backgrounds; gradient mesh stops.
- **Blue** (`{colors.blue}` - `#266fff`): sampled from the investment tile; gradient mesh stop, focus ring, progress fills.
- **Blue Deep** (`{colors.blue-deep}` - `#0a3fb5`, *derived*): text and links on light surfaces (the sampled blue is only about 4.4:1 on white, so it is not used for small text).
- **Blue BG** (`{colors.blue-bg}` - `#e3edff`, *derived*): score badge and Bank View label background.
- **Lilac** (`{colors.lilac}` - `#dfbfff`): sampled from the "Кредит наличными" tile; gradient mesh stop. **Lilac Soft** (`{colors.lilac-soft}`, *derived*) is the AI Inference label background and **Lilac Deep** (`{colors.lilac-deep}`, *derived*) is its left border.

### Surface
- **Surface Dark** (`{colors.surface-dark}` - `#121212`): sampled from the site background; app top bar, Agent Trace panel and the home-screen shell.
- **Surface Dark Raised** (`{colors.surface-dark-raised}` - `#212124`): sampled from the active segmented-control pill; active role pill, trace steps, user chat bubble.
- **Surface Dark Button** (`{colors.surface-dark-button}` - `#2c2c2e`): sampled from the "Стать клиентом" button; secondary button.
- **Canvas** (`{colors.canvas}`): default background and cards.
- **Canvas Soft** (`{colors.canvas-soft}` - `#f3f4f5`): sampled from the product-grid cards; page background behind cards, selected feed card, chips, agent chat bubble.
- **Canvas Track** (`{colors.canvas-track}` - `#edeef0`): sampled from the segmented-control track; role switcher background.
- **Canvas Grey** (`{colors.canvas-grey}` - `#e8ecee`): sampled from the "Привилегии" tile; neutral interludes.
- **Hairline** (`{colors.hairline}`, *derived*): 1px card and table borders. **Hairline Input** (`{colors.hairline-input}`, *derived*): input borders.
- **Hairline on Dark** (`{colors.hairline-on-dark}`, *derived*): dividers inside the trace panel.

### Text
- **Ink** (`{colors.ink}` - `#121212`): default text; headings on the site sample as `#222224`.
- **Ink Secondary** (`{colors.ink-secondary}` - `#2c2c2e`): secondary text; use this instead of ink-mute for text under 14px on `{colors.canvas-soft}`.
- **Ink Mute** (`{colors.ink-mute}` - `#6d7078`, *derived*): helper text and timestamps on white only.
- **On Dark Mute** (`{colors.on-dark-mute}`, *derived*): secondary text inside the trace panel.

### Semantic (product UI only)
The bank's marketing surfaces have no semantic palette. Radar is a product UI, so these are added and stay out of the gradient mesh:

| Meaning | Background | Text/Icon | Used for |
|---|---|---|---|
| Fact | `{colors.success-bg}` | ink + check icon | claims verified against a source |
| Bank View | `{colors.blue-bg}` | `{colors.blue-deep}` + bank icon | conclusions from Alfa-Bank research |
| AI Inference | `{colors.lilac-soft}` | ink + spark icon, 3px `{colors.lilac-deep}` left border on the claim block | model-generated conclusions |
| Risk | `{colors.risk-bg}` | ink + red dot | risk chips in consequences |
| Opportunity | `{colors.success-bg}` | ink + green dot | opportunity chips in consequences |
| Critic pass / fail | `{colors.success}` / `{colors.danger}` | white | trace panel badges |

Because Alfa red is both the brand CTA and the natural "danger" hue, red is never used for risk text or icons alone: risk chips always pair the red-tinted background with a text label and a dot, and the Critic fail badge always carries the word "Не пройдено".

### Gradient Mesh
Cyan, cyan soft, blue and lilac washed horizontally, with a small red accent stop near the right edge. It replaces the original cream / orange / lavender / indigo / ruby mesh and echoes the tile colors on alfabank.ru.

## Typography

### Font Family
Sohne is proprietary and has no Cyrillic coverage, and the whole UI is Russian. Use **Inter** (SIL OFL, Latin + Cyrillic) as the primary face and **JetBrains Mono** (SIL OFL, Latin + Cyrillic) for the Agent Trace. Both are self-hosted at build time through `next/font`, so no external font request is needed and the free-tier deployment stays self-contained.

Inter's `ss01` changes digit shapes, so it is **not** used. Use `cv11` (single-story a) on display sizes only, and `tnum` on every numeric cell.

### Hierarchy

| Token | Size | Weight | Line Height | Letter Spacing | Use |
|---|---|---|---|---|---|
| `{typography.display-lg}` | 32px | 300 | 1.15 | -0.64px | Insight page title (event headline) |
| `{typography.display-md}` | 26px | 300 | 1.2 | -0.26px | Radar page title, empty states |
| `{typography.heading-lg}` | 22px | 300 | 1.25 | -0.22px | Radar widget title, section titles |
| `{typography.heading-md}` | 20px | 300 | 1.4 | -0.2px | Feed card title |
| `{typography.heading-sm}` | 18px | 400 | 1.4 | 0 | Block headings (the six answers) |
| `{typography.body-lg}` | 16px | 400 | 1.5 | 0 | Insight body text |
| `{typography.body-md}` | 15px | 400 | 1.5 | 0 | Default UI body |
| `{typography.body-tabular}` | 14px | 400 | 1.4 | -0.14px | Tables with numbers (`tnum`) |
| `{typography.number-score}` | 28px | 300 | 1.0 | -0.56px | Relevance score (`tnum`) |
| `{typography.caption}` | 13px | 400 | 1.4 | -0.13px | Chips, helper text, timestamps |
| `{typography.label-claim}` | 11px | 500 | 1.15 | 0.4px | Fact / Bank View / AI Inference labels |
| `{typography.mono-trace}` | 13px | 400 | 1.5 | 0 | Agent Trace content |

### Principles
- Thin weight (300) is reserved for display and headings at 20px and above. Anything smaller or denser than 18px is weight 400, because thin Cyrillic at 15px loses legibility on low-density screens.
- Negative tracking applies to display sizes only.
- Numbers that change meaning when misread (key rate 14,0%, scores, RUB amounts, dates) always use `tnum`. Use the Russian decimal comma in copy.
- Claim labels are uppercase in the code but rendered with the Russian copy in the table under **Content Rules**.

## Layout

### Spacing System
Base unit 8px with the same tokens as the source system: `{spacing.xxs}` 2 / `{spacing.xs}` 4 / `{spacing.sm}` 8 / `{spacing.md}` 12 / `{spacing.lg}` 16 / `{spacing.xl}` 24 / `{spacing.xxl}` 32 / `{spacing.huge}` 64. Product screens use 24-32px section gaps; the home screen and Radar landing header may use 64px.

### Three-Panel Workspace (desktop >= 1280px)

| Panel | Width | Contents | PRD |
|---|---|---|---|
| Feed | 340px fixed | client and role switcher, ranked feed cards, "test a new news item" entry | FR-4, FR-17, FR-21 |
| Interpretation | flexible, max 760px reading column | event header, the six answer blocks, typed claims, follow-up chat | FR-12, FR-18, FR-20 |
| Agent Trace | 380px, collapsible | dark trace panel: plan, tools, sources, features, Critic results | FR-19 |

### Home Screen (Alfa-Business mock)
- Standard app shell with sidebar and top bar on `{colors.canvas-soft}`.
- The **Radar widget** sits in the first row of the main grid, spans two columns, and is never below the fold on desktop or mobile (criterion 09).
- The widget has a gradient mesh header strip (about 96px high), a one-line summary of the top ranked event for the current client, and one `button-primary-pill` "Открыть Radar".

### Whitespace
Marketing-style whitespace is used only on the home screen and the Radar landing header. Inside the workspace, density wins: 16px between claims, 24px between cards.

## Elevation & Depth

| Level | Treatment | Use |
|---|---|---|
| 0 | Flat, 1px `{colors.hairline}` border | feed cards, claim blocks, inputs |
| 1 | `box-shadow: rgba(18,18,18,0.08) 0 1px 3px` | selected feed card, radar widget |
| 2 | `box-shadow: rgba(18,18,18,0.10) 0 8px 24px, rgba(18,18,18,0.05) 0 2px 6px` | trace panel, dropdowns, dialogs |
| 3 | Gradient mesh | radar widget header and Radar landing header only |

The mesh is a static SVG asset (about 20-40 KB), re-tiled on mobile. It is never placed behind text smaller than 20px.

## Shapes

| Token | Value | Use |
|---|---|---|
| `{rounded.xs}` | 4px | table chrome |
| `{rounded.sm}` | 6px | text inputs |
| `{rounded.md}` | 8px | claim blocks, trace steps, budget meter |
| `{rounded.lg}` | 12px | feed cards, insight cards, chat bubbles, news input |
| `{rounded.xl}` | 16px | radar widget, trace panel |
| `{rounded.pill}` | 9999px | all buttons, chips, labels, badges |

## Components

### Buttons
- **`button-primary-pill`**: one per band. Examples: "Открыть Radar", "Проверить новость".
- **`button-secondary`**: 1px `{colors.primary}` border. Examples: "Открыть источник", "Сменить клиента".
- **`button-on-dark`**: only inside the trace panel (for example "Развернуть шаг").
- **`feedback-button`**: three buttons in a row ("Полезно", "Не полезно", "Неверно"). Selected state fills with `{colors.blue-bg}`.

### Inputs
- **`text-input`**: 1px `{colors.hairline-input}` border; focus swaps the border to `{colors.blue}` plus a 3px `rgba(38,111,255,0.20)` ring (blue, not red, so focus is never mistaken for an error).
- **`news-test-input`**: multi-line, min 4 rows, accepts text or a URL, with a `button-primary-pill` under it. Progress states appear below it (see **States**).

### Client and Role Switcher
`client-role-switcher` is a segmented pill group: a client dropdown (anonymized ID, industry, revenue bucket) followed by role pills CEO / CFO / Treasurer / Chief accountant / Other. The active pill is `client-role-switcher-active` (dark pill `{colors.surface-dark-raised}` with white text on a `{colors.canvas-track}` track, as in the bank's own segmented control). A small caption under it reads "Роль выбирается вручную в демо-режиме" so graders know roles are simulated.

### Radar Widget
`radar-widget`: gradient mesh strip, title "Radar", one-line top event for the current client with its score badge, and the primary CTA.

### Feed Card
`feed-card` layout, top to bottom:
1. Row: source name and time (`{typography.caption}`, `{colors.ink-mute}`) on the left, `score-badge` on the right.
2. Event title (`{typography.heading-md}`), max 2 lines.
3. One-line reason in plain text, for example "У вас есть кредитные продукты, а ключевая ставка не изменилась" (FR-4).
4. Row of up to 3 `reason-chip` items (sector match, supply chain, product match, geo, scale) plus `risk-chip` or `opportunity-chip` if the event has an expected direction.

Hover raises to Level 1. The selected card uses `feed-card-selected` with a 2px `{colors.primary}` left border. The score badge opens a small popover with the weighted breakdown from the scoring engine (sector 0,30 / supply chain 0,20 / product 0,20 / geo 0,15 / scale 0,10 / recency 0,05).

### Insight Page
`insight-section-card` is used for each of the six blocks, in this order, each with a `{typography.heading-sm}` heading:

1. Что произошло
2. Почему это важно для вашей компании
3. Возможные последствия
4. Какие действия могут быть актуальны
5. Как это оценивает банк
6. На чём основаны выводы

Blocks 1-5 contain claim blocks; block 6 lists the sources, the company features used, and the Critic outcome.

### Claim Block and Labels
Every claim is a `claim-block` with:
- A label at the top-left: `claim-label-fact`, `claim-label-bank-view` or `claim-label-ai-inference`. Each label has an icon and a text, and the label order never changes.
- The claim text (`{typography.body-md}`).
- A footer row with one or more `source-chip` items (for example `news:123`, `bank:rate_note:p2`) and, if the claim used company features, small `reason-chip` items such as `CL_PRODUCT_LOA_MARK`.
- For AI Inference only: a 3px `{colors.lilac-deep}` left border and, in the footer, the confidence value formatted with `tnum`.

Clicking a source chip opens the original source (the news URL, or the bank PDF at the cited page) in a side drawer or new tab (FR-18, FR-20a).

### Agent Trace Panel
`trace-panel` is the dark IDE-like surface.
- Header: "Agent Trace", total time, number of Critic loops, cost in RUB (`tnum`).
- Body: a vertical list of `trace-step` rows in `{typography.mono-trace}`, each with a step number, role (Planner / Executor / Interpreter / Critic), tool name, and a one-line result. Rows expand to show inputs, outputs, source IDs, company features applied and model name.
- A Critic row ends with `critic-badge-pass` or `critic-badge-fail`. A failed check is followed by an indented retry row ("Повторный поиск", "Пересмотр") so the correction loop is visible at a glance (FR-13).
- Dividers use `{colors.hairline-on-dark}`; secondary text uses `{colors.on-dark-mute}`.

### Follow-up Chat
`chat-bubble-user` (dark) and `chat-bubble-agent` (soft). Agent replies reuse `claim-block` formatting when they state facts, so labels and sources stay visible even in chat. Quick-action chips under the input: "Открыть источник", "Другой срез данных", "Объяснить подробнее".

### Budget Meter (P2)
`budget-meter` shows spent and remaining budget in RUB with a thin progress bar (`{colors.blue}` fill, `{colors.hairline}` track), the active model name, and cache hit count.

## States

| State | Treatment |
|---|---|
| Loading feed | 3 skeleton `feed-card` shapes on `{colors.canvas-soft}`, no spinner |
| New news processing | Stepper under `news-test-input`: Нормализация, Извлечение фактов, Оценка релевантности, Анализ агентом, Проверка Critic. Current step in blue, done steps with a check |
| Insight loading | Skeletons for the six blocks; the trace panel streams steps as they arrive |
| Empty feed | `{typography.display-md}` message, a short explanation and a secondary button to switch client |
| Missing data | A claim that depends on a missing feature shows a `reason-chip` "Нет данных: <field>" and the claim is typed AI Inference with lower confidence, never Fact |
| Critic failed after 2 loops | Insight is shown with a visible banner "Часть выводов не прошла проверку" and the failed claims are marked; nothing is hidden |
| Error | Plain message, a retry `button-secondary`, request ID in `{typography.caption}` for the audit log |

## Content Rules

- All UI strings and generated insights are in Russian.
- Label copy:

| Type | Label text | Tooltip |
|---|---|---|
| FACT | Факт | Подтверждено источником |
| BANK_VIEW | Позиция банка | Основано на аналитике Альфа-Банка |
| AI_INFERENCE | Вывод ИИ | Сформировано моделью по доступным данным |

- A claim without a source can never carry the Fact label. The UI refuses to render it as Fact even if the API sends it that way.
- A native product mention (FR-15) is a separate block with the label "Реклама" in `{colors.ink-mute}` on `{colors.canvas-soft}`, visually distinct from claims.
- Numbers: decimal comma, thin non-breaking space as thousands separator, "млрд руб." and "%" in the same line as the number (non-breaking).

## Do's and Don'ts

### Do
- Show a label, icon and text on every claim; color is a reinforcement only.
- Keep the gradient mesh on the home widget and the Radar landing header only.
- Use one filled red button per band.
- Use `tnum` on every number that can be compared.
- Keep the trace panel dark and the reading surfaces light.
- Show Critic failures and retries; a visible correction loop is evidence of agentic logic.

### Don't
- Don't put gradient mesh behind insight text or claim blocks.
- Don't use cyan, blue or lilac as button colors; they are for mesh, labels and focus only.
- Don't use red for text, links or risk icons on their own; red is the CTA and Critic-fail color.
- Don't use weight 300 below 18px.
- Don't present an AI Inference with the visual weight of a Fact (no green, no check icon).
- Don't hide the source chip row to make a card look cleaner.
- Don't use Stripe's name, logo, or the Sohne font in the product or the repository.

## Responsive Behavior

| Name | Width | Key Changes |
|---|---|---|
| Wide | >= 1440px | Three panels at full width, mesh edge to edge on the landing header |
| Desktop | 1280-1439px | Three panels as specified |
| Laptop | 1024-1279px | Trace panel becomes a right-side drawer opened from a "Trace" button |
| Tablet | 768-1023px | Feed becomes a left drawer; interpretation is the main column |
| Mobile | < 768px | Single column with a bottom tab bar: Лента / Анализ / Trace / Чат; display sizes drop 32 → 26 and 26 → 22 |

### Touch Targets
Pills are at least 40px high on desktop and 44px on mobile. Source chips get a 44px tap area through padding on mobile. Form fields are at least 44px high on mobile.

## Accessibility

- Text contrast is at least 4.5:1; use `{colors.ink-secondary}` rather than `{colors.ink-mute}` for text under 14px on `{colors.canvas-soft}`.
- Labels use icon plus text, so the three claim types stay distinguishable for color-blind users.
- The trace panel is keyboard navigable; each step is a button with `aria-expanded`.
- Focus ring: 2px `{colors.primary}` with 2px offset on every interactive element.
- Respect `prefers-reduced-motion`: no streaming animations, steps appear instantly.

## Implementation Notes

### Fonts (Next.js)
```ts
import { Inter, JetBrains_Mono } from "next/font/google";

export const inter = Inter({
  subsets: ["latin", "cyrillic"],
  weight: ["300", "400", "500"],
  variable: "--font-sans",
  display: "swap",
});

export const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin", "cyrillic"],
  weight: ["400"],
  variable: "--font-mono",
  display: "swap",
});
```

### Tokens (global CSS)
```css
:root {
  --primary: #ef3124;
  --primary-press: #c4271c;
  --surface-dark: #121212;
  --surface-dark-raised: #212124;
  --surface-dark-button: #2c2c2e;
  --hairline-on-dark: #3a3a3d;
  --on-dark-mute: #a0a3ab;
  --ink: #121212;
  --ink-secondary: #2c2c2e;
  --ink-mute: #6d7078;
  --canvas: #ffffff;
  --canvas-soft: #f3f4f5;
  --canvas-track: #edeef0;
  --canvas-grey: #e8ecee;
  --hairline: #e3e5e8;
  --hairline-input: #c9cdd2;
  --cyan: #01d2f1;
  --cyan-soft: #6ae9ed;
  --blue: #266fff;
  --blue-deep: #0a3fb5;
  --blue-bg: #e3edff;
  --lilac: #dfbfff;
  --lilac-soft: #f1e4ff;
  --lilac-deep: #9b5de5;
  --success: #108c3d;
  --success-bg: #e3f5e8;
  --risk-bg: #ffe5e2;
  --danger: #c4271c;
  --shadow-1: 0 1px 3px rgba(18, 18, 18, 0.08);
  --shadow-2: 0 8px 24px rgba(18, 18, 18, 0.10), 0 2px 6px rgba(18, 18, 18, 0.05);
}

body {
  font-family: var(--font-sans), system-ui, -apple-system, "Segoe UI", sans-serif;
  color: var(--ink);
  background: var(--canvas-soft);
}

.tnum {
  font-feature-settings: "tnum";
}
```

### Assets and Licensing
- Add to `THIRD_PARTY_NOTICES`: Inter (SIL OFL 1.1), JetBrains Mono (SIL OFL 1.1), the icon set you pick, and a line stating the visual structure is inspired by a public design analysis, and that the colors were sampled from the public alfabank.ru site for a hackathon prototype; no Alfa-Bank or Stripe logos, illustrations or proprietary fonts are bundled.
- Do not copy the 3D illustrations or card art from the bank's site; the gradient mesh is an original SVG created for the project and stored in `frontend/public/mesh.svg`.

## PRD Traceability

| PRD item | Design element |
|---|---|
| FR-16 Radar widget on home screen | `radar-widget` in the first row of the home grid |
| FR-4, FR-17 Ranked feed with reasons | `feed-card`, `score-badge`, `reason-chip`, score popover |
| FR-18 Insight page with six answers and labels | `insight-section-card`, `claim-block`, three claim labels |
| FR-19 Agent Trace | `trace-panel`, `trace-step`, `critic-badge-*` |
| FR-20 Follow-up chat and open source | chat bubbles, `source-chip` drawer |
| FR-21 Test a new news item | `news-test-input` with stepper |
| FR-22 Feedback | `feedback-button` group |
| FR-23 Quality and cost dashboard | `budget-meter` |
| FR-14 Role Lens | `client-role-switcher` role pills; the insight header shows "Для роли: CFO" |
| Criteria 03 (Bank View vs AI) | label colors, icons, tooltips, lilac border on AI Inference |
| Criteria 12 (traceable origin) | source chips, company feature chips, trace panel |

## Iteration Guide

1. Build tokens and fonts first, then the three claim labels and the claim block, since every screen depends on them.
2. Next build the feed card and the insight page against the mock server.
3. Add the trace panel last; it needs real step data from the agent service.
4. Reference tokens by name (`{colors.primary}`, `{rounded.pill}`) and add new variants as separate entries.
5. Run `npx @google/design.md lint DESIGN.md` after every edit.
6. Do not add new accent colors; any new semantic color needs an entry in the Semantic table with an icon and text pairing.