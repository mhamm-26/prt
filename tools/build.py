#!/usr/bin/env python3
"""Build the static website. Python 3.10+, no third-party dependencies."""
import json, html, shutil, csv
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'dist'; BASE='https://prorecoverytech.com'
A=json.loads((ROOT/'content/articles.json').read_text()); E=lambda s:html.escape(str(s),quote=True)
CATS={'data':'Data & AMS','health':'Health & Performance'}
ANNOUNCE='Due to concerns regarding customer service and workmanship, Pro Recovery Tech has decided to discontinue its role as a distributor for Rice Lake scales.'
if OUT.exists():shutil.rmtree(OUT)
shutil.copytree(ROOT/'public',OUT)
pages=[]
def link(path,label,cls=''):return f'<a class="{cls}" href="{E(path)}">{label}</a>'
def rice():return link('https://www.ricelake.com/','Visit Rice Lake','button primary')
def image(a,cls=''):
 if not a:return ''
 return f'<img class="{cls}" src="{a["path"]}" width="{a["width"]}" height="{a["height"]}" alt="{E(a.get("alt",""))}" loading="lazy" decoding="async">'
def cards(items):
 result='<div class="cards">'
 for a in items:
  pic=dict(a['image'],alt=a['title']) if a['image'] else None
  visual=image(pic) if pic else ''
  result+=f'<article class="card"><a class="card-image {a["category"]}" href="{a["path"]}" tabindex="-1" aria-hidden="true">{visual}</a><div class="card-body"><span class="eyebrow">{CATS[a["category"]]}</span><h3>{link(a["path"],E(a["title"]))}</h3><p>{E(a["description"])}</p><div class="card-meta"><span>{E(a["date_label"])}</span></div></div></article>'
 return result+'</div>'
def crumbs(items):
 return '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li>'+''.join(f'<li>{link(p,E(n)) if p else E(n)}</li>' for n,p in items)+'</ol></nav>'
