# Grand Street Works — marketing site

Single static page, no build step, no framework. `index.html` is the whole
site.

## Working on it

Open `index.html` in a browser. That's the dev loop — there is nothing to
install and nothing to compile.

To update the live site: edit `index.html`, commit, push. Render deploys
`main` automatically.

## Structure

One page, sectioned with the shared `[SEC_0x]` header bars:

| Section | Contents |
|---|---|
| Hero | Headline, lede, primary CTA, metrics ticker |
| `SEC_01` | Where the hours go — the symptoms owners recognise |
| `SEC_02` | Services — audit, training day, back-office assistant |
| `SEC_03` | How the audit runs — four steps |
| `SEC_04` | Software you own — the build offer |
| `SEC_05` | What we won't do |
| `SEC_06` | Who this is for |
| `SEC_07` | Principal |
| `SEC_08` | Fair questions (FAQ) |
| Footer | Contact CTA |

## Look and feel

Deliberately identical to [grandstreetai.com](https://grandstreetai.com) — the
CSS and the WebGL shader hero were **copied verbatim** from that site's
`index.html` so the two read as one practice. Additions live in a second
`<style>` block at the end of `<head>`: `.tile`, `.band`, `.refusal-grid`,
`.verticals-list`, `.callout`.

**This is a copy, not an import.** Changing the design system on grandstreetai
does not propagate here. If you restyle one, restyle both.

External dependencies are Google Fonts (Inter, JetBrains Mono) and three.js
from a CDN. The hero shader degrades to the flat background when WebGL is
unavailable.

Verified in headless Chrome at 500 / 700 / 900 / 1100 / 1440px: no horizontal
overflow, all grids collapse correctly.

## Contact address

Every CTA on the page is `mailto:joe@grandstreetworks.com` — five places.
Email forwarding and Gmail send-as must be live **before** the site is. A live
site with a dead mailto is worse than no site.

## Hosting: GitHub → Render

`render.yaml` is a Render blueprint — static site, publish path `.`, no build
command, auto-deploy on push to `main`.

1. dashboard.render.com → New → **Blueprint** → connect this repo.
2. Add both custom domains (Settings → Custom Domains), then create the DNS
   records at the registrar:

   | Host | Type | Value |
   |---|---|---|
   | `@` | A | `216.24.57.1` |
   | `www` | CNAME | `<service>.onrender.com` |

   `216.24.57.1` is Render's apex IP, in use by the sibling sites today —
   but confirm against what the Render dashboard shows you, since it can
   change. Use ALIAS/ANAME for the apex instead if the DNS host supports it.
3. TLS certificates are automatic once DNS resolves.
