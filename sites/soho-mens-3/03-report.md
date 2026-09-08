# 03 — Final Report

**Project:** SoHo Men's Health redesign — direction "The Member's Rooms"
**Run:** soho-mens-3 (run_id 3) · **Date:** 2026-09-01 → 2026-09-02 · **Budget:** 4h

---

## 1. Direction delivered

**The Member's Rooms** — the practice as a discreet members' club:
hospitality-led, warm and tactile; booking an appointment feels like being
expected, not processed. Per the brief, Phase Two was prescribed; no
alternative directions were explored. The single direction, its thesis and its
risk are documented in Figma (02 Directions) and in `01-audit.md`.

Signature ideas shipped:

- **The concierge booking strip** — "When would you like to come in?" A sage,
  28px-radius band with two fields (preferred office, preferred time) and the
  primary CTA, placed directly after the hero and echoed in the Services-page
  quiz band. Implemented with real error → loading → success states.
- **The guest book** — testimonials reframed from a carousel into a signed
  guest book: three published Google reviews (J.L., P.C., K.G.) as cream
  cards with Newsreader quotes, "shortened only for length".
- **The eight rooms of care** — the live site's ~70-item, 3-level mega-menu
  collapsed into eight clearly named rooms (the site's own published service
  categories), each card numbered like a door in the house.

## 2. How the credibility line was held (required by the brief)

The risk: spa/lifestyle softness underselling surgical authority. Concrete
choices that held the "private practice, not day spa" line:

1. **Credentials lead, warmth frames.** The doctor chapter is titled "Your
   host" but the content is a surgeon-scientist's CV: MD, PhD (Oxford), MBA
   (Toronto), FACS, Yale/Penn training, Dartmouth assistant professorship,
   NYU Long Island faculty, named teaching and research awards. No lifestyle
   adjectives appear anywhere near his name.
2. **Medical vocabulary stays medical.** Room descriptions name procedures —
   BHRT, TRT, Peyronie's, PRP, NAD+/NR/NMN, anal pap smear, CO2 laser,
   Morpheus8. The hospitality layer is in the *service experience* (concierge,
   guest book, "hosted"), never in the clinical nouns.
3. **No spa visual clichés.** Palette is warm ivory/espresso/oxblood over
   sage — no eucalyptus greens-on-white, no pastel gradients, no candles or
   stones. Photography is the practice's own published imagery: a
   consultation, rooms, cabinetry, the doctor's portrait. Typography pairs an
   editorial serif (Newsreader) with a plain grotesque (DM Sans) — journal,
   not wellness-blog.
4. **Surgery is a first-class room.** "Surgical Diseases" is room 04 of 8,
   described as "office-based surgical care, led by a board-certified
   surgeon" — the surgical offer is visible in the primary navigation path,
   not buried under wellness.
5. **Price transparency signals confidence.** Fees ($150 cosmetic consult
   applied to treatment, $750 hormone consult, out-of-network billing
   breakdown) are printed, not hidden — premium medical practices state
   prices; spas hide them behind "journeys".
6. **Calm motion, no playfulness.** 180–240ms ease-out, opacity/transform
   only, no carousels, no autoplay, full `prefers-reduced-motion` support.
   Restraint reads as clinical confidence.

## 3. Audit summary (full text: `01-audit.md`)

Five problems with business consequences, ranked: (1) ~70-item mega-menu
buries revenue services; (2) carousel abuse and duplicated copy; (3) no
webfonts, mid-page h1, visible typos — credibility tax on $150–$750 consults;
(4) stock-photo saturation; (5) conflicting published facts (phone
646-370-4050 display vs tel:+1-347-749-1174 in JSON-LD; footer hours
Mon–Fri 8am–8pm/Sat 8am–1pm vs JSON-LD Mo–Fr 8–5). **Conflicts were
documented, not resolved by invention** — the redesign shows the footer
hours and display phone (most prominent on the live site) and preserves the
original JSON-LD verbatim.

