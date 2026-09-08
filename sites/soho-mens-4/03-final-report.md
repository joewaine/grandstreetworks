# Final report

## Preview and repository

From this directory, run:

```sh
python3 -m http.server 4173
```

Then open `http://127.0.0.1:4173/` for the homepage and `http://127.0.0.1:4173/services.html` for the service directory.

- Repository root: `/Users/josephwaine/fractal/grandstreetworks`
- Result directory: `/Users/josephwaine/fractal/grandstreetworks/sites/soho-mens-4`
- Base commit available at handoff: `5190f01`
- Build state: uncommitted; no commit was requested, and unrelated changes elsewhere in the shared repository were preserved.
- Deployment: not required and not performed.

## Editable design artifacts

- Figma: `https://www.figma.com/design/L07XTNmYQwISBZBNb2cTx2`
- Canva editable source: `https://www.canva.com/d/2LaX00YLrDgbXFB`
- Canva view link: `https://www.canva.com/d/Dt5fDPYtkcZ_r2U`
- Canva exports: `assets/canva-art-direction.png` (lossless, 1200×1800) and `assets/canva-art-direction.webp` (optimized web derivative, 1200×1800).

Figma pages and exact top-level frames:

- `00 Cover & Notes` — `Cover — The Member's Rooms`
- `01 Audit` — `Audit / Findings & consequences`
- `02 Direction` — `The Member's Rooms / Selected direction`
- `03 Foundations` — `Foundations / Tokens & principles`
- `04 Components` — 15 reusable components covering button and field states, desktop/mobile headers, service room, guest-book entry, location card, and footer
- `05 Desktop` — `Homepage / 1440 / Default`; `Services / 1440 / Default`
- `06 Mobile` — `Homepage / 390 / Default`; `Services / 390 / Default`; `Homepage / 390 / Open navigation`
- `07 Prototype & States` — `Prototype / States & edge cases`

The Figma file includes two semantic variable collections with 18 variables, responsive editable frames, reusable components, component instances, interaction-state examples, edge-case notes, and reduced-motion guidance. The fixed-brief Phase Two exception is reflected in the singular `02 Direction` page; its three documented pillars are expressions of one direction, not alternative concepts.

## Direction and implementation

**The Member's Rooms** frames the private practice as an expected, hosted visit rather than an administrative transaction. Warm ivory, espresso, muted sage, restrained oxblood, Newsreader display type, DM Sans UI type, rounded photo crops, the concierge strip, and guest-book testimonials deliver warmth. The founder's real portrait, credential rail, named training, explicit service language, and high-contrast authority section keep the work on the private-practice side of the spa/private-club line.

The production-oriented implementation is dependency-free HTML, CSS, and JavaScript. It includes a complete editorial homepage, a searchable/filterable service directory, accessible mobile navigation, concierge validation/loading and live handoff, local optimized imagery and fonts, semantic metadata, and MedicalClinic structured data based on current visible details.

Audit: `01-audit.md`. QA evidence: `02-qa-log.md`. Asset sources: `ASSET-PROVENANCE.md`.

## Verification and limitations

Final QA covered all five required viewport sizes, three correction loops, 0 axe violations on the audited homepage and mobile Services page, no document overflow, no console errors, keyboard/focus behavior, reduced motion, image/font loading, and JavaScript syntax. Required screenshots are in `screenshots/`.

Known limitations: operational facts need owner confirmation because live visible content conflicts with JSON-LD and legacy insurance copy; appointment submission and portal authentication remain external; and deployment, CMS wiring, analytics, and legal/privacy approval were outside scope.

Elapsed working time was approximately 50 minutes. Approximate tool-call count: 95.

## File inventory

### Task inputs / run record

- `PROMPT.md` — supplied, unchanged
- `RUN-SETUP.yml` — completed artifact URLs and audit date
- `codex-launch.log` — supplied session log, unchanged

### Implementation and QA utility

- `index.html`
- `services.html`
- `styles.css`
- `script.js`
- `qa-browser.mjs`

### Documentation

- `01-audit.md`
- `02-qa-log.md`
- `03-final-report.md`
- `ASSET-PROVENANCE.md`

### Fonts

- `assets/fonts/dm-sans-latin.woff2`
- `assets/fonts/newsreader-latin.woff2`
- `assets/fonts/newsreader-italic-latin.woff2`

### Published source imagery and Canva output

- `assets/images/soho-logo.jpg`
- `assets/images/dr-bortecen.webp`
- `assets/images/consultation-hands.webp`
- `assets/images/consultation-room.webp`
- `assets/images/conversation.webp`
- `assets/canva-art-direction.png`
- `assets/canva-art-direction.webp`

### Screenshots

- `screenshots/primary-desktop.png`
- `screenshots/primary-mobile.png`
- `screenshots/secondary-desktop.png`
- `screenshots/secondary-mobile.png`
- `screenshots/qa-1024.png`
- `screenshots/qa-768.png`
- `screenshots/qa-360.png`
