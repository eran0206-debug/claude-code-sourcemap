from playwright.sync_api import sync_playwright
import pathlib
url = pathlib.Path('quote.html').resolve().as_uri()
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
    pg = b.new_page()
    pg.goto(url, wait_until='networkidle')
    pg.pdf(path='SH_PROJECT_quote.pdf', width='8.5in', height='11in', print_background=True, margin={'top':'0','bottom':'0','left':'0','right':'0'})
    # also full-page screenshots for review
    pg.screenshot(path='preview_full.png', full_page=True)
    b.close()
print('done')
