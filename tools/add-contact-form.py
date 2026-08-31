#!/usr/bin/env python3
"""Give every build's contact section a form that does something.

The closing section of all 114 CSS-only builds ends in a primary button
("Book a discovery call", "Book now") whose href is #contact — the section it
already sits in — beside a phone number that is deliberately not a tel: link
(see renumber-phones.py: the numbers are real lines). Nothing on the page
took a name. This drops a short enquiry form into that section: name, a way
to reach them, an optional note, and a submit that confirms in place. No
backend; these are reference builds, and the point is that the visitor can
see the thing work.

The form borrows rather than declares: the section's own colour for text and
rules via currentColor, the build's own .btn.btn-primary for the button, so
the dark builds get a dark form with no special case. It also gives the
href-less "Call now" buttons a destination (#contact), leaving the phone-number
buttons as they are.

    python3 tools/add-contact-form.py roofing
    python3 tools/add-contact-form.py --all
    python3 tools/add-contact-form.py roofing --replace

Idempotent; everything sits between gsw:contact-form markers.
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "work"
MARKER = "<!-- gsw:contact-form -->"
END_MARKER = "<!-- /gsw:contact-form -->"
PHONE_RE = re.compile(r"^\(?\d{3}\)?[ .-]?\d{3}[ .-]?\d{4}$")

FORM = """<!-- gsw:contact-form -->
    <form class="gsw-cf{centred}" novalidate>
      <p class="gsw-cf-lead">Or leave your details and we'll call you back.</p>
      <div class="gsw-cf-grid">
        <label><span>Name</span><input type="text" name="name" autocomplete="name" required></label>
        <label><span>Phone or email</span><input type="text" name="contact" autocomplete="tel" required></label>
        <label class="gsw-cf-wide"><span>What can we help with? <em>(optional)</em></span><textarea name="message" rows="3"></textarea></label>
      </div>
      <div class="gsw-cf-row">
        <button type="submit" class="btn btn-primary">Request a call back</button>
        <span class="gsw-cf-err" role="alert" hidden>Add your name and a way to reach you.</span>
      </div>
      <p class="gsw-cf-done" role="status" hidden>Thanks. Someone will call you back within one business day.</p>
    </form>
    <!-- /gsw:contact-form -->"""

CSS = """
<style>
  /* gsw:contact-form — the closing section takes a name. Borrows the section's
     colour through currentColor and the build's own .btn for the button. */
  .gsw-cf { max-width: 640px; margin: 28px 0 0; text-align: left; }
  .gsw-cf--centred { margin-left: auto; margin-right: auto; }
  .gsw-cf-lead { margin: 0 0 12px; font-size: 15px; opacity: .85; }
  .gsw-cf-grid { display: grid; gap: 10px; }
  .gsw-cf label { display: flex; flex-direction: column; gap: 5px; font-size: 11px;
                  font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
  .gsw-cf label em { font-style: normal; font-weight: 400; text-transform: none; letter-spacing: 0; opacity: .7; }
  .gsw-cf input, .gsw-cf textarea { font: inherit; font-size: 16px; color: inherit; background: transparent;
                                    border: 1.5px solid currentColor; border-radius: 0; padding: 10px 12px; width: 100%;
                                    box-sizing: border-box; letter-spacing: 0; text-transform: none; font-weight: 400; }
  .gsw-cf input:focus, .gsw-cf textarea:focus { outline: 2px solid currentColor; outline-offset: 2px; }
  .gsw-cf textarea { resize: vertical; min-height: 84px; }
  .gsw-cf-row { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; margin-top: 14px; }
  .gsw-cf button.btn { font: inherit; cursor: pointer; appearance: none; }
  .gsw-cf-err { font-size: 14px; font-weight: 600; }
  .gsw-cf-done { margin: 0; font-size: 17px; font-weight: 600; }
  .gsw-cf[data-sent] .gsw-cf-lead, .gsw-cf[data-sent] .gsw-cf-grid, .gsw-cf[data-sent] .gsw-cf-row { display: none; }
  @media (min-width: 640px) {
    .gsw-cf-grid { grid-template-columns: 1fr 1fr; }
    .gsw-cf-wide { grid-column: 1 / -1; }
  }
</style>"""

SCRIPT = """
<!-- gsw:contact-form -->
<script>
/* The enquiry form confirms in place. Nothing is sent: a reference build. */
(function () {
  var form = document.querySelector('.gsw-cf');
  if (!form) return;
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var name = form.name.value.trim(), contact = form.contact.value.trim();
    var err = form.querySelector('.gsw-cf-err');
    if (!name || !contact) { err.hidden = false; (name ? form.contact : form.name).focus(); return; }
    err.hidden = true;
    form.setAttribute('data-sent', '');
    form.querySelector('.gsw-cf-done').hidden = false;
  });
})();
</script>
<!-- /gsw:contact-form -->
"""


def patch(page: Path, replace: bool) -> str:
    src = page.read_text()
    if MARKER in src:
        if not replace:
            return "already has a form"
        src = re.sub(r"\n?\s*" + re.escape(MARKER) + r".*?" + re.escape(END_MARKER) + r"\n?", "\n", src, flags=re.S)
        src = re.sub(r"\n<style>\n  /\* gsw:contact-form.*?</style>", "", src, flags=re.S)

    m = re.search(r'<section class="([^"]*)"[^>]*id="contact"[^>]*>(.*?)</section>', src, re.S)
    if not m:
        # The photographic builds close on a "closing" section with no id;
        # it gains one so the buttons have somewhere to point.
        m = re.search(r'<section class="([^"]*\bclosing\b[^"]*)"([^>]*)>(.*?)</section>', src, re.S)
        if not m:
            # Last resort: the final section on the page, whatever it is called.
            all_secs = list(re.finditer(r'<section\b([^>]*)>(.*?)</section>', src, re.S))
            if not all_secs:
                return "no #contact or closing section"
            last = all_secs[-1]
            src = (src[:last.start()] + "<section class=\"gsw-cf-last\" id=\"contact\"" + last.group(1)
                   + ">" + src[last.start(2):])
        else:
            head = m.group(0)[:m.start(3) - m.start()]
            src = src[:m.start()] + head.replace(">", ' id="contact">', 1) + src[m.start(3):]
        m = re.search(r'<section class="([^"]*)"[^>]*id="contact"[^>]*>(.*?)</section>', src, re.S)
    body = m.group(2)
    # After the buttons; failing that, before the closing note; failing that, at the end.
    anchor = None
    cm = re.search(r'<div class="ctas">.*?</div>\s*', body, re.S)
    if cm:
        anchor = cm.end()
    else:
        nm = re.search(r'<p class="note">', body)
        anchor = nm.start() if nm else body.rfind("</div>")
    cls = m.group(1).split()[0]
    centred = bool(re.search(r"\." + re.escape(cls) + r"\{[^}]*text-align:\s*center", src))
    form = FORM.format(centred=" gsw-cf--centred" if centred else "")
    new_body = body[:anchor] + form + "\n    " + body[anchor:]
    src = src[:m.start(2)] + new_body + src[m.end(2):]

    # Dead "Call now" buttons: an anchor with the button class and no href.
    fixed = 0
    def point(mm: re.Match) -> str:
        nonlocal fixed
        text = mm.group(2).strip()
        if 'href=' in mm.group(1) or PHONE_RE.match(text):
            return mm.group(0)
        fixed += 1
        return f'<a{mm.group(1)} href="#contact">{mm.group(2)}</a>'
    src = re.sub(r'<a(\s[^>]*class="[^"]*\bbtn\b[^"]*"[^>]*)>([^<]{0,80})</a>', point, src)

    css = CSS
    if not re.search(r"\.btn-primary\s*\{", src):
        # No button class to borrow: a plain outlined button in the section's own colour.
        css = css.replace("</style>", "  .gsw-cf button.btn { border: 1.5px solid currentColor; background: transparent;"
                          " color: inherit; padding: 12px 20px; font-weight: 700; }\n</style>")
    src = src.replace("</head>", css + "\n</head>", 1)
    src = src.replace("</body>", SCRIPT + "</body>", 1)
    page.write_text(src)
    return f"form added{f', {fixed} dead button(s) pointed at #contact' if fixed else ''}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--replace", action="store_true")
    args = ap.parse_args()
    trades = sorted(p.name for p in WORK.iterdir() if p.is_dir() and not p.name.startswith("_")) \
        if args.all else args.trades
    if not trades:
        sys.exit("name a trade or pass --all")
    for trade in trades:
        for page in sorted((WORK / trade).glob("*.html")):
            if page.name == "index.html":
                continue
            print(f"  {trade}/{page.stem:<34} {patch(page, args.replace)}")


if __name__ == "__main__":
    main()
