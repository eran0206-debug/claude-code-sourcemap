# הצעת מחיר — SH PROJECT (E.A. VISUALS)

הצעת מחיר מעוצבת ל-3 סרטונים מהמחנה של שירה העליון (SH PROJECT), בסגנון המותג E.A. VISUALS.

- **SH_PROJECT_quote.pdf** — קובץ ההצעה הסופי (2 עמודים, Letter).
- **quote.html** — ה-HTML המרונדר.
- **build.py** — בונה את ה-HTML מהתוכן (טקסטים, מחירים, סעיפים).
- **render.py** — ממיר את ה-HTML ל-PDF דרך Chromium (Playwright).
- **assets/logo.png** — הלוגו שחולץ מההצעה המקורית.
- **fonts/** — פונט Heebo (400/500/700) לרינדור עברית.

## תוכן ההצעה
| # | סרטון | מחיר |
|---|-------|------|
| 1 | סרטון תדמית — את מדברת | 1,300 ₪ |
| 2 | סרטון אווירה — ראיונות שחקניות | 1,300 ₪ |
| 3 | סרטון אווירה — הייליטס אימונים | 1,000 ₪ |
| | **סה"כ** | **3,600 ₪** |

עוסק פטור (ללא מע"מ).

## שחזור
```bash
pip install pymupdf playwright
python3 build.py      # -> quote.html
python3 render.py     # -> SH_PROJECT_quote.pdf
```

## פלטת המותג
- Navy `#1F3A5E` · Gold `#B9902D` · Cream header `#EFE7D5` · Card `#F6F1E7`
