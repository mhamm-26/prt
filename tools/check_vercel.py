"""Regression checks for the Vercel output directory and URL routing contract."""
import json, re
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from vercel_config import configuration
ROOT = Path(__file__).resolve().parents[1]
config = json.loads((ROOT/'vercel.json').read_text())
migrations = json.loads((ROOT/'content/routes.json').read_text())
pages = [urlsplit(e.text).path for e in ET.parse(ROOT/'dist/sitemap.xml').findall('.//{*}loc')]
assert config == configuration(pages, migrations), 'Stale vercel.json; rebuild and commit it'
assert config['buildCommand'] == 'python3 tools/build.py'
assert config['outputDirectory'] == 'dist'
assert (ROOT/'dist/index.html').is_file()
for rule in config['routes']:
    if 'dest' in rule:
        assert (ROOT/'dist'/rule['dest'].lstrip('/')).is_file(), rule

def resolve(url):
    path = urlsplit(url).path
    for rule in config['routes']:
        if rule.get('handle') == 'filesystem':
            if (ROOT/'dist'/path.lstrip('/')).is_file():
                return 200, path
        elif re.search(rule['src'], path):
            return rule.get('status', 200), rule.get('headers', {}).get('Location', rule.get('dest'))
    raise AssertionError(url)

for path in pages:
    status, destination = resolve(path)
    assert status == 200 and destination.endswith('index.html'), (path,status,destination)
for row in migrations:
    for suffix in ['', '?page=2']:
        status, destination = resolve(row['old_path'] + suffix)
        assert status == row['status'], (row,status)
        if status == 301:
            assert destination == row['destination']
            assert resolve(destination)[0] == 200, 'Redirect loop or missing destination'
        elif status == 410:
            assert destination == '/410.html'
assert resolve('/missing-page') == (404, '/404.html')
assert resolve('/assets/site.css') == (200, '/assets/site.css')
print(f'PASS: Vercel build output, {len(pages)} pages, {len(migrations)} migrations, assets and custom 404/410 routes')
