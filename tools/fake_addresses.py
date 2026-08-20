"""A stable invented address for each reference business.

Deterministic from the firm name, so a rebuild never reshuffles them — these
end up in a footer next to a phone number and it should read like the same
business every time you look.

Towns are invented rather than real. A fictional practice at a real street
address in a real town is the one combination that could plausibly land on
somebody's actual doorstep.
"""

import hashlib
import re

STREETS = [
    "Ridgeway Avenue", "Marigold Street", "Corbin Road", "Halsey Street",
    "Wexford Lane", "Ashmount Road", "Delancey Avenue", "Kestrel Way",
    "Bellamy Street", "Orchard Row", "Sandover Road", "Thistle Lane",
    "Fenwick Avenue", "Larkspur Street", "Cobblewood Road", "Amberside Drive",
    "Trellis Court", "Windmere Avenue", "Halloway Street", "Pardon Road",
]
TOWNS = [
    ("Riverbend", "NY"), ("Eastport Hills", "NJ"), ("Fairhill", "PA"),
    ("Westmoor", "CT"), ("Millbrook Park", "NY"), ("Stonebridge", "MA"),
    ("Cedar Reach", "NY"), ("Ashford Green", "NJ"), ("Lakeview Bend", "NY"),
    ("Northfields", "CT"),
]
UNITS = ["", "", "", " Suite 200", " Suite 4B", " Unit 12", " Floor 2"]


def address_for(firm):
    """One invented street address, stable for this firm's name."""
    h = hashlib.md5(firm.encode("utf-8")).digest()
    number = 100 + (int.from_bytes(h[0:2], "big") % 8900)
    street = STREETS[h[2] % len(STREETS)]
    unit = UNITS[h[3] % len(UNITS)]
    town, state = TOWNS[h[4] % len(TOWNS)]
    # kept in the north-east band so it reads right beside the state
    zipcode = 10000 + (int.from_bytes(h[5:7], "big") % 9999)
    return f"{number} {street}{unit}, {town}, {state} {zipcode}"


DISCLAIMER_RE = re.compile(
    r"(<([a-z]+)[^>]*>)([^<>]*\bis a fictional\b[^<>]*)(</\2>)")


def swap_disclaimer(page, firm):
    """Replace the 'X is a fictional company' line with a street address.

    Every design puts that sentence in the same place — last line of the
    footer, under the firm and its phone number — which is exactly where a real
    business puts where it is. So the slot stays and the content changes.
    """
    replaced = [False]

    def sub(m):
        replaced[0] = True
        return m.group(1) + address_for(firm) + m.group(4)

    page = DISCLAIMER_RE.sub(sub, page, count=1)
    return page, replaced[0]