def page(path,title,description,body,active='',breadcrumbs=None,article=None,noindex=False):
 canonical=BASE+path; structured=[{'@context':'https://schema.org','@type':'Organization','name':'Pro Recovery Tech','url':BASE,'logo':BASE+'/assets/logo.png'}]
 if breadcrumbs:
  structured.append({'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':n,'item':BASE+p} for i,(n,p) in enumerate([('Home','/')]+breadcrumbs)]})
 if article:
  data={'@context':'https://schema.org','@type':'Article','headline':article['title'],'description':description,'datePublished':article['date'],'mainEntityOfPage':canonical,'publisher':{'@type':'Organization','name':'Pro Recovery Tech'}}
  if article['author']:data['author']={'@type':'Person','name':article['author']}
  if article['image']:data['image']=BASE+article['image']['path']
  structured.append(data)
 nav=''.join(f'<a href="{p}"'+(' aria-current="page"' if active==n else '')+f'>{n}</a>' for p,n in [('/','Home'),('/resources/','Resources'),('/support/','Support & Contact')])
 social=BASE+(article['image']['path'] if article and article['image'] else '/assets/logo.png')
 output=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} | Pro Recovery Tech</title><meta name="description" content="{E(description)}"><link rel="canonical" href="{canonical}"><meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{social}"><meta property="og:image:alt" content="{E(article['title'] if article and article['image'] else 'Pro Recovery Tech')}"><meta property="og:site_name" content="Pro Recovery Tech"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/assets/favicon.png" type="image/png"><link rel="stylesheet" href="/assets/site.css"><script src="/assets/site.js" defer></script>{'<meta name="robots" content="noindex">' if noindex else ''}<script type="application/ld+json">{json.dumps(structured).replace('<','\\u003c')}</script></head><body><a class="skip" href="#main">Skip to content</a><div class="topline"><div class="wrap">An independent educational resource <span>Data. Recovery. Performance.</span></div></div><header class="header"><div class="wrap header-inner"><a class="brand" href="/" aria-label="Pro Recovery Tech home"><img src="/assets/logo.png" width="600" height="98" alt="Pro Recovery Tech"></a><button class="menu-toggle" aria-expanded="false" aria-controls="navigation"><span class="menu-icon" aria-hidden="true">☰</span><span class="menu-label">Menu</span></button><nav id="navigation" aria-label="Main navigation">{nav}</nav></div></header><main id="main" tabindex="-1">{body}</main><footer><div class="wrap footer-top"><div><a class="footer-brand" href="/">Pro Recovery Tech<span class="brand-dot">.</span></a><p>Knowledge for better-informed decisions.</p></div><nav aria-label="Footer navigation"><a href="/">Home</a><a href="/resources/">Resources</a><a href="/support/">Support & Contact</a><a href="/privacy/">Privacy</a></nav></div><div class="wrap footer-bottom"><span>© {datetime.now().year} Pro Recovery Tech</span><span>Educational resources. No online store.</span></div></footer></body></html>'''
 dest=OUT/(path.strip('/')+'/index.html' if path!='/' else 'index.html')
 if path.endswith('.html'):dest=OUT/path.lstrip('/')
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(output)
 if not noindex:pages.append(path)

body=f'''<section class="announcement wrap"><div class="announcement-heading"><span class="eyebrow"><span class="status-dot"></span> A note to our community</span><h1>An Update from <br>Pro Recovery Tech</h1><p class="intro-caption">Our role has changed.<br>Our resources remain.</p></div><div class="announcement-copy"><p>{ANNOUNCE}</p><p>If you need assistance with a Rice Lake product, please contact Rice Lake Weighing Systems directly through its website.</p><p>Our educational resources remain available for reference.</p><div class="actions">{rice()}{link('/resources/','Browse Resources','button secondary')}</div></div></section><section class="library-section"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">The resource center</span><h2>Practical knowledge.<br>At your fingertips.</h2></div><p>Explore our collection of guides on athlete data, connected technology, health, and performance. Original articles, kept available for reference.</p></div><div class="category-links"><a href="/resources/data-ams/"><span class="category-icon" aria-hidden="true">≋</span><span><strong>Data & AMS</strong><small>Integrations, workflows & connected tools</small></span></a><a href="/resources/health-performance/"><span class="category-icon" aria-hidden="true">＋</span><span><strong>Health & Performance</strong><small>Recovery, wearables & performance insights</small></span></a></div><div class="section-heading compact"><h2>From the library</h2>{link('/resources/','View all resources','text-link')}</div>{cards([A[0],next(a for a in A if a['slug'].startswith('3-ways')),next(a for a in A if 'fitbit' in a['slug'])])}</div></section>'''
page('/','Educational resources & distributor update','Read the Pro Recovery Tech distributor update and explore educational guides on athlete data, recovery, health, and performance.',body,'Home')
for category,path in [(None,'/resources/'),('data','/resources/data-ams/'),('health','/resources/health-performance/')]:
 items=[a for a in A if not category or a['category']==category]; title=CATS[category] if category else 'The resource library'
 body='<div class="wrap">'+crumbs([('Resources',None)])+f'<section class="page-intro"><span class="eyebrow">Explore & learn</span><h1>{title}</h1><p>Practical guides and original perspectives on the technology behind health and performance. Browse the collection below.</p></section><nav class="filters" aria-label="Resource categories">'
 for key,p,label in [(None,'/resources/','All resources'),('data','/resources/data-ams/','Data & AMS'),('health','/resources/health-performance/','Health & Performance')]:
  body+=f'<a href="{p}"'+(' aria-current="page"' if key==category else '')+f'>{label} <span>{len([a for a in A if not key or a["category"]==key])}</span></a>'
 body+='</nav><p class="archive-note">From the archive · Original publication dates are shown. See each guide for current-context notes.</p>'+cards(items)+'</div>'
 page(path,title,f'Browse {len(items)} archived Pro Recovery Tech guides'+(' about '+CATS[category] if category else ' on data, athlete management systems, health, and performance')+'.',body,'Resources', [('Resources','/resources/')]+([(title,path)] if category else []))
for a in A:
 catpath='/resources/'+('data-ams/' if a['category']=='data' else 'health-performance/')
 body='<div class="wrap">'+crumbs([('Resources','/resources/'),(CATS[a['category']],catpath),(a['title'],None)])+'</div>'
 body+=f'<header class="article-header"><span class="eyebrow">{CATS[a["category"]]} · Archived guide</span><h1>{E(a["title"])}</h1><p class="byline">Originally published <time datetime="{a["date"]}">{E(a["date_label"])}</time>'+(' · '+E(a['author']) if a['author'] else '')+'</p></header>'
 body+='<div class="article-layout wrap"><aside class="toc" aria-label="On this page"><strong>In this guide</strong><ol>'+''.join(f'<li><a href="#{h["id"]}">{E(h["text"])}</a></li>' for h in a['headings'])+'</ol><a class="back-link" href="/resources/">All resources</a></aside><article class="article-body"><section class="editor-note" aria-label="Archive and distributor notice"><strong>Before you read</strong>'+''.join('<p>'+E(n)+'</p>' for n in a['notices'])+('<a href="https://www.ricelake.com/">Visit Rice Lake</a>' if any('no longer distributes' in n for n in a['notices']) else '')+'</section>'
 if a.get('hero'):body+=image(dict(a['hero'],alt=a['title']),'article-hero')
 body+=(ROOT/'content/articles'/f'{a["slug"]}.html').read_text()
 body+='<div class="editorial-footer">Archive presentation updated October 15, 2026: store offers and purchasing links removed; original technical material retained with context notes. This is not a technical revision of the guide.</div></article></div>'
 related=[x for x in A if x['category']==a['category'] and x!=a][:3]
 body+='<section class="wrap related"><span class="eyebrow">Keep exploring</span><h2>Related resources</h2>'+cards(related)+'</section>'
 page(a['path'],a['title'],a['description'],body,'Resources',[('Resources','/resources/'),(CATS[a['category']],catpath),(a['title'],a['path'])],a)
