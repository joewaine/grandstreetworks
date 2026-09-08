# 02 — Visual QA Log

Static implementation served locally (`python3 -m http.server 8765`).
Screenshots captured with Chromium headless shell (Playwright build 1234),
`--hide-scrollbars`, virtual-time-budget 8–12s. Inspection method: Vision OCR
with bounding boxes + CoreGraphics pixel sampling (region variance for photo
presence, row-scans for section map and blank-run detection).

## Viewports covered

| Viewport | Home | Services |
|---|---|---|
| 1440×1000 (desktop) | ✓ loop1-home-1440.png | — |
| 1440 full page | ✓ loop1/loop2-home-1440-full.png | ✓ loop1-services-1440-full.png |
| 1024×768 | ✓ loop1-home-1024.png | — |
| 768×1024 | ✓ loop1-home-768.png | — |
| 390×844 | ✓ loop1-home-390.png | — |
| 390 full page | ✓ loop1/loop2-home-390-full.png | ✓ loop1-services-390-full.png |
| 360×800 | ✓ loop1-home-360.png | — |

## Loop 1 — findings

- All key texts present at all widths (hero, concierge strip incl. both fields
  and button, 8 room cards, doctor credentials, 3 guest-book quotes, visit
  section, footer). Dark sections (sage #44564A, espresso #241C18) render at
  expected positions (verified by pixel sampling).
- Photos render at all widths: hero consult, hero overlap, welcome office,
  doctor portrait (region stddev ≈ 67–71 — photographic, not placeholder).
- Reveal-on-scroll cards fully visible in static captures — no JS-hidden
  content.
- No text overlaps, no right-edge cutoff (max text extent 1308/1440, 367/390,
  334/360). No horizontal overflow at 360px.
- 768px switches to the mobile nav ("Menu" button) correctly; 1024px keeps the
  desktop nav with the 2-column rooms/concierge rules per CSS.
- **Issue L1-1:** home full-page captures truncated (5600px desktop / 9500px
  mobile caps) — visit section and footer unverifiable. Capture artifact, not a
  page defect (services page footer rendered fine at both widths).
- **Issue L1-2:** services captures taller than content (~650px desktop /
  ~1700px mobile trailing ivory) — capture overshoot; body background matches,
  no page defect.

## Loop 2 — corrections & verification

- Re-captured home at 1440×6800 and 390×12000.
- Visit section verified complete at both widths: "Two Manhattan rooms. One
  standard of care.", both location cards (11 Broadway Suite 570 NY 10004;
  30 Central Park South Suite 10A NY 10019) with "Open map ↗", HOURS & FEES
  card (Mon–Fri 8am–8pm, Sat 8am–1pm, Sun closed, out-of-network note), and
  both CTAs ("Request appointment", "Call 646-370-4050").
- Footer verified complete at both widths: wordmark, tagline, Explore /
  Connect / Call columns, phone, email, "Medical emergencies: call 911.",
  © line. Content ends y≈6417 (desktop) / y≈11405 (mobile).
- No defects found in loop 2. Verdict: home and services complete & clean at
  1440 and 390; earlier viewport shots (1024/768/360) clean in loop 1.

## Final captures (judging set)

- screenshots/primary-desktop.png — home, 1440, full page
- screenshots/primary-mobile.png — home, 390, full page
- screenshots/secondary-desktop.png — services, 1440, full page
- screenshots/secondary-mobile.png — services, 390, full page

## Notes / known limitations

- Screenshot pipeline captures rendered pixels only; interactive states
  (hover, focus-visible, concierge error/loading/success, mobile nav overlay)
  are specified in Figma (07 Prototype & States) and implemented in CSS/JS but
  not pixel-captured.
- Google Fonts (Newsreader, DM Sans) load from the network; the headless
  captures rendered with them available. Offline fallback stacks are declared.
