#!/usr/bin/env python3
"""Validate the built site and a running preview using only Python 3."""
import json, re
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlopen, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist';BASE='http://127.0.0.1:8000'
class Document(HTMLParser):
 def __init__(self,text):
  super().__init__();self.tags=[];self.feed(text)
 def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))
class NoRedirect(HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
opener=build_opener(NoRedirect)
def request(path):
 try:return opener.open(BASE+path)
 except HTTPError as e:return e
files=list(DIST.rglob('*.html'));titles=set();descriptions=set();links=set()
for file in files:
 text=file.read_text();doc=Document(text);tags=doc.tags
 assert len([t for t,a in tags if t=='h1'])==1,file
 title=re.search(r'<title>(.*?)</title>',text).group(1);assert title not in titles; titles.add(title)
 desc=next(a['content'] for t,a in tags if t=='meta' and a.get('name')=='description');assert desc and desc not in descriptions;descriptions.add(desc)
 assert any(a.get('rel')=='canonical' for t,a in tags if t=='link')
 assert any(a.get('property')=='og:image' for t,a in tags if t=='meta')
 for schema in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text):
  data=json.loads(schema);assert all(x['@type'] not in ['Product','Offer','AggregateRating'] for x in data)
 for tag,a in tags:
  if tag=='img':assert all(a.get(x) for x in ['src','alt','width','height']), (file,a)
  if tag in {'img','script','link'}:
   ref=a.get('src') or a.get('href','')
   if ref and not a.get('rel')=='canonical':assert ref.startswith('/'),(file,ref)
  if tag=='a' and a.get('href','').startswith('/'):
   links.add(a['href']);assert not re.match(r'^/(products|cart|checkout|account|collections)(/|$)',a['href']),file
  if a.get('src','').startswith('/'):assert (DIST/a['src'].lstrip('/')).is_file(),a
 assert 'cdn.shopify.com' not in text and '/cdn/shop/' not in text
 assert not any(t in {'iframe','form'} for t,a in tags)
 ids={a['id'] for t,a in tags if 'id' in a}
 for t,a in tags:
  if a.get('href','').startswith('#'):assert a['href'][1:] in ids,(file,a)
for ref in links:
 path=urlsplit(ref).path
 with request(path) as r:assert r.status==200,(path,r.status)
articles=json.loads((ROOT/'content/articles.json').read_text());assert len(articles)==9
assert len([a for a in articles if a['category']=='data'])==7
for a in articles:
 with request(a['path']) as response:
  text=response.read().decode(); content=(ROOT/'content/articles'/f'{a["slug"]}.html').read_text();assert content in text
routes=json.loads((ROOT/'content/routes.json').read_text())
for route in routes:
 with request(route['old_path']) as r:
  assert r.status==route['status'],(route,r.status)
  if r.status==301:assert r.headers['Location']==route['destination']
 with request(route['old_path']+'?test=1') as r:assert r.status==route['status']
with request('/does-not-exist') as r:assert r.status==404 and 'This page isn' in r.read().decode()
for loc in ET.parse(DIST/'sitemap.xml').findall('.//{*}loc'):
 with request(urlsplit(loc.text).path) as r:assert r.status==200
print(f'PASS: {len(files)} HTML pages, 9 full article bodies, {len(links)} internal links, {len(routes)} URL mappings, images, metadata, sitemap, 404/410, no store dependencies.')
