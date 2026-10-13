import threading,http.server,functools,json,time,sys,os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1];BASE='http://127.0.0.1:8765/'
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',8765),functools.partial(Quiet,directory=str(ROOT/'site')))
threading.Thread(target=server.serve_forever,daemon=True).start()
checks=[]
def ok(name,expr=True):
 if not expr:raise AssertionError(name)
 checks.append(name);print('PASS:',name,flush=True)
errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--no-sandbox'],**({'executable_path':os.environ['CHROMIUM_PATH']} if os.environ.get('CHROMIUM_PATH') else {}))
 ctx=b.new_context(viewport={'width':1440,'height':1050},device_scale_factor=1)
 page=ctx.new_page();page.set_default_timeout(7000);page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(BASE);page.wait_for_selector('.hero');ok('Desktop home rendered')
 page.screenshot(path=str(ROOT/'qa/desktop-home.png'),full_page=True)
 # All 30 source articles must render, with no broken local images or wide viewport.
 ids=page.evaluate('KB.chapters.map(c=>c.id)');ok('All 30 chapters included',len(ids)==30)
 ok('41 retained source references',page.evaluate('KB.sources.length')==41)
 for id in ids:
  page.goto(BASE+'#article/'+id);page.wait_for_selector('.reader-body');ok('Article '+id,page.locator('.reader-body').inner_text().strip()!='')
 page.goto(BASE+'#library');page.locator('#search').fill('колтун');ok('Full-text Russian search finds coat',page.locator('#book-results a[href="#article/coat"]').count()==1)
 page.locator('#search').fill('абракадабранеизвестное');ok('Search empty state',page.get_by_text('Пока ничего не нашлось').is_visible())
 page.locator('#search').fill('');page.locator('[data-filter="start"]').click();ok('Category filter',page.locator('.book-card').count()==5)
 page.locator('.book-card .bookmark').first.click();page.locator('[data-action="bookmarks"]').click();ok('Bookmark filter',page.locator('.book-card').count()==1)
 # Atomic/once-only read rewards.
 page.goto(BASE+'#article/home');page.locator('[data-action="read"]').click();page.locator('[data-action="read"]').click();ok('Read not awarded twice',page.evaluate('JSON.parse(localStorage.getItem("lapaza-puppy-v1")).reads.filter(x=>x==="home").length')==1)
 page.reload();ok('Progress persists on reload',page.evaluate('JSON.parse(localStorage.getItem("lapaza-puppy-v1")).reads.includes("home")'))
 # Day state respects preparation and actual puppy as separate sets.
 page.goto(BASE+'#day');page.locator('[data-action="task"][data-block="morning"][data-id="t1"][data-status="help"]').click();ok('Help does not pretend to notify',page.locator('#toast').inner_text().find('не отправляет')>=0)
 page.locator('[data-phase="home"]').click();ok('Prep and real-care lists separated',page.locator('.task.help').count()==0)
 page.locator('[data-action="task"][data-block="morning"][data-id="t1"][data-status="done"]').click();page.locator('[data-action="task"][data-block="morning"][data-id="t1"][data-status="todo"]').click();ok('Day completion can be undone',page.locator('.task.done').count()==0)
 # Room finding opens explanation; merely opening isn't a completed lesson.
 page.goto(BASE+'#game/room');page.locator('.hotspot').first.click();ok('Room explanation dialog',page.locator('#modal').is_visible());ok('Room no auto completion on opening',page.evaluate('JSON.parse(localStorage.getItem("lapaza-puppy-v1")).games.room.length')==0)
 page.locator('[data-action="hazard-understood"]').click();ok('Room understanding recorded',page.evaluate('JSON.parse(localStorage.getItem("lapaza-puppy-v1")).games.room.length')==1)
 for i in range(1,6):page.locator('.hotspot').nth(i).click();page.locator('[data-action="hazard-understood"]').click()
 ok('Room completion',page.get_by_text('Шесть находок разобраны!').is_visible())
 # Quiz: wrong answers have explicit safe corrective feedback and clickable source.
 page.goto(BASE+'#game/stories');page.locator('[data-action="answer"][data-answer="0"]').click();ok('Wrong quiz answer has explanation',page.locator('.feedback.wrong').count()==1);page.locator('[data-action="next-story"]').click();ok('Story advances',page.get_by_text('История 2 из 12').is_visible())
 for i in range(1,12):
  answer=page.evaluate(f'PLAY.scenarios[{i}].answer');page.locator(f'[data-action="answer"][data-answer="{answer}"]').click();page.locator('[data-action="next-story"]').click()
 ok('All stories complete',page.get_by_text('Истории разобраны').is_visible());ok('Story completion counts 12',page.evaluate('JSON.parse(localStorage.getItem("lapaza-puppy-v1")).games.scenarios.length')==12)
 # Packing reject unsafe and incomplete; succeeds only exact safe set.
 page.goto(BASE+'#game/bag');page.locator('[data-action="bag-item"][data-id="pills"]').click();page.locator('[data-action="check-bag"]').click();ok('Unsafe packing rejected',page.locator('.feedback.wrong').count()==1)
 page.locator('[data-action="clear-bag"]').click()
 for id in page.evaluate('PLAY.bag.filter(x=>x[3]).map(x=>x[0])'):page.locator(f'[data-action="bag-item"][data-id="{id}"]').click()
 page.locator('[data-action="check-bag"]').click();ok('Correct packing completed',page.evaluate('JSON.parse(localStorage.getItem("lapaza-puppy-v1")).games.bag') is True)
 # Reorder via accessible click buttons.
 page.goto(BASE+'#game/sequence');page.locator('[data-action="check-order"]').click();ok('Wrong sequence rejected',page.locator('.feedback.wrong').count()==1)
 page.locator('[data-action="order"][data-index="1"][data-dir="-1"]').click();page.locator('[data-action="order"][data-index="3"][data-dir="-1"]').click();page.locator('[data-action="order"][data-index="2"][data-dir="-1"]').click();page.locator('[data-action="check-order"]').click();ok('Correct sequence recorded',page.evaluate('JSON.parse(localStorage.getItem("lapaza-puppy-v1")).games.sequence') is True)
 page.goto(BASE+'#game/myths')
 for i in range(8):
  answer=page.evaluate(f'PLAY.myths[{i}].answer');page.locator('[data-action="myth-answer"][data-value="'+str(answer).lower()+'"]').click();page.locator('[data-action="next-myth"]').click()
 ok('Eight myth cards complete',page.get_by_text('Догадки проверены').is_visible())
 # Mother checklist cannot be approved from statuses alone or before review.
 page.goto(BASE+'#mom');page.locator('[data-action="mom-tab"][data-tab="prepare"]').click()
 for i in range(10):page.locator(f'[data-prep="c{i}"]').select_option('done')
 ok('No notes means not ready',page.evaluate('Lapaza.prepReady()') is False)
 page.locator('#decision').select_option('go');ok('Premature approval blocked',page.locator('#decision').input_value()=='none')
 for i in range(10):page.locator(f'[data-proof="c{i}"]').fill('Проверено в тестовом сценарии')
 ok('Proof completes checklist',page.evaluate('Lapaza.prepReady()') is True)
 ok('No automatic buy approval',page.locator('#decision').input_value()=='none')
 page.locator('#decision').select_option('wait');ok('Postpone overrides checked items','отложили' in page.locator('#prep-summary').inner_text())
 page.locator('#decision').select_option('go');page.locator('[data-prep="c3"]').select_option('questions');ok('Changing clinical prerequisite invalidates approval',page.locator('#decision').input_value()=='none')
 page.locator('[data-action="mom-tab"][data-tab="travel"]').click();ok('Travel phases separated',page.locator('.phase-card').count()==3)
 page.locator('[data-trip="stay-0-0"]').check();page.locator('[data-action="trip-mode"][data-mode="travel"]').click();ok('Trip modes independent',page.locator('[data-trip="travel-0-0"]').is_checked() is False)
 # Locally stored text must be escaped. Fill fictional test value then reset before shipping.
 page.locator('[data-action="mom-tab"][data-tab="passport"]').click();page.locator('input[name="puppy"]').fill('<img src=x onerror=alert(1)>');page.locator('#passport-form button[type=submit]').click();page.reload();ok('HTML injection in profile remains text',page.locator('input[name="puppy"]').input_value()=='<img src=x onerror=alert(1)>')
 page.locator('[data-action="mom-tab"][data-tab="log"]').click();page.locator('[name="what"]').fill('Тестовый корм, фактическая запись');page.locator('[name="who"]').fill('Тест');page.locator('#log-form button[type="submit"]').click();ok('Actual log saved',page.locator('.log-item').count()==1)
 # Invalid import schema/prototype fields are rejected or stripped.
 ok('Sanitizer discards dangerous keys',page.evaluate('Object.getPrototypeOf(Lapaza.sanitize(JSON.parse(\'{"version":1,"__proto__":{"polluted":true},"reads":["wrong","home"],"days":{"__proto__":{}}}\'))).polluted === undefined'))
 ok('Sanitizer filters invalid article IDs',page.evaluate('Lapaza.sanitize({version:1,reads:["wrong","home"]}).reads.length')==1)
 # Emergency route always reachable even with zero progress.
 page.goto(BASE+'#emergency');ok('Emergency has no learning prerequisite',page.get_by_text('Сейчас нужна помощь?').is_visible())
 # Offline activation must complete before claiming ready.
 page.goto(BASE+'#settings');page.locator('[data-action="offline"]').click();expect(page.locator('#offline-status')).to_contain_text('Готово:',timeout=15000);ok('Explicit offline cache completed')
 page.reload();ctx.set_offline(True);page.reload();page.wait_for_selector('h1');ok('Offline reload works',page.locator('h1').inner_text()=='Ваши данные — у вас');ctx.set_offline(False)
 # Fresh mobile context, screenshots, and overflow for 320/390/768.
 mobile=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=1)
 mp=mobile.new_page();mp.on('pageerror',lambda e:errors.append(str(e)));mp.goto(BASE);mp.wait_for_selector('.hero');mp.screenshot(path=str(ROOT/'qa/mobile-home.png'),full_page=True)
 routes=['home','library','day','mom','game/room','game/stories','game/bag','game/sequence','game/myths','badges','article/feeding','article/coat','emergency','sources','settings']
 for route in routes:
  mp.goto(BASE+'#'+route);mp.wait_for_timeout(60);ok('Mobile no horizontal overflow '+route,mp.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
  if route in ['day','game/room','article/feeding','mom','game/stories']:
   mp.screenshot(path=str(ROOT/'qa'/('mobile-'+route.replace('/','-')+'.png')),full_page=True)
 mp.set_viewport_size({'width':320,'height':740});mp.goto(BASE);ok('320px header fits',mp.evaluate('document.documentElement.scrollWidth <= innerWidth+1'))
 mp.goto(BASE+'#library');mp.locator('#search').fill('зубы');mp.locator('#book-results a').first.click();mp.wait_for_selector('.reader-body');ok('Touch-friendly library opens reader',mp.locator('.reader-body').count()==1)
 # Broken images: wait for every source src by evaluating direct loads, not just lazy loaded viewport.
 assets=mp.evaluate('[...new Set(KB.chapters.flatMap(c=>[...c.html.matchAll(/src="([^"]+)"/g)].map(x=>x[1]))) ]')
 broken=mp.evaluate('''async list => (await Promise.all(list.map(src => new Promise(resolve => {const i=new Image();i.onload=()=>resolve(null);i.onerror=()=>resolve(src);i.src=src;})))).filter(Boolean)''',assets)
 ok('Every source image loads',not broken)
 ok('No uncaught JavaScript errors',not errors)
 b.close()
server.shutdown();(ROOT/'qa/test_results.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'errors':errors},ensure_ascii=False,indent=2));print(json.dumps({'passed':len(checks),'errors':errors},ensure_ascii=False))
