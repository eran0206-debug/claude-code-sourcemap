# E.A. VISUALS — Brand & Layout Reference

Studio that makes sports content ("NOT YOUR REGULAR SPORTS CONTENT"). Owner:
Eran. Quotes are in Hebrew (RTL), warm and confident, never corporate-stiff.

## Palette (do not change — these are sampled from the real brand PDF)

| Role | Hex | Used for |
|------|-----|----------|
| Navy | `#1F3A5E` | Titles, headings, labels, totals, base-package accent bar |
| Gold | `#B9902D` | Gold rule under header, line-item prices, bullet dots, "מומלץ" badge, recommended-package accent bar |
| Cream (header) | `#EFE7D5` | Top hero band |
| Card cream | `#F6F1E7` | Package card background |
| Ink | `#3A3A3A` | Body text |
| Muted | `#6B6B6B` | Item descriptions, footer contact |
| Line | `#E3DECF` | Section divider rules |

Font: **Heebo** (400/500/700), embedded from `assets/fonts/`. It's a clean,
Arial-like Hebrew face — matches the original quote, which used Arial.

## Page anatomy (top to bottom)

1. **Hero band** (cream): centered logo (`assets/logo.png`) + navy quote title.
2. **Gold rule**: 6px `--gold` bar directly under the hero.
3. **Meta**: right-aligned `תאריך:` and `לכבוד:` lines (navy bold labels).
4. **רקע**: a short navy heading + one justified paragraph framing the offer.
5. **Divider**, then the packages heading (`החבילה` for one, `החבילות` for many).
6. **Package card(s)**: cream card with a colored accent bar on the *right*
   (leading edge in RTL). Header row = package name (right) + big navy total
   (left). Then line items separated by dashed rules: each item is a bold navy
   title (right) with a gold price (left), and a muted description underneath.
   A `סה"כ` total row closes the card. A package can carry a gold **"מומלץ"**
   badge and a gold accent bar to mark it as the recommended option.
7. **Term sections**: `כלול בהצעה`, `תנאי תשלום`, `תנאי צילום`, `צעדים הבאים`
   — each a navy heading over a gold-bulleted list, separated by thin rules.
8. **Footer**: centered `E.A. VISUALS` + LTR contact line
   `@e.a.visuals_  |  eran0206@gmail.com  |  053-933-1782`.

## House voice (how items are written)

Short, punchy, concrete. Sell the *feeling* and the *outcome*, not the process.
Fragments are good. Look at how the real items read:

- "אקשן מהיר ומדויק — 2–3 שניות לפריים, קצב, אנרגיה." — rhythm over full sentences.
- "מוכר, מרגש, משכנע." — a three-beat closer lands the value.
- "סרטון שמכניס אותך לתוך המחנה בשניות." — one vivid promise.

Guidelines that keep the voice consistent:
- Open with what the viewer *sees/feels*, not "we will film…".
- Name the concrete ingredients (B-roll, ראיונות, מוזיקה, קצב) — specificity sells.
- Close each item with a short punch (a 2–3 word beat or a single promise).
- Address the client directly and warmly ("את מדברת…", "מוזמנת לעדכן אותי").
- Keep descriptions to ~1–2 lines. If it needs a paragraph, it's a section, not an item.

## Standard terms (defaults — always confirm with Eran, don't invent silently)

- **Payment**: 50% on approval (state the shekel amount), 50% on final delivery.
- **Validity**: ~14 days from the quote date (spell out the end date).
- **Filming day**: up to 3 active hours; extra hours billed at 150 ₪/hour.
- **Included**: filming, full edit + color, music, one revision round per video,
  vertical + wide formats.
- **VAT**: Eran is עוסק פטור — prices carry **no VAT**. If that ever changes,
  ask before adding it.

## Bidi / typography gotchas

- Wrap any Latin run embedded in Hebrew in `<bdi class='ltr'>…</bdi>`
  (e.g. `B-roll`, `SH PROJECT`) so it isn't split across lines.
- Prices render as `1,300 ₪` with the ₪ on the left — leave the markup as
  `{price} <span class="sh">₪</span>`; the CSS handles direction.
- The footer contact line is LTR; keep the `&nbsp;&nbsp;|&nbsp;&nbsp;` separators.
