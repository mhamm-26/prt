"""One-time migration from backup. Requires beautifulsoup4 and Pillow.
Run after tools/backup_source.py; normal site builds require only Python 3.
"""
import hashlib, json, re, io
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import urlopen
from bs4 import BeautifulSoup
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
backup=sorted((ROOT/'backups').glob('*/manifest.json'))[-1]
records=json.loads(backup.read_text())['records']; byurl={r['url']:r for r in records}
assets=[]; edits=[]; missing=[]

def asset(url, name=None):
 url=urljoin('https://prorecoverytech.com',url)
 cached=next((a for a in assets if a['source']==url),None)
 if cached:return cached
 record=byurl.get(url)
 try:
  if record and 'file' in record: data=(backup.parent/record['file']).read_bytes()
  else:
   with urlopen(url,timeout=30) as response:data=response.read()
 except Exception as e:
  missing.append({'url':url,'error':str(e)});return None
 im=Image.open(io.BytesIO(data)); im.thumbnail((1200,1200))
 filename=name or hashlib.sha256(url.encode()).hexdigest()[:16]+'.webp'
 path=ROOT/'public/assets'/filename
 if filename.endswith('.webp'):im.save(path,'WEBP',quality=85)
 else:im.save(path)
 item={'source':url,'path':'/assets/'+filename,'width':im.width,'height':im.height,'source_sha256':hashlib.sha256(data).hexdigest()}
 assets.append(item);return item

home=BeautifulSoup((backup.parent/byurl['https://prorecoverytech.com/']['file']).read_text(),'html.parser')
logo=asset(home.select_one('header img')['src'],'logo.png')
favicon=asset(home.select_one('link[rel*=icon]')['href'],'favicon.png')
for variant,name in [('n4','assistant-regular.woff2'),('n7','assistant-bold.woff2')]:
 url=re.search(r'//prorecoverytech.com/cdn/fonts/assistant/assistant_'+variant+r'\.[a-z0-9]+\.woff2',str(home))[0]
 with urlopen('https:'+url) as r:data=r.read()
 (ROOT/'public/assets'/name).write_bytes(data)
 assets.append({'source':'https:'+url,'path':'/assets/'+name,'source_sha256':hashlib.sha256(data).hexdigest()})
