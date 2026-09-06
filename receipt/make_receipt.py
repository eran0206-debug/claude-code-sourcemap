#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a two-page A4 receipt PDF (RTL/Hebrew) from a JSON config.

Page 1 is the typeset receipt; page 2 shows a photo of the signed paper
original. Rendering goes through headless Chromium, so the layout is plain
HTML/CSS and every measurement below is in PostScript points.

    python3 make_receipt.py receipt.json -o receipt_0053.pdf

See receipt.example.json for the config shape and README.md for the rest.
"""

import argparse
import base64
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import tempfile

# --- palette -----------------------------------------------------------------
NAVY = "#1f3a5f"
GOLD = "#ba912d"
CREAM = "#efe7d6"      # header band
CREAM_SOFT = "#f7f2e7"  # total box, note block
OFFWHITE = "#faf7f0"    # business card, photo mat
BORDER = "#e3ddd0"
GREEN = "#2e7d32"       # "paid" stamp

CHROMIUM_CANDIDATES = (
    os.environ.get("CHROMIUM"),
    "/opt/pw-browsers/chromium",
    "chromium",
    "chromium-browser",
    "google-chrome",
    "google-chrome-stable",
)


def find_chromium():
    for cand in CHROMIUM_CANDIDATES:
        if not cand:
            continue
        path = cand if os.path.isabs(cand) else shutil.which(cand)
        if path and os.path.exists(path):
            return path
    sys.exit(
        "chromium not found. Install it, or point $CHROMIUM at the binary."
    )


def data_uri(path):
    """Inline a local file so the PDF carries no external references."""
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as fh:
        return "data:%s;base64,%s" % (mime, base64.b64encode(fh.read()).decode())


def image_aspect(path):
    """Width / height, so the photo frame on page 2 follows the real photo."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Pillow is required to size the scan frame: pip install pillow")
    with Image.open(path) as im:
        return im.size[0] / im.size[1]


