#!/usr/bin/env python3
"""Local static preview with production-equivalent redirects and status codes."""
import argparse, json
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, unquote
ROOT=Path(__file__).resolve().parents[1]; DIST=ROOT/'dist'
ROUTES=json.loads((ROOT/'content/routes.json').read_text())
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(DIST),**kwargs)
 def send_head(self):
  path=unquote(urlsplit(self.path).path)
  for r in ROUTES:
   if r['status']==200:continue
   if path in {r['old_path'],r['old_path'].rstrip('/')+'/'} and path!=r['destination']:
    if r['status']==301:
     self.send_response(301);self.send_header('Location',r['destination']);self.send_header('Content-Length','0');self.end_headers();return None
    return self.error_document(410)
  file=(DIST/path.lstrip('/')).resolve()
  if not file.is_relative_to(DIST.resolve()):return self.error_document(404)
  if file.is_dir():file=file/'index.html'
  if not file.is_file():return self.error_document(404)
  stream=file.open('rb');self.send_response(200);self.send_header('Content-Type',self.guess_type(str(file)));self.send_header('Content-Length',str(file.stat().st_size));self.end_headers();return stream
 def error_document(self,code):
  file=DIST/f'{code}.html';self.send_response(code);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(file.stat().st_size));self.end_headers();return file.open('rb')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',type=int,default=8000);p.add_argument('--host',default='127.0.0.1');args=p.parse_args()
 print(f'Serving on {args.host}:{args.port}',flush=True)
 ThreadingHTTPServer((args.host,args.port),Handler).serve_forever()
