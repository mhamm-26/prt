"""Browser validation. Requires Playwright, Chromium, and AXE_SCRIPT env path."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
paths=['/','/resources/','/resources/data-ams/','/resources/health-performance/','/support/','/privacy/','/404.html','/410.html']+[a['path'] for a in json.loads((ROOT/'content/articles.json').read_text())]
errors=[];violations=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=b.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
 for width in [320,390,768,1440]:
  page.set_viewport_size({'width':width,'height':900})
  for path in paths:
   page.goto('http://127.0.0.1:8000'+path);page.evaluate('document.fonts.ready');page.locator('footer').scroll_into_view_if_needed();page.wait_for_timeout(60)
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(width,path,'overflow')
   assert page.locator('h1').count()==1
   for img in page.locator('img').all():
    img.scroll_into_view_if_needed();img.evaluate('(el)=>el.decode()');assert img.evaluate('(el)=>el.complete && el.naturalWidth > 0'),(path,'image')
   if width==390:
    page.add_script_tag(path=os.environ['AXE_SCRIPT'])
    result=page.evaluate("async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})")
    if result['violations']:violations.append({'path':path,'violations':[{ 'id':v['id'],'nodes':[n['html'] for n in v['nodes']]} for v in result['violations']]})
 page.set_viewport_size({'width':390,'height':844});page.goto('http://127.0.0.1:8000/')
 toggle=page.locator('.menu-toggle');assert not page.locator('#navigation').is_visible()
 toggle.focus();page.keyboard.press('Enter');assert toggle.get_attribute('aria-expanded')=='true';assert page.get_by_role('button',name='Close').is_visible()
 page.keyboard.press('Tab');assert page.evaluate('document.activeElement.textContent')=='Home'
 page.keyboard.press('Escape');assert toggle.get_attribute('aria-expanded')=='false';assert toggle.evaluate('(el)=>el===document.activeElement')
 toggle.click();page.locator('#navigation').get_by_role('link',name='Resources',exact=True).click();assert page.url.endswith('/resources/');assert not page.locator('#navigation').is_visible()
 page.goto('http://127.0.0.1:8000/');page.screenshot(path='/tmp/prt-mobile-final.png',full_page=True)
 page.set_viewport_size({'width':1440,'height':1000});page.screenshot(path='/tmp/prt-desktop-final.png',full_page=True)
 page.goto('http://127.0.0.1:8000'+paths[-1]);page.screenshot(path='/tmp/prt-article-final.png',full_page=True)
 context=b.new_context(java_script_enabled=False,viewport={'width':390,'height':844});nojs=context.new_page();nojs.goto('http://127.0.0.1:8000/');assert nojs.locator('#navigation').is_visible()
 b.close()
print(json.dumps({'browser_errors':errors,'accessibility_violations':violations},indent=2))
assert not errors and not violations
print('PASS: 17 pages × 4 widths, images, keyboard/mobile navigation, no-JS navigation, WCAG A/AA axe checks.')