def font_faces(fonts):
    """@font-face blocks for embedded fonts.

    Pass STATIC instances. A variable font makes Chromium emit Type3 glyph
    outlines instead of a TrueType subset, which bloats the PDF and renders
    poorly in some viewers. fontTools can flatten one:

        from fontTools.varLib import instancer
        instancer.instantiateVariableFont(f, {"wght": 700}, inplace=True)
    """
    css, family = [], fonts.get("family", "Arimo")
    for weight, key in ((400, "regular"), (700, "bold")):
        path = fonts.get(key)
        if not path:
            continue
        if not os.path.exists(path):
            sys.exit("font not found: %s" % path)
        css.append(
            "@font-face { font-family:'%s'; font-weight:%d; font-style:normal;\n"
            "  src:url(%s) format('truetype'); }" % (family, weight, data_uri(path))
        )
    return "\n".join(css)


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_html(cfg):
    biz = cfg["business"]
    rcp = cfg["receipt"]
    scan = cfg.get("scan") or {}
    fonts = cfg.get("fonts") or {}

    family = fonts.get("family", "Arimo")
    stack = "'%s',Arial,'DejaVu Sans',sans-serif" % family
    currency = rcp.get("currency", "₪")

    def money(value):
        # Force LTR so the currency sign lands left of the digits, the way it
        # reads on the printed receipts, instead of being flipped by bidi.
        return '<bdi dir="ltr">%s %s</bdi>' % (esc(currency), esc(value))

    # -- page 2 frame, derived from the photo's own aspect ratio --------------
    frame_html = ""
    rule_top = 517.1
    if scan.get("image"):
        img_w = 303.0
        img_h = round(img_w / image_aspect(scan["image"]), 1)
        mat_w, mat_h = img_w + 18.7, img_h + 18.8
        nav_w, nav_h = mat_w + 21.5, mat_h + 21.4
        frame_top = 40.0
        rule_top = round(frame_top + nav_h + 40.7, 1)
        frame_html = (
            '<div class="frame" style="margin-left:-{half}pt; top:{top}pt;'
            ' width:{w}pt; height:{h}pt;">\n'
            '    <div class="mat" style="width:{mw}pt; height:{mh}pt;">'
            '<img class="shot" style="width:{iw}pt; height:{ih}pt;" src="{src}" alt="">'
            "</div>\n  </div>"
        ).format(
            half=nav_w / 2, top=frame_top, w=nav_w, h=nav_h,
            mw=mat_w, mh=mat_h, iw=img_w, ih=img_h,
            src=data_uri(scan["image"]),
        )

    # -- service rows ---------------------------------------------------------
    # One row is the norm; extra rows step down by ROW_STEP.
    ROW_TOP, ROW_STEP = 457.9, 24.0
    rows = []
    for i, item in enumerate(rcp["items"]):
        top = ROW_TOP + i * ROW_STEP
        rows.append(
            '  <div class="t itname" style="top:%.1fpt; right:47.9pt;">%s</div>\n'
            '  <div class="t itsub"  style="top:%.1fpt; right:47.9pt;">%s</div>\n'
            '  <div class="t itname" style="top:%.1fpt; left:143.8pt; width:81pt;'
            ' text-align:center; font-weight:400;">%s</div>\n'
            '  <div class="t itname" style="top:%.1fpt; left:47.8pt;">%s</div>'
            % (top, esc(item["title"]), top + 10.3, esc(item.get("subtitle", "")),
               top, esc(item.get("qty", "1")), top, money(item["amount"]))
        )
    rows_html = "\n".join(rows)

    stamp_html = ""
    if rcp.get("paid", True):
        stamp_html = '<div class="stamp"><span>%s</span></div>' % esc(
            rcp.get("paid_label", "✓ שולם")
        )

    logo_html = ""
    if biz.get("logo"):
        logo_html = '<img class="logo" src="%s" alt="">' % data_uri(biz["logo"])

    # The page-2 footer often carries a different (studio) number from the
    # mobile printed on the receipt pad, so it falls back rather than assuming.
    contact = " \u00a0|\u00a0 ".join(
        p for p in (biz.get("instagram"), biz.get("email"),
                    biz.get("contact_phone") or biz.get("phone")) if p
    )
    brand = esc(biz.get("brand", ""))
    # The dots in the wordmark are gold; the letters are charcoal.
    brand_html = brand.replace(".", '<i>.</i>')

    return TEMPLATE.format(
        faces=font_faces(fonts), stack=stack,
        navy=NAVY, gold=GOLD, cream=CREAM, cream_soft=CREAM_SOFT,
        offwhite=OFFWHITE, border=BORDER, green=GREEN,
        title=esc(rcp.get("doc_title", "קבלה")),
        num_label=esc(rcp.get("number_label", "מס׳")), num=esc(rcp["number"]),
        date=esc(rcp["date"]), client=esc(rcp["client"]),
        client_id=esc(rcp.get("client_id", "")),
        logo=logo_html, rows=rows_html, stamp=stamp_html,
        total=money(rcp["total"]),
        total_label=esc(rcp.get("total_label", "סה״כ שולם")),
        biz_name=esc(biz["name"]), biz_addr=esc(biz.get("address", "")),
        biz_id=esc(biz.get("business_id", "")), biz_phone=esc(biz.get("phone", "")),
        note_title=esc(rcp.get("note_title", "")),
        note_body=esc(rcp.get("note_body", "")),
        signature=esc(rcp.get("signature", "")),
        scan_title=esc(scan.get("title", "")), frame=frame_html,
        rule_top=rule_top, brand_top=rule_top + 12.4, meta_top=rule_top + 29.7,
        brand=brand_html, contact=esc(contact),
    )


