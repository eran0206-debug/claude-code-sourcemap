import base64
logo = open('logo_b64.txt').read().strip()

items_pkg = [
    ("סרטון תדמית — את מדברת",
     "את מדברת על האימונים ועל כל המעטפת שמאחוריהם — החזון, הגישה, מה שהופך את SH PROJECT למה שהוא. תוך כדי, <bdi class='ltr'>B-roll</bdi> חי מהמגרש שמלווה בדיוק את מה שאת מספרת. הקריטיב המדויק ייבנה יחד בשיחה לאחר אישור.",
     "1,300"),
    ("סרטון אווירה — ראיונות שחקניות",
     "שחקניות מהמחנה מספרות במילים שלהן על השיפור, על החוויה, ועל כמה שהאימונים תרמו למשחק שלהן. ראיונות אמיתיים על רקע אווירה ואקשן מהאימונים. מוכר, מרגש, משכנע.",
     "1,300"),
    ("סרטון אווירה — הייליטס אימונים",
     "הייליטס נטו מהאימונים — התרגילים, האנרגיה, הקצב — עם מוזיקה בהתאם שמרימה את הכל. סרטון שמכניס אותך לתוך המחנה בשניות.",
     "1,000"),
]

def item_html(title, desc, price):
    return f'''
      <div class="item">
        <div class="item-head">
          <div class="item-title">{title}</div>
          <div class="item-price">{price} <span class="sh">₪</span></div>
        </div>
        <div class="item-desc">{desc}</div>
      </div>'''

items = "".join(item_html(*it) for it in items_pkg)

incl = ["צילום מלא ביום המחנה","עריכה מלאה + קולור לכל סרטון","מוזיקה מותאמת לכל סרטון","סבב תיקונים אחד לכל סרטון","פורמט אנכי לרשתות + פורמט רחב"]
pay = ["50% עם אישור ההצעה — 1,800 ₪ (ניתן לאשר בצ'אט)","50% במסירת החומרים הסופיים","ההצעה בתוקף עד 15.08.2026"]
film = ["יום צילום כולל עד שעתיים וחצי צילום פעיל","כל שעה נוספת מעבר לכך תחויב ב-150 ₪"]
steps = ["אישור ההצעה + תשלום מקדמה","שיחת תכנון קריטיב לסרטונים — נגדיר יחד את הסגנון, הכיוון והמסר","תיאום יום צילום מהמחנה"]

def bullets(arr):
    return "".join(f'<li>{x}</li>' for x in arr)

html = f'''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html,body {{ font-family:"Heebo", Arial, sans-serif; color:#3A3A3A; -webkit-font-smoothing:antialiased; }}
  @page {{ size: 8.5in 11in; margin:0; }}
  :root {{
    --navy:#1F3A5E; --gold:#B9902D; --cream:#EFE7D5; --card:#F6F1E7;
    --ink:#3A3A3A; --muted:#6B6B6B; --line:#E3DECF;
  }}
  .page {{ width:8.5in; min-height:11in; background:#fff; margin:0 auto; }}
  /* HERO */
  .hero {{ background:var(--cream); padding:52px 64px 34px; text-align:center; }}
  .hero img {{ height:96px; margin:14px auto 30px; display:block; }}
  .hero-title {{ color:var(--navy); font-weight:700; font-size:23px; letter-spacing:.2px; }}
  .gold-rule {{ height:6px; background:var(--gold); }}
  /* BODY */
  .body {{ padding:34px 64px 40px; }}
  .meta {{ text-align:right; line-height:2; }}
  .meta .lbl {{ color:var(--navy); font-weight:700; }}
  .meta .val {{ color:var(--ink); }}
  h2.sec {{ color:var(--navy); font-weight:700; font-size:16px; text-align:right; margin:6px 0 10px; }}
  p.lead {{ text-align:justify; line-height:1.85; color:var(--ink); font-size:13.5px; }}
  .divider {{ height:1px; background:var(--line); margin:26px 0; }}
  h2.block {{ color:var(--navy); font-weight:700; font-size:17px; text-align:right; margin:0 0 14px; }}
  /* CARD */
  .card {{ background:var(--card); border-right:6px solid var(--navy); border-radius:6px; padding:24px 26px; }}
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
  /* TERM SECTIONS */
  section.terms {{ margin-top:26px; padding-top:22px; border-top:1px solid var(--line); }}
  section.terms:first-of-type {{ }}
  ul.bul {{ list-style:none; }}
  ul.bul li {{ position:relative; padding-right:20px; margin:9px 0; text-align:right; font-size:13px; line-height:1.7; color:var(--ink); }}
  ul.bul li::before {{ content:""; position:absolute; right:2px; top:9px; width:6px; height:6px; border-radius:50%; background:var(--gold); }}
  /* FOOTER */
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
      <div class="hero-title">הצעת מחיר — SH PROJECT</div>
    </div>
    <div class="gold-rule"></div>

    <div class="body">
      <div class="meta">
        <div><span class="lbl">תאריך:</span> <span class="val">01.08.2026</span></div>
        <div><span class="lbl">לכבוד:</span> <span class="val">שירה העליון</span></div>
      </div>
      <h2 class="sec">רקע</h2>
      <p class="lead">כמו שדיברנו — שלושה סרטונים מהמחנה שיקדמו את SH PROJECT גם קדימה. כל סרטון עומד בפני עצמו ומשרת מטרה אחרת, וביחד הם נותנים לך מעטפת תוכן שלמה: תדמית, עדות אמיתית ואווירה. מוזמנת לעבור על ההצעה ולעדכן אותי בכל שאלה או שינוי שתרצי.</p>

      <div class="divider"></div>
      <h2 class="block">החבילה</h2>

      <div class="card avoid">
        <div class="card-head">
          <div class="card-title">3 סרטונים מהמחנה</div>
          <div class="card-price">3,600 <span class="sh">₪</span></div>
        </div>
        <div class="items">
          {items}
        </div>
        <div class="total">
          <div class="total-lbl">סה"כ</div>
          <div class="total-price">3,600 <span class="sh">₪</span></div>
        </div>
      </div>

      <section class="terms avoid">
        <h2 class="block">כלול בהצעה</h2>
        <ul class="bul">{bullets(incl)}</ul>
      </section>

      <section class="terms avoid">
        <h2 class="block">תנאי תשלום</h2>
        <ul class="bul">{bullets(pay)}</ul>
      </section>

      <section class="terms avoid">
        <h2 class="block">תנאי צילום</h2>
        <ul class="bul">{bullets(film)}</ul>
      </section>

      <section class="terms avoid">
        <h2 class="block">צעדים הבאים</h2>
        <ul class="bul">{bullets(steps)}</ul>
      </section>

      <div class="footer">
        <div class="brand">E.A. VISUALS</div>
        <div class="contact">@e.a.visuals_&nbsp;&nbsp;|&nbsp;&nbsp;eran0206@gmail.com&nbsp;&nbsp;|&nbsp;&nbsp;053-933-1782</div>
      </div>
    </div>
  </div>
</body>
</html>'''

open('quote.html','w').write(html)
print('wrote quote.html', len(html), 'chars')
