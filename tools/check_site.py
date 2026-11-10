#!/usr/bin/env python3
"""Check every static page, local asset, fragment and deployment-relative URL."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'tools','.git','node_modules','artifacts','.openai'}
pages=sorted(p for p in ROOT.rglob('*.html') if not EXCLUDED.intersection(p.relative_to(ROOT).parts))
errors=[]
links=0

class Document(HTMLParser):
    def __init__(self,path):
        super().__init__(convert_charrefs=True)
        self.path=path
        self.ids=set()
        self.urls=[]
        self.headings=0
        self.language=None
        self.has_title=False
        self.has_viewport=False
        self.has_main=False
        self.has_home=False
        self.has_style=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            if a['id'] in self.ids: errors.append(f'{self.path}: duplicate id {a["id"]}')
            self.ids.add(a['id'])
        if tag=='html': self.language=a.get('lang')
        if tag=='title': self.has_title=True
        if tag=='h1': self.headings+=1
        if tag=='main': self.has_main=True
        if tag=='meta' and a.get('name')=='viewport': self.has_viewport=True
        if tag=='link' and a.get('rel')=='stylesheet': self.has_style=True
        if tag=='img' and not a.get('alt'): errors.append(f'{self.path}: missing image alt')
        for attr in ['href','src','poster']:
            if attr in a: self.urls.append(a[attr])

docs={}
for path in pages:
    doc=Document(path.relative_to(ROOT))
    doc.feed(path.read_text(encoding='utf-8'))
    docs[path]=doc
    if doc.language!='ru' or not all([doc.has_title,doc.has_viewport,doc.has_main,doc.has_style]) or doc.headings!=1:
        errors.append(f'{doc.path}: missing metadata, stylesheet or exactly one h1')
for path,doc in docs.items():
    for url in doc.urls:
        parsed=urlsplit(url)
        if parsed.scheme in {'https','http','mailto','tel','data'}: continue
        links+=1
        if url.startswith('/'):
            errors.append(f'{doc.path}: root-relative URL {url}')
            continue
        target=(path.parent/unquote(parsed.path)).resolve() if parsed.path else path
        if target.is_dir(): target/='index.html'
        if not target.is_relative_to(ROOT) or not target.is_file(): errors.append(f'{doc.path}: missing resource {url}')
        elif parsed.fragment and target in docs and parsed.fragment not in docs[target].ids: errors.append(f'{doc.path}: missing fragment {url}')
        if target==ROOT/'index.html': doc.has_home=True
    if not doc.has_home: errors.append(f'{doc.path}: no link back to home')
css=(ROOT/'style.css').read_text()
for url in re.findall(r'url\([\'\"]?([^\)\'\"]+)',css):
    if not urlsplit(url).scheme and not (ROOT/url).is_file(): errors.append(f'CSS missing asset: {url}')
search=json.loads((ROOT/'search-index.json').read_text())
if len(search)!=len(pages) or {p['path'] for p in search}!={str(p.relative_to(ROOT)) for p in pages}: errors.append('Search index does not match HTML pages')
assert len(pages)==15,f'Expected 15 HTML pages, found {len(pages)}'
if errors: raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} HTML pages, {links} internal URLs, all assets and fragments present; relative URLs only.')