## 4. Design system (Figma 03 Foundations)

- **Color:** ivory `#FFFCF7`, cream `#F5F0E7`, sage `#44564A`, sage-deep
  `#35423A`, espresso `#241C18`, muted `#6F675F`, oxblood `#6B2632`,
  oxblood-deep `#541B25`, brass `#B08C57` (focus), line `#D8CEC0`, error
  `#9C4638`, success `#4F6B4A`.
- **Type:** Newsreader (display serif) + DM Sans (UI) — two families, the
  brief's maximum.
- **Form:** 24px card/photo radius, 12px buttons, 14px fields, 28px
  concierge strip; soft shadows on hover only; 8pt-based spacing.
- **Component library (15 components):** Button Primary Default/Hover,
  Secondary, Disabled; Field Default/Focus/Error/Loading/Success;
  Header/Desktop, Header/Mobile/Closed; ServiceRoom, GuestBook/Entry,
  LocationCard/Light, Footer/Desktop — plus the ConciergeStrip composite and
  a focus-visible button treatment (2px brass ring).

## 5. Figma file

**"SoHo Men's Health — The Member's Rooms"** (Figma desktop, built through
the local plugin bridge; the bridge cannot produce a publishable share URL —
open the file from Figma Recents; it is the file connected to bridge channel
`ktuiz8nw`).

Page structure (single page "00 Cover & Notes", seven sections):

| Section | Contents | Key node IDs |
|---|---|---|
| Cover | Direction cover (pre-seeded, kept) | 2:29 |
| 01 Audit | Strengths / Problems / Opportunities columns | 16:16, 16:23 |
| 02 Directions | The single prescribed direction + risk note | 16:17, 16:37–41 |
| 03 Foundations | 12 swatches, type samples, spacing scale, notes | 16:18, 16:47–79 |
| 04 Components | All 15 components incl. every field/button state + ConciergeStrip | 16:19, 16:83–154 |
| 05 Desktop | Home 1440 (5034px, 11 chapters) + Services 1440 (3444px, 8 rooms + quiz band) | 16:162, 16:320 |
| 06 Mobile | Home 390 (all chapters stacked) + Mobile nav — open 390×844 | 18:404, 18:513 |
| 07 Prototype & States | Button states (default/hover/active/focus-visible/disabled), field states (focus/error/loading/success), long-content edge case, motion & reduced-motion spec | 18:520 |

Component keys for reuse: Button/Primary/Default `2:148`, Primary/Hover
`2:150`, Secondary `2:152`, Disabled `2:154`; Field `2:156/2:159/2:162/
2:165/2:168`; Header/Desktop `15:2`, Header/Mobile/Closed `15:10`,
ServiceRoom `15:13`, GuestBook/Entry `15:18`, LocationCard/Light `15:22`,
Footer/Desktop `15:27`.

**Limitation:** prototype connector lines could not be drawn (no default
connector exists in the file and the bridge cannot create one); navigation
relationships are instead labeled on the frames themselves.

## 6. Canva

**Purposeful asset, not decoration:** "The Guest Book — J.L." — a 1080×1350
Instagram post in the Member's Rooms art direction, quoting a real published
Google review with the practice wordmark and phone. It extends the
redesign's signature idea into the practice's actual social channel
(Facebook/Twitter/Instagram links are published on the live site).

