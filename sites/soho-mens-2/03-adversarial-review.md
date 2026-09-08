# Adversarial design review

Reviewed against the selected Figma direction before implementation, then checked again against the first browser capture. This is a failure list, not a presentation of strengths.

## 1. First-time customer in a hurry

- The first design draft let the hero heading collide with its explanatory copy at desktop width. That made the fastest reading path look unfinished.
- Four care-path labels still require the visitor to interpret a category before seeing a treatment name.
- “Request appointment” did not say that the visitor would continue to an existing scheduling system.

**Fixes:** Desktop hero spacing was corrected in Figma; the appointment microcopy now previews the scheduler handoff; every care path points directly to an expandable, complete treatment directory rather than a separate promotional page.

## 2. Skeptical customer looking for credibility

- A five-star claim without a review count could look inflated if embellished.
- The credential section originally collided with its paragraph in Figma and made the evidence hard to scan.
- The current site's contradictory phone/hours schema cannot be responsibly resolved in design.

**Fixes:** No review count was invented; all eight attributed testimonials remain available; the credential ledger spacing was repaired; phone, hours, addresses, insurance status, and affiliations use visible published content, while contradictions remain called out in the audit for owner verification.

## 3. Keyboard or screen-reader user

- A visually compelling numbered rail can become a non-semantic list of panels.
- A custom carousel would risk hidden focus, autoplay, and unclear position.
- The mobile menu needs reliable focus containment and an Escape path.

**Fixes:** The implementation uses an ordered list for care paths, native `details` disclosure widgets for service groups, a native modal `dialog` for mobile navigation, visible 3 px focus treatment, semantic landmarks and headings, a skip link, and a non-autoplay review scroller. Every treatment remains in the document and linked.

## 4. Mobile user on a slow connection

- The published portrait source is large, and the first mobile design devoted substantial height to it.
- A sticky conversion bar would obscure reading on a 360 px screen.
- Long service and credential labels could create horizontal overflow.

**Fixes:** The portrait has an optimized WebP derivative with explicit dimensions and is the only content photograph; fonts are self-hosted; no sticky bottom bar, video, third-party scheduler iframe, or animation library is loaded; long names wrap and the QA script asserts `scrollWidth === innerWidth` at all five required viewports.

## 5. Senior creative director looking for cliché or borrowed taste

- The first direction was at risk of becoming a generic beige-and-green “premium clinic” layout.
- Rounded white cards could reproduce the current template's visual sameness.
- A platform emoji arrow appeared in the first Figma render, breaking the otherwise restrained system.

**Fixes:** The numbered ledger is allowed to carry the concept across navigation, service hierarchy, credentials, and responsive behavior; white cards are limited to disclosures and quotes; hard rules and flat fields do most of the composition; the emoji glyph was replaced with a typographic arrow; clay appears only at the terminal action. No gradient, glass, decorative blob, stock lifestyle image, or competitor composition is used.

## Recorded Figma changes

- Re-spaced hero, physician, and service-directory copy after screenshot inspection.
- Replaced platform-rendered arrow emoji with a consistent text glyph.
- Added a content-driven 768 px tablet frame because the layout changes from a split hero to an intentional single sequence at the 800 px breakpoint.
- Retained separate 390 px default and open-navigation frames.
- Verified the revised desktop, tablet, and mobile frames through rendered Figma screenshots.
