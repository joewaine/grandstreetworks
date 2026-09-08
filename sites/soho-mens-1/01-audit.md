# 01 — Independent Audit: SoHo Men's Health (sohomenshealth.com)

Audited: 2026-09-01 · Method: live-site crawl (home, services, meet-the-doctor, testimonials,
contact-us, appointments, about-us, our-office, price-list), structured-data extraction,
full-page screenshots (1440px + 390px, `site-capture/shots/`), asset inventory
(`site-capture/assets/`). No changes made to the live site.

## Experiment setup (completed from this audit)

```yaml
run_id: "3"
agent_and_model: "WITHHELD FOR BLIND JUDGING — recorded in ../MAPPING.md"
website_url: "https://sohomenshealth.com/"
repository_path_or_url: "NONE — build inside your own result folder"
figma_file_url: "Plugin-bridge file (see 03-report.md — the bridge writes into the open file and does not expose its URL; sections 00–07 created there)"
canva_project_url: "created during Phase Two — recorded in 03-report.md"
business_name: "SoHo Men's Health"
business_type: "Physician-led men's health & wellness clinic — outpatient specialty medical practice (schema.org MedicalClinic), two Manhattan offices"
primary_audience: "Men ~30–65 in Manhattan/NYC seeking confidential, doctor-led care for hormonal, sexual & reproductive, aesthetic, pain, and wellness concerns; discretion- and credential-conscious; comfortable paying out-of-network fees"
primary_conversion: "Request an appointment (appointment request / call 646-370-4050 / OnPatient portal booking)"
secondary_conversions: "Wellness quizzes (Testosterone Wellness Quiz, Sexual Health & Wellness Quiz), ask-the-doctor contact form, patient portal login, phone call"
required_pages: "Homepage is in scope. Add one secondary page only if the audit shows the conversion path needs it."
required_content: "Every published business fact on the live site: name, phone, address, licence/registration numbers, services, service areas, testimonials, partnerships."
brand_assets: "Only what the live site publishes — logo, photography, video, copy. No stock, no invented imagery."
reference_sites: "NONE supplied. No competitor was opened or imitated."
known_constraints: "Static production-oriented implementation; WCAG 2.2 AA where practical; preserve factual content; two font families maximum; no deployment."
time_budget: "4 hours"
implementation_required: true
deployment_required: false
audited_on: "2026-09-01"
```

## Verified business facts (source of truth for the redesign)

