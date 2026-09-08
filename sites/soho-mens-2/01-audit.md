# Independent website audit

Audited 2026-09-01 from the public homepage, About, Meet the Doctor, and Contact pages. No competitor sites were opened. This run treats visible page content as authoritative where it conflicts with stale structured data and flags those conflicts for approval rather than resolving them by invention.

## Completed experiment setup

```yaml
run_id: "2"
agent_and_model: "WITHHELD FOR BLIND JUDGING — recorded outside this result folder"
website_url: "https://sohomenshealth.com/"
repository_path_or_url: "NONE — static implementation created in this result folder"
figma_file_url: "https://www.figma.com/design/zGIH0tnRnSkplK5Voghjhh"
canva_project_url: "https://www.canva.com/d/Ge0Hz7WVCob_C16"
business_name: "SoHo Men's Health"
business_type: "New York City men's specialty health and wellness medical clinic"
primary_audience: "Adult men in New York City seeking discreet, personalized specialty care, particularly hormonal, sexual, reproductive, pelvic, prostate, anorectal, wellness, and aesthetic care"
primary_conversion: "Request an appointment"
secondary_conversions: "Call the clinic; explore services; complete a wellness quiz; access the patient portal; get directions"
required_pages: "Homepage only; the existing appointment scheduler remains the conversion destination"
required_content: "Every published business fact on the audited pages: name, phone, fax, addresses, services, hours, insurance note, testimonials, physician credentials and affiliations"
brand_assets: "Only assets published by the live site: logo and Dr. Bortecen portrait selected; no stock or invented imagery added"
reference_sites: "UNKNOWN — none supplied; no competitor was opened"
known_constraints: "Static production-oriented implementation; WCAG 2.2 AA where practical; preserve factual content; two font families maximum; no deployment"
time_budget: "4 hours"
implementation_required: true
deployment_required: false
audited_on: "2026-09-01"
```

## Five strongest existing qualities

1. **A clear niche with high recognition value.** The name and recurring mineral-green color immediately position the practice around men's health without hiding behind generic wellness language.
2. **Substantial physician credibility.** Dr. Kerem H. Bortecen is named and pictured; the site publishes his Oxford PhD, Toronto MBA, Yale and Penn training, former Dartmouth appointment, FACS status, American Board of Surgery diplomate status, awards, publications, and current NYU Long Island School of Medicine faculty appointment.
3. **A broad and unusually specific care offering.** Hormonal, sexual, reproductive, pelvic-floor, prostate, anorectal, rejuvenation, aesthetics, and wellness services let a visitor recognize a sensitive concern in concrete language.
4. **Strong first-party trust material.** Eight attributed Google testimonials consistently mention care, listening, professionalism, follow-up, comfort, and results. The site also states a five-star rating and 20+ years of provider experience.
5. **Useful access information is published.** Two Manhattan addresses, phone and fax numbers, office hours, an out-of-network disclosure, quizzes, patient portal, prices, and an appointment scheduler give visitors multiple practical next steps.

## Five highest-impact problems and business consequences

1. **The mobile homepage is visibly broken above the fold.** At 390 px, the hero image and headline disappear, leaving large blank bands, a lone appointment button, and unrelated media entering the viewport. **Consequence:** mobile visitors may assume the clinic is unmaintained or unsafe before they understand the offer, sharply weakening appointment confidence.
2. **The desktop hero sends mixed signals.** A generic lifestyle image, a long centered paragraph, two quiz buttons, navigation, contact data, and an appointment CTA all compete. The physician and medical credentials appear later. **Consequence:** a visitor with a sensitive, urgent concern has to work too hard to answer “can this clinic help me, and can I trust it?”
3. **Information architecture is service-led but not task-led.** The navigation exposes dozens of treatments in deeply nested menus while the homepage repeats eight broad service buckets without helping people start from a symptom, concern, or care path. **Consequence:** choice overload increases abandonment and can push uncertain visitors back to search results.
4. **Trust content is duplicated and inconsistently maintained.** Testimonials appear twice on the homepage; visible contact facts conflict with schema (646-370-4050 vs. a different structured-data phone, and 8am–8pm visible weekday hours vs. 8am–5pm schema hours). A map label also references 40 Exchange Plaza while the visible location is 11 Broadway, Suite 570. **Consequence:** contradictions harm local SEO and can make prospective patients question basic operational accuracy.
5. **Accessibility and performance are treated as add-ons.** Empty image alt text, carousel-heavy content, a fixed-size third-party scheduling iframe, white-on-image text, multiple animation libraries, numerous plugin assets, and unclear focus behavior create likely barriers. **Consequence:** disabled users and slow-connection mobile visitors face avoidable friction, while the heavy page delays the moment of trust.

