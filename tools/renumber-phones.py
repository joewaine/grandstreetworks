#!/usr/bin/env python3
"""Replace the 555 placeholder numbers, and stop the call links dialling.

Every one of the 120 builds carried a (555) number. Six firms in a trade with
six 555 numbers reads as one template filled in six times, which is the exact
impression the set exists to avoid. Twenty-two of the numbers were also invalid
NANP on their own terms — an exchange cannot begin with 0 or 1.

This assigns each build a plausible number instead:

  * a real area code, never repeated inside one trade, so six builds on a trade
    index page never show the same code twice;
  * a valid exchange (first digit 2-9, no N11, never 555);
  * the build's existing last four digits, which were already unique.

Assignment is deterministic from the build's slug, so re-running is a no-op and
a rebuilt page gets the number it had.

It rewrites the built pages *and* the copy decks they are generated from
(tools/demo_copy/*.py, tools/photo_copy_pi.py, tools/identity_specs.py), so a
later `build-demo-copy.py` run does not put 555 back.

`SOURCE_PHONE` / `SOURCE_TEL` are left alone by construction: those are the
original prospect's numbers, and the builders use them as a guard that refuses
to emit a page still carrying the source's branding.

    python3 tools/renumber-phones.py --dry-run
    python3 tools/renumber-phones.py
    python3 tools/renumber-phones.py --keep-call-links

By default the tel: hrefs are removed — the number stays visible and styled,
but a click does nothing, because these are demonstrations of invented firms
and the numbers now look real enough to dial.
"""

import argparse
import hashlib
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
DECKS = [REPO / "tools" / "photo_copy_pi.py",
         REPO / "tools" / "identity_specs.py"]

# Real, in-service, geographically spread. No toll-free, no N11, no 900.
AREA_CODES = [
    "205", "207", "210", "217", "225", "231", "251", "253", "269", "302",
    "309", "316", "319", "337", "351", "360", "385", "402", "406", "413",
    "419", "435", "458", "463", "502", "507", "520", "534", "540", "559",
    "564", "570", "573", "580", "585", "603", "605", "607", "620", "641",
    "660", "662", "681", "715", "717", "719", "726", "731", "743", "754",
    "765", "772", "812", "815", "830", "843", "850", "854", "878", "903",
    "906", "912", "915", "920", "928", "930", "934", "936", "947", "959",
    "970", "971", "984",
]

PHONE_RE = re.compile(r"\(555\)\s(\d{3})-(\d{4})")
# Anchors whose only job is to dial.
TEL_HREF_RE = re.compile(r'\shref="tel:\+?1?\d+"')


def digest(*parts: str) -> int:
    """Stable across runs and interpreters, unlike hash()."""
    return int(hashlib.sha256("|".join(parts).encode()).hexdigest(), 16)


def exchange_for(slug: str, existing: str) -> str:
    """A valid NANP exchange: 2-9 first digit, not N11, not 555."""
    n = digest(slug, "exchange")
    for attempt in range(40):
        first = str(2 + (n >> (attempt * 5)) % 8)
        rest = f"{(n >> (attempt * 7)) % 100:02d}"
        candidate = first + rest
        if candidate != "555" and not re.fullmatch(r"(\d)11", candidate):
            # Keep the original exchange when it was already valid, so the
            # change to a page is the area code alone wherever possible.
            if re.fullmatch(r"[2-9]\d\d", existing) and existing != "555" \
                    and not re.fullmatch(r"(\d)11", existing):
                return existing
            return candidate
    return "204"


def assign(trade: str, slug: str, taken: set[str]) -> str:
    """An area code this trade has not used yet."""
    start = digest(trade, slug) % len(AREA_CODES)
    for i in range(len(AREA_CODES)):
        code = AREA_CODES[(start + i) % len(AREA_CODES)]
        if code not in taken:
            taken.add(code)
            return code
    return AREA_CODES[start]


def build_map() -> dict[str, tuple[str, str]]:
    """old 10 digits -> (new display, new digits), one entry per build."""
    mapping: dict[str, tuple[str, str]] = {}
    for trade_dir in sorted(p for p in WORK.iterdir()
                            if p.is_dir() and p.name != "_assets"):
        taken: set[str] = set()
        for page in sorted(trade_dir.glob("*.html")):
            if page.name == "index.html":
                continue
            m = PHONE_RE.search(page.read_text())
            if not m:
                continue
            old_digits = "555" + m.group(1) + m.group(2)
            npa = assign(trade_dir.name, page.stem, taken)
            nxx = exchange_for(page.stem, m.group(1))
            new_digits = npa + nxx + m.group(2)
            mapping[old_digits] = (f"({npa}) {nxx}-{m.group(2)}", new_digits)
    return mapping


def targets() -> list[Path]:
    files = [p for p in WORK.glob("*/*.html")]
    files += sorted((REPO / "tools" / "demo_copy").glob("*.py"))
    files += [p for p in DECKS if p.exists()]
    return files


def rewrite(path: Path, mapping: dict, keep_links: bool) -> tuple[int, int]:
    src = path.read_text()
    original = src
    swapped = 0
    for old_digits, (new_display, new_digits) in mapping.items():
        old_display = f"({old_digits[:3]}) {old_digits[3:6]}-{old_digits[6:]}"
        if old_display in src:
            src = src.replace(old_display, new_display)
            swapped += 1
        # tel: forms, with and without the country code.
        for old_tel in (f"+1{old_digits}", old_digits):
            if old_tel in src:
                src = src.replace(old_tel, f"+1{new_digits}"
                                  if old_tel.startswith("+1") else new_digits)

    unlinked = 0
    if not keep_links and path.suffix == ".html":
        src, unlinked = TEL_HREF_RE.subn("", src)

    if src != original:
        path.write_text(src)
    return swapped, unlinked


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--keep-call-links", action="store_true",
                    help="leave the tel: hrefs dialling")
    args = ap.parse_args()

    mapping = build_map()
    print(f"{len(mapping)} builds carry a 555 number")
    for old, (disp, _) in list(mapping.items())[:6]:
        print(f"  ({old[:3]}) {old[3:6]}-{old[6:]}  ->  {disp}")
    if len(mapping) > 6:
        print(f"  ... and {len(mapping) - 6} more")
    if args.dry_run:
        return

    files = swaps = links = 0
    for path in targets():
        s, u = rewrite(path, mapping, args.keep_call_links)
        if s or u:
            files += 1
            swaps += s
            links += u
    print(f"\nrewrote {files} files, {swaps} number substitutions, "
          f"{links} call links disabled")

    left = [p.name for p in targets() if PHONE_RE.search(p.read_text())]
    print("remaining 555 numbers:", ", ".join(left) if left else "none")


if __name__ == "__main__":
    main()
