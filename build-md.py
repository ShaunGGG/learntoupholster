#!/usr/bin/env python3
"""Generate clean markdown variants of every page into /md/<slug>.md.
Run after content changes:  python3 build-md.py   (then deploy)
"""
import glob, re, os
from lxml import html

EXCL = {'tools', 'related', 'capture'}
SKIP = {'404.html', 'search.html'}
BASE = 'https://www.learntoupholster.com'

def excluded(el):
    a = el
    while a is not None:
        c = a.get('class') or ''
        if any(x in c.split() for x in EXCL): return True
        a = a.getparent()
    return False

def text_of(el):
    parts = []
    for node in el.iter():
        if node.tag == 'a' and node.get('href'):
            href = node.get('href')
            if href.startswith('/'): href = BASE + href
            label = re.sub(r'\s+', ' ', ''.join(node.itertext())).strip()
            if label: parts.append(f'[{label}]({href})')
            if node.tail: parts.append(node.tail)
        elif node.text and (node.getparent() is None or node.getparent().tag != 'a'):
            parts.append(node.text)
            if node is not el and node.tail: parts.append(node.tail)
    s = ''.join(p for p in parts if p)
    return re.sub(r'\s+', ' ', s).strip()

os.makedirs('md', exist_ok=True)
n = 0
for f in sorted(glob.glob('*.html')):
    if f in SKIP: continue
    t = html.parse(f)
    title = (t.xpath('//h1/text()') or [f])[0].strip()
    desc = (t.xpath('//meta[@name="description"]/@content') or [''])[0].strip()
    chno = (t.xpath('//p[@class="chno"]/text()') or [''])[0].strip()
    slug = 'index' if f == 'index.html' else f[:-5]
    body = t.xpath('//article') or t.xpath('//section[@class="wrap"]')
    out = [f'# {title}', '']
    if chno: out += [f'*{chno}*', '']
    if desc: out += [f'> {desc}', '']
    out += [f'Canonical: {BASE}/' + ('' if slug == 'index' else slug), '']
    if body:
        for el in body[0].iter():
            if not isinstance(el.tag, str) or excluded(el): continue
            if el.tag == 'h2': out += ['## ' + re.sub(r'\s+', ' ', ''.join(el.itertext())).strip(), '']
            elif el.tag == 'h3': out += ['### ' + re.sub(r'\s+', ' ', ''.join(el.itertext())).strip(), '']
            elif el.tag == 'p':
                s = text_of(el).replace('(paid link)', '').strip()
                if s: out += [s, '']
            elif el.tag == 'li':
                s = text_of(el).replace('(paid link)', '').strip()
                if s: out.append('- ' + s)
            elif el.tag == 'figcaption':
                s = text_of(el)
                if s: out += ['*Figure: ' + s + '*', '']
            elif el.tag == 'table':
                rows = []
                for tr in el.xpath('.//tr'):
                    cells = [re.sub(r'\s+', ' ', ''.join(td.itertext())).strip() for td in tr.xpath('./th|./td')]
                    rows.append('| ' + ' | '.join(cells) + ' |')
                if rows:
                    rows.insert(1, '|' + '---|' * (rows[0].count('|') - 1))
                    out += rows + ['']
    out += ['', '---', f'By Shaun Greenwood, master upholsterer (AMUSF accredited). Part of The Working Upholsterer\u2019s Bible, free at {BASE}/']
    open(f'md/{slug}.md', 'w').write('\n'.join(out) + '\n')
    n += 1
print(f'{n} markdown variants written to md/')
