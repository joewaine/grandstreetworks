# 01 — Independent Audit: sohomenshealth.com

Audited 2026-09-02 against the live site (homepage, /meet-the-doctor/, /our-office/,
/testimonials/, /about-us/) including its JSON-LD structured data. Raw captures in
`./audit/`.

## Run setup (completed block, copied from RUN-SETUP.yml)

```yaml
run_id: "3"
agent_and_model: "WITHHELD FOR BLIND JUDGING — recorded in ../MAPPING.md"
website_url: "https://sohomenshealth.com/"
repository_path_or_url: "NONE — build inside your own result folder"
figma_file_url: "recorded in 03-report.md — bridge-bound file (see tooling note)"
canva_project_url: "recorded in 03-report.md"
business_name: "SoHo Men's Health"
business_type: "Physician-led men's health & wellness clinic — outpatient specialty medical practice (schema.org MedicalClinic), two Manhattan offices"
primary_audience: "Men ~30–65 in Manhattan/NYC seeking confidential, doctor-led care for hormonal, sexual & reproductive, aesthetic, pain, and wellness concerns; discretion- and credential-conscious"
primary_conversion: "Request an appointment (appointment request / call 646-370-4050 / OnPatient portal booking)"
secondary_conversions: "Wellness quizzes (Testosterone, Sexual Health), ask-the-doctor contact form, patient portal login, phone call"
required_pages: "Homepage is in scope. Secondary page: Services — audit showed the ~70-item mega-menu buries revenue services; a structured services page is required for the conversion path."
required_content: "Every published business fact on the live site: name, phone, address, licence/registration numbers, services, service areas, testimonials, partnerships."
brand_assets: "Only what the live site publishes — logo, photography, video, copy. No stock, no invented imagery."
reference_sites: "NONE supplied. No competitor was opened or imitated."
known_constraints: "Static production-oriented implementation; WCAG 2.2 AA where practical; preserve factual content; two font families maximum; no deployment."
time_budget: "4 hours"
implementation_required: true
deployment_required: false
audited_on: "2026-09-01"
```

## Business facts verified from the live site

- **Name:** SoHo Men's Health — "Specialty Healthcare for Men"; claims "The First
  Men's Health & Wellness Experience in New York City".
- **Phone:** 646-370-4050 (header + footer display). **Fax:** 347-474-7595.
  JSON-LD and one header `tel:` link carry 347-749-1174 — discrepancy flagged below.
- **Email:** info@sohosurgery.com (JSON-LD).
- **Offices:** 11 Broadway, Suite 570, New York, NY 10004 · 30 Central Park South,
  Suite 10A, New York, NY 10019.
- **Hours (footer, displayed):** Mon–Fri 8am–8pm, Sat 8am–1pm, Sun closed.
  JSON-LD says Mo–Fr 8AM–5PM — discrepancy flagged below.
- **Out of network:** "Please note, we are out of network. Upon request, we will
  provide you a detailed breakdown and coding should you wish to make an insurance
  claim." A public price list page exists (/price-list/).
- **Founder:** Kerem H. Bortecen, MD, PhD, MBA, FACS — Founder & Surgical Director.
  PhD Oxford (England); MBA University of Toronto (Canada); surgical training Yale,
  then University of Pennsylvania; appointed Assistant Professor of Surgery at
  Dartmouth Medical School; current faculty appointment at the Surgery Department
  of NYU Long Island School of Medicine. Awards: Yale Surgery Teaching Award;
  Transplantation Society Young Investigator Award. Member Yale Surgical Society;
  Fellow, American College of Surgeons; Diplomate, American Board of Surgery.
  Peer-reviewed publications; national/international conference presentations.
- **Experience claim:** "Our providers have been practicing for over 20+ years."
- **Services (8 homepage categories):** Hormonal Therapy; Sexual & Reproductive
  (penis health, prostate, pelvic floor, anal/anorectal health); Rejuvenation &
  Aesthetics (PRP facial, MicroPeel, microdermabrasion, injectables, Morpheus8,
  Density RF, Edge One CO2, Hydrafacial, Letybo…); Surgical Diseases; IV Drip
  Therapy (IV, NAD+/NR/NMN, lipotropic); Pain Management; Wellness & Education
  (Ozempic, exosomes, peptides…); Screening & Prevention. Full catalog ≈ 70
  published service pages.
- **Testimonials:** 13 published (8 Google-sourced on homepage carousel, 5 named on
  /testimonials/). Google review link: g.page/r/CUKFjXq2fwzSEAg/review.
