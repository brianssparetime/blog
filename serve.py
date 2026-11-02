#!/usr/bin/env python3
"""Dev server with auto-rebuild on file changes."""

import html
import http.server
import os
import sys
import threading
import time
import traceback
from functools import partial

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
WATCH_DIRS = ["content", "templates", "static"]
POLL_INTERVAL = 1  # seconds

PORT = 8000

# Traceback from the last failed build, or None if the last build succeeded.
# Set by rebuild(), read by the request handler.
BUILD_ERROR = None


def get_mtimes():
    """Collect mtime for every file under the watched directories."""
    mtimes = {}
    for dirname in WATCH_DIRS:
        watch_path = os.path.join(ROOT, dirname)
        if not os.path.isdir(watch_path):
            continue
        for dirpath, _, filenames in os.walk(watch_path):
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                try:
                    mtimes[fp] = os.path.getmtime(fp)
                except OSError:
                    pass
    return mtimes


def rebuild():
    """Run build.py in-process. Returns True on success.

    A failed build leaves dist/ half-written, so record the traceback and let
    the handler serve that instead of the wreckage.
    """
    global BUILD_ERROR
    # Import fresh each time so template/content changes are picked up
    import importlib
    sys.path.insert(0, ROOT)
    try:
        import build
        importlib.reload(build)
        build.build()
    except Exception:
        BUILD_ERROR = traceback.format_exc()
        print("\nBUILD FAILED - the site was not regenerated:\n")
        print(BUILD_ERROR)
        return False
    BUILD_ERROR = None
    return True


def watch_and_rebuild():
    """Poll for file changes and rebuild when detected."""
    prev = get_mtimes()
    while True:
        time.sleep(POLL_INTERVAL)
        curr = get_mtimes()
        if curr != prev:
            print("\nChange detected, rebuilding...")
            if rebuild():
                print("Rebuild complete.")
            prev = get_mtimes()


ERROR_PAGE = """<!doctype html>
<meta charset="utf-8">
<title>Build failed</title>
<style>
  body {{ font: 15px/1.5 -apple-system, sans-serif; margin: 3rem auto; max-width: 60rem; }}
  h1 {{ color: #b00; }}
  pre {{ background: #f4f4f4; padding: 1rem; overflow-x: auto; white-space: pre-wrap; }}
</style>
<h1>Build failed</h1>
<p>dist/ is stale or incomplete. Fix the error below and save; the server
rebuilds on its own, then reload this page.</p>
<pre>{traceback}</pre>
"""


class DevHandler(http.server.SimpleHTTPRequestHandler):
    """Serves dist/, but shows the build traceback while the build is broken."""

    def do_GET(self):
        if BUILD_ERROR is not None and self.wants_page():
            self.send_build_error()
            return
        super().do_GET()

    def do_HEAD(self):
        if BUILD_ERROR is not None and self.wants_page():
            self.send_build_error(body=False)
            return
        super().do_HEAD()

    def wants_page(self):
        """True for navigation requests, so broken pages surface the error.

        Assets keep being served normally - a stale stylesheet is more useful
        than an error page in an <img> tag.
        """
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        return path.endswith("/") or os.path.splitext(path)[1] in ("", ".html")

    def send_build_error(self, body=True):
        payload = ERROR_PAGE.format(traceback=html.escape(BUILD_ERROR)).encode("utf-8")
        self.send_response(500)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if body:
            self.wfile.write(payload)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])

    # Initial build. A failure still starts the server, which then reports it.
    rebuild()

    handler = partial(DevHandler, directory=DIST)
    httpd = http.server.HTTPServer(("", PORT), handler)

    watcher = threading.Thread(target=watch_and_rebuild, daemon=True)
    watcher.start()

    print(f"Serving dist/ at http://localhost:{PORT}")
    print("Watching content/, templates/, static/ for changes...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
