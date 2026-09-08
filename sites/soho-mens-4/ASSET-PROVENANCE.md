# Asset provenance

All photographic and brand imagery in the website implementation and final Canva board was published by SoHo Men's Health. No new stock or generated imagery is included.

| Local asset | Live source | Treatment |
| --- | --- | --- |
| `assets/images/soho-logo.jpg` | `https://s33929.pcdn.co/wp-content/uploads/sites/411/2021/05/Screenshot-30x.jpg` | Original published JPEG retained. |
| `assets/images/dr-bortecen.webp` | `https://s33929.pcdn.co/wp-content/uploads/sites/411/2021/06/DrKeremBortecen_6.jpg` | Converted to WebP; subject and crop preserved. |
| `assets/images/consultation-hands.webp` | `https://s33929.pcdn.co/wp-content/uploads/sites/411/2021/05/shutterstock_1188007651-1.jpg` | Converted to WebP for the hero detail crop. |
| `assets/images/consultation-room.webp` | `https://s33929.pcdn.co/wp-content/uploads/sites/411/2021/05/shutterstock_740979067-1.jpg` | Converted to WebP for the services module. |
| `assets/images/conversation.webp` | `https://s33929.pcdn.co/wp-content/uploads/sites/411/2021/06/shutterstock_160661273-1.jpg` | Converted to WebP for the visit narrative. |

`assets/canva-art-direction.png` is the lossless 1200×1800 Canva export. `assets/canva-art-direction.webp` is the optimized 86 KB web derivative. The board contains only the published portrait, hands, and consultation-room images above plus flat type and color fields. It is a design-process artifact and is not shipped in either webpage.

Newsreader and DM Sans are open-licensed typefaces distributed through Google Fonts. The local WOFF2 files are self-hosted to avoid a runtime third-party request. Newsreader is used for editorial display copy; DM Sans is used for interface and body text. These fonts were prescribed as the direction's serif/humanist-sans pairing and are not business-owned brand assets.

SHA-256 checksums are available with `shasum -a 256 assets/images/* assets/fonts/*`.