body='<div class="wrap narrow">'+crumbs([('Support & Contact',None)])+f'''<section class="page-intro"><span class="eyebrow">Finding the right help</span><h1>Support & Contact</h1><p>For Rice Lake products, the manufacturer is your direct point of contact.</p></section><section class="contact-panel"><h2>Rice Lake product assistance</h2><p>{ANNOUNCE}</p><p>For product questions, service, or warranty inquiries, visit Rice Lake Weighing Systems’ official website and use its contact options.</p>{rice()}<p class="small">Pro Recovery Tech is no longer a Rice Lake distributor. Rice Lake determines its own service and warranty terms; we cannot promise a particular outcome.</p></section><section class="prose"><h2>About these resources</h2><p>Our educational articles remain available for reference. They reflect their original publication dates and do not establish current product compatibility, an active partnership, or ongoing technical support.</p><p>For questions about this website or its content, email <a href="mailto:sales@prorecoverytech.com">sales@prorecoverytech.com</a>, the address listed on our original website. Please direct Rice Lake product inquiries to Rice Lake.</p><a class="text-link" href="/resources/">Explore the resource library</a></section></div>'''
page('/support/','Support & Contact','Find Rice Lake’s official website for product, service, and warranty inquiries, and read about Pro Recovery Tech’s distributor status.',body,'Support & Contact',[('Support & Contact','/support/')])
body='<div class="wrap narrow">'+crumbs([('Privacy',None)])+'''<section class="page-intro"><span class="eyebrow">About this website</span><h1>Privacy</h1><p>Last updated October 15, 2026</p></section><div class="prose"><h2>A simple informational website</h2><p>This website provides educational articles and contact links. It has no online store, customer accounts, newsletter signup, contact form, analytics scripts, advertising pixels, or embedded social media. Its code does not set cookies or use browser storage. Fonts and images are served locally.</p><h2>Basic hosting information</h2><p>When you visit, the hosting provider receives information needed to deliver pages, including your IP address, requested URL, browser information, and request time. The website application does not keep a visitor database. Server logs and their retention depend on the hosting configuration.</p><h2>Email</h2><p>If you choose to email Pro Recovery Tech, your email provider and ours process your message and contact details so we can receive and respond to it. Do not send passwords, health records, or other sensitive information.</p><h2>External websites</h2><p>Links to Rice Lake and other reference sources take you to independent websites with their own privacy practices. Those sites are not loaded until you follow a link.</p><h2>Questions</h2><p>For website privacy questions, email <a href="mailto:sales@prorecoverytech.com">sales@prorecoverytech.com</a>.</p></div></div>'''
page('/privacy/','Privacy','How the Pro Recovery Tech informational website handles visits, external links, and email correspondence.',body,breadcrumbs=[('Privacy','/privacy/')])
for code,title,description in [(404,'This page isn’t here.','The address may have changed, or the page may no longer exist.'),(410,'This store page has been retired.','Pro Recovery Tech no longer operates an online store. This page has no direct replacement.')]:
 body=f'<section class="wrap error-page"><span class="eyebrow">{code}</span><h1>{title}</h1><p>{description}</p><p>Our educational resources remain available, and Rice Lake can help with product inquiries.</p><div class="actions">{link("/resources/","Browse Resources","button primary")}{link("/support/","Support & Contact","button secondary")}</div></section>'
 page(f'/{code}.html',title,description,body,noindex=True)
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+E(p)+'</loc></url>' for p in pages)+'</urlset>\n')
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n')
routes=json.loads((ROOT/'content/routes.json').read_text())
# Exact matches handle both trailing slash forms and preserve query strings.
nginx=['# Include inside your nginx server block. Generated by tools/build.py.','error_page 404 /404.html;','error_page 410 /410.html;']
for r in routes:
 if r['status']==200:continue
 for path in sorted({r['old_path'],r['old_path'].rstrip('/')+'/'}):
  if path==r['destination']:continue
  nginx.append(f'location = {path} {{ return {r["status"]}'+(' '+r['destination'] if r['status']==301 else '')+'; }')
nginx+=['location / { try_files $uri/index.html $uri =404; }']
(ROOT/'hosting').mkdir(exist_ok=True)
(ROOT/'hosting/nginx-routes.conf').write_text('\n'.join(nginx)+'\n')
with (ROOT/'docs/url-migration.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=['old_path','status','destination','reason'],lineterminator='\n');writer.writeheader();writer.writerows(routes)
print(f'Built {len(pages)} crawlable pages, custom error pages, sitemap, and nginx routes.')

# Commit this generated configuration so Vercel knows how to build on first deploy.
from vercel_config import configuration
(ROOT/"vercel.json").write_text(json.dumps(configuration(pages, routes), indent=2)+"\n")