- Edit: https://www.canva.com/d/GpM3ADxJ6O86NjY
- View: https://www.canva.com/d/rTTBRCxaD78mOZj
- Design id `DAHUGp3ZEAA`; exported PNG archived at `canva-guest-book.png`.
- Verified by Vision OCR + pixel sampling: all six expected strings present
  and verbatim, warm ivory background (#F9EFDD), no edge collisions.

## 7. Implementation (static, in this folder)

- `index.html` — homepage, semantic landmarks, JSON-LD preserved verbatim
  from the live site (MedicalClinic/Organization/Place/WebSite graph).
- `services.html` — the required secondary page: eight room chapters with
  published service lists, fees note, quiz band.
- `styles.css` — every value derives from central `:root` tokens mirroring
  Figma 03 Foundations; no hard-coded one-offs.
- `main.js` — progressive enhancement only: mobile nav overlay
  (aria-expanded, Escape, focus handling), concierge form
  error/loading/success states, motion-safe scroll reveals.
- **Accessibility (WCAG 2.2 AA targeted):** skip link, semantic
  header/nav/main/section/footer with aria-labels, labelled form fields with
  `aria-live` hints, `:focus-visible` brass ring everywhere, contrast-checked
  palette pairs, `prefers-reduced-motion` disables all transitions/reveals,
  keyboard-operable nav overlay, alt text on all photography, width/height +
  lazy-loading on images.
- **Responsive:** 4-col → 2-col (≤1024px) → 1-col (≤520px) rooms grid; nav
  collapses to the overlay at ≤768px; no horizontal overflow down to 360px.

## 8. QA (full log: `02-qa-log.md`)

Two complete inspect → correct → recapture loops across 1440×1000, 1440
full-page, 1024×768, 768×1024, 390×844, 390 full-page, 360×800, for both
pages. Method: Chromium headless screenshots + Vision OCR (bounding boxes,
inverted OCR for dark sections) + pixel sampling (section maps, photo
variance, blank-run detection). Loop 1 found only capture-truncation
ambiguities; loop 2 verified the full home page including visit section and
footer at both widths. Zero rendering defects in the final captures.

Judging set (neutral names): `screenshots/primary-desktop.png`,
`primary-mobile.png`, `secondary-desktop.png`, `secondary-mobile.png`.

## 9. Tool-call count

Approximately **400** tool invocations end-to-end: ~300 Figma bridge calls
(node creation, parenting, fills, text overrides, verification reads), ~40
shell commands (audit fetches, assets, server, screenshots), 6 Canva MCP
calls, 4 explore-agent inspections, ~10 file writes/edits, remainder
reads/searches. (Count is an honest estimate from session flow; no automatic
counter was available.)

## 10. File inventory

```
PROMPT.md                  brief (input)
RUN-SETUP.yml              setup, figma/canva fields now recorded
01-audit.md                Phase One audit
02-qa-log.md               QA loops and verdicts
03-report.md               this report
index.html  services.html  implementation
styles.css  main.js        tokens + styles + interactions
canva-guest-book.png       archived Canva export (1080×1350)
audit/                     live-site HTML snapshots (source of facts)
assets/                    13 JPEGs published by the live site (only imagery used)
screenshots/               loop1/loop2 captures + neutral judging set
session launch log         pre-existing environment log (not a deliverable)
```

## 11. Assumptions & limitations

- **Conflicting facts shown as-published:** display phone 646-370-4050 and
  footer hours (Mon–Fri 8am–8pm, Sat 8am–1pm) are used in the UI; the
  JSON-LD's differing tel/openingHours are preserved untouched in the schema
  block. Flagged for the client — not silently "fixed".
- **Service detail pages were fetch-blocked** during audit; Surgical
  Diseases and Pain Management room copy therefore uses only
  homepage-published facts (deliberately shorter lists — no invented
  procedures).
- **Figma text frames** created via the bridge render in Inter in-file
  (bridge limitation: no font-family parameter); the type system is
  documented in 03 Foundations and correctly implemented in code with
  Newsreader + DM Sans. Component library text uses the correct fonts.
- **Prototype connectors** absent (no default connector available via
  bridge) — relationships labeled instead.
- **No deployment** (per constraints); the site runs from any static server
  (`python3 -m http.server`).
- Concierge form and quiz links are front-end states/anchors — no backend
  exists; the demo success message says so explicitly.
- The live site's own conflicting-email situation (info@sohosurgery.com on a
  sohomenshealth.com domain) is reproduced as published.
