#!/usr/bin/env python3
"""
build-sewing-selector.py — the thread and needle selector.

Three questions, one answer: fibre, thread size, needle size, point type and
stitch length, with the reasoning for each.

The logic is deterministic and runs in the browser \u2014 no API call, nothing to
go wrong, works offline once loaded. Same pattern as the fire regulations
checker.

Everything it returns comes from sewing-data.py, so the selector and the guide
pages can never disagree with each other.

Run after build-sewing.py, before build-inline.py.
"""

import os, re, sys, html, json, datetime, importlib.util

SITE = 'https://www.learntoupholster.com'
OUT = 'sewing-selector.html'
CHROME_FROM = 'webbing.html'
OG = SITE + '/assets/og-card.jpg'


def load():
    spec = importlib.util.spec_from_file_location('sd', 'sewing-data.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def get_chrome():
    if not os.path.exists(CHROME_FROM):
        sys.exit('Cannot find %s.' % CHROME_FROM)
    h = open(CHROME_FROM, encoding='utf-8').read()
    art = re.search(r'<article[^>]*>.*?</article>', h, re.S)
    hdr = re.search(r'<header class="chapter-head">.*?</header>', h, re.S)
    tail = h[art.end():]
    links = ('<div class="related">\n'
             '    <a href="/sewing-thread"><span class="dir">Sewing</span><br>'
             '<span class="ttl">The thread guide \u2192</span></a>\n'
             '    <a href="/sewing-needles"><span class="dir">Sewing</span><br>'
             '<span class="ttl">The needle guide \u2192</span></a>\n  </div>')
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
.sel-q{background:#fff;border:1px solid var(--rule);border-radius:3px;padding:1.05rem 1.25rem;margin:0 0 .9rem}
.sel-q h2{font-family:var(--display);font-size:1.12rem;margin:0 0 .25rem;color:var(--green-deep)}
.sel-q p.hint{font-size:.91rem;margin:0 0 .7rem}
.sel-opts{display:flex;flex-wrap:wrap;gap:.5rem}
.sel-opt{background:#fff;border:1px solid var(--rule);border-radius:3px;padding:.5rem .9rem;
  font:inherit;font-size:.95rem;cursor:pointer;color:var(--ink)}
.sel-opt[aria-pressed="true"]{background:var(--green-deep);color:var(--cream);border-color:var(--green-deep)}
.sel-out{background:var(--cream-deep);border-left:4px solid var(--gold);border-radius:3px;
  padding:1.1rem 1.3rem;margin:1.5rem 0 0;display:none}
.sel-out.show{display:block}
.sel-out h2{font-family:var(--display);font-size:1.25rem;margin:0 0 .8rem;color:var(--green-deep)}
.sel-spec{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.8rem;margin:0 0 1rem}
.sel-cell{background:#fff;border-radius:3px;padding:.7rem .85rem}
.sel-cell .lab{font-size:.78rem;text-transform:uppercase;letter-spacing:.03em;
  color:var(--green-deep);font-weight:600}
.sel-cell .val{font-family:var(--display);font-size:1.12rem;margin-top:.15rem}
.sel-cell .sub{font-size:.85rem;margin-top:.1rem}
.sel-why{margin:0 0 .8rem}
.sel-why h3{font-family:var(--display);font-size:1rem;margin:.8rem 0 .15rem;color:var(--green-deep)}
.sel-why p{margin:0;font-size:.96rem}
.sel-reset{background:none;border:0;color:var(--green-deep);text-decoration:underline;
  cursor:pointer;font:inherit;font-size:.92rem;padding:0}
@media print{.sel-opts,.sel-reset,.sel-q p.hint{display:none}.sel-out{display:block}}
</style>"""


QUESTIONS = [
    ('material', 'What are you sewing?',
     'This decides the needle point and, less obviously, the stitch length.',
     [('woven', 'Woven cloth'), ('vinyl', 'Vinyl or faux leather'), ('leather', 'Leather')]),
    ('where', 'Where will the finished piece live?',
     'Ultraviolet light is what decides nylon or polyester, and it is the choice people '
     'most often get wrong.',
     [('indoors', 'Indoors'), ('vehicle', 'Vehicle or campervan interior'),
      ('outdoors', 'Outdoors, marine, or strong sunlight')]),
    ('seam', 'What kind of seam?',
     'A seam that is meant to be seen is specified differently from one that holds the '
     'piece together.',
     [('construction', 'Construction \u2014 holding it together'),
      ('topstitch', 'Visible top stitching')]),
]


def build_js(d):
    sizes = {s['tex']: dict(commercial=s['commercial'], ticket=s['ticket'],
                            needle=s['needle'], common=s['common']) for s in d.THREAD_SIZES}
    data = dict(sizes=sizes,
                stitch={k: dict(spi=v['spi'], mm=v['mm'], why=v['why'])
                        for k, v in d.STITCH.items()},
                topstitch=dict(spi=d.STITCH_TOPSTITCH['spi'], mm=d.STITCH_TOPSTITCH['mm'],
                               why=d.STITCH_TOPSTITCH['why']),
                point={k: dict(name=v[0], why=v[1]) for k, v in d.POINT.items()})
    return """<script>
(function(){
  var D = %s;
  var state = {};
  var out = document.getElementById('selOut');

  function pick(material, where, seam){
    // Fibre. UV is the deciding property, and the one most often got wrong.
    var fibre, fibreWhy;
    if (where === 'outdoors'){
      fibre = 'Bonded polyester';
      fibreWhy = 'Sunlight is what will kill this seam, not wear. Nylon is marginally '+
        'stronger and more abrasion resistant, but it degrades in ultraviolet light and '+
        'polyester does not. Outdoors that is the only property that matters.';
    } else if (where === 'vehicle'){
      fibre = 'Bonded polyester';
      fibreWhy = 'A vehicle interior sits behind glass in the sun for years, and a campervan '+
        'more than most. Bonded nylon is a reasonable choice for a car that lives in a garage '+
        'and is valued for abrasion resistance, but polyester is the safer default here.';
    } else {
      fibre = 'Bonded nylon or polyester';
      fibreWhy = 'Indoors either will serve. Nylon has slightly higher tensile strength and '+
        'better abrasion resistance; polyester copes better with cleaning products. Use '+
        'whichever your supplier stocks in the colour you need.';
    }

    // Thread size.
    var tex, texWhy;
    if (seam === 'topstitch'){
      tex = (material === 'leather') ? 'T210' : 'T135';
      texWhy = 'Top stitching has to read as a deliberate line rather than a seam, which '+
        'means a heavier thread than the construction seams around it.' +
        (material === 'leather' ? ' On leather you can carry the extra weight of T210.' : '');
    } else if (material === 'woven'){
      tex = (where === 'outdoors') ? 'T90' : 'T70';
      texWhy = (where === 'outdoors')
        ? 'A step up from the usual furniture size, because outdoor work takes more punishment.'
        : 'The everyday upholstery size. Strong enough for any domestic seam without the '+
          'stitching becoming a feature, and the heaviest a domestic machine will manage.';
    } else {
      tex = 'T90';
      texWhy = 'Vinyl and leather are heavier materials under more load at the seam than '+
        'woven cloth, and T90 is the usual working size for both.';
    }

    var sz = D.sizes[tex] || {};
    // A visible top stitch is set longer whatever the material.
    var st = (seam === 'topstitch') ? D.topstitch : D.stitch[material];
    var pt = D.point[material];

    var h = '<h2>Your specification</h2>';
    h += '<div class="sel-spec">';
    h += cell('Thread', fibre, tex + ' \\u00b7 ' + (sz.commercial||'') + ' \\u00b7 ' + (sz.ticket||''));
    h += cell('Needle', sz.common || '', 'workable range ' + (sz.needle||''));
    h += cell('Point', pt.name, '');
    h += cell('Stitch length', st.mm, st.spi + ' stitches per inch');
    h += '</div>';

    h += '<div class="sel-why">';
    h += '<h3>Why this thread</h3><p>'+fibreWhy+'</p>';
    h += '<h3>Why this size</h3><p>'+texWhy+'</p>';
    h += '<h3>Why this point</h3><p>'+pt.why+'</p>';
    h += '<h3>Why this stitch length</h3><p>'+st.why+'</p>';
    h += '</div>';

    h += '<p style="font-size:.93rem;margin:0"><strong>Test it on an offcut of the actual '+
      'material before you commit on a customer\\u2019s job.</strong> These are sound starting '+
      'points, not a substitute for a trial seam \\u2014 and if your thread supplier publishes '+
      'a chart for their own product, theirs beats this one.</p>';
    return h;
  }

  function cell(lab, val, sub){
    return '<div class="sel-cell"><div class="lab">'+lab+'</div>'+
           '<div class="val">'+val+'</div>'+
           (sub ? '<div class="sub">'+sub+'</div>' : '')+'</div>';
  }

  function render(){
    if(!state.material || !state.where || !state.seam){ out.className='sel-out'; return; }
    out.innerHTML = pick(state.material, state.where, state.seam);
    out.className = 'sel-out show';
  }

  document.querySelectorAll('.sel-opt').forEach(function(b){
    b.addEventListener('click', function(){
      var q = b.getAttribute('data-q');
      state[q] = b.getAttribute('data-v');
      document.querySelectorAll('.sel-opt[data-q="'+q+'"]').forEach(function(o){
        o.setAttribute('aria-pressed', o===b ? 'true' : 'false');
      });
      render();
    });
  });
  var r = document.getElementById('selReset');
  if(r) r.addEventListener('click', function(){
    state = {};
    document.querySelectorAll('.sel-opt').forEach(function(o){o.setAttribute('aria-pressed','false');});
    out.className='sel-out'; out.innerHTML='';
  });
})();
</script>""" % json.dumps(data)


def schema(url):
    return ('<script type="application/ld+json">\n'
            '{"@context":"https://schema.org","@graph":['
            '{"@type":"WebApplication","@id":"%s#app","name":"Upholstery thread and needle selector",'
            '"applicationCategory":"UtilityApplication","operatingSystem":"Any","url":"%s",'
            '"description":"Three questions returning thread fibre, size, needle, point type and '
            'stitch length for an upholstery job.","isAccessibleForFree":true,'
            '"offers":{"@type":"Offer","price":"0","priceCurrency":"GBP"},'
            '"author":{"@id":"%s/about#shaun"},"publisher":{"@id":"%s#org"}},'
            '{"@type":"FAQPage","@id":"%s#faq","mainEntity":['
            '{"@type":"Question","name":"What stitch length should I use on leather or vinyl?",'
            '"acceptedAnswer":{"@type":"Answer","text":"Longer than you would use on cloth: '
            'roughly 6 to 8 stitches per inch, which is 3.2 to 4.2 mm. Every stitch in leather or '
            'vinyl is a permanent hole, and crowding them perforates the material along a line so '
            'the seam tears like a stamp edge. This is the opposite of woven cloth, where more '
            'stitches make a stronger seam because the thread passes between the yarns."}},'
            '{"@type":"Question","name":"Does a shorter stitch make a stronger seam?",'
            '"acceptedAnswer":{"@type":"Answer","text":"On woven fabric, yes. A&amp;E express the '
            'relationship as seam strength = stitches per inch \\u00d7 thread strength \\u00d7 1.5. '
            'On leather and vinyl the opposite is true, because the material is weakened by every '
            'hole rather than strengthened by every stitch."}}]},'
            '{"@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
            '{"@type":"ListItem","position":2,"name":"Sewing","item":"%s/sewing"},'
            '{"@type":"ListItem","position":3,"name":"Selector","item":"%s"}]}]}\n</script>'
            % (url, url, SITE, SITE, url, SITE, SITE, url))


def main():
    if not os.path.exists('sewing-data.py'):
        sys.exit('sewing-data.py not found. Run this from ~/learntoupholster.')
    d = load()
    pre, mid, tail = get_chrome()
    url = SITE + '/sewing-selector'

    qs = []
    for key, title, hint, opts in QUESTIONS:
        buttons = ''.join(
            '<button class="sel-opt" data-q="%s" data-v="%s" aria-pressed="false" type="button">%s</button>'
            % (key, v, html.escape(l)) for v, l in opts)
        qs.append('<div class="sel-q">\n  <h2>%s</h2>\n  <p class="hint">%s</p>\n'
                  '  <div class="sel-opts">%s</div>\n</div>'
                  % (html.escape(title), html.escape(hint), buttons))

    body = (
        '<article class="article wrap read">\n'
        '  <p class="lede">Three questions, and you get the thread, the size, the needle, the '
        'point and the stitch length \u2014 with the reasoning for each, so you can judge whether '
        'it fits the job in front of you.</p>\n\n'
        '  %s\n\n'
        '  <p><button class="sel-reset" id="selReset" type="button">Start again</button></p>\n\n'
        '  <div class="sel-out" id="selOut"></div>\n\n'
        '  <h2>The one thing worth knowing before you start</h2>\n'
        '  <p>Stitch length works in opposite directions depending on what you are sewing, and a '
        'great deal of advice ignores it.</p>\n'
        '  <p>On <strong>woven cloth</strong>, more stitches make a stronger seam. The thread '
        'passes between the yarns rather than cutting them, and each stitch adds holding power. '
        'A&amp;E put the relationship as seam strength = stitches per inch \u00d7 thread strength '
        '\u00d7 1.5.</p>\n'
        '  <p>On <strong>leather and vinyl</strong>, more stitches make a <em>weaker</em> one. '
        'Every stitch is a permanent hole, and the closer together they are the more the material '
        'is perforated along a line, until the seam tears the way a stamp does. Longer stitches, '
        'fewer holes, stronger seam.</p>\n'
        '  <p>So the instinct to sew finer for neatness is right on cloth and wrong on hide. That '
        'is the sort of thing a table cannot tell you, which is why this page asks what you are '
        'sewing first.</p>\n\n'
        '  <p>Fuller detail: <a href="/sewing-thread">thread</a> \u00b7 '
        '<a href="/sewing-needles">needles</a> \u00b7 '
        '<a href="/sewing-machines">machines</a> \u00b7 '
        '<a href="/sewing-troubleshooting">troubleshooting</a> \u00b7 '
        '<a href="/sewing-setup">setup</a> \u00b7 '
        '<a href="/sewing">everything in this section</a>.</p>\n</article>' % '\n\n  '.join(qs))

    desc = ('Three questions returning the thread, size, needle, point and stitch length for an '
            'upholstery job, with the reasoning for each.')
    page = swap_head(pre, 'Thread and needle selector for upholstery', desc, url)
    page = page.replace('</head>', CSS + '\n' + schema(url) + '\n</head>', 1)
    t = datetime.date.today()
    page += ('<header class="chapter-head">\n  <div class="wrap">\n'
             '    <p class="chno">Sewing \u00b7 Free tool</p>\n'
             '    <h1>Thread &amp; needle selector</h1>\n'
             '    <p class="updated">Last updated: <time datetime="%s">%s</time></p>\n'
             '  </div>\n</header>' % (t.isoformat(), t.strftime('%-d %B %Y')))

    open(OUT, 'w', encoding='utf-8').write(page + mid + body + build_js(d) + tail)
    print('%s written \u2014 3 questions, %d thread sizes, %d materials'
          % (OUT, len(d.THREAD_SIZES), len(d.STITCH)))


if __name__ == '__main__':
    main()
