# Grand Street Works — client-facing marketing site

Single static page, no build step. `index.html` is the whole site.

The landing page for the **cash_rich** cold-outreach campaign
(`~/fractal/cash_rich`, ~5.8k sendable contacts across ~100 categories in NY,
LA, Chicago, Houston, Phoenix, Philadelphia). Every email in that campaign
points here.

## Why this exists separately from Grand Street AI

Same offers, different audience. Grand Street AI speaks to technical teams
shipping AI features. Grand Street Works speaks to owner-operators — dental
practices, PI firms, CPAs, roofers, med spas — who are suspicious of "AI" as a
brand promise and want to see a firm, not a startup. The name drops the "AI",
the copy leads with hours and dollars, and the trust wedge (what we *won't*
do) is on the front page rather than in a contract.

The two sites cross-link: `[SEC_07] Principal` here points at grandstreetai.com
as the sister practice.

## Look and feel

Deliberately identical to grandstreetai.com — the CSS and the WebGL shader hero
were **copied verbatim** from `~/fractal/grandstreetai/index.html` so the two
sites read as one practice. Additions live in a second `<style>` block at the
end of `<head>` (`.tile`, `.band`, `.refusal-grid`, `.verticals-list`,
`.callout`).

**This is a copy, not an import.** Changing the design system on grandstreetai
does not propagate here. If you restyle one, restyle both.

Verified in headless Chrome at 500 / 700 / 900 / 1100 / 1440px: no horizontal
overflow, all grids collapse correctly. The hero shader degrades to the flat
background when WebGL is unavailable (same fallback as the sibling site).

## Copy source

Offers and copy come from `~/fractal/1m/offers/` — the audit, training,
assistant, and SaaS-replacement docs. When an offer changes there, change it
here.

**No prices on the page**, matching grandstreetai. Pricing is quoted per
engagement over email; internal pricing stays in the offer docs. Don't add
numbers without Joe's say-so.

## Before this goes live

1. **Register `grandstreetworks.com`.** Confirmed unregistered by whois on
   2026-08-19 (`grandstreetworks.ai` was also free). Registrars can still price
   a name as premium — check before assuming.
2. **Email must work first.** Every CTA on the page is
   `mailto:joe@grandstreetworks.com` (5 places). Set up forwarding at the
   DNS/registrar layer → joe.waine@gmail.com, plus Gmail send-as so replies
   come from the domain. A live site with a dead mailto is worse than no site.
3. **Never send cold volume from this domain.** Use a separate sending domain,
   same rule as grandstreetai.

## Hosting: GitHub → Render

`render.yaml` is a Render blueprint (static site, publish path `.`, no build
command), identical in shape to the grandstreetai one.

1. Create `github.com/joewaine/grandstreetworks`, push this directory.
2. dashboard.render.com → New → **Blueprint** → connect the repo.
3. Custom domains (Settings → Custom Domains):
   - `grandstreetworks.com` → A record to Render's apex IP (confirm the value
     Render shows you; it was `216.24.57.1` for the sibling) or ALIAS/ANAME
   - `www.grandstreetworks.com` → CNAME to the `*.onrender.com` hostname
4. TLS is automatic once DNS resolves.

To update the site: edit `index.html`, commit, push. That's the whole pipeline.

## Known gaps

- **No proof on the page.** No case studies, testimonials, or client names —
  nothing was invented. The Interior Motives audit in
  `1m/offers/ai-opportunity-audit.md` is the obvious first one to write up
  (anonymised if needed) and drop in above `[SEC_08]`.
- **"90+ projects shipped"** is inherited from grandstreetai's live copy. If
  that number is stale, it's stale in two places now.
- No analytics. Add whatever you use before the campaign sends, or you won't
  know which of the ~100 verticals actually clicks.
