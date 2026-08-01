#!/usr/bin/env python3
"""Build an E.A. VISUALS price-quote HTML page from a JSON spec.

Usage:
    python build.py quote.json quote.html

The JSON spec drives all content; the design (palette, layout, logo, fonts)
is fixed here so every quote looks like it came from the same studio.
See references/brand.md for the meaning of each field and the house voice.

Text fields (background, item title/desc, bullets) may contain raw HTML.
Wrap any Latin run inside Hebrew text in <bdi class='ltr'>...</bdi> so it
doesn't get split across lines by the RTL engine (e.g. B-roll, SH PROJECT).
"""
import base64
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")


def b64_logo():
    with open(os.path.join(ASSETS, "logo.png"), "rb") as f:
        return base64.b64encode(f.read()).decode()


def b64_font(name):
    with open(os.path.join(ASSETS, "fonts", name), "rb") as f:
        return base64.b64encode(f.read()).decode()


def item_html(it):
    return f'''
      <div class="item">
        <div class="item-head">
          <div class="item-title">{it["title"]}</div>
          <div class="item-price">{it["price"]} <span class="sh">₪</span></div>
        </div>
        <div class="item-desc">{it["desc"]}</div>
      </div>'''


def package_html(pkg):
    accent = pkg.get("accent", "navy")  # "navy" or "gold"
    badge = ('<div class="badge">מומלץ</div>' if pkg.get("recommended") else "")
    items = "".join(item_html(it) for it in pkg["items"])
    return f'''
      <div class="card avoid accent-{accent}">
        {badge}
        <div class="card-head">
          <div class="card-title">{pkg["name"]}</div>
          <div class="card-price">{pkg["total"]} <span class="sh">₪</span></div>
        </div>
        <div class="items">{items}</div>
        <div class="total">
          <div class="total-lbl">סה"כ</div>
          <div class="total-price">{pkg["total"]} <span class="sh">₪</span></div>
        </div>
      </div>'''


def section_html(sec):
    bullets = "".join(f"<li>{b}</li>" for b in sec["bullets"])
    return f'''
      <section class="terms avoid">
        <h2 class="block">{sec["heading"]}</h2>
        <ul class="bul">{bullets}</ul>
      </section>'''


