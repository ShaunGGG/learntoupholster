#!/usr/bin/env python3
"""Rebuild ask-index.json from the site's HTML. Run after adding or editing chapters:
    python3 build-ask-index.py
Requires: pip install lxml
"""
import glob, json, re
from lxml import html

SKIP={'search.html','index.html','privacy-policy.html','cookie-policy.html','terms-of-use.html','disclaimer.html','contents.html','contact.html','our-work.html','find-an-upholsterer.html','about.html'}
EXCL={'tools','related','capture'}

def excluded(el):
    a=el
    while a is not None:
        c=a.get('class') or ''
        if any(x in c.split() for x in EXCL): return True
        a=a.getparent()
    return False

chunks=[]
for f in sorted(glob.glob('*.html')):
    if f in SKIP: continue
    t=html.parse(f)
    title=(t.xpath('//h1/text()') or [f])[0].strip()
    url='/'+f[:-5]
    body=t.xpath('//article') or t.xpath('//section[@class="wrap"]')
    if not body: continue
    cur_head='Overview'; cur=[]
    def flush():
        global cur
        txt=re.sub(r'\s+',' ',' '.join(cur)).strip().replace('(paid link)','')
        if len(txt)>80:
            while len(txt)>2000:
                cut=txt.rfind('. ',800,2000); cut=cut+1 if cut>0 else 2000
                chunks.append({'u':url,'t':title,'h':cur_head,'x':txt[:cut].strip()}); txt=txt[cut:].strip()
            chunks.append({'u':url,'t':title,'h':cur_head,'x':txt})
        cur=[]
    for el in body[0].iter():
        if not isinstance(el.tag,str): continue
        if el.tag=='h2':
            if not excluded(el): flush(); cur_head=re.sub(r'\s+',' ',''.join(el.itertext())).strip()
        elif el.tag in ('p','li','h3','h4','figcaption','dt','dd','summary'):
            if excluded(el): continue
            s=re.sub(r'\s+',' ',''.join(el.itertext())).strip()
            if s: cur.append(s)
    flush()

seen=set(); dedup=[]
for c in chunks:
    k=c['x'][:120]
    if k in seen: continue
    seen.add(k); dedup.append(c)
json.dump(dedup,open('ask-index.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(dedup),'chunks written to ask-index.json')
