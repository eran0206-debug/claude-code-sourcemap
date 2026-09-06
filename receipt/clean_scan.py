#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepare a phone photo of a signed paper receipt for page 2 of the PDF.

A photo of a receipt still in its book comes out tilted, with the neighbouring
pages (and their index tabs) showing along one edge. This straightens the page,
paints over that edge with cloned paper texture, crops, and lifts the exposure.

    python3 clean_scan.py photo.jpg -o assets/scan.jpg

--angle and --edge are measured automatically; pass them explicitly to override.
Run with --inspect first to see what was measured before committing to a crop.
"""

import argparse
import sys

try:
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    sys.exit("needs numpy and Pillow: pip install numpy pillow")

import math


def measure_tilt(gray, y_windows=((0.055, 0.095), (0.31, 0.35))):
    """Angle of the printed horizontal rules, in degrees.

    Printed rules run the width of the page, so the darkest pixel in a narrow
    vertical window tracks one of them. Fitting a line across many columns and
    dropping the worst 20% of residuals shakes off handwriting that dips into
    the window.
    """
    h, w = gray.shape
    angles = []
    for y0, y1 in y_windows:
        pts = []
        for x in range(int(w * 0.18), int(w * 0.85), 60):
            col = gray[int(h * y0):int(h * y1), x]
            j = int(np.argmin(col))
            if col[j] < 140:
                pts.append((x, int(h * y0) + j))
        if len(pts) < 10:
            continue
        xs = np.array([p[0] for p in pts], float)
        ys = np.array([p[1] for p in pts], float)
        m, b = np.polyfit(xs, ys, 1)
        resid = np.abs(ys - (m * xs + b))
        keep = resid < np.percentile(resid, 80)
        m, _ = np.polyfit(xs[keep], ys[keep], 1)
        angles.append(math.degrees(math.atan(m)))
    if not angles:
        return 0.0
    return sum(angles) / len(angles)


def measure_edge(gray, x_from=0.90):
    """The right-hand boundary of the sheet as a line: (x at y=0, slope).

    The boundary shows up as the strongest horizontal brightness step out in
    the right margin. Sampling it down the whole page and fitting a line (then
    refitting without the worst quarter of the residuals, which is where
    printed rules and handwriting intrude) tracks a sheet that is not perfectly
    parallel to whatever it is lying on.

    Caveat: when the receipt is still bound in its book, the strongest step is
    the OUTER edge of the pages behind it, not the receipt's own edge. Check
    --inspect, and pass --edge X0 SLOPE if the drawn line sits too far out.
    """
    h, w = gray.shape
    x0 = int(w * x_from)
    pts = []
    for y in range(int(h * 0.03), h - 40, 40):
        seg = gray[y, x0:]
        if seg.size < 8:
            continue
        d = np.diff(seg)
        k = int(np.argmax(np.abs(d)))
        if abs(d[k]) > 12:
            pts.append((y, x0 + k))
    if len(pts) < 6:
        return float(w), 0.0
    ys = np.array([p[0] for p in pts], float)
    xs = np.array([p[1] for p in pts], float)
    for _ in range(2):
        slope, intercept = np.polyfit(ys, xs, 1)
        resid = np.abs(xs - (slope * ys + intercept))
        keep = resid < max(np.percentile(resid, 75), 1.0)
        if keep.sum() < 6:
            break
        ys, xs = ys[keep], xs[keep]
    slope, intercept = np.polyfit(ys, xs, 1)
    return intercept, slope


def write_inspect(img, angle, edge_x0, edge_slope, path, scale=8):
    """Downscaled photo with the detected sheet edge drawn on, for eyeballing."""
    from PIL import ImageDraw
    small = img.resize((img.size[0] // scale, img.size[1] // scale))
    draw = ImageDraw.Draw(small)
    h = small.size[1]
    draw.line([((edge_x0) / scale, 0),
               ((edge_x0 + edge_slope * img.size[1]) / scale, h)],
              fill=(255, 0, 0), width=2)
    small.save(path, quality=85)
    print("wrote %s (tilt %+.2f deg, edge drawn in red)" % (path, angle))


def clone_over_edge(img, edge_x0, edge_slope, right, safe=12, src_w=140):
    """Replace everything past the sheet edge with mirrored paper texture.

    Mirroring keeps the grain and the lighting gradient continuous, so the
    repair does not read as a flat patch the way a solid fill would.
    """
    a = np.asarray(img).astype(np.float32).copy()
    h = a.shape[0]
    for y in range(h):
        ex = int(edge_x0 + edge_slope * y) - safe
        if ex >= right or ex - src_w < 0:
            continue
        src = a[y, ex - src_w:ex][::-1]
        need = right - ex
        reps = int(np.ceil(need / src_w))
        tiles = [src if i % 2 == 0 else src[::-1] for i in range(reps)]
        a[y, ex:right] = np.concatenate(tiles)[:need]

    patched = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    # Feather the seam so the join disappears.
    mask = np.zeros(a.shape[:2], dtype=np.uint8)
    for y in range(h):
        ex = int(edge_x0 + edge_slope * y) - safe
        if ex >= right or ex - 30 < 0:
            continue
        mask[y, ex - 25:min(ex + 25, right)] = 255
    soft = Image.fromarray(mask).filter(ImageFilter.GaussianBlur(6))
    return Image.composite(patched.filter(ImageFilter.GaussianBlur(2.0)),
                           patched, soft)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("photo")
    ap.add_argument("-o", "--out", default="scan.jpg")
    ap.add_argument("--angle", type=float,
                    help="deskew angle in degrees (default: measured)")
    ap.add_argument("--edge", type=float, nargs=2, metavar=("X0", "SLOPE"),
                    help="sheet's right edge as a line: x at y=0, and px of x "
                         "per px of y (default: measured)")
    ap.add_argument("--crop", type=int, nargs=4, metavar=("L", "T", "R", "B"),
                    help="crop box after deskew (default: derived)")
    ap.add_argument("--brightness", type=float, default=1.10)
    ap.add_argument("--contrast", type=float, default=1.12)
    ap.add_argument("--quality", type=int, default=88)
    ap.add_argument("--inspect", action="store_true",
                    help="print measurements and exit without writing")
    args = ap.parse_args()

    img = Image.open(args.photo).convert("RGB")
    gray = np.asarray(img.convert("L"), dtype=np.float32)
    angle = args.angle if args.angle is not None else measure_tilt(gray)
    print("tilt: %+.2f deg" % angle)

    # measure_tilt returns the rules' own slope angle, and PIL rotates
    # counter-clockwise for positive values, so rotating BY that angle cancels
    # the tilt. Fill matches bright paper so the corners the expand adds do not
    # show as dark wedges if the crop overshoots.
    img = img.rotate(angle, resample=Image.BICUBIC, expand=True,
                     fillcolor=(238, 236, 233))
    gray = np.asarray(img.convert("L"), dtype=np.float32)
    h, w = gray.shape

    edge_x0, edge_slope = measure_edge(gray)
    if args.edge is not None:
        edge_x0, edge_slope = args.edge
    print("sheet edge: x=%.0f at y=0, slope %+.4f px/px" % (edge_x0, edge_slope))

    if args.crop:
        left, top, right, bottom = args.crop
    else:
        # Default crop: hug the paper, leaving the cloned strip to cover the
        # right margin. Tune with --crop once you have seen the result.
        left, top = int(w * 0.013), int(h * 0.019)
        right, bottom = min(int(edge_x0) + 60, w), int(h * 0.991)
    print("crop: %d %d %d %d  (%dx%d)" % (left, top, right, bottom,
                                          right - left, bottom - top))
    if args.inspect:
        write_inspect(img, angle, edge_x0, edge_slope, args.out + ".inspect.jpg")
        return

    img = clone_over_edge(img, edge_x0, edge_slope, right)
    out = img.crop((left, top, right, bottom))
    out = ImageEnhance.Brightness(out).enhance(args.brightness)
    out = ImageEnhance.Contrast(out).enhance(args.contrast)
    out.save(args.out, quality=args.quality, optimize=True)
    print("wrote %s  %dx%d  aspect %.3f"
          % (args.out, out.size[0], out.size[1], out.size[0] / out.size[1]))


if __name__ == "__main__":
    main()