def build(spec):
    logo = b64_logo()
    f400, f500, f700 = b64_font("Heebo-400.ttf"), b64_font("Heebo-500.ttf"), b64_font("Heebo-700.ttf")

    packages_block = "".join(package_html(p) for p in spec["packages"])
    packages_heading = spec.get("packages_heading", "החבילה" if len(spec["packages"]) == 1 else "החבילות")
    sections_block = "".join(section_html(s) for s in spec.get("sections", []))

    meta_rows = f'''
        <div><span class="lbl">תאריך:</span> <span class="val">{spec["date"]}</span></div>
        <div><span class="lbl">לכבוד:</span> <span class="val">{spec["to"]}</span></div>'''

    return f'''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<style>
  @font-face {{ font-family:"Heebo"; font-weight:400; src:url(data:font/ttf;base64,{f400}) format("truetype"); }}
  @font-face {{ font-family:"Heebo"; font-weight:500; src:url(data:font/ttf;base64,{f500}) format("truetype"); }}
  @font-face {{ font-family:"Heebo"; font-weight:700; src:url(data:font/ttf;base64,{f700}) format("truetype"); }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html,body {{ font-family:"Heebo", Arial, sans-serif; color:#3A3A3A; -webkit-font-smoothing:antialiased; }}
  @page {{ size: 8.5in 11in; margin:0; }}
  :root {{
    --navy:#1F3A5E; --gold:#B9902D; --cream:#EFE7D5; --card:#F6F1E7;
    --ink:#3A3A3A; --muted:#6B6B6B; --line:#E3DECF;
  }}
  .page {{ width:8.5in; min-height:11in; background:#fff; margin:0 auto; }}
  .hero {{ background:var(--cream); padding:52px 64px 34px; text-align:center; }}
  .hero img {{ height:96px; margin:14px auto 30px; display:block; }}
  .hero-title {{ color:var(--navy); font-weight:700; font-size:23px; letter-spacing:.2px; }}
  .gold-rule {{ height:6px; background:var(--gold); }}
  .body {{ padding:34px 64px 40px; }}
  .meta {{ text-align:right; line-height:2; }}
  .meta .lbl {{ color:var(--navy); font-weight:700; }}
  .meta .val {{ color:var(--ink); }}
  h2.sec {{ color:var(--navy); font-weight:700; font-size:16px; text-align:right; margin:6px 0 10px; }}
  p.lead {{ text-align:justify; line-height:1.85; color:var(--ink); font-size:13.5px; }}
  .divider {{ height:1px; background:var(--line); margin:26px 0; }}
  h2.block {{ color:var(--navy); font-weight:700; font-size:17px; text-align:right; margin:0 0 14px; }}
  .card {{ position:relative; background:var(--card); border-radius:6px; padding:24px 26px; margin-bottom:22px; }}
  .card.accent-navy {{ border-right:6px solid var(--navy); }}
  .card.accent-gold {{ border-right:6px solid var(--gold); }}
  .badge {{ position:absolute; top:-11px; right:22px; background:var(--gold); color:#fff;
            font-weight:700; font-size:11px; padding:4px 12px; border-radius:5px; }}
  .card-head {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; }}
  .card-title {{ color:var(--navy); font-weight:700; font-size:16px; }}
  .card-price {{ color:var(--navy); font-weight:700; font-size:26px; direction:rtl; }}
  .items {{ margin-top:8px; }}
  .item {{ padding:14px 0; border-top:1px dashed #CFC7B0; }}
  .item:first-child {{ border-top:none; padding-top:6px; }}
  .item-head {{ display:flex; justify-content:space-between; align-items:baseline; gap:14px; }}
  .item-title {{ color:var(--navy); font-weight:700; font-size:14px; }}
  .item-price {{ color:var(--gold); font-weight:700; font-size:14px; white-space:nowrap; direction:rtl; }}
  .item-desc {{ color:var(--muted); font-size:12.5px; line-height:1.75; margin-top:5px; text-align:justify; }}
  .sh {{ font-size:.9em; }}
  bdi.ltr {{ direction:ltr; unicode-bidi:isolate; white-space:nowrap; }}
  .total {{ display:flex; justify-content:space-between; align-items:center; border-top:2px solid var(--navy); margin-top:12px; padding-top:14px; }}
  .total-lbl {{ color:var(--navy); font-weight:700; font-size:16px; }}
  .total-price {{ color:var(--navy); font-weight:700; font-size:26px; direction:rtl; }}
  section.terms {{ margin-top:26px; padding-top:22px; border-top:1px solid var(--line); }}
  ul.bul {{ list-style:none; }}
  ul.bul li {{ position:relative; padding-right:20px; margin:9px 0; text-align:right; font-size:13px; line-height:1.7; color:var(--ink); }}
  ul.bul li::before {{ content:""; position:absolute; right:2px; top:9px; width:6px; height:6px; border-radius:50%; background:var(--gold); }}
  .footer {{ margin-top:38px; padding-top:22px; border-top:1px solid var(--line); text-align:center; }}
  .footer .brand {{ color:var(--navy); font-weight:700; font-size:16px; letter-spacing:1px; }}
  .footer .contact {{ direction:ltr; color:var(--muted); font-size:12px; margin-top:7px; }}
  .avoid {{ break-inside:avoid; }}
</style>
</head>
<body>
  <div class="page">
    <div class="hero">
      <img src="data:image/png;base64,{logo}" alt="E.A. VISUALS">
      <div class="hero-title">{spec["title"]}</div>
    </div>
    <div class="gold-rule"></div>
    <div class="body">
      <div class="meta">{meta_rows}</div>
      <h2 class="sec">רקע</h2>
      <p class="lead">{spec["background"]}</p>
      <div class="divider"></div>
      <h2 class="block">{packages_heading}</h2>
      {packages_block}
      {sections_block}
      <div class="footer">
        <div class="brand">E.A. VISUALS</div>
        <div class="contact">{spec.get("contact", "@e.a.visuals_&nbsp;&nbsp;|&nbsp;&nbsp;eran0206@gmail.com&nbsp;&nbsp;|&nbsp;&nbsp;053-933-1782")}</div>
      </div>
    </div>
  </div>
</body>
</html>'''


def main():
    if len(sys.argv) < 3:
        print("usage: python build.py <spec.json> <out.html>", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        spec = json.load(f)
    html = build(spec)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {sys.argv[2]} ({len(html)} chars)")


if __name__ == "__main__":
    main()
