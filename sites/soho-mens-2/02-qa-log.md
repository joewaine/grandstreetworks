# Visual QA log

All captures were rendered in local Google Chrome from an isolated repository-local HTTP server. The final capture script uses the Chrome DevTools protocol to enforce CSS viewport dimensions exactly; its JSON report records viewport, document width, loaded fonts and images, and console issues.

## Required viewport matrix

| Viewport | Final capture | Result |
|---|---|---|
| 1440 × 1000 | `qa/loop-03-1440x1000.png` | Pass; `scrollWidth` 1440 |
| 1024 × 768 | `qa/loop-03-1024x768.png` | Pass; `scrollWidth` 1024 |
| 768 × 1024 | `qa/loop-03-768x1024.png` | Pass; `scrollWidth` 768 |
| 390 × 844 | `qa/loop-03-390x844.png` | Pass; `scrollWidth` 390 |
| 360 × 800 | `qa/loop-03-360x800.png` | Pass; `scrollWidth` 360 |

The final machine-readable record is `qa/loop-03-browser-report.json`. Both local fonts reported `loaded`, both content images reported complete with nonzero natural width, and the final console issue count is zero.

## Inspect → correct → recapture loop 1

**Inspection:** The initial browser pass showed that the smallest hero heading was depending too heavily on automatic line breaks, creating overflow risk and pushing the mobile menu beyond the visible crop in a browser with a minimum window width. The first Figma render also exposed desktop copy collisions and a platform-colored arrow glyph.

**Corrections:** Added an intentional mobile heading break and smaller 360/390 type clamp; constrained all hero flex children; corrected Figma hero, physician, and directory spacing; replaced the emoji arrow; added a full 768 px tablet frame; switched to an exact device-metrics capture harness.

**Recapture:** `qa/loop-01-*`. The exact report confirmed `innerWidth === scrollWidth` at all five target widths. Desktop, tablet, 390 px, 360 px, and open-dialog frames were visually inspected.

## Inspect → correct → recapture loop 2

**Inspection:** Below-the-fold captures exposed a dark-on-ink care-path intro caused by selector specificity. Review arrow controls also requested smooth scrolling even when the operating system preferred reduced motion. `file://` font-preload warnings made console evidence noisy.

**Corrections:** Increased the care-path intro to the mint AA-oriented token; made review scrolling instant under `prefers-reduced-motion`; moved the QA page to an isolated HTTP origin; disabled smooth scroll while capturing anchored inspection states.

**Recapture:** `qa/loop-02-*`. The physician ledger, all service summary cards, long open sexual-health directory, full testimonials, locations, footer, mobile menu, and 390 px scroll cues were visually inspected. No layout or content overflow was found. The only console issue was a favicon 404.

## Final verification

**Correction:** Declared the published wordmark as the favicon, removing the only resource error.

**Recapture:** `qa/loop-03-*`. All five viewport reports pass with exact width, loaded fonts/images, no horizontal overflow, and zero console issues. Neutral deliverables were copied from this run as `primary-desktop.png` and `primary-mobile.png`. No secondary-page screenshots are present because the audited conversion path did not justify adding a duplicate secondary page.

## Interaction and accessibility checks

- Native `dialog` opens from the mobile menu button, contains a visible Close action, closes with Escape, and keeps focus modal while open.
- Care paths are an ordered list; full services are native `details`/`summary` controls with long names wrapping at 390 px.
- Review scrolling has buttons on larger screens, native touch/trackpad scrolling, no autoplay, and reduced-motion handling.
- Skip link, semantic header/nav/main/sections/footer, one page-level heading, logical heading order, explicit image dimensions, descriptive physician alt text, visible focus, and high-contrast buttons are present.
- Appointment, call, review, maps, quizzes, price, patient portal, social, service, and doctor destinations were retained as links rather than recreated or submitted during QA.
- No animation library, third-party scheduler iframe, video, tracking script, or unnecessary dependency is loaded.
