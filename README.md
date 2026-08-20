# Grand Street Works — marketing site

Live at **[grandstreetworks.com](https://grandstreetworks.com)** (`www` 301s to the apex).

No build step, no framework. `index.html` is the whole marketing site; `work/`
is a folder of static reference builds it links into.

## Working on it

Open `index.html` in a browser. That's the dev loop — there is nothing to
install and nothing to compile.

To update the live site: edit `index.html`, commit, push. Render deploys
`main` automatically.

## Structure

One page, sectioned with the shared `[SEC_0x]` header bars:

| Section | Contents |
|---|---|
| Hero | Headline, lede, primary CTA (jumps to `#work`), metrics ticker |
| `SEC_01` | Where it leaks — the symptoms owners recognise, site first |
| `SEC_02` | What we build — websites, native apps, back-office systems |
| `SEC_03` | How a build runs — read, directions, build, handover |
| `SEC_04` | Work — the twenty reference industries, linked into `work/` |
| `SEC_05` | The free homepage rebuild — the way in |
| `SEC_06` | Operations audit — for businesses whose site isn't the problem |
| `SEC_07` | What we won't do |
| `SEC_08` | Principal |
| `SEC_09` | Fair questions (FAQ) |
| Footer | Contact CTA |

## `work/` — the reference builds

`work/` holds twenty industries, six homepage directions each (120 pages plus
twenty per-industry index pages), and `work/index.html` lists them in the site's
own design system. They came from `~/fractal/cash_rich/demos/` and are copied in,
not linked — editing them there does not change what is published here.

Every business in them is **fictional**, which the pages say in their own footers
and the site says in `SEC_04`. Every page under `work/` carries
`<meta name="robots" content="noindex">` so invented practices never compete with
the real page in search results. If you ever want that traffic, removing the tag
is a one-line change per file — but read the warning in the internal notes first.

The reference pages themselves are self-contained: one `<style>` block, no JS, no
images, one Google Fonts request each, and no outbound links. They do not carry a
contact address, so the `mailto:` count below is unaffected by them.

The per-industry `work/<industry>/index.html` pages are ours, not the harness's:
site header, then straight into the viewer — the six directions in a rail, and a
live `<iframe>` preview that swaps when you pick one. The width toggle above it
**defaults to desktop**; Phone reloads the same page at 390px on a black stage.
There is deliberately no title block or intro copy above the frame: the point of
the page is to land on a finished homepage, not to read about one. (That also
means these pages carry no `<h1>` — acceptable here because they are `noindex`
and the identity lives in the tab title and the footer.) Below 1000px the rail
becomes a horizontal scroller above the frame and the width toggle hides,
because the viewport is already the phone the demo was built for.
Without JavaScript every direction is still a plain link — the preview just
stops swapping.

Regenerate those twenty pages with:

    python3 tools/build-work-index.py [--source <demos dir>]

It parses the direction names, the FIX each one answers, the axis picks and the
accent swatch out of the demo harness's own index pages in
`~/fractal/cash_rich/demos` and rewrites ours from a template. It always reads
the harness format, never the page it last wrote, so running it twice is a no-op.
It is a maintenance tool, **not** a build step — Render still publishes the repo
exactly as committed.

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

Verified in headless Chrome at 500 / 768 / 1024 / 1440px: `scrollWidth` equals
`innerWidth` at every one, no element's bounding box crosses the viewport edge,
and all grids collapse correctly. 500px is the floor because headless Chrome
clamps its window width there — narrower phone widths have to be checked in a
real browser's device emulation.

## Contact address

Every CTA on the page is `mailto:joe@grandstreetworks.com` — four places (header,
`SEC_05`, `SEC_06`, footer).
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
