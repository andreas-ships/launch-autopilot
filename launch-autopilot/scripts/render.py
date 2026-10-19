#!/usr/bin/env python3
"""Render HTML to PNG or PDF with headless Chromium (Playwright).

  render.py in.html out.png [--data data.json ...] [--size 1080x1350]
  render.py in.html out.pdf                      # print PDF at the page's @page size
  render.py --batch SRC_DIR OUT_DIR [--data ...] # every *.html; size from <meta name="size">

{{key}} placeholders are filled from the --data JSON files (later files win), so
brand.json + a per-post JSON drive one template. {{qr}} becomes an inline QR SVG of
data["qr_url"] (needs: pip install segno). Unfilled placeholders fail the render,
so no "{{headline}}" ever ships.
"""
import argparse, json, os, re, sys
from pathlib import Path


def fill(html, data):
    if "{{qr}}" in html and data.get("qr_url"):
        import segno, io
        buf = io.BytesIO()
        segno.make(data["qr_url"], error="m").save(buf, kind="svg", border=4, xmldecl=False, svgns=True, omitsize=True)
        data = {**data, "qr": buf.getvalue().decode()}
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: str(data.get(m.group(1), m.group(0))), html)
    left = set(re.findall(r"\{\{(\w+)\}\}", out))
    if left:
        sys.exit(f"unfilled placeholders: {sorted(left)}")
    return out


def size_of(html, override):
    m = re.search(r'<meta name="size" content="(\d+x\d+)"', html)
    w, h = map(int, (override or (m and m.group(1)) or "1080x1350").split("x"))
    return w, h


def settle(page):
    """Let finite CSS animations finish so stills show the end state (cap 5s)."""
    page.evaluate("Promise.race([Promise.all(document.getAnimations().map(a=>a.finished)),new Promise(r=>setTimeout(r,5000))])")


def render(page, src, out, data, size=None):
    html = fill(Path(src).read_text(), data)
    tmp = Path(src).with_suffix(".rendered.html")  # same dir so relative asset paths resolve
    tmp.write_text(html)
    try:
        w, h = size_of(html, size)
        page.set_viewport_size({"width": w, "height": h})
        page.goto(tmp.resolve().as_uri(), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        settle(page)
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        if out.endswith(".pdf"):
            page.pdf(path=out, prefer_css_page_size=True, print_background=True)
        else:
            page.screenshot(path=out, clip={"x": 0, "y": 0, "width": w, "height": h})
        # overflow check: content wider/taller than the canvas means clipped text
        sw, sh = page.evaluate("[document.documentElement.scrollWidth, document.documentElement.scrollHeight]")
        if not out.endswith(".pdf") and (sw > w or sh > h):
            print(f"WARNING {out}: content {sw}x{sh} overflows canvas {w}x{h}", file=sys.stderr)
    finally:
        tmp.unlink(missing_ok=True)
    print(out)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("src"); a.add_argument("out")
    a.add_argument("--data", action="append", default=[])
    a.add_argument("--size"); a.add_argument("--batch", action="store_true")
    o = a.parse_args()
    data = {}
    for d in o.data:
        data.update(json.loads(Path(d).read_text()))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(device_scale_factor=1)
        if o.batch:
            for f in sorted(Path(o.src).glob("*.html")):
                if not f.name.endswith(".rendered.html"):
                    render(page, f, os.path.join(o.out, f.stem + ".png"), data, o.size)
        else:
            render(page, o.src, o.out, data, o.size)
        b.close()


if __name__ == "__main__":
    main()