- **Name:** SoHo Men's Health — tagline "Providing Excellent Care"; positioning line "The First Men's Health & Wellness Experience in New York City"
- **Phone:** 646-370-4050 · **Fax:** 347-474-7595 · **Email:** info@sohosurgery.com (different domain — published as-is)
- **Locations:** 11 Broadway, Suite 570, New York, NY 10004 (FiDi) · 30 Central Park South, Suite 10A, New York, NY 10019
- **Hours (footer, most prominent source):** Mon–Fri 8am–8pm, Sat 8am–1pm, Sun closed
- **Doctor:** Kerem H. Bortecen, MD, PhD, MBA, FACS — Founder & Surgical Director; PhD Oxford; MBA Univ. of Toronto; training Yale + Univ. of Pennsylvania; former Assistant Professor of Surgery, Dartmouth; faculty appointment, NYU Long Island School of Medicine; Fellow, American College of Surgeons; Diplomate, American Board of Surgery; Yale Surgery Teaching Award; Transplantation Society Young Investigator Award; 20+ years of provider experience
- **Service categories (8):** Hormonal Therapy (BHRT, hormone testing, TRT) · Sexual & Reproductive Health (ED, Peyronie's, premature ejaculation, P-Shot, shockwave, Xiaflex, Trimix; prostate: BPH, prostatitis, cancer; pelvic floor; anal health) · Surgical Diseases · Pain Management · Recovery · Rejuvenation & Aesthetics (PRP facial/hair/under-eyes, MicroPeel, microdermabrasion, injectables & fillers, Lip Flip, hyperhidrosis, Density RF, Edge One CO2 Laser, Hydrafacial, Letybo, Morpheus8) · Wellness & Education (Ozempic, exosomes, Skinvive, Kybella, Salmon DNA, peptides, NAD+/NR/NMN, IV drip, vitamin injections) · Screening & Prevention. Also EMSculpt NEO, EMSella, sclerotherapy.
- **Social proof:** 8 published Google reviews, rated 5/5 (K.G., R.D., O.S., M.P.S., J.L., P.C., P.S., A.G.)
- **Conversion assets:** Request Appointment (OnPatient portal), Testosterone Wellness Quiz, Sexual Health & Wellness Quiz, ask-the-doctor form, patient portal
- **Fees (published):** Cosmetic consult $150 (applied toward treatment); HRT consult $750; 24-hour cancellation policy, $75 late/no-show fee; out-of-network with detailed billing breakdown on request
- **Social:** Facebook, Twitter/X, Instagram (@sohomenshealth) · Sister brand: SoHo Men's Beauty

## Five strongest existing qualities

1. **Physician credibility that competitors can't copy.** A named founder with Oxford/Yale/UPenn/Dartmouth/NYU credentials and FACS fellowship — in a market dominated by anonymous med-spas, this is the decisive trust asset.
2. **Real, specific social proof.** Eight detailed Google 5-star reviews that name the doctor and describe outcomes — far stronger than generic star widgets.
3. **Genuinely comprehensive men's-health scope.** Hormonal, sexual/reproductive, surgical, pain, aesthetic, and wellness care under one roof — a real "one practice for men's health" story.
4. **Clear conversion intent and access.** Phone + Request Appointment + two self-assessment quizzes + patient portal; extended hours (8am–8pm) and two Manhattan locations reduce friction.
5. **An ownable brand seed.** The sage-green/charcoal palette, the "SoHo Men's Health" name, and the "Providing Excellent Care" tagline are calm, masculine, and clinical — worth keeping and sharpening.

## Five highest-impact problems (with business consequence)

1. **Navigation bloat: ~70-item, three-level Services mega-menu with "NEW!" badges.**
   Every service is shouted at equal volume; nothing is prioritized. *Consequence:* choice paralysis and drop-off before the appointment CTA; key revenue services (TRT, ED shockwave, aesthetics) are buried three levels deep; mobile nav is unusable.
2. **Carousel abuse + duplicated content.** A 7-photo hero background slideshow, two *identical* testimonial carousels, and the same welcome paragraph + quiz buttons repeated verbatim mid-page. *Consequence:* the page reads as a template, not a practice; autoplay hurts performance and accessibility; repeated copy dilutes the value proposition and wastes the reviews.
3. **No typographic identity and a broken heading outline.** Zero webfonts (system sans everywhere), the page's only `<h1>` sits mid-page, and live copy contains typos ("convienience", "We invite you complete a wellness quiz"). *Consequence:* a credibility tax on premium-priced consultations ($150–$750); weak scannability; SEO/accessibility defects.
4. **Stock-photo saturation and an authenticity gap; the mobile hero hides the pitch.** Every image is a Shutterstock file (filenames visible in source), 3 of 8 service-card photos don't match their topic, a vendor-branded EMSella video sits above the fold on mobile, and the mobile hero variant drops the headline entirely, leaving only a button. *Consequence:* the site feels interchangeable with any med-spa; the majority-mobile audience never sees the value proposition.
5. **Inconsistent contact facts and trust friction.** Schema.org lists phone +1-347-749-1174 and 8–5 hours; the footer shows 646-370-4050 and 8–8; the contact page says 10–7; email lives on a different domain; a sister-site banner is the first element on the page. *Consequence:* patients hesitate over which number to call or whether the practice is current; NAP inconsistency damages local SEO; first-impression screen space is spent on an exit link.

Additional accessibility/performance notes: autoplay carousels with no reduced-motion handling, `elementor-invisible` entrance animations (content blank until JS fires), heavy slider stack (Elementor Pro + HappyAddons), low-resolution JPEG logo (262×71 screenshot reused as favicon), native-controls embedded videos with internal filenames.

## Ranked redesign opportunities

1. **Rebuild the hero** as one confident statement + primary "Request Appointment" CTA + secondary call CTA, identical in substance on mobile — no slideshow.
2. **Collapse services IA** into the 8 published categories as scannable cards with plain-language summaries; retire the mega-menu.
3. **Build a trust stack near the top:** doctor portrait + condensed credentials + real review quotes — convert credibility into appointments.
4. **Establish a real design system:** two font families, a token palette grown from sage/charcoal, consistent spacing/radii — retire the clashing bright-blue accent and shape-divider curves.
5. **De-duplicate and sequence the narrative:** welcome → trust → services → doctor → reviews → locations/CTA; one testimonial module, verbatim quotes.
6. **Normalize the facts panel:** one phone, one hours table, both addresses, out-of-network note — present consistently everywhere (discrepancies flagged for the client, not silently "fixed").
7. **Performance & accessibility as features:** static build, no carousels, semantic headings, visible focus, reduced-motion support, responsive images with explicit dimensions.

## Explicit assumptions and unknowns

- **Hours conflict** (footer 8am–8pm vs contact page 10am–7pm vs schema 8–5): the footer table is used as the most prominently published source; the conflict is flagged for client confirmation, not resolved by invention.
- **Phone conflict** (646-370-4050 visible site-wide vs +1-347-749-1174 in schema only): 646-370-4050 is treated as primary.
- **Email domain mismatch** (info@sohosurgery.com on sohomenshealth.com): preserved exactly as published.
- **Logo:** only available as a 262×71 JPEG screenshot. The redesign uses a text wordmark in the published palette — no invented icon or mark.
- **Photography:** no authentic practice photography exists on the site except the doctor portrait (800×964, downloaded) and licensed Shutterstock images already published by the business. The redesign reuses a small, curated subset of those published images; no new stock is introduced.
- **Reviews:** quoted verbatim (including reviewers' own typos) as published user content.
- **Videos:** the two self-hosted videos and the skyline background clip are treated as out of scope for the static redesign; their role (credibility/ambience) is served by the doctor portrait and published photography.
- **Sister-site banner** ("SoHo Men's Beauty"): retained as a subtle footer link instead of a top banner (presentation change; fact preserved).
