# Zach Becker — "Lake Light" preview

Static, dependency-free. Open `index.html` from any web server; every path
is relative so the folder can be lifted onto any host or sub-folder.

    python3 -m http.server 8471      # then http://localhost:8471/

## Files

    index.html          the page (semantic HTML, JSON-LD RealEstateAgent)
    styles.css          design tokens at the top, everything else refers to them
    script.js           nav drawer, hero video gating, form validation — ~130 lines
    assets/fonts/       Instrument Serif (regular, italic) + Inter variable, latin subset, self-hosted
    assets/img/         responsive ladders: JPEG + WebP at 640 / 1280 / 1920
    assets/video/       hero-1920.mp4 (1.3 MB) and hero-960.mp4 (0.6 MB), 7 s seamless loops, no audio

## The contact form has no delivery endpoint yet

`data-endpoint=""` on the `<form>` is empty, so a submit hands the message to
the visitor's mail client via `mailto:` and says so. To deliver server-side,
set `data-endpoint` to any URL that accepts a multipart POST and returns 2xx
(Formspree, the GSW intake API, a Cloudflare Worker, the franchise CRM) — the
existing success and failure messages are the live site's own strings. Call,
text and email links work as-is.

## Provenance

- Headshot, BHHS wordmarks, Leading Edge Society badge, bio, phone numbers,
  address, legal text and every outbound link: taken verbatim from
  zachbecker.bhhsnw.com on 2026-09-02.
- Aerial photographs and the hero video are **generated** (Gemini image model
  + Veo image-to-video) from prompts describing generic Eastside / Lake
  Washington scenery. They show no real address or listing and are captioned
  as illustrative on the page. Swap in real drone footage by replacing the
  files in `assets/img/` and `assets/video/` with the same names.
- Email address: the live site prints `Zachbecker@bhhsnwre.com` and links
  `zachbecker@bhhswre.com`. This build uses the printed one. Confirm with Zach.

## Video behaviour

The hero video is loaded only when `prefers-reduced-motion` is not set,
`Save-Data` is off and the connection is not 2G; otherwise the still stays.
A Pause control appears once playback starts (WCAG 2.2.2). The 960 cut is
served under 900 px.
