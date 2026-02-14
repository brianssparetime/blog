#!/usr/bin/env python3
"""Dev server with auto-rebuild on file changes."""

import http.server
import os
import sys
import threading
import time
from functools import partial

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
WATCH_DIRS = ["content", "templates", "static"]
POLL_INTERVAL = 1  # seconds

PORT = 8000


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
    """Run build.py in-process."""
    # Import fresh each time so template/content changes are picked up
    import importlib
    sys.path.insert(0, ROOT)
    import build
    importlib.reload(build)
    build.build()


def watch_and_rebuild():
    """Poll for file changes and rebuild when detected."""
    prev = get_mtimes()
    while True:
        time.sleep(POLL_INTERVAL)
        curr = get_mtimes()
        if curr != prev:
            print("\nChange detected, rebuilding...")
            try:
                rebuild()
                print("Rebuild complete.")
            except Exception as e:
                print(f"Rebuild failed: {e}")
            prev = get_mtimes()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])

    # Initial build
    rebuild()

    handler = partial(http.server.SimpleHTTPRequestHandler, directory=DIST)
    httpd = http.server.HTTPServer(("", PORT), handler)

    watcher = threading.Thread(target=watch_and_rebuild, daemon=True)
    watcher.start()

    print(f"Serving dist/ at http://localhost:{PORT}")
    print("Watching content/, templates/, static/ for changes...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
