import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
URL = os.environ.get('PUBLIC_URL', 'https://rawcdn.githack.com/getcher123/Life/d591accbfeca5fd65e8c423e6878372432a83f82/puppy-care/site/index.html')
passed, errors = [], []

def record(text):
    passed.append(text)
    print('PASS PUBLIC:', text, flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    context = browser.new_context(viewport={'width':390,'height':844}, is_mobile=True, has_touch=True)
    page = context.new_page()
    page.set_default_timeout(30000)
    page.on('pageerror', lambda e: errors.append(str(e)))
    try:
        response = page.goto(URL, wait_until='domcontentloaded', timeout=60000)
        assert response and response.status == 200, 'Public endpoint did not return HTTP 200'
        consent = page.get_by_text('Open the page', exact=True)
        if consent.is_visible():
            # The service asks the visitor to explicitly open this known, generated page.
            # Click the normal visible control; never bypass the hosting security screen.
            consent.click()
            record('Hosting asks for a visible Open the page confirmation on the first visit')
        expect(page.locator('.hero-copy')).to_be_visible(timeout=45000)
        assert 'Лапа за лапой' in page.title(), page.title()
        record('Actual published app loads over HTTPS after the visible hosting confirmation')
        page.screenshot(path=str(ROOT/'qa/public-mobile-home.png'), full_page=True)
        page.locator('.hero-copy a.button').first.click()
        expect(page.locator('.reader-body')).to_be_visible()
        record('Public start button opens the source chapter')
        page.goto(URL+'#library')
        page.locator('#search').fill('шерсть')
        expect(page.locator('#book-results a[href="#article/coat"]')).to_be_visible()
        record('Public full-text search works')
        page.goto(URL+'#game/room')
        page.locator('.hotspot').first.click()
        expect(page.locator('#modal')).to_be_visible()
        page.locator('[data-action="hazard-understood"]').click()
        expect(page.locator('.hotspot.found')).to_have_count(1)
        record('Public touch game and feedback work')
        page.screenshot(path=str(ROOT/'qa/public-mobile-room.png'), full_page=True)
        page.goto(URL+'#mom')
        page.locator('[data-action="mom-tab"][data-tab="prepare"]').click()
        expect(page.locator('[data-proof-tick]')).to_have_count(10)
        page.locator('[data-action="mom-tab"][data-tab="passport"]').click()
        expect(page.locator('#passport-form')).to_have_count(0)
        record('Shared host accepts non-sensitive checks but does not expose private contact forms')
        page.goto(URL+'#emergency')
        expect(page.get_by_text('Сейчас нужна помощь?')).to_be_visible()
        record('Emergency section has no lesson prerequisite')
        page.goto(URL+'#settings')
        page.locator('[data-action="offline"]').click()
        expect(page.locator('#offline-status')).to_contain_text('Готово:', timeout=90000)
        record('Public app files cached after explicit request')
        page.reload()
        context.set_offline(True)
        page.reload()
        expect(page.get_by_text('Ваши данные — у вас')).to_be_visible()
        record('Published app reloads offline after successful caching')
        context.set_offline(False)
        assert not errors, errors
        record('No uncaught public-page JavaScript errors')
    except Exception:
        page.screenshot(path=str(ROOT/'qa/public-failure.png'), full_page=True)
        (ROOT/'qa/public-failure.html').write_text(page.content())
        (ROOT/'qa/public_partial.json').write_text(json.dumps({'passed':passed,'errors':errors,'url':page.url},ensure_ascii=False,indent=2))
        raise
    finally:
        browser.close()
result = {'public_url':URL,'passed':len(passed),'checks':passed,'errors':errors}
(ROOT/'qa/public_smoke_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