# Positions come from the house receipt layout: A4, 37.3pt side margins, a
# 301.5pt cream header band, and text placed at its PDF bbox top with
# line-height:1 (for Arial metrics the two coincide).
TEMPLATE = """<meta charset="utf-8">
<title>{title} {num}</title>
<style>
{faces}
@page {{ size:A4; margin:0; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ background:#fff; }}
body {{ font-family:{stack}; color:#3a3a3a;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
.page {{ position:relative; width:595.28pt; height:841.89pt; overflow:hidden;
  background:#fff; page-break-after:always; }}
.page:last-child {{ page-break-after:auto; }}
.t {{ position:absolute; line-height:1; white-space:nowrap; }}
.ctr {{ position:absolute; left:0; right:0; text-align:center; line-height:1; }}

.band     {{ position:absolute; left:0; right:0; top:0; height:301.5pt; background:{cream}; }}
.bandrule {{ position:absolute; left:0; right:0; top:301.5pt; height:3pt; background:{gold}; }}
.logo     {{ position:absolute; left:50%; margin-left:-112.5pt; top:21pt; width:225pt; height:225pt; }}
.doctitle {{ top:256.6pt; font-size:14.25pt; font-weight:700; color:{navy}; letter-spacing:.4pt; }}
.docnum   {{ top:274.9pt; font-size:9.75pt;  font-weight:700; color:{gold}; }}

.lbl  {{ font-size:8.25pt; font-weight:700; color:{gold}; letter-spacing:.3pt; }}
.val  {{ font-size:10.5pt; font-weight:700; color:{navy}; }}
.meta {{ font-size:9pt; color:#666; }}
.sect {{ font-size:10.5pt; font-weight:700; color:{navy}; }}
.hr   {{ position:absolute; left:37.3pt; width:520.5pt; height:.8pt; background:{border}; }}
.hr2  {{ position:absolute; left:37.3pt; width:520.5pt; height:1.5pt; background:{cream}; }}

.thead {{ position:absolute; left:37.3pt; top:424.5pt; width:520.5pt; height:24.7pt; background:{navy}; }}
.thead .c {{ position:absolute; top:7.7pt; font-size:9pt; font-weight:700; color:#fff; line-height:1; }}
.divv  {{ position:absolute; top:0; width:.6pt; height:24.7pt; background:rgba(255,255,255,.35); }}
.itname {{ font-size:9.75pt; font-weight:700; color:#3a3a3a; }}
.itsub  {{ font-size:9pt; color:#666; }}

.totbox {{ position:absolute; left:37.25pt; top:503.25pt; width:521.3pt; height:43.5pt;
  background:{cream_soft}; border:1.5pt solid {navy}; border-radius:4pt; }}
.totlbl {{ top:519pt;   right:55.8pt; font-size:11.25pt; font-weight:700; color:{navy}; }}
.totamt {{ top:515.1pt; left:55.3pt;  font-size:18.75pt; font-weight:700; color:{gold}; }}

.stamp {{ position:absolute; left:39.05pt; top:556.4pt; width:86.5pt; height:32.5pt;
  border:2.25pt solid {green}; border-radius:4pt; background:#fff;
  transform:rotate(-4.5deg); display:flex; align-items:center; justify-content:center; }}
.stamp span {{ font-size:13.5pt; font-weight:700; color:{green}; letter-spacing:2.2pt;
  padding-right:2.2pt; line-height:1; }}

.card  {{ position:absolute; left:37.25pt; top:606pt; width:521.25pt; height:46.5pt;
  background:{offwhite}; border:.75pt solid {border}; border-radius:3pt; }}
.cname {{ top:616.9pt; right:51.7pt; font-size:9.75pt; font-weight:700; color:{navy}; }}
.caddr {{ top:629.4pt; right:51.7pt; font-size:9pt; color:#555; }}
.creg  {{ top:619.7pt; left:51.5pt;  font-size:9pt; color:#555; }}
.ctel  {{ top:631.7pt; left:51.5pt;  font-size:9pt; color:#555; }}

.note  {{ position:absolute; left:37.3pt; top:670.5pt; width:521.2pt; height:123pt;
  background:{cream_soft}; border-right:1.9pt solid {gold}; }}
.nhead {{ top:686.6pt; right:56.2pt; font-size:10.88pt; font-weight:700; color:{navy}; }}
.nbody {{ position:absolute; top:707.4pt; right:56.2pt; width:483.9pt; text-align:right;
  font-size:9.75pt; line-height:18pt; color:#444; }}
.nsig  {{ top:765.2pt; right:56.2pt; font-size:9.75pt; font-weight:700; color:#444; }}

.p2title {{ top:24pt; font-size:8.62pt; font-weight:700; color:{gold}; letter-spacing:.5pt; }}
.frame   {{ position:absolute; left:50%; background:{navy}; border-radius:2pt; }}
.mat     {{ position:absolute; left:10.7pt; top:9.3pt; background:{offwhite};
  border:.75pt solid {border}; }}
.shot    {{ position:absolute; left:9.4pt; top:9.4pt; display:block; }}
.frule   {{ position:absolute; left:0; right:0; top:{rule_top}pt; height:.8pt; background:{border}; }}
.fbrand  {{ top:{brand_top}pt; font-size:12pt; font-weight:700; color:#3a3a3a; letter-spacing:.6pt; }}
.fbrand i {{ color:{gold}; font-style:normal; }}
.fmeta   {{ top:{meta_top}pt; font-size:8.62pt; color:#888; letter-spacing:.2pt; }}
</style>

<div class="page" dir="rtl">
  <div class="band"></div><div class="bandrule"></div>
  {logo}
  <div class="ctr doctitle">{title}</div>
  <div class="ctr docnum">{num_label} {num}</div>

  <div class="t lbl"  style="top:327pt;   right:37.4pt;">לכבוד</div>
  <div class="t val"  style="top:338.8pt; right:37.4pt;">{client}</div>
  <div class="t meta" style="top:354.9pt; right:37.4pt;">{client_id}</div>
  <div class="t lbl"  style="top:327pt;   left:37.3pt;">תאריך</div>
  <div class="t val"  style="top:338.8pt; left:37.3pt;">{date}</div>

  <div class="hr" style="top:380.2pt;"></div>
  <div class="t sect" style="top:400.3pt; right:37.4pt;">פרטי השירות</div>
  <div class="hr2" style="top:415.5pt;"></div>

  <div class="thead">
    <div class="divv" style="left:187.5pt;"></div>
    <div class="divv" style="left:106.5pt;"></div>
    <div class="c" style="right:10.8pt;">תיאור</div>
    <div class="c" style="left:106.5pt; width:81pt; text-align:center;">כמות</div>
    <div class="c" style="left:10.5pt;">סכום</div>
  </div>

{rows}

  <div class="totbox"></div>
  <div class="t totlbl">{total_label}</div>
  <div class="t totamt">{total}</div>
  {stamp}

  <div class="card"></div>
  <div class="t cname">{biz_name}</div>
  <div class="t caddr">{biz_addr}</div>
  <div class="t creg">ע.פ {biz_id}</div>
  <div class="t ctel">נייד {biz_phone}</div>

  <div class="note"></div>
  <div class="t nhead">{note_title}</div>
  <div class="nbody">{note_body}</div>
  <div class="t nsig">{signature}</div>
</div>

<div class="page" dir="rtl">
  <div class="ctr p2title">{scan_title}</div>
  {frame}
  <div class="frule"></div>
  <div class="ctr fbrand">{brand}</div>
  <div class="ctr fmeta" dir="ltr">{contact}</div>
</div>
"""