- **Conversion surfaces:** Request Appointment (/appointments/), Call 646-370-4050,
  Patient Portal (onpatient.com), Testosterone Wellness Quiz, Sexual Health &
  Wellness Quiz, contact/ask-the-doctor form.
- **Social/partners:** Facebook, Twitter/X, Instagram (@sohomenshealth); sister
  site sohomensbeauty.com; site credit O360®; video "OFFICIAL SoHo TV" (mp4).
- **Assets published:** logo (Screenshot-30x.jpg, 262×71), mark (Screenshot-32.jpg),
  Dr. Bortecen portraits (2), 8 real office photographs (853×1000), Shutterstock
  library licensed by the site (8+ images incl. hero "two men discussing their
  health", 1280×853).

## Five strongest existing qualities

1. **Credential depth that money can't buy.** An MD/PhD/MBA/FACS founder with
   Oxford–Yale–Penn–Dartmouth–NYU history, stated plainly. This is the brand's
   core differentiator and it is real.
2. **A genuinely deep service catalog.** ~70 condition/treatment pages — strong
   long-tail SEO and proof of clinical range few competitors match.
3. **Real photography exists.** Eight actual office photos and real doctor
   portraits are published — the practice has honest raw material most clinics lack.
4. **Authentic social proof.** 13 specific, physician-naming testimonials
   (Google-sourced) with a live review link.
5. **Conversion surfaces are numerous.** Phone, appointment request, portal,
   quizzes, price list, ask-the-doctor — the intent infrastructure exists.

## Five highest-impact problems (and business consequence)

1. **A ~70-item mega-menu organized by medical taxonomy, not patient intent.**
   Revenue services (TRT, ED, hair loss) sit three levels deep beside "Anal Skin
   Tags". *Consequence:* visitors can't self-locate; anxiety rises; bookings lost.
2. **Dated template aesthetics undersell premium pricing.** Generic medical-stock
   look, low-res screenshot logo, default Elementor widgets, autoplay carousel.
   *Consequence:* the out-of-network price point feels unjustified; trust leaks
   before the credentials are ever read.
3. **The privacy promise is buried mid-page.** "Confidential & Personalized
   Experience" — the single strongest anxiety-reducer in men's health — is an H1
   below a generic hero. *Consequence:* the biggest barrier (discretion) is
   unanswered above the fold; bounce among first-time visitors.
4. **Trust signals are fragmented and inconsistent.** Two different phone numbers,
   two different sets of hours (footer vs JSON-LD), credentials on one page,
   reviews on another. *Consequence:* skeptical cross-checkers find contradictions;
   SEO/structured-data quality suffers.
5. **Heavy, inaccessible front-end.** Elementor + jQuery + Swiper carousel
   (autoplay, duplicated slides), render-blocking assets, empty alt attributes,
   testimonial content reachable only via carousel. *Consequence:* slow mobile
   experience, poor screen-reader access, weakened Core Web Vitals/SEO.

## Ranked redesign opportunities

1. Rebuild IA around patient concerns with a structured Services page (mega-menu →
   8 clear "rooms" of care).
2. Discretion-first hero: lead with confidentiality + physician-led care.
3. Consolidate trust: credentials, publications, awards, and guest-book
   testimonials in one authoritative narrative.
4. Persistent concierge booking strip ("When would you like to come in?") that
   follows the scroll narrative.
5. Art-direct the real office/doctor photography (warm grade, rounded frames,
   collage) instead of stock-look presentation.
6. Static, semantic, accessible rebuild (performance + WCAG 2.2 AA).
7. Fix data consistency (single phone/hours source of truth) in copy and JSON-LD.

## Explicit assumptions and unknowns

- **Phone:** 646-370-4050 treated as primary (it is the displayed number in header
  and footer); 347-749-1174 appears only in JSON-LD/one stale `tel:` link.
  Flagged for client, not silently "fixed" in facts — the redesign displays the
  public number consistently.
- **Hours:** footer hours (Mon–Fri 8–8, Sat 8–1) treated as current; JSON-LD
  hours are stale. Both recorded here for client verification.
- **No licence/registration numbers** are published anywhere on the site; none
  invented.
- **Booking backend** (/appointments/, onpatient.com) is third-party; the static
  build links to the live public endpoints rather than replicating them.
- **Figma access** is via the open-source plugin bridge (see tooling note in
  03-report.md): no `create_new_file`, no variables API; tokens are built as
  documented swatch/type-style frames inside the file.
- **Newsreader + Source Sans 3** chosen for the prescribed direction (soft text
  serif + humanist sans; two families max, both Google Fonts/OFL).
