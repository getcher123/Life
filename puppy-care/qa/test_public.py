import json, os, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
try:
    ref = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT.parent, text=True).strip()
except Exception:
    ref = '121ebcc5e1d0bf6456d080eb9dca7d7baa4141d2'
URL = os.environ.get('PUBLIC_URL', 'https://rawcdn.githack.com/getcher123/Life/'+ref+'/puppy-care/site/index.html')
passed, errors, console_errors = [], [], []

def record(text):
    passed.append(text)
    print('PASS PUBLIC:', text, flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    context = browser.new_context(viewport={'width':390,'height':844}, is_mobile=True, has_touch=True)
    page = context.new_page()
    page.set_default_timeout(30000)
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: console_errors.append(m.text) if m.type == 'error' else None)
    try:
        response = page.goto(URL, wait_until='domcontentloaded', timeout=60000)
        assert response and response.status == 200, 'Public endpoint did not return HTTP 200'
        consent = page.get_by_text('Open the page', exact=True)
        if consent.is_visible():
            # Use the hosting service's normal visible confirmation for this known page.
            consent.click()
            record('Hosting asks for a visible Open the page confirmation on the first visit')
        expect(page.locator('.hero-copy')).to_be_visible(timeout=45000)
        assert 'Лапа за лапой' in page.title(), page.title()
        record('Actual published app loads over HTTPS after the visible hosting confirmation')
        assets = page.evaluate('''() => [...new Set([
            ...KB.chapters.flatMap(c => [...c.html.matchAll(/src="([^"]+)"/g)].map(m=>m[1])),
            ...KB.photos.map(p=>'assets/'+p.file),
            ...['play','sleep','carrier','walk'].map(n=>'assets/art-'+n+'.webp')
        ])]''')
        failures = page.evaluate('''async list => (await Promise.all(list.map(src => new Promise(resolve => {
            const image = new Image();
            const timer=setTimeout(()=>resolve({src,error:'timeout'}),20000);
            image.onload=()=>{clearTimeout(timer);resolve(image.naturalWidth>0?null:{src,error:'empty image'});};
            image.onerror=()=>{clearTimeout(timer);resolve({src,error:'load failed'});};
            image.src=src;
        })))).filter(Boolean)''',assets)
        assert not failures, {'images':failures,'console':console_errors}
        page.evaluate('''async () => {const imgs=[...document.images]; imgs.forEach(i=>i.loading='eager'); await Promise.all(imgs.map(i=>i.decode()));}''')
        record('All '+str(len(assets))+' published photos, illustrations and source diagrams decode successfully')
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
        (ROOT/'qa/public_partial.json').write_text(json.dumps({'passed':passed,'errors':errors,'console':console_errors,'url':page.url},ensure_ascii=False,indent=2))
        raise
    finally:
        browser.close()
result = {'public_url':URL,'passed':len(passed),'checks':passed,'errors':errors}
(ROOT/'qa/public_smoke_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