articles=[]
for record in records:
 if record['kind']!='page' or not re.search(r'/blogs/(news|health-performance)/[^/?]+$',record['url']):continue
 soup=BeautifulSoup((backup.parent/record['file']).read_text(),'html.parser'); body=soup.select_one('.article-template__content')
 if not body:raise RuntimeError('Missing article body: '+record['url'])
 slug=record['url'].split('/')[-1];original=body.get_text(' ',strip=True)
 schema=next(json.loads(t.string) for t in soup.select('script[type="application/ld+json"]') if t.string and json.loads(t.string).get('@type')=='Article')
 title=soup.h1.get_text(' ',strip=True); changes=[]
 def remove(el,reason):
  changes.append({'reason':reason,'removed_text':el.get_text(' ',strip=True)});el.decompose()
 # Remove only identified commercial passages; record every removed passage.
 for el in list(body.select('p,li,h2')):
  if not el.parent:continue
  text=el.get_text(' ',strip=True)
  if any(x in text for x in ['PRT has you covered','If you are interested in purchasing','Interested in purchasing a Fitbit','We offer a price match','Pro Recovery Tech is an authorized distributor','If you have any questions about the scale please','If you have any questions about the scales or functionality','PRT can assist with developing','Reach out via our contact page']):remove(el,'Obsolete promotion or support offer');continue
  if text in ['How to Purchase',"What's Included with a Scale Purchase?",'Questions?','Need Help?','Free Shipping - within 1 business day','Comes with 6 months of Fitbit Premium']:
   remove(el,'Obsolete store heading, fulfillment term, or offer');continue
  if text.startswith('1. A scale.') and 'click here' in text:
   changes.append({'reason':'Removed scale purchase invitation','removed_text':text});el.clear();el.append('1. A Teamworks AMS compatible Rice Lake Bluetooth Scale.')
  elif 'If you decide to order from Pro Recovery Tech' in text:
   changes.append({'reason':'Removed included adapter sales offer; retained technical power-adapter note','removed_text':text});el.clear();el.append(text.split('If you decide to order from Pro Recovery Tech')[0].strip())
  elif text.startswith('Here is the link for the Bluetooth enabled'):
   changes.append({'reason':'Removed purchasing invitation; retained original compatibility claim, flagged as historical','removed_text':text});el.clear();el.append('Bluetooth enabled Rice Lake Scale, Model 150-10-7 BLE, integrates with Smartabase. This is the only scale model that is capable of successfully integrating.')
  elif 'PRT has shipped hundreds' in text:
   changes.append({'reason':'Removed unverified shipment claim; retained Bluetooth instructions','removed_text':'PRT has shipped hundreds of bluetooth scales and we have not had a single one delivered incorrectly.'})
   for t in list(el.find_all(string=True)):
    if 'PRT has shipped hundreds' in t:t.replace_with(str(t).replace('PRT has shipped hundreds of bluetooth scales and we have not had a single one delivered incorrectly.',''))
  elif text=='Affordable (under $100)':
   changes.append({'reason':'Removed historical retail price','removed_text':text});el.clear();el.append('Affordable')
 for a in list(body.select('a')):
  href=a.get('href','')
  if not href:a.unwrap();continue
  if 'smartabase.zendesk.com' in href:
   changes.append({'reason':'Original help center closed; replaced scale guide with current reference or marked unavailable','url':href})
   if '15009765477396' in href:
    a['href']='https://help.teamworks.com/ams/s/article/recording-data-from-bluetooth-scales-using-kiosk-mode-on-the-ams-mobile-app';continue
   a.insert_after(' [Original help-center reference is no longer available.]');a.unwrap();continue
  u=urlsplit(urljoin(record['url'],href))
  if u.hostname in {'prorecoverytech.com','www.prorecoverytech.com'}:
   if u.path.startswith('/products/'):
    changes.append({'reason':'Removed purchase link, retained link text','url':href});a.unwrap()
   elif u.path=='/pages/contact':a['href']='/support/'
   else:a['href']=u.path+(('?'+u.query) if u.query else '')+(('#'+u.fragment) if u.fragment else '')
  elif u.scheme in {'http','https'}:a['href']=urljoin(record['url'],href);a['rel']='noopener noreferrer'
  else:a.unwrap()
 for el in body.select('script,style,iframe,form'):remove(el,'Removed embedded executable content')
 for img in list(body.select('img')):
  source=img.get('src');item=asset(source)
  if not item:
   replacement=soup.new_tag('p');replacement['class']='missing-media';replacement.string='An image in the original article is no longer available from the source.';img.replace_with(replacement);continue
  alt=img.get('alt') or {'rice-lake-bluetooth-physician-scales':'Rice Lake physician scale — '+urlsplit(source).path.split('/')[-1].split('_480')[0].replace('_',' '),'installing-smartabaser-a-step-by-step-guide':'Original smartabaseR code summary screenshot'}.get(slug,title+' — original article illustration')
  img.attrs={'src':item['path'],'alt':alt,'width':str(item['width']),'height':str(item['height']),'loading':'lazy','decoding':'async'}
 # Strip editor styling and metadata while preserving meaningful HTML and text.
 for el in body.find_all(True):
  for attr in list(el.attrs):
   if attr not in {'href','src','alt','width','height','loading','decoding','rel','colspan','rowspan','class'}:del el[attr]
  if el.name!='p':el.attrs.pop('class',None)
  if el.name=='h1':el.name='h2'
  if el.name in {'h4','h5','h6'}:el.name='h3'
 for h in body.select('h2,h3'):
  if not h.get_text(strip=True):h.name='div'
 for nested in list(body.select('ul > ul, ul > ol, ol > ul, ol > ol')):
  previous=nested.find_previous_sibling('li')
  if previous:previous.append(nested.extract())
  else:
   wrapper=soup.new_tag('li');nested.wrap(wrapper)
  changes.append({'reason':'Corrected inherited nested-list HTML without changing wording'})
 for el in list(body.select('span')):el.unwrap()
 for p in list(body.select('p')):
  if not p.get_text(strip=True) and not p.select('img'):p.decompose()
 headings=[]
 for i,h in enumerate(body.select('h2,h3')):
  h['id']='section-'+str(i+1)
  if h.name=='h2':headings.append({'id':h['id'],'text':h.get_text(' ',strip=True)})
 hero=soup.select_one('.article-template__hero-container img');hero=asset(hero['src']) if hero else None
 card_image=hero
 if not card_image and body.select_one('img'):
  card_image=next((x for x in assets if x['path']==body.select_one('img')['src']),None)
 paragraphs=[p.get_text(' ',strip=True) for p in body.select('p') if len(p.get_text(' ',strip=True))>60]
 desc=('A practical guide to scale requirements, the Teamworks AMS app, Bluetooth connectivity, and common setup questions.' if slug.startswith('how-to-set-up') else (paragraphs[0] if paragraphs else title));desc=desc[:157].rsplit(' ',1)[0]+'…' if len(desc)>160 else desc
 notices=['Archived educational content. Instructions, availability, and third-party features reflect the original publication and have not been revalidated for current versions.']
 if 'rice-lake' in slug or 'gatorade' in slug:
  notices.append('Pro Recovery Tech no longer distributes Rice Lake products. For product, service, or warranty inquiries, contact Rice Lake Weighing Systems directly.')
 if 'installing-smartabaser' in slug:notices.append('Code caution: the original example includes install.packages(devtools) without quotes and df -> sb_get_event(...), which may not run as intended. The original instructions are retained for transparency; consult the current package documentation before use. No live AMS credentials or integration were tested.')
 if slug=='rice-lake-bluetooth-scale-integration-with-smartabase-emr':notices.append('The original claim that only one scale model integrates conflicts with the later physician-scales article. Verify current model compatibility with the manufacturers; the historical claim is preserved below.')
 if '/health-performance/' in record['url']:notices.append('Historical health information, not medical advice. Product comparisons, research citations, and claimed benefits have not been independently verified. In particular, older Fitbit studies do not directly validate the Inspire 3, and the red-light protocol should not be treated as an established clinical recommendation. Consult a qualified healthcare professional.')
 if any(m['url'].endswith('IMG_8709_480x480.png?v=1727055792') for m in missing) and 'fitbit' in slug:notices.append('One original image (IMG_8709) returns 404 at the source and could not be recovered. The remaining images are preserved locally.')
 (ROOT/'content/articles'/f'{slug}.html').write_text('\n'.join(line.rstrip() for line in body.decode_contents().splitlines()).strip()+'\n')
 article={'slug':slug,'path':urlsplit(record['url']).path,'title':title,'description':desc,'category':'data' if '/news/' in record['url'] else 'health','date':schema['datePublished'],'date_label':soup.select_one('time').get_text(strip=True),'author':schema.get('author',{}).get('name'),'image':card_image,'hero':hero,'headings':headings,'notices':notices,'source_sha256':record['sha256'],'original_word_count':len(original.split()),'migrated_word_count':len(body.get_text(' ',strip=True).split())}
 articles.append(article);edits.append({'path':article['path'],'changes':changes})
articles.sort(key=lambda x:x['date'],reverse=True)
(ROOT/'content/articles.json').write_text(json.dumps(articles,indent=2)+'\n')
(ROOT/'docs/content-edits.json').write_text(json.dumps(edits,indent=2)+'\n')
(ROOT/'docs/asset-inventory.json').write_text(json.dumps({'assets':assets,'missing':missing},indent=2)+'\n')
print('Migrated',len(articles),'articles;',len(assets),'assets;',len(missing),'missing images')