## Brand, content, and experience observations

- **Character / audience fit:** The current sage-green, serif-and-sans palette feels calm and private, but the beach lifestyle photography and aesthetic-treatment promos pull the voice between medical authority and lifestyle advertising.
- **Navigation:** Core tasks are present, but “Services” acts as a near-sitemap. Phone, locations, beauty cross-link, portal, prices, quizzes, and appointment access all compete in the header.
- **Hierarchy / scannability:** Key claims recur while physician credentials and insurance status arrive late. Long testimonial carousels obscure how much proof exists.
- **Typography / composition:** Lora and Montserrat are recognizable and usable, but long centered copy and repeated rounded white panels flatten hierarchy. The mobile composition does not intentionally re-sequence content.
- **Trust / conversion:** The strongest trust signal is the physician, yet the first CTA cluster prioritizes quizzes. Appointment language is clear but does not preview what happens next.
- **Responsive / interaction:** The audited 390 × 844 state loses the core hero content. Mega-menu and carousel behavior likely create keyboard and small-target friction.
- **Accessibility / performance:** Contrast needs systematic verification, all controls need visible focus, motion needs a reduced-motion path, and images need explicit sizes, useful alt text, and modern compression. The WordPress/Elementor/plugin payload is much heavier than the proposed static page needs.
- **Recognition to retain:** Wordmark, mineral green, calm serif voice, named doctor portrait, two-location presence, five-star review language, quiz entry points, and language of confidentiality/personalized care.

## Ranked redesign opportunities

1. Put a concise, discreet care promise, one primary appointment CTA, and a direct call option above the fold; explain that scheduling continues on the clinic's existing secure scheduler.
2. Introduce Dr. Bortecen and a compact credential ledger near the hero so trust precedes treatment browsing.
3. Replace the mega-menu mental model with four understandable care paths, then keep the complete published service list in a searchable/expandable directory.
4. Make mobile a deliberate sequence: promise → action → care paths → doctor → proof → locations, with a persistent but unobtrusive appointment action.
5. Consolidate reviews into one accessible horizontal list, publish insurance and hours once, and flag source-data conflicts for owner correction.
6. Centralize an AA-oriented color/type/spacing system and use semantic HTML, visible focus, 44 px targets, reduced motion, and no essential carousel automation.
7. Retain only the logo and real physician/office imagery needed to establish identity; remove decorative stock imagery and redundant promotional graphics.

## Assumptions and unknowns

- The primary visitor is an adult man in or near Manhattan who values discretion and wants either to identify the right care path or schedule directly. This is inferred from the services, location, and published privacy language.
- Requesting an appointment is the primary conversion because it is the dominant repeated CTA and leads to the current scheduler. No scheduler backend is recreated in this static build.
- The homepage alone is sufficient for this benchmark because the existing scheduler and deeper service pages remain the destinations; a new secondary page would duplicate those flows without new verified content.
- Visible facts are preserved as published: phone 646-370-4050, fax 347-474-7595, 11 Broadway Suite 570, 30 Central Park South Suite 10A, Monday–Friday 8am–8pm, Saturday 8am–1pm, Sunday closed, and the out-of-network note.
- No medical licence or registration number was found on the audited pages. FACS and American Board of Surgery status are professional credentials, not licence numbers.
- The site states “Rated 5 out of 5” but does not publish a review count in the audited homepage content; no count is invented.
- The owner should verify the conflicting structured-data phone/hours and the 40 Exchange Plaza map label before deployment.
- All treatment suitability, outcomes, prices, and insurance reimbursement remain matters for the clinic; the redesign makes no new medical or financial claim.
