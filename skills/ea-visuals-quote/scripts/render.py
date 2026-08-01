#!/usr/bin/env python3
"""Render an E.A. VISUALS quote HTML to PDF (+ a preview PNG) via headless Chromium.

Usage:
    python render.py quote.html quote.pdf [preview.png]

Fonts and logo are embedded in the HTML by build.py, so no system font
install is required. Needs Playwright's Python package and a Chromium build
(the pre-installed one under PLAYWRIGHT_BROWSERS_PATH is auto-detected).
"""
import glob
import os
import pathlib
import sys

from playwright.sync_api import sync_playwright


def find_chromium():
    roots = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")]
    for root in roots:
        for pat in ("chromium-*/chrome-linux/chrome", "chromium/chrome-linux/chrome",
                    "chromium-*/chrome-linux/headless_shell"):
            hits = sorted(glob.glob(os.path.join(root, pat)))
            if hits:
                return hits[-1]
    return None  # let Playwright fall back to its bundled default


def main():
    if len(sys.argv) < 3:
        print("usage: python render.py <in.html> <out.pdf> [preview.png]", file=sys.stderr)
        sys.exit(1)
    html, pdf = sys.argv[1], sys.argv[2]
    preview = sys.argv[3] if len(sys.argv) > 3 else None
    url = pathlib.Path(html).resolve().as_uri()
    exe = find_chromium()

    with sync_playwright() as p:
        launch = {"args": ["--no-sandbox"]}
        if exe:
            launch["executable_path"] = exe
        b = p.chromium.launch(**launch)
        pg = b.new_page()
        pg.goto(url, wait_until="networkidle")
        pg.pdf(path=pdf, width="8.5in", height="11in", print_background=True,
               margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        if preview:
            pg.screenshot(path=preview, full_page=True)
        b.close()
    print(f"wrote {pdf}" + (f" and {preview}" if preview else ""))


if __name__ == "__main__":
    main()
