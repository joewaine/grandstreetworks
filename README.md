# Grand Street Works — marketing site

Live at **[grandstreetworks.com](https://grandstreetworks.com)** (`www` 301s to the apex).

No build step, no framework. `index.html` is the home page, `what-we-build/`
is the one secondary page, `styles.css` is the design system both share, and
`work/` is a folder of static reference builds they link into.

## Working on it

Open `index.html` in a browser. That's the dev loop — there is nothing to
install and nothing to compile. Paths between the pages and to `styles.css`
are relative, so `file://` works as well as a server; `python3 tools/serve.py`
serves the repo on :8777 with caching off if you want real URLs.

To update the live site: edit `index.html`, commit, push. Render deploys
`main` automatically.

## Structure

Three pages, all sectioned with the shared `[SEC_0x]` header bars, all linking
`/styles.css`. The split is deliberate: the home page carries one argument
(here is the problem, here is the proof, here is the free way in) and every
description of the services themselves lives on the second page, so nobody has
to scroll past a price list to reach the work.

`index.html` — the home page:

| Section | Contents |
|---|---|
| Hero | Headline, lede, the URL capture that starts the free rebuild, metrics ticker |
| `SEC_01` | Where it leaks — the three symptoms a website is answerable for |
| `SEC_02` | Work — the twenty reference industries, linked into `work/` |
| `SEC_03` | The free homepage rebuild — the way in |
| `SEC_04` | Principal |
| `SEC_05` | Fair questions (FAQ) |
| Footer | Contact CTA |

`what-we-build/index.html` — everything a buyer asks about second:

| Section | Contents |
|---|---|
| Intro | What the three services are and the order they come in |
| `SEC_01` | What we build — websites, native apps, back-office systems |
| `SEC_02` | Where the hours go — the three back-office symptoms |
| `SEC_03` | Operations audit — for businesses whose site isn't the problem |
| `SEC_04` | What we won't do |
| `SEC_05` | Join us |
| Footer | Contact CTA |

The home page reaches it from the header nav, from a callout under the work
intro, and from the `Builds` row of the principal table.

`start/index.html` — the intake diagnostic, and the destination of every CTA
on both sites:

| Part | Contents |
|---|---|
| `Q_01` | The site you have — seeded from the hero and the work-gallery bands |
| `Q_02` | The trade — the same twenty keys as the `work/` directories |
| `Q_03` | How old the site is |
| `Q_04` | What is actually costing money — the routing question, ranked, pick two |
| `Q_05` | Headcount |
| Result | The verdict, then the contact capture |

The engine is `start/intake.js`; everything site-specific — questions, options,
scoring weights, verdict copy — is the `INTAKE_CONFIG` object in the page. The
same `intake.js` runs grandstreetai.com/start/ as a **copy, not a link**, the
same rule the design system already follows between the two sites.

Four verdicts plus a fifth that sells nothing. Each option carries a `scores`
map; the engine sums them, first pick at full weight and second at half, then
the config's `adjust()` hook nudges for trade and size. `services` declaration
order breaks ties, and the "don't buy anything" verdict is declared first on
purpose: a set of answers that scores nothing lands there rather than
defaulting into a pitch. That branch renders no contact form at all. It is the
reason the other four read as a diagnosis instead of a funnel.

The verdict is **ungated** — it renders before anything is asked for. That
costs some leads and it is the right call on a page whose own copy promises
"no call required, no obligation". Revisit it only if the inbox stays empty
while `/start/` completions do not.

The old `SEC_03` "How a build runs" — the read / directions / build / handover
walkthrough — was cut outright rather than moved. It repeated what the
websites card and the free-rebuild section already say.

`styles.css` is the whole design system, lifted verbatim out of the two
`<style>` blocks `index.html` used to carry. The generated pages under `work/`
still inline their own subset and are unaffected by it.

## `work/` — the reference builds

`work/` holds twenty trades, six builds each — 120 pages plus twenty per-trade
index pages — and `work/index.html` lists them in the site's own design system.

URLs read `work/<trade>/<business>.html`, e.g. `work/roofing/fair-oaks-roofing.html`.
Every one of the 120 is a **different fictional business** with its own name,
phone number, headline and argument; the trade-generic copy underneath is shared
on purpose, because six roofers really do all tear off and re-deck.

The pages are generated, not hand-edited. Sources are the harness in
`~/fractal/cash_rich/demos/` and the photographic set in `cash_rich/static2`;
per-page copy lives in `tools/demo_copy/<trade>.py` and `tools/photo_copy_*.py`.
Editing a file under `work/` directly will be overwritten on the next build.

Every business in them is **fictional**, which the pages say in their own footers.
Every page under `work/` carries
`<meta name="robots" content="noindex">` so invented practices never compete with
the real page in search results. If you ever want that traffic, removing the tag
is a one-line change per file — but read the warning in the internal notes first.

The reference pages themselves are self-contained: one `<style>` block, no JS, no
images, one Google Fonts request each, and no outbound links. They do not carry a
contact address, so the `mailto:` count below is unaffected by them.

The per-trade `work/<trade>/index.html` pages are ours, not the harness's:
site header, then the six builds stacked top to bottom on a neutral ground, each
in a live `<iframe>` at 90% of the browser width with air between them, so it is
obvious at a glance that another build follows. Above each one sits a bar carrying its accent, a `C1`–`C6` position marker, the
business the build is for, a **Desktop / Mobile** toggle, and **View full site**.
Only the first frame loads eagerly; the other five are `loading="lazy"`.

There is deliberately no title block or intro copy above the first frame: the
point of the page is to land on a finished homepage, not to read about one. (That
also means these pages carry no `<h1>` — acceptable while they are `noindex` and
the identity lives in the tab title and the footer.) Below 860px the width toggle
hides and every frame goes full-bleed, because the viewport is already the phone
the builds were made for.
Without JavaScript every direction is still a plain link — the preview just
stops swapping.

Two industries are **photographic** sets rather than CSS-only ones —
`01-personal-injury` today, built from `cash_rich/static2`, with real imagery,
self-hosted fonts and no external requests at all. Their pages are built by
`tools/build-photo-sets.py` and their per-page copy lives in
`tools/photo_copy_*.py`; their shared fonts and plates live in `work/_assets/`.

Rebuild, in this order — the copy builders need the plates on disk, and the
index generator reads the firm names out of the pages the other two write:

    python3 tools/prep-hero-images.py     # resample the plate library (once)
    python3 tools/build-photo-sets.py     # the photographic trade
    python3 tools/build-demo-copy.py      # the nineteen CSS-only trades
    python3 tools/build-work-index.py     # the twenty index pages

## Imagery

Every build carries one photographic plate, full-bleed, immediately under its
hero. They come from `~/fractal/cash_rich/hero_images` — five per trade,
Gemini-generated, no faces or text — resampled 2752px → 1600px at q66, which
takes the library from 278MB to 21MB and each plate to roughly 180KB.

The plate is injected after the first `<section>` in the body. That is the one
structural hook that holds across all 114 designs: most call their hero `.hero`,
a few call it `.band`, but in every case it is the first section on the page.

Fourteen builds instead put their plate **behind** the hero, with a directional
scrim in that design's own colour over it — measured from the rendered page by
`tools/measure-hero-colors.py`, cached in `tools/hero_colors.json`, and applied
by `tools/hero_backdrops.py`. Two of six in a chosen trade, so scrolling a set
shows both treatments.

Deliberately no border on the plate. These designs each own a different rule
weight and ink colour, and a borrowed hairline reads as a mistake in about half
of them.

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

CTAs funnel into `/start/`, not into a mail client: the hero URL capture, the
`SEC_03` rebuild band, the closing band on all twenty work-gallery pages, and
the footer. `mailto:joe@grandstreetworks.com` survives as the secondary
option under each of them, and as the fallback `/start/` composes for itself
when the intake endpoint cannot be reached.

That change is the point of the rework. A `mailto:` opens nothing on a lot of
phones, opens the wrong client for anyone living in webmail, asks a stranger
to compose a cold email from a blank window, and cannot be measured — which is
exactly the gap the "no analytics" note complains about. A form fixes all four.

Mail still has to be live **before** the site is — it is now the backstop
rather than the front door, and a backstop that bounces is worse than none.
The route is a Google Workspace user alias domain on the existing tenant, so
replies leave from the domain rather than from a personal Gmail; the
step-by-step is in the internal notes under "Email — runbook".

## Social

Content pipeline (formats, production recipes, caption skeletons, cadence):
see `~/fractal/1m/social-pipeline-works.md`. The sibling file
`social-pipeline.md` in the same folder covers Grand Street AI; the loop is
shared, the channel order is inverted — Instagram leads here, LinkedIn leads
there.

Instagram and the LinkedIn company page are **not set up yet**; the doc
carries the handles, bio copy and setup order. Card templates and the
`render.sh` screenshot script live in `../grandstreetai/assets/social/` and
need copying into `assets/social/` here before the first card ships.

Two rules that live in that doc but matter to anyone touching `work/`:
every reference build is a fictional business and any post using one has to
say so, and the invented firm names have never been searched against real
firms — do that before one goes out publicly.

## Hosting: GitHub → Render

`render.yaml` is a Render blueprint carrying **two** services: the static site
(publish path `.`, no build command) and `grandstreetworks-intake`, the Node
endpoint in `intake-api/` that `/start/` posts to. Both auto-deploy on push to
`main`.

The intake service is deliberately **not** on the free plan. Free services
spin down when idle and cold-start in roughly a minute; on a form submit that
means most real prospects would hit the mailto fallback instead of the form
working. It has no dependencies, so its build is a genuine no-op.

Set `RESEND_API_KEY` in the dashboard — it is `sync: false` in the blueprint
and must never be committed. Everything else has a default in `render.yaml`.
Without the key the service still accepts, validates and logs submissions and
still answers 200; it just does not email, so a missing key degrades to
"silently recorded" rather than "lost". Check `/health` to see which of mail
and logging are live.

`MAIL_FROM` defaults to `intake@send.grandstreetworks.com`. Resend verifies a
**subdomain**, so its DNS records sit on `send.` and do not touch the apex MX
that Google Workspace needs — the two do not collide. See `intake-api/README.md`.

One more consequence of `staticPublishPath: .` — everything in the repo is
served, so `intake-api/server.js` and `tools/` are publicly readable at their
paths. That was already true of `tools/`, and there are no secrets in either
(the service reads everything from the environment), but do not put one there.

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
