# SoHo Men's Health — independent audit

Audited on 2026-09-02. The review covered the live homepage, Services navigation, Meet the Doctor, Contact, Office, Appointments, Testimonials, and both wellness-quiz paths, plus homepage JSON-LD. The redesign source set was restricted to content and imagery published by `https://sohomenshealth.com/`.

## Completed run setup

```yaml
run_id: "3"
agent_and_model: "WITHHELD FOR BLIND JUDGING — recorded in ../MAPPING.md"
website_url: "https://sohomenshealth.com/"
repository_path_or_url: "NONE — build inside your own result folder"
figma_file_url: "https://www.figma.com/design/L07XTNmYQwISBZBNb2cTx2"
canva_project_url: "https://www.canva.com/d/2LaX00YLrDgbXFB"
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
audited_on: "2026-09-02"
```

## Five strongest existing qualities

1. **Unusually broad service depth.** The live navigation makes clear that the practice can address hormonal, sexual and reproductive, surgical, pain, recovery, aesthetic, and preventive concerns in one setting.
2. **A credible founder story.** Dr. Kerem H. Bortecen's MD, PhD, MBA, FACS credentials and Oxford, Toronto, Yale, and University of Pennsylvania history are a strong reason to trust the practice.
3. **Privacy is already part of the promise.** The live copy repeatedly stresses a confidential, personalized experience, which directly answers a central barrier in men's health.
4. **Real conversion choices exist.** Appointment request, telephone, OnPatient, contact, and two quizzes accommodate visitors at different levels of readiness.
5. **Two Manhattan locations support convenience.** The Downtown and Central Park South offices make the service feel established and locally accessible.

## Five highest-impact problems

| Problem | Likely business consequence |
| --- | --- |
| The large, deeply nested service menu asks visitors to understand the clinic's taxonomy before they can find help. | High-intent visitors may abandon or choose a competitor whose relevant pathway is easier to recognize. |
| The founder's clinical authority is visually secondary to broad lifestyle and treatment imagery. | Premium out-of-network pricing has less visible justification, especially for skeptical first-time visitors. |
| Appointment actions are repeated, but the path feels administrative rather than reassuring or guided. | Visitors with privacy anxiety can defer the request even after finding a relevant service. |
| Information hierarchy is inconsistent across long pages, with many similarly weighted modules and calls to action. | Scanning is slower, the primary conversion loses prominence, and high-value proof is easy to miss. |
| Contradictory phone, hours, and insurance statements exist across visible content, structured data, and an older office page. | Search engines and patients can receive different operational details, creating avoidable trust and scheduling risk. |

## Ranked redesign opportunities

1. Put physician credentials and the appointment path in the first viewport without making the experience feel institutional.
2. Turn the service mega-menu into a searchable, grouped directory organized around recognizable needs.
3. Make booking feel hosted: ask for a preferred room, validate clearly, then hand off to the existing live appointment request.
4. Build a distinct editorial system around the real portrait and consultation imagery, with clear clinical language anchoring every warm moment.
5. Consolidate location, hours, network status, telephone, fax, and email in one scannable visit section.
6. Improve semantic structure, focus behavior, contrast, image loading, and mobile navigation.

## Factual reconciliation

| Topic | Live-site evidence | Decision in this build |
| --- | --- | --- |
| Telephone | Current visible header/footer and contact content show `646-370-4050`; homepage JSON-LD shows `+1-347-749-1174`. | Use the current visible number and flag the structured-data discrepancy for owner review. |
| Hours | Current visible footer shows Monday–Friday 8am–8pm, Saturday 8am–1pm, Sunday closed; homepage JSON-LD shows weekday hours ending at 5pm. | Use the current visible hours in page content; omit hours from new JSON-LD pending confirmation. |
| Insurance | Current visible site says the practice is out of network and can provide coding; an older office page says it accepts most insurance. | Use the current out-of-network statement and flag the older copy for removal or correction. |
| Address | Current visible site publishes 11 Broadway, Suite 570 and 30 Central Park South, Suite 10A. JSON-LD lists only Central Park South. | Present both current visible offices; include both in the new clinic schema. |

## Assumptions and unknowns

- The current visible header/footer and appointment information are treated as more operationally current than conflicting JSON-LD and legacy-page copy. Business-owner confirmation is still required before production migration.
- The appointment request remains on the live WordPress site; this static build demonstrates validation and then hands off rather than reproducing medical intake.
- No validated license/registration number or formal partnership claim surfaced on the audited pages, so none was invented or reproduced.
- The published menu is treated as the service source of truth. Category groupings in the new directory are editorial organization, not new clinical claims.
- No analytics, form endpoint, CMS, hosting target, privacy/legal review, or performance budget was supplied.

## Selected direction

The brief explicitly fixes Phase Two as **The Member's Rooms**, so no competing creative directions were invented or evaluated. To preserve the benchmark's strategy discipline without violating that instruction, the single direction is expressed through three coordinated pillars: **Hosted arrival** (the concierge strip), **Rooms of care** (category-led service modules), and **Clinical host** (founder credentials and guest-book proof). These are facets of one system, not alternatives.

The direction suits a discretion- and credential-conscious audience because hospitality language lowers the temperature of a difficult first visit while the founder's qualifications explain why the experience is premium. Newsreader supplies warmth and editorial gravity; DM Sans keeps navigation, forms, and service discovery direct. Ivory, espresso, muted sage, and oxblood are tactile but restrained. Rounded image crops focus on hands, rooms, and conversation, while the real surgeon portrait and a dedicated authority section prevent the composition from drifting into generic wellness.

### Holding the line against the spa cliché

Warmth is always adjacent to evidence: the hero pairs privacy language with `MD · PhD · MBA · FACS`; the darkest, highest-contrast section is the founder's training; treatment names remain explicit; and the visual system avoids flowers, wellness iconography, cosmetic promises, gradients, and invented lifestyle imagery. A noncompliant early Canva draft introduced decorative library elements; it was rejected and replaced with a board containing only live-published clinic imagery and flat color/type treatment.

## Adversarial review and fixes

| Perspective | Specific failure found | Correction made |
| --- | --- | --- |
| First-time customer in a hurry | The breadth of care still risked looking like six vague categories. | Added a searchable secondary directory and direct category anchors; kept appointment, phone, and services visible in the first viewport. |
| Skeptical customer | Hospitality styling initially outweighed surgical proof. | Moved credentials into the hero and added an authority-led founder section with named institutions and fellowship. |
| Keyboard or screen-reader user | The mobile navigation and concierge needed explicit state and error communication. | Added skip navigation, semantic landmarks, `aria-expanded`, Escape handling, focus transfer, labels, `aria-live`, invalid state, and strong focus styles. |
| Mobile user on a slow connection | Full-resolution source photography and decorative motion would have been costly. | Converted published imagery to compact WebP, added dimensions and lazy loading, self-hosted WOFF2 fonts, and reduced-motion behavior. |
| Senior creative director | A founder badge collided with the collage and the room motif risked feeling theatrical. | Removed the badge, simplified the collage, reduced the mobile services hero, and kept oxblood/sage accents subordinate to clinical hierarchy. |

## Recognition retained

The business name and published logo, real founder portrait, confidentiality/personalization promise, complete visible service vocabulary, testimonial excerpts and initials, contact details, two locations, published hours, out-of-network explanation, quizzes, patient portal, and doctor biography remain recognizable. The redesign changes hierarchy and organization, not the underlying medical claims.