def render(html, out_pdf, chromium):
    """Print the page with headless Chromium."""
    tmp = tempfile.mkdtemp(prefix="receipt-")
    src = os.path.join(tmp, "receipt.html")
    with open(src, "w", encoding="utf-8") as fh:
        fh.write(html)
    cmd = [
        chromium, "--headless", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer",
        "--print-to-pdf=%s" % os.path.abspath(out_pdf),
        "--virtual-time-budget=20000",
        "file://%s" % src,
    ]
    proc = subprocess.run(cmd, capture_output=True)
    if not os.path.exists(out_pdf):
        sys.stderr.write(proc.stderr.decode("utf-8", "replace"))
        sys.exit("chromium failed to produce %s" % out_pdf)
    shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config", help="receipt JSON (see receipt.example.json)")
    ap.add_argument("-o", "--out", help="output PDF (default: receipt_<number>.pdf)")
    ap.add_argument("--html", help="also write the intermediate HTML here")
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as fh:
        cfg = json.load(fh)

    # Asset paths in the config are relative to the config file itself.
    base = os.path.dirname(os.path.abspath(args.config))
    for section, key in (("business", "logo"), ("scan", "image"),
                         ("fonts", "regular"), ("fonts", "bold")):
        val = (cfg.get(section) or {}).get(key)
        if val and not os.path.isabs(val):
            cfg[section][key] = os.path.join(base, val)

    out = args.out or "receipt_%s.pdf" % cfg["receipt"]["number"]
    html = build_html(cfg)
    if args.html:
        with open(args.html, "w", encoding="utf-8") as fh:
            fh.write(html)
    render(html, out, find_chromium())
    print("wrote %s (%.2f MB)" % (out, os.path.getsize(out) / 1048576))


if __name__ == "__main__":
    main()
