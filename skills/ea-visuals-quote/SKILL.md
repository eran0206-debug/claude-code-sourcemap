---
name: ea-visuals-quote
description: >-
  Create a branded Hebrew price quote (הצעת מחיר) as a polished PDF in the
  E.A. VISUALS studio style — cream header with the E.A. VISUALS logo, navy +
  gold palette, package cards, and Hebrew RTL layout. Use this whenever Eran
  (E.A. VISUALS) wants to send a client a quote or proposal for video work —
  image/תדמית videos, atmosphere/אווירה videos, highlights, interviews, social
  graphics, photo galleries, camp/מחנה content, and similar. Trigger on phrases
  like "הצעת מחיר", "price quote", "proposal for a client", "quote for X
  videos", or when continuing/editing an E.A. VISUALS quote, even if the word
  "quote" isn't used. Prefer this over a generic document so the output stays
  on-brand.
---

# E.A. VISUALS — Price Quote

Turn a list of deliverables and prices into an on-brand Hebrew PDF quote that
looks like every other E.A. VISUALS quote: cream hero with the logo, gold rule,
navy/gold palette, package cards, and clean RTL typography.

The design is fixed in `scripts/build.py`; you supply the *content* as a JSON
spec. This keeps every quote visually identical while letting the words change.

## Workflow

1. **Gather the content.** You need: the client name, the videos/deliverables
   with prices, and whether prices include VAT (Eran is normally עוסק פטור →
   no VAT). If the user gave these in chat, use them — don't re-ask what you
   already know. Confirm only the genuinely missing / ambiguous bits (validity
   date, payment split, filming terms) rather than interrogating. Sensible
   defaults live in `references/brand.md` — apply them and mention what you
   assumed.

2. **Write the words in the house voice.** Read `references/brand.md` for the
   palette, full page anatomy, and — importantly — the writing voice. Item
   descriptions are short, punchy, and concrete: sell the feeling and the
   outcome, close on a beat. Match the register of the examples there; don't
   drift into corporate copy.

3. **Author the spec.** Copy `assets/example-quote.json` to your working
   directory and edit it. Fields:
   - `title` — hero title, e.g. `הצעת מחיר — SH PROJECT`.
   - `date`, `to` — quote date and client name.
   - `background` — one warm paragraph framing the offer.
   - `packages` — one or more. Each has `name`, `total`, `accent`
     (`"navy"` default, `"gold"` for the recommended one), optional
     `recommended: true` (adds a gold "מומלץ" badge), and `items` (each with
     `title`, `desc`, `price`). Use several packages to give the client
     options (as in the original two-option base/full quote); use one for a
     single fixed offer.
   - `sections` — the term blocks (`כלול בהצעה`, `תנאי תשלום`, `תנאי צילום`,
     `צעדים הבאים`), each a `heading` + `bullets`.
   - `contact` — leave the default unless it changed.

   Wrap Latin runs inside Hebrew (`B-roll`, `SH PROJECT`) in
   `<bdi class='ltr'>…</bdi>` so they don't break across lines. Text fields
   accept raw HTML, so this just works.

4. **Build and render:**
   ```bash
   python scripts/build.py quote.json quote.html
   python scripts/render.py quote.html quote.pdf preview.png
   ```
   `render.py` needs Playwright's Python package and Chromium. If Playwright
   isn't installed: `pip install playwright` (Chromium is pre-installed in
   this environment under `/opt/pw-browsers` and is auto-detected — do **not**
   run `playwright install`).

5. **Always eyeball the preview before delivering.** Open `preview.png` (and
   the rendered PDF pages) and check: logo crisp, nothing overflowing, no
   Latin word split mid-line, prices and totals correct, page breaks land
   between cards/sections (never mid-card). Fix the spec and re-run if needed.

6. **Deliver the PDF** to the user (via the file-delivery tool available in the
   environment) with a one-line caption of what it contains and the total.
   Then offer quick follow-ups: adjust wording, add a package/option, or a
   Word version.

## Editing an existing quote

When the user asks to tweak a quote already made (change a price, filming
hours, add a line), edit the JSON spec and re-run build + render. Don't rebuild
from scratch — the spec is the source of truth. Keep the same filename so the
delivered PDF replaces the previous one cleanly.

## Notes

- Output is US-Letter (matches the original). It naturally flows to 2 pages for
  a typical quote — that's expected, not a problem.
- The logo and Heebo fonts are embedded into the HTML by `build.py`, so the PDF
  is fully self-contained and needs no system font install.
- If a value is genuinely unknown (e.g. Eran didn't say the validity date),
  ask — don't fabricate a business term.
