# Visual QA log

QA was run against the local static site on 2026-09-02. The primary page is `index.html`; the secondary page is `services.html`.

## Coverage

- Screenshots: 1440×1000, 1024×768, 768×1024, 390×844, and 360×800.
- Required neutral captures: `primary-desktop.png`, `primary-mobile.png`, `secondary-desktop.png`, and `secondary-mobile.png`.
- Browser checks: true device metrics at 390 and 360 widths, document overflow, console errors, navigation behavior, search/filter behavior, concierge validation/loading, font loading, and image crops.
- Automated accessibility scan: axe-core 4.10.3 on the homepage and mobile Services page.
- Source checks: JavaScript syntax, internal file references, image dimensions/formats, and local HTTP responses.

## Inspect → correct → recapture loops

### Loop 1 — responsive navigation and runtime hygiene

Inspection found that the desktop navigation remained too dense at the 1024 breakpoint and the browser requested a missing favicon. The breakpoint was changed so the intentional mobile navigation sheet takes over at tablet widths; a published logo asset was wired as the favicon. Captures were regenerated at 1024, 768, 390, and 360 widths. Console output was clean afterward.

### Loop 2 — collage and mobile hierarchy

Inspection found a founder/collage label collision and a Services mobile hero that pushed the first useful controls too far below the fold. The overlapping label was removed, the founder's name and role were carried by stable adjacent copy, and the Services hero was shortened so search and filter controls appear sooner. All primary and secondary captures were regenerated.

### Loop 3 — authority and contrast refinement

The final adversarial pass found a remaining decorative badge that weakened the clinical tone and three service-card text combinations below AA contrast. The badge was removed; the physician's name was strengthened in hero copy; featured-card text was changed to white; and the quiet-card paragraph was changed to espresso. The required homepage captures were regenerated and the same fills were synchronized back to Figma.

## Final results

| Check | Result |
| --- | --- |
| Homepage axe scan | 41 passes, 0 violations |
| Services mobile axe scan | 41 passes, 0 violations |
| Console | No errors on audited routes |
| Document horizontal overflow | None at 1440, 1024, 768, 390, or 360 widths |
| Keyboard affordances | Skip link, visible focus, menu state, focus handoff, Escape close, labeled controls, and live validation present |
| Motion | `prefers-reduced-motion` disables nonessential transitions and smooth scrolling |
| Images | Local WebP/JPEG, explicit dimensions, hero priority, below-fold lazy loading |
| Fonts | Local WOFF2 with `font-display: swap`; two-family limit observed |
| SEO | Titles, descriptions, canonicals, landmarks, and MedicalClinic JSON-LD present |

The mobile filter-chip row is intentionally horizontally scrollable so medical labels remain readable and touch targets stay large. The row itself can scroll, but the document width does not overflow.

## Known unverified behavior

- The local concierge validates and demonstrates a loading state, then hands off to the live appointment page. No protected health information is collected locally.
- External appointment, portal, map, quiz, and source-site links were preserved but not submitted or authenticated during QA.
- Current operating details still need owner confirmation because the live site's visible content, JSON-LD, and a legacy office page conflict. See `01-audit.md`.
- No deployment, CMS integration, production analytics, or live form endpoint was in scope.
