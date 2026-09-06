# Receipt builder

Generates the two-page A4 receipt PDF used for E.A. VISUALS client receipts:

- **Page 1** — the typeset receipt (RTL/Hebrew): letterhead band and logo, receipt
  number, client, service table, total, a "paid" stamp, business details and a
  thank-you note.
- **Page 2** — a photo of the signed paper original, matted in a navy frame, over
  a brand footer.

Layout is plain HTML/CSS printed by headless Chromium, so every measurement in
`make_receipt.py` is in PostScript points against a 595.28 × 841.89pt page.

## Requirements

- Python 3.8+
- `pip install pillow` (page-2 frame sizing) and `numpy` (only for `clean_scan.py`)
- Chromium or Chrome. Auto-detected; override with `CHROMIUM=/path/to/chrome`.

## Usage

```sh
# 1. tidy up the photo of the signed original
python3 clean_scan.py photo.jpg -o assets/scan.jpg

# 2. copy the example, fill in your details, then build
cp receipt.example.json receipt.json
python3 make_receipt.py receipt.json -o receipt_0053.pdf
```

`--html out.html` also writes the intermediate page, which is quicker to iterate
on in a browser than re-printing the PDF each time.

## Config

`receipt.example.json` has the full shape. Asset paths are resolved relative to
the config file. Notable fields:

| Field | Notes |
| --- | --- |
| `business.phone` | mobile printed on the receipt card (page 1) |
| `business.contact_phone` | number in the page-2 footer; falls back to `phone` |
| `business.brand` | wordmark in the footer — the dots render gold |
| `fonts.regular` / `fonts.bold` | **static** TTFs, embedded in the PDF |
| `receipt.items[]` | one row is normal; extra rows step down 24pt |
| `receipt.paid` | set false to drop the stamp |
| `scan.image` | frame follows this photo's aspect ratio automatically |

Amounts are written as bare numbers (`"1,000"`); `receipt.currency` is prepended
inside an LTR isolate so the ₪ sits left of the digits instead of being flipped
by bidi.

### Fonts

Pass **static** font instances, not a variable font — Chromium falls back to
Type3 glyph outlines for variable fonts, which bloats the PDF and renders badly
in some viewers. Arimo is a good match here: it is metric-compatible with Arial
and covers Hebrew, so it stands in for the macOS-only Arial Hebrew the original
receipts were set in. Flatten a variable build once with fontTools:

```python
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
for wght, out in ((400, "Arimo-Regular.ttf"), (700, "Arimo-Bold.ttf")):
    f = TTFont("Arimo[wght].ttf")
    instancer.instantiateVariableFont(f, {"wght": wght}, inplace=True,
                                      updateFontNames=True)
    f.save(out)
```

Verify with `pymupdf`: `{f[3] for f in doc[0].get_fonts(full=True)}` should list
`Arimo-Regular` / `Arimo-Bold`, not `Type3`.

## Cleaning the scan

`clean_scan.py` deskews the photo, paints over the neighbouring pages along the
right edge with mirrored paper texture, crops, and lifts the exposure.

The tilt is measured from the printed rules and is reliable. The sheet edge is
not always: when the receipt is still bound in its book, the strongest step in
the right margin is the OUTER edge of the pages behind it, and the sheet's own
edge (paper on paper) is far weaker. Check it first —

```sh
python3 clean_scan.py photo.jpg -o assets/scan.jpg --inspect
```

— which prints the measurements and writes `assets/scan.jpg.inspect.jpg` with
the detected edge drawn in red. If the line sits too far out, read the real edge
off the image and pass it as `x` at `y=0` plus a slope in px per px:

```sh
python3 clean_scan.py photo.jpg -o assets/scan.jpg \
    --edge 4971 0.044 --crop 70 130 5140 6760
```

A sheet photographed loose on a desk usually needs no override.

## Privacy

`.gitignore` keeps `assets/`, `receipt.json` and built PDFs out of the repo:
they carry client tax IDs, personal contact details and a scanned signature.
Only the generator, the placeholder example and this README are tracked.
