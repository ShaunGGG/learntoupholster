#!/usr/bin/env python3
"""
build-suppliers.py — the upholstery supplier directory.

Generates /suppliers from supplier-data.py. The list is static rather than
read from a database on every request: it changes a few times a year, so a
DB read per page view would be pure cost, and a static page is faster and
easier for an AI to cite.

Submissions go to D1 through /api/supplier-submit and are moderated. Nothing
appears here until it has been checked and added to supplier-data.py.

Run before build-md-extra.py and build-inline.py.
"""

import os, re, sys, html, datetime, importlib.util

SITE = 'https://www.learntoupholster.com'
OUT = 'suppliers.html'
CHROME_FROM = 'webbing.html'
OG = SITE + '/assets/og-card.jpg'
API = '/api/supplier-submit'


def icon_slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def load_data():
    if not os.path.exists('supplier-data.py'):
        sys.exit('supplier-data.py not found.')
    spec = importlib.util.spec_from_file_location('sd', 'supplier-data.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def get_chrome():
    if not os.path.exists(CHROME_FROM):
        sys.exit('Cannot find %s to use as the page template.' % CHROME_FROM)
    h = open(CHROME_FROM, encoding='utf-8').read()
    art = re.search(r'<article[^>]*>.*?</article>', h, re.S)
    if not art:
        sys.exit('No <article> in %s.' % CHROME_FROM)
    hdr = re.search(r'<header class="chapter-head">.*?</header>', h, re.S)
    tail = h[art.end():]
    links = ('<div class="related">\n'
             '    <a href="/business/"><span class="dir">Business Hub</span><br>'
             '<span class="ttl">Making a living from upholstery \u2192</span></a>\n'
             '    <a href="/tools"><span class="dir">Free tools</span><br>'
             '<span class="ttl">Calculators &amp; checkers \u2192</span></a>\n  </div>')
    tail = re.sub(r'<div class="related">.*?</div>', lambda _m: links, tail, count=1, flags=re.S)
    if hdr and hdr.end() <= art.start():
        return h[:hdr.start()], h[hdr.end():art.start()], tail
    return h[:art.start()], '', tail


def swap_head(head, title, desc, url):
    def sub(pat, val, s):
        return re.sub(pat, lambda m: m.group(1) + val + m.group(2), s, count=1)
    head = re.sub(r'<title>.*?</title>',
                  lambda _m: '<title>%s | Learn to Upholster</title>' % html.escape(title),
                  head, count=1, flags=re.S)
    for attr, val in (('name="description"', html.escape(desc)),
                      ('property="og:title"', html.escape(title)),
                      ('property="og:description"', html.escape(desc)),
                      ('property="og:url"', url),
                      ('property="og:image"', OG)):
        head = sub(r'(<meta\s+' + attr + r'\s+content=")(?:[^"]*)(")', val, head)
    head = sub(r'(<link\s+rel="canonical"\s+href=")(?:[^"]*)(")', url, head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', '', head, flags=re.S)
    return head


CSS = """<style>
.sup-filters{background:var(--cream-deep);border-radius:3px;padding:1rem 1.2rem;margin:1.4rem 0 1.8rem}
.sup-filters h2{font-family:var(--display);font-size:1.05rem;margin:0 0 .5rem;color:var(--green-deep)}
.sup-chips{display:flex;flex-wrap:wrap;gap:.4rem;margin:0 0 .7rem}
.sup-chip{background:#fff;border:1px solid var(--rule);border-radius:99px;padding:.32rem .8rem;
  font:inherit;font-size:.9rem;cursor:pointer;color:var(--ink)}
.sup-chip[aria-pressed="true"]{background:var(--green-deep);color:var(--cream);border-color:var(--green-deep)}
.sup-count{font-size:.9rem;margin:0}
.sup-list{list-style:none;padding:0;margin:0}
.sup-item{border-bottom:1px solid var(--rule);padding:1rem 0}
.sup-head{display:flex;gap:.8rem;align-items:flex-start}
.sup-headtext{flex:1;min-width:0}
.sup-icon{flex:0 0 auto;width:40px;height:40px;object-fit:contain;border:1px solid var(--rule);
  border-radius:4px;background:#fff;padding:3px;box-sizing:border-box}
.sup-icon-blank{display:block;background:var(--cream-deep)}
.sup-item h3{font-family:var(--display);font-size:1.12rem;margin:0 0 .2rem}
.sup-item h3 a{text-decoration:none}
.sup-meta{font-size:.86rem;margin:0 0 .35rem}
.sup-flag{display:inline-block;background:var(--cream-deep);border-radius:2px;padding:.1rem .45rem;margin-right:.4rem}
.sup-item p.note{margin:0 0 .35rem}
.sup-cats{font-size:.84rem}
.sup-cats span{display:inline-block;background:var(--cream-deep);border-radius:2px;
  padding:.1rem .45rem;margin:0 .3rem .3rem 0}
.sup-disclosure{background:var(--cream-deep);border-left:3px solid var(--terracotta);
  padding:.45rem .7rem;margin:0 0 .4rem;font-size:.9rem;border-radius:2px}
.sup-caveat{background:#fff;border:1px solid var(--rule);border-left:4px solid var(--gold);
  border-radius:3px;padding:1rem 1.2rem;margin:1.6rem 0}
.sup-specialists{margin:2.6rem 0 0;padding-top:1.6rem;border-top:2px solid var(--green-deep)}
.sup-specialists h2{font-family:var(--display);color:var(--green-deep);font-size:1.4rem;margin:0 0 .5rem}
.sup-crit{background:var(--cream-deep);border-left:3px solid var(--sage);padding:.6rem .9rem;
  border-radius:3px;font-size:.93rem}
.sup-form{background:var(--cream-deep);border-radius:3px;padding:1.2rem 1.4rem;margin:2rem 0 0}
.sup-form h2{font-family:var(--display);font-size:1.2rem;margin:0 0 .5rem;color:var(--green-deep)}
.sup-form .row{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:.8rem}
.sup-form label{display:block;font-size:.85rem;font-weight:600;color:var(--green-deep);margin-bottom:.2rem}
.sup-form input,.sup-form select,.sup-form textarea{width:100%;padding:.45rem .55rem;
  border:1px solid var(--rule);border-radius:3px;font:inherit;font-size:.95rem;background:#fff;
  box-sizing:border-box}
.sup-form textarea{min-height:4rem;resize:vertical}
.sup-full{grid-column:1/-1}
.sup-hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.sup-submit{background:var(--green-deep);color:var(--cream);border:0;border-radius:3px;
  padding:.6rem 1.3rem;font:inherit;font-weight:600;cursor:pointer;margin-top:.8rem}
.sup-submit:disabled{opacity:.55}
.sup-msg{margin:.8rem 0 0;padding:.7rem .9rem;border-radius:3px;display:none}
.sup-msg.ok{display:block;background:#fff;border-left:4px solid var(--sage)}
.sup-msg.err{display:block;background:#fff;border-left:4px solid var(--terracotta)}
@media print{.sup-filters,.sup-form,.sup-chip{display:none}}
</style>"""



def specialists_block(data):
    """A separate list, deliberately. These workshops do not sell materials."""
    items = getattr(data, 'SPECIALISTS', [])
    if not items:
        return ''
    rows = []
    for x in sorted(items, key=lambda v: (v['country'], v['name'].lower())):
        icon = '/assets/supplier-icons/%s.png' % icon_slug(x['name'])
        img = ('<img class="sup-icon" src="%s" alt="" width="40" height="40" '
               'loading="lazy" decoding="async">' % icon) if os.path.exists(icon.lstrip('/')) \
              else '<span class="sup-icon sup-icon-blank" aria-hidden="true"></span>'
        rows.append(
            '<li class="sup-item" id="p-%s">\n'
            '  <div class="sup-head">%s<div class="sup-headtext">\n'
            '  <h3><a href="%s" target="_blank" rel="noopener nofollow">%s</a></h3>\n'
            '  <p class="sup-meta"><span class="sup-flag">%s</span>website verified %s</p>\n'
            '  </div></div>\n  <p class="note">%s</p>\n</li>'
            % (icon_slug(x['name']), img, x['url'], html.escape(x['name']),
               html.escape(data.COUNTRIES.get(x['country'], x['country'])),
               data.VERIFIED, html.escape(x['note'])))
    return (
        '<div class="sup-specialists" id="specialists">\n'
        '  <h2>Heritage &amp; conservation specialists</h2>\n'
        '  <p>These workshops do not sell materials \u2014 they take commissions. '
        'Listed because upholsterers are regularly asked who can be trusted with a piece '
        'that genuinely matters, and there is nowhere to look it up.</p>\n'
        '  <p class="sup-crit"><strong>How something gets on this list:</strong> '
        'museum, heritage or public-collection work that can be verified from public '
        'record. Nobody pays, nobody is here on their own say-so, and this is not a '
        'general list of upholsterers.</p>\n'
        '  <ul class="sup-list">%s</ul>\n</div>' % ''.join(rows))


def render(data):
    by_country = {}
    for s in data.SUPPLIERS:
        by_country.setdefault(s['country'], []).append(s)

    order = [c for c in ('GB', 'US', 'CA', 'AU', 'NZ') if c in by_country]
    order += sorted(c for c in by_country if c not in order)

    chips = ['<button class="sup-chip" data-f="country" data-v="all" aria-pressed="true">'
             'All countries</button>']
    for c in order:
        chips.append('<button class="sup-chip" data-f="country" data-v="%s" aria-pressed="false">'
                     '%s (%d)</button>' % (c, html.escape(data.COUNTRIES.get(c, c)), len(by_country[c])))

    cat_chips = ['<button class="sup-chip" data-f="cat" data-v="all" aria-pressed="true">'
                 'Everything</button>']
    for key, label, _d in data.CATEGORIES:
        n = sum(1 for s in data.SUPPLIERS if key in s['cats'])
        cat_chips.append('<button class="sup-chip" data-f="cat" data-v="%s" aria-pressed="false">'
                         '%s (%d)</button>' % (key, html.escape(label), n))

    catname = {k: l for k, l, _ in data.CATEGORIES}
    items = []
    for c in order:
        for s in sorted(by_country[c], key=lambda x: x['name'].lower()):
            cats = ''.join('<span>%s</span>' % html.escape(catname.get(k, k)) for k in s['cats'])
            blocked = ('' if s['status'] == 'live' else
                       ' \u00b7 site blocks automated checks, verified by hand')
            disc = ('<p class="sup-disclosure"><strong>Declared interest:</strong> %s</p>'
                    % html.escape(s['disclosure'])) if s.get('disclosure') else ''
            icon = '/assets/supplier-icons/%s.png' % icon_slug(s['name'])
            has_icon = os.path.exists(icon.lstrip('/'))
            img = ('<img class="sup-icon" src="%s" alt="" width="40" height="40" '
                   'loading="lazy" decoding="async">' % icon) if has_icon else \
                  '<span class="sup-icon sup-icon-blank" aria-hidden="true"></span>'
            items.append(
                '<li class="sup-item" id="s-%s" data-country="%s" data-cats="%s">\n'
                '  <div class="sup-head">%s<div class="sup-headtext">\n'
                '  <h3><a href="%s" target="_blank" rel="noopener nofollow">%s</a></h3>\n'
                '  <p class="sup-meta"><span class="sup-flag">%s</span>'
                'website verified %s%s</p>\n'
                '  </div></div>\n'
                '  <p class="note">%s</p>\n'
                '  %s\n'
                '  <p class="sup-cats">%s</p>\n</li>'
                % (icon_slug(s['name']), s['country'], ' '.join(s['cats']), img,
                   s['url'], html.escape(s['name']),
                   html.escape(data.COUNTRIES.get(s['country'], s['country'])),
                   data.VERIFIED, blocked, html.escape(s['note']), disc, cats))

    country_opts = ''.join('<option value="%s">%s</option>' % (k, html.escape(v))
                           for k, v in data.COUNTRIES.items())
    cat_checks = ''.join(
        '<label style="font-weight:400;display:flex;gap:.35rem;align-items:center">'
        '<input type="checkbox" name="cat" value="%s" style="width:auto"> %s</label>'
        % (k, html.escape(l)) for k, l, _ in data.CATEGORIES)

    return '\n'.join(chips), '\n'.join(cat_chips), '\n'.join(items), country_opts, cat_checks, len(data.SUPPLIERS), len(order)


JS = """<script>
(function(){
  var state={country:'all',cat:'all'};
  var items=[].slice.call(document.querySelectorAll('.sup-item'));
  var count=document.getElementById('supCount');
  function apply(){
    var n=0;
    items.forEach(function(li){
      var okC = state.country==='all' || li.getAttribute('data-country')===state.country;
      var okK = state.cat==='all' || (' '+li.getAttribute('data-cats')+' ').indexOf(' '+state.cat+' ')>-1;
      var show = okC && okK;
      li.style.display = show ? '' : 'none';
      if(show) n++;
    });
    if(count) count.textContent = n + (n===1?' supplier':' suppliers') + ' shown';
  }
  [].slice.call(document.querySelectorAll('.sup-chip')).forEach(function(b){
    b.addEventListener('click',function(){
      var f=b.getAttribute('data-f');
      state[f]=b.getAttribute('data-v');
      [].slice.call(document.querySelectorAll('.sup-chip[data-f="'+f+'"]')).forEach(function(o){
        o.setAttribute('aria-pressed', o===b ? 'true':'false');
      });
      apply();
    });
  });
  apply();

  var f=document.getElementById('supForm');
  if(!f) return;
  var btn=document.getElementById('supBtn'), msg=document.getElementById('supMsg');
  f.addEventListener('submit',function(e){
    e.preventDefault();
    var d={cats:[]}, ok=true;
    [].slice.call(f.elements).forEach(function(el){
      if(!el.name) return;
      if(el.type==='checkbox'){ if(el.checked) d.cats.push(el.value); return; }
      var v=(el.value||'').trim();
      if(el.hasAttribute('required') && !v){ ok=false; el.style.borderColor='#B5552D'; }
      else if(el.style){ el.style.borderColor=''; }
      if(v) d[el.name]=v;
    });
    if(!ok){ msg.className='sup-msg err'; msg.textContent='Name, website and country are needed.'; return; }
    btn.disabled=true; btn.textContent='Sending\\u2026';
    fetch('%API%',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)})
      .then(function(r){return r.json();})
      .then(function(j){
        if(j.error){ msg.className='sup-msg err'; msg.textContent=j.error;
          btn.disabled=false; btn.textContent='Send it in'; return; }
        f.style.display='none'; msg.className='sup-msg ok';
        msg.innerHTML='<strong>Thank you.</strong> I check every submission before it goes on the '+
          'list, so it will not appear straight away.';
      })
      .catch(function(){ msg.className='sup-msg err';
        msg.textContent='That did not send. Please try again shortly.';
        btn.disabled=false; btn.textContent='Send it in'; });
  });
})();
</script>""".replace('%API%', API)


def schema(data, n):
    esc = lambda t: (t or '').replace('\\', '\\\\').replace('"', '\\"')
    items = []
    for i, s in enumerate(data.SUPPLIERS, 1):
        items.append('{"@type":"ListItem","position":%d,"item":{"@type":"Organization",'
                     '"name":"%s","url":"%s"}}' % (i, esc(s['name']), s['url']))
    return ('<script type="application/ld+json">\n'
            '{"@context":"https://schema.org","@graph":['
            '{"@type":"CollectionPage","@id":"%s/suppliers#page","name":"Upholstery supplier directory",'
            '"url":"%s/suppliers","inLanguage":"en",'
            '"description":"Verified suppliers of upholstery materials in the UK, US, Canada, '
            'Australia and New Zealand \\u2014 traditional materials, foam, fabric, tools and sundries.",'
            '"author":{"@type":"Person","@id":"%s/about#shaun","name":"Shaun Greenwood"},'
            '"publisher":{"@type":"Organization","@id":"%s#org","name":"Learn to Upholster"},'
            '"mainEntity":{"@type":"ItemList","numberOfItems":%d,"itemListElement":[%s]}},'
            '{"@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
            '{"@type":"ListItem","position":2,"name":"Suppliers","item":"%s/suppliers"}]}]}\n'
            '</script>' % (SITE, SITE, SITE, SITE, n, ','.join(items), SITE, SITE))


def main():
    data = load_data()
    pre, mid, tail = get_chrome()
    chips, cat_chips, items, country_opts, cat_checks, n, ncountry = render(data)
    today = datetime.date.today()

    body = (
        '<article class="article wrap read">\n'
        '  <p class="lede">Where to buy upholstery materials, by country. %d suppliers across %d '
        'countries \u2014 traditional materials, foam, fabric, tools, sundries, and the fabric '
        'houses themselves. Free to use, and nobody pays to be listed.</p>\n\n'
        '  <div class="sup-caveat">\n'
        '    <p><strong>How this list is checked.</strong> Every website here was fetched and read on '
        '%s. That confirms the site was live and trading-looking on that date \u2014 it is not a '
        'statement about whether a company is solvent, which nobody can check from outside. '
        'The list is re-checked every six months.</p>\n'
        '    <p>No supplier has paid to appear and there are no affiliate links on this page. '
        'One listing is a business I run myself; it says so on the entry. '
        'If a listing is wrong or a supplier has closed, '
        '<a href="/contact">tell me</a> and I will fix it.</p>\n'
        '  </div>\n\n'
        '  <div class="sup-filters">\n'
        '    <h2>Country</h2>\n    <div class="sup-chips">%s</div>\n'
        '    <h2>What they supply</h2>\n    <div class="sup-chips">%s</div>\n'
        '    <p class="sup-count" id="supCount">%d suppliers shown</p>\n'
        '  </div>\n\n'
        '  <ul class="sup-list">\n%s\n  </ul>\n\n'
        '  %s\n\n'
        '  <div class="sup-form">\n'
        '    <h2>Know one that should be here?</h2>\n'
        '    <p>Suppliers you actually use are worth more than anything I could find by searching. '
        'Anywhere in the world \u2014 the list is thin outside the countries above and I would '
        'particularly like Ireland, South Africa and mainland Europe.</p>\n'
        '    <form id="supForm" novalidate>\n'
        '      <div class="sup-hp" aria-hidden="true"><label>Leave empty'
        '<input type="text" name="website_confirm" tabindex="-1" autocomplete="off"></label></div>\n'
        '      <div class="row">\n'
        '        <div><label for="s_name">Supplier name *</label>'
        '<input id="s_name" name="name" type="text" required></div>\n'
        '        <div><label for="s_url">Website *</label>'
        '<input id="s_url" name="url" type="url" placeholder="https://" required></div>\n'
        '        <div><label for="s_country">Country *</label>'
        '<select id="s_country" name="country" required>'
        '<option value="">\u2014 choose \u2014</option>%s</select></div>\n'
        '        <div class="sup-full"><label>What do they supply?</label>'
        '<div style="display:flex;flex-wrap:wrap;gap:.4rem 1.1rem;margin-top:.2rem">%s</div></div>\n'
        '        <div class="sup-full"><label for="s_note">Anything worth knowing</label>'
        '<textarea id="s_note" name="note" placeholder="Trade account needed? Minimum order? '
        'Do they ship abroad? What are they especially good for?"></textarea></div>\n'
        '      </div>\n'
        '      <button type="submit" class="sup-submit" id="supBtn">Send it in</button>\n'
        '      <div class="sup-msg" id="supMsg" role="status"></div>\n'
        '    </form>\n'
        '  </div>\n'
        '</article>' % (n, ncountry, data.VERIFIED, chips, cat_chips, n, items,
                        specialists_block(data), country_opts, cat_checks))

    desc = ('Verified upholstery suppliers in the UK, US, Canada, Australia and New Zealand: '
            'traditional materials, foam, fabric, tools and sundries. Nobody pays to be listed.')
    page = swap_head(pre, 'Upholstery supplier directory', desc, SITE + '/suppliers')
    page = page.replace('</head>', CSS + '\n' + schema(data, n) + '\n</head>', 1)
    page += ('<header class="chapter-head">\n  <div class="wrap">\n'
             '    <p class="chno">Free resource</p>\n    <h1>Upholstery supplier directory</h1>\n'
             '    <p class="updated">Last updated: <time datetime="%s">%s</time></p>\n'
             '  </div>\n</header>' % (today.isoformat(), today.strftime('%-d %B %Y')))

    open(OUT, 'w', encoding='utf-8').write(page + mid + body + JS + tail)
    print('%s written \u2014 %d suppliers across %d countries' % (OUT, n, ncountry))
    for c in ('GB', 'US', 'CA', 'AU', 'NZ'):
        k = sum(1 for s in data.SUPPLIERS if s['country'] == c)
        if k:
            print('   %-4s %d' % (c, k))


if __name__ == '__main__':
    main()
