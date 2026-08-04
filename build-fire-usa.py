#!/usr/bin/env python3
"""
build-fire-usa.py — US upholstery fire regulations checker.

Separate page from the UK checker, because the two regimes are genuinely
different and mixing them is how people end up applying the wrong one.

Everything on this page is sourced from:
  16 CFR Part 1640            ecfr.gov/current/title-16/chapter-II/subchapter-D/part-1640
  California TB 117-2013      bhgs.dca.ca.gov/about_us/tb117_2013.pdf
  CPSC direct final rule      federalregister.gov/documents/2021/04/09/2021-06977
  NUA guidance for upholsterers, including their CPSC clarification on
  reupholstery and change of ownership

The two things most US upholsterers do not know, and the reasons this page is
worth having at all:

  1. Reupholstery is named in the standard. It applies to furniture
     "manufactured, imported, or reupholstered on or after" 25 June 2021.
  2. But not when the piece stays with the same owner. A customer's own chair
     coming back to them is outside it. Reupholster something you then sell and
     it is inside.

Run before build-inline.py.
"""

import os, re, sys, html, datetime

SITE = 'https://www.learntoupholster.com'
OUT = 'fire-regulations-usa.html'
CHROME_FROM = 'webbing.html'
OG = SITE + '/assets/og-card.jpg'


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
             '    <a href="/fire-safety-checker"><span class="dir">United Kingdom</span><br>'
             '<span class="ttl">UK fire regulations checker \u2192</span></a>\n'
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
.fc-q{background:#fff;border:1px solid var(--rule);border-radius:3px;padding:1.1rem 1.3rem;margin:0 0 1rem}
.fc-q h2{font-family:var(--display);font-size:1.15rem;margin:0 0 .3rem;color:var(--green-deep)}
.fc-q p.hint{font-size:.92rem;margin:0 0 .7rem}
.fc-opts{display:flex;flex-wrap:wrap;gap:.5rem}
.fc-opt{background:#fff;border:1px solid var(--rule);border-radius:3px;padding:.5rem .9rem;
  font:inherit;font-size:.95rem;cursor:pointer;color:var(--ink)}
.fc-opt[aria-pressed="true"]{background:var(--green-deep);color:var(--cream);border-color:var(--green-deep)}
.fc-out{background:var(--cream-deep);border-left:4px solid var(--gold);border-radius:3px;
  padding:1.1rem 1.3rem;margin:1.6rem 0 0;display:none}
.fc-out.show{display:block}
.fc-out h2{font-family:var(--display);font-size:1.25rem;margin:0 0 .5rem;color:var(--green-deep)}
.fc-out h3{font-family:var(--display);font-size:1.02rem;margin:1rem 0 .3rem;color:var(--green-deep)}
.fc-out ul{margin:.3rem 0 .6rem;padding-left:1.1rem}
.fc-badge{display:inline-block;border-radius:2px;padding:.15rem .55rem;font-size:.85rem;
  font-weight:600;margin-bottom:.5rem}
.fc-in{background:var(--terracotta);color:#fff}
.fc-outof{background:var(--sage);color:#22382C}
.fc-label{background:#fff;border:1px solid #000;padding:.7rem .9rem;margin:.6rem 0;
  font-family:ui-monospace,monospace;font-size:.9rem;color:#000}
.fc-sources{font-size:.88rem;border-top:1px solid var(--rule);margin-top:1.6rem;padding-top:.8rem}
.fc-sources li{margin-bottom:.2rem}
.fc-note{background:#fff;border-left:3px solid var(--terracotta);padding:.8rem 1rem;
  border-radius:3px;margin:1.2rem 0;font-size:.96rem}
.fc-reset{background:none;border:0;color:var(--green-deep);text-decoration:underline;
  cursor:pointer;font:inherit;font-size:.92rem;padding:0}
@media print{.fc-opts,.fc-reset{display:none}.fc-out{display:block}}
</style>"""


QUESTIONS = [
    ('ownership', 'Who owns the piece when it leaves your shop?',
     'This is the question that decides most jobs, and the one almost nobody knows about. '
     'The National Upholstery Association asked CPSC directly, and the answer was that the '
     'standard does not apply where the furniture keeps the same owner through the work.',
     [('same', 'The customer\u2019s own piece, going back to them'),
      ('sold', 'I am selling it, or it changes hands'),
      ('unsure', 'Not sure yet')]),

    ('type', 'What is it?',
     'The standard covers upholstered seating for indoor use.',
     [('seating', 'Seating \u2014 sofa, chair, recliner, ottoman, upholstered headboard'),
      ('mattress', 'Mattress or bed base'),
      ('outdoor', 'Outdoor or garden furniture'),
      ('other', 'Something else')]),

    ('materials', 'What fire evidence do you have for the materials?',
     'TB 117-2013 tests four component types separately: cover fabric, barrier material, '
     'resilient filling, and decking material where there is a loose cushion.',
     [('barrier', 'I fit a compliant barrier layer'),
      ('components', 'Certificated cover and filling, no barrier'),
      ('unknown', 'Nothing certificated \u2014 customer\u2019s own cloth or unknown materials')]),
]


RESULTS_JS = """<script>
(function(){
  var state={};
  var out=document.getElementById('fcOut');

  function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML;}

  var LABEL = 'Complies with U.S. CPSC requirements for upholstered furniture flammability.';

  function render(){
    if(!state.ownership || !state.type || !state.materials){ out.className='fc-out'; return; }
    var h='';
    var inScope = true;

    // Ownership is the gate. Same owner in, same owner out, and 16 CFR 1640 does
    // not bite \u2014 CPSC confirmed this to the NUA.
    if(state.ownership==='same'){
      inScope=false;
      h+='<span class="fc-badge fc-outof">Outside 16 CFR Part 1640</span>';
      h+='<h2>The federal standard does not apply to this job</h2>';
      h+='<p>The standard applies to upholstered furniture <em>manufactured, imported, or '+
         'reupholstered</em> on or after 25 June 2021 \\u2014 but CPSC confirmed to the National '+
         'Upholstery Association that it does not apply where the piece keeps the same owner '+
         'through the work. A customer bringing you their own chair and taking it home again '+
         'is that situation.</p>';
      h+='<h3>What still matters</h3><ul>'+
         '<li>Your <strong>state or city</strong> may have its own rules and its own labelling '+
         'requirements. California has had labelling requirements since 2015. Check locally.</li>'+
         '<li>If the customer later sells the piece through a business, it may fall in scope '+
         'at that point.</li>'+
         '<li>Doing it to the standard anyway costs little and removes all doubt. A compliant '+
         'barrier is cheap insurance.</li></ul>';
    } else if(state.type==='mattress'){
      inScope=false;
      h+='<span class="fc-badge fc-outof">Different standard</span>';
      h+='<h2>Mattresses are covered elsewhere</h2>';
      h+='<p>Mattresses and mattress sets are excluded from 16 CFR Part 1640 because they have '+
         'their own federal standards: <strong>16 CFR Part 1632</strong> (cigarette ignition) '+
         'and <strong>16 CFR Part 1633</strong> (open flame). Those are stricter and separate. '+
         'Do not assume upholstery compliance carries across.</p>';
    } else if(state.type==='outdoor'){
      h+='<span class="fc-badge fc-outof">Probably outside</span>';
      h+='<h2>Outdoor furniture is generally not covered</h2>';
      h+='<p>16 CFR Part 1640 covers upholstered furniture <strong>intended for indoor use</strong>. '+
         'Genuinely outdoor furniture sits outside it.</p>';
      h+='<p>The caution is the same as in the UK: if the piece could reasonably be brought '+
         'indoors \\u2014 a conservatory chair, a bench cushion that lives in a porch \\u2014 treat it '+
         'as indoor furniture and comply.</p>';
    } else if(state.type==='other'){
      h+='<span class="fc-badge fc-in">Check the definition</span>';
      h+='<h2>Check whether it meets the definition</h2>';
      h+='<p>16 CFR 1640.3 defines regulated upholstered furniture by reference to structural '+
         'units, filling material and covering that together support a person\\u2019s body or limbs. '+
         'If you are not sure whether your piece qualifies, CPSC runs a Small Business Ombudsman '+
         'who will tell you.</p>';
    } else {
      // In scope: seating, changing hands.
      h+='<span class="fc-badge fc-in">In scope \\u2014 16 CFR Part 1640</span>';
      h+='<h2>The federal standard applies</h2>';
      h+='<p>Upholstered seating for indoor use that changes hands is covered. The standard is '+
         'California <strong>TB 117-2013</strong>, adopted federally as 16 CFR Part 1640, and it '+
         'applies to anything manufactured, imported or <strong>reupholstered</strong> on or after '+
         '25 June 2021.</p>';

      h+='<h3>What TB 117-2013 actually tests</h3>';
      h+='<p><strong>Smoulder resistance only.</strong> This is the single biggest difference from '+
         'the British regime, and it catches people who have worked to UK rules: TB 117-2013 was '+
         'not designed to test performance against an open flame. There is no match-equivalent '+
         'test at federal level.</p>';
      h+='<p>Four component types are tested separately, each pass or fail: cover fabric, '+
         'barrier material, resilient filling, and decking material where there is a loose cushion.</p>';

      if(state.materials==='barrier'){
        h+='<h3>Your route: the barrier layer</h3>';
        h+='<p>This is the simplest way to comply and the one the National Upholstery Association '+
           'recommends. Under TB 117-2013, <strong>if the barrier passes, the piece complies even '+
           'if the cover and filling would fail on their own.</strong></p>';
        h+='<ul><li>Fit the barrier between the cover fabric and the filling</li>'+
           '<li>Keep the barrier supplier\\u2019s test certificate on the job record</li>'+
           '<li>Note on the job sheet which barrier went into which piece</li></ul>';
        h+='<p>It also means a customer\\u2019s own uncertificated cloth stops being a problem, which '+
           'is why it is worth doing as standard practice.</p>';
      } else if(state.materials==='components'){
        h+='<h3>Your route: certificated components</h3>';
        h+='<p>Legitimate, but you are relying on every component holding up. Keep the '+
           'certificates for the cover, the filling and the decking, and file them against the job.</p>';
        h+='<p>Worth knowing that a barrier layer would let you stop worrying about the cover '+
           'entirely \\u2014 see the barrier option above.</p>';
      } else {
        h+='<h3>You cannot certify this as it stands</h3>';
        h+='<p>With no fire evidence for the materials you have no basis for the label, and the '+
           'label is a certification you are personally making.</p>';
        h+='<p><strong>Fit a compliant barrier layer.</strong> Because a passing barrier brings the '+
           'whole piece into compliance regardless of the cover and filling, it solves exactly this '+
           'problem \\u2014 including a customer\\u2019s own cloth of unknown provenance.</p>';
      }

      h+='<h3>The label</h3>';
      h+='<p>Required on covered furniture reupholstered on or after 25 June 2022. This wording, '+
         'exactly:</p>';
      h+='<div class="fc-label">'+esc(LABEL)+'</div>';
      h+='<ul><li>Permanent label, on the front of the tag, in English</li>'+
         '<li>White background, black text, black border</li>'+
         '<li>If your state or city has its own label rules, follow those too \\u2014 you may combine '+
         'the statements or use separate labels</li></ul>';
    }

    h+='<h3>Records</h3><p>Keep the certificates and a written note of what you fitted, against '+
       'the job. Your paperwork is the only evidence you will have if you are ever asked.</p>';

    out.innerHTML=h;
    out.className='fc-out show';
    out.scrollIntoView({behavior:'smooth',block:'nearest'});
  }

  document.querySelectorAll('.fc-opt').forEach(function(b){
    b.addEventListener('click',function(){
      var q=b.getAttribute('data-q');
      state[q]=b.getAttribute('data-v');
      document.querySelectorAll('.fc-opt[data-q="'+q+'"]').forEach(function(o){
        o.setAttribute('aria-pressed', o===b ? 'true':'false');
      });
      render();
    });
  });
  var r=document.getElementById('fcReset');
  if(r) r.addEventListener('click',function(){
    state={};
    document.querySelectorAll('.fc-opt').forEach(function(o){o.setAttribute('aria-pressed','false');});
    out.className='fc-out'; out.innerHTML='';
  });
})();
</script>"""


def schema():
    return ('<script type="application/ld+json">\n'
            '{"@context":"https://schema.org","@graph":['
            '{"@type":"WebApplication","@id":"%s/fire-regulations-usa#app",'
            '"name":"US upholstery fire regulations checker",'
            '"applicationCategory":"BusinessApplication","operatingSystem":"Any",'
            '"url":"%s/fire-regulations-usa",'
            '"description":"Which US upholstery fire requirements apply to a job: 16 CFR Part 1640, '
            'California TB 117-2013, reupholstery, the change-of-ownership rule, barrier layers and '
            'the CPSC label.",'
            '"offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},'
            '"isAccessibleForFree":true,'
            '"author":{"@id":"%s/about#shaun"},"publisher":{"@id":"%s#org"}},'
            '{"@type":"FAQPage","@id":"%s/fire-regulations-usa#faq","mainEntity":['
            '{"@type":"Question","name":"Does the US flammability standard apply to reupholstery?",'
            '"acceptedAnswer":{"@type":"Answer","text":"16 CFR Part 1640 applies to upholstered '
            'furniture manufactured, imported or reupholstered on or after 25 June 2021. However, '
            'CPSC confirmed to the National Upholstery Association that it does not apply where the '
            'furniture retains the same ownership after reupholstery \\u2014 so a customer\\u2019s own '
            'piece returned to them is outside the standard, while a piece you reupholster and sell '
            'is inside it."}},'
            '{"@type":"Question","name":"What does California TB 117-2013 test?",'
            '"acceptedAnswer":{"@type":"Answer","text":"Smoulder resistance only. It tests cover '
            'fabric, barrier material, resilient filling and decking material separately on a '
            'pass or fail basis, and was not designed to evaluate performance against an open '
            'flame. If the barrier material passes, the piece complies even where other components '
            'would fail."}},'
            '{"@type":"Question","name":"What label does US upholstered furniture need?",'
            '"acceptedAnswer":{"@type":"Answer","text":"A permanent label stating \\u201cComplies '
            'with U.S. CPSC requirements for upholstered furniture flammability.\\u201d in English '
            'on the front of the tag, with a white background, black text and a black border. '
            'Required for covered furniture reupholstered on or after 25 June 2022."}}]}]}\n'
            '</script>' % (SITE, SITE, SITE, SITE, SITE))


def main():
    pre, mid, tail = get_chrome()
    today = datetime.date.today()

    qs = []
    for key, title, hint, opts in QUESTIONS:
        buttons = ''.join(
            '<button class="fc-opt" data-q="%s" data-v="%s" aria-pressed="false" type="button">%s</button>'
            % (key, v, html.escape(l)) for v, l in opts)
        qs.append('<div class="fc-q">\n  <h2>%s</h2>\n  <p class="hint">%s</p>\n'
                  '  <div class="fc-opts">%s</div>\n</div>'
                  % (html.escape(title), html.escape(hint), buttons))

    body = (
        '<article class="article wrap read">\n'
        '  <p class="lede">Which US fire requirements apply to an upholstery job, and what you '
        'have to put on the label. Three questions.</p>\n\n'
        '  <div class="fc-note"><p><strong>Reupholstery is named in the standard \u2014 and there '
        'is an exception most people have never heard of.</strong> 16 CFR Part 1640 applies to '
        'furniture manufactured, imported or <em>reupholstered</em> on or after 25 June 2021. But '
        'CPSC confirmed to the National Upholstery Association that it does not apply where the '
        'piece keeps the same owner through the work. That single distinction decides most jobs, '
        'so it is the first question below.</p></div>\n\n'
        '  %s\n\n'
        '  <p><button class="fc-reset" id="fcReset" type="button">Start again</button></p>\n\n'
        '  <div class="fc-out" id="fcOut"></div>\n\n'
        '  <div class="fc-sources">\n'
        '    <p><strong>Sources.</strong> Everything above is taken from:</p>\n'
        '    <ul>\n'
        '      <li>16 CFR Part 1640, Standard for the Flammability of Upholstered Furniture '
        '\u2014 <a href="https://www.ecfr.gov/current/title-16/chapter-II/subchapter-D/part-1640" '
        'rel="noopener nofollow" target="_blank">eCFR</a></li>\n'
        '      <li>California Technical Bulletin 117-2013 '
        '\u2014 <a href="https://bhgs.dca.ca.gov/about_us/tb117_2013.pdf" rel="noopener nofollow" '
        'target="_blank">Department of Consumer Affairs</a></li>\n'
        '      <li>CPSC direct final rule, 9 April 2021 '
        '\u2014 <a href="https://www.federalregister.gov/documents/2021/04/09/2021-06977/standard-for-the-flammability-of-upholstered-furniture" '
        'rel="noopener nofollow" target="_blank">Federal Register</a></li>\n'
        '      <li>National Upholstery Association guidance for upholsterers, including their '
        'clarification from CPSC on reupholstery and change of ownership '
        '\u2014 <a href="https://nationalupholsteryassociation.org/Upholstered-Furniture-Flammability-Standard" '
        'rel="noopener nofollow" target="_blank">NUA</a></li>\n'
        '    </ul>\n'
        '    <p>This is informational guidance from a working upholsterer, not legal advice, and '
        'I work in Britain rather than the United States. State and municipal rules sit on top of '
        'the federal standard and differ. Where a job carries real risk, confirm the specification '
        'in writing with whoever is responsible for it, or ask the '
        '<a href="https://www.cpsc.gov/Newsroom/Small-Business-Resources" rel="noopener nofollow" '
        'target="_blank">CPSC Small Business Ombudsman</a>, who exists for exactly this.</p>\n'
        '    <p>Working in Britain instead? Use the '
        '<a href="/fire-safety-checker">UK fire regulations checker</a> \u2014 the two regimes are '
        'genuinely different and the British one tests against an open flame as well as a '
        'cigarette.</p>\n'
        '  </div>\n'
        '</article>' % '\n\n  '.join(qs))

    desc = ('Which US fire regulations apply to an upholstery job: 16 CFR Part 1640, TB 117-2013, '
            'the reupholstery ownership rule, barrier layers and the CPSC label.')
    page = swap_head(pre, 'US upholstery fire regulations checker', desc,
                     SITE + '/fire-regulations-usa')
    page = page.replace('</head>', CSS + '\n' + schema() + '\n</head>', 1)
    page += ('<header class="chapter-head">\n  <div class="wrap">\n'
             '    <p class="chno">Free tools \u00b7 United States</p>\n'
             '    <h1>US fire regulations checker</h1>\n'
             '    <p class="updated">Last updated: <time datetime="%s">%s</time></p>\n'
             '  </div>\n</header>' % (today.isoformat(), today.strftime('%-d %B %Y')))

    open(OUT, 'w', encoding='utf-8').write(page + mid + body + RESULTS_JS + tail)
    print('%s written' % OUT)
    print('   3 questions, sourced from 16 CFR 1640, TB 117-2013, CPSC and NUA')


if __name__ == '__main__':
    main()
