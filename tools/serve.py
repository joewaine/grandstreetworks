#!/usr/bin/env python3
"""Static server for working on this site, with caching turned off.

`python -m http.server` lets the browser cache, which is invisible right up
until you edit a page that is displayed inside an iframe: the frame keeps
showing the old file while the page around it updates, and it looks like a bug
in the site rather than in the browser. This sends no-store on everything.

    python3 tools/serve.py [port]        # default 8777
"""

import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class NoCache(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, *args):
        pass  # quiet; the point is to watch the browser, not the terminal


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
    handler = partial(NoCache, directory=str(ROOT))
    print(f"serving {ROOT} on http://localhost:{port}  (no-store)")
    ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()
