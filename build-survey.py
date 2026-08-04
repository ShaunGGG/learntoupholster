#!/usr/bin/env python3
"""
build-survey.py — State of the Upholstery Trade: form + live results.

Generates two pages, both inheriting the site chrome from an existing chapter
page so they follow any restyling automatically:

    state-of-the-trade/index.html      live aggregate results
    state-of-the-trade/take-part.html  the survey form

Results are gated server-side until enough responses exist, so the results page
shows a progress state early on rather than a misleading average of six people.

Run before build-md-extra.py and update-sitemap.py.
"""

import os, re, sys, html, datetime

CHROME_FROM = 'webbing.html'
OUT_DIR = 'state-of-the-trade'
SITE = 'https://www.learntoupholster.com'
OG_DEFAULT = SITE + '/assets/og-card.jpg'
# The sitewide card advertises the book. On a survey whose pitch is that nothing
# is being sold, that reads as a plug and undercuts the whole thing.
OG_SURVEY = SITE + '/assets/og-state-of-the-trade.jpg'
API = '/api/survey'

COUNTRIES = [
    ('GB', 'United Kingdom'), ('US', 'United States'), ('CA', 'Canada'),
    ('AU', 'Australia'), ('NZ', 'New Zealand'), ('IE', 'Ireland'),
    ('ZA', 'South Africa'), ('FR', 'France'), ('DE', 'Germany'),
    ('NL', 'Netherlands'), ('BE', 'Belgium'), ('ES', 'Spain'), ('IT', 'Italy'),
    ('PT', 'Portugal'), ('SE', 'Sweden'), ('NO', 'Norway'), ('DK', 'Denmark'),
    ('FI', 'Finland'), ('PL', 'Poland'), ('CH', 'Switzerland'), ('AT', 'Austria'),
    ('IN', 'India'), ('JP', 'Japan'), ('SG', 'Singapore'), ('AE', 'United Arab Emirates'),
    ('BR', 'Brazil'), ('MX', 'Mexico'), ('XX', 'Somewhere else'),
]
CURRENCIES = ['GBP', 'USD', 'EUR', 'AUD', 'CAD', 'NZD', 'ZAR', 'SEK', 'DKK',
              'NOK', 'CHF', 'JPY', 'OTHER']

QUESTIONS = [
    ('country', 'Where do you work?', 'select', COUNTRIES, True, ''),
    ('currency', 'What currency do you charge in?', 'select',
     [(c, c) for c in CURRENCIES], True, 'Rates are compared within a currency, never converted.'),
    ('years_trade', 'How long have you worked in upholstery?', 'select', [
        ('<2', 'Under 2 years'), ('2-5', '2 to 5 years'), ('6-10', '6 to 10 years'),
        ('11-20', '11 to 20 years'), ('21-30', '21 to 30 years'), ('30+', 'Over 30 years')], True, ''),
    ('business_type', 'How is the business set up?', 'select', [
        ('sole-trader', 'Sole trader / self-employed'), ('partnership', 'Partnership'),
        ('limited', 'Limited company / incorporated'), ('employed', 'Employed by a workshop'),
        ('part-time', 'Part-time alongside other work'), ('hobby', 'Hobby, moving toward professional')], True, ''),
    ('premises', 'Where do you work from?', 'select', [
        ('home', 'Home workshop or garage'), ('rented-unit', 'Rented unit'),
        ('shared', 'Shared or co-operative workshop'), ('shop-frontage', 'Shop with a frontage'),
        ('mobile', 'Mobile / on site')], True, ''),
    ('hourly_rate', 'Your hourly or shop rate', 'number', None, False,
     'In the currency above. Leave blank if you never work to an hourly figure.'),
    ('pricing_method', 'How do you price a job?', 'select', [
        ('hourly', 'Hours multiplied by a rate'), ('per-job', 'A judged price for the whole job'),
        ('per-piece-type', 'Set prices by piece type'), ('mixed', 'A mix')], False, ''),
    ('fabric_markup', 'What do you mark fabric up by?', 'select', [
        ('none', 'No markup'), ('under-25', 'Under 25%'), ('25-50', '25 to 50%'),
        ('50-100', '50 to 100%'), ('over-100', 'Over 100%'),
        ('customer-supplies', 'Customers usually supply their own')], False, ''),
    ('hours_wingback', 'Bench hours: wing-back, full traditional rebuild', 'number', None, False,
     'Stripped to the frame and rebuilt \u2014 webbing, springs, hair, stitched edges. Not a re-cover.'),
    ('hours_wingback_modern', 'Bench hours: wing-back, modern re-cover', 'number', None, False,
     'The same chair stripped and rebuilt in foam and modern materials.'),
    ('lead_time', 'Current lead time', 'select', [
        ('under-2', 'Under 2 weeks'), ('2-4', '2 to 4 weeks'), ('5-8', '5 to 8 weeks'),
        ('9-16', '9 to 16 weeks'), ('over-16', 'Over 16 weeks')], False, ''),
    ('best_work', 'Which work is most profitable for you?', 'select', [
        ('domestic-recover', 'Domestic recovers'), ('traditional-restoration', 'Traditional restoration'),
        ('contract', 'Contract and commercial'), ('caravan-marine', 'Caravan, motorhome or marine'),
        ('teaching', 'Teaching and courses'), ('soft-furnishings', 'Curtains and soft furnishings'),
        ('antiques-trade', 'Work for the antiques trade')], False, ''),
    ('turning_away', 'Do you turn work away for lack of capacity?', 'select', [
        ('often', 'Often'), ('sometimes', 'Sometimes'), ('never', 'Never')], False, ''),
]

CSS = """<style>
.sv-form{margin:1.6rem 0 0}
.sv-q{margin:0 0 1.35rem}
.sv-q label{display:block;font-family:var(--display);font-weight:600;color:var(--green-deep);
  margin-bottom:.3rem;font-size:1.04rem}
.sv-q .hint{display:block;font-size:.9rem;margin:0 0 .4rem}
.sv-q select,.sv-q input[type=number]{width:100%;max-width:26rem;padding:.55rem .6rem;
  border:1px solid var(--rule);border-radius:3px;background:#fff;font:inherit;font-size:1rem}
.sv-req{color:var(--terracotta);font-weight:400}
.sv-hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.sv-submit{background:var(--green-deep);color:var(--cream);border:0;border-radius:3px;
  padding:.7rem 1.5rem;font:inherit;font-weight:600;font-size:1.02rem;cursor:pointer}
.sv-submit:disabled{opacity:.55;cursor:default}
.sv-big{font-size:1.1rem;padding:.85rem 1.7rem;margin:0 0 1rem}
.sv-msg{margin:1rem 0 0;padding:.85rem 1rem;border-radius:3px;display:none}
.sv-msg.ok{display:block;background:var(--cream-deep);border-left:4px solid var(--sage)}
.sv-msg.err{display:block;background:var(--cream-deep);border-left:4px solid var(--terracotta)}
.sv-stat{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:.9rem;margin:1.4rem 0}
.sv-stat div{background:#fff;border:1px solid var(--rule);border-radius:3px;padding:.9rem 1rem}
.sv-stat b{display:block;font-family:var(--display);font-size:1.9rem;color:var(--green-deep);line-height:1.1}
.sv-stat span{font-size:.92rem}
.sv-table{width:100%;border-collapse:collapse;margin:1rem 0 1.8rem;font-size:.98rem}
.sv-table th,.sv-table td{text-align:left;padding:.5rem .6rem;border-bottom:1px solid var(--rule)}
.sv-table th{font-family:var(--display);color:var(--green-deep);font-weight:600}
.sv-table td.n{text-align:right;font-variant-numeric:tabular-nums}
.sv-bar{background:var(--cream-deep);border-radius:2px;height:.5rem;overflow:hidden;margin-top:.2rem}
.sv-bar i{display:block;height:100%;background:var(--sage)}
.sv-progress{background:var(--cream-deep);border-left:4px solid var(--gold);padding:1rem 1.2rem;
  border-radius:3px;margin:1.4rem 0}
</style>"""


def get_chrome():
    if not os.path.exists(CHROME_FROM):
        sys.exit('Cannot find %s to use as the page template.' % CHROME_FROM)
    h = open(CHROME_FROM, encoding='utf-8').read()
    art = re.search(r'<article[^>]*>.*?</article>', h, re.S)
    if not art:
        sys.exit('No <article> found in %s.' % CHROME_FROM)
    hdr = re.search(r'<header class="chapter-head">.*?</header>', h, re.S)
    tail = h[art.end():]
    links = ('<div class="related">\n'
             '    <a href="/state-of-the-trade/"><span class="dir">Results</span><br>'
             '<span class="ttl">State of the Trade \u2192</span></a>\n'
             '    <a href="/business/"><span class="dir">Business Hub</span><br>'
             '<span class="ttl">Making a living from upholstery \u2192</span></a>\n  </div>')
    tail = re.sub(r'<div class="related">.*?</div>', lambda _m: links, tail, count=1, flags=re.S)
    if hdr and hdr.end() <= art.start():
        return h[:hdr.start()], h[hdr.end():art.start()], tail
    return h[:art.start()], '', tail


def page_header(title, kicker):
    today = datetime.date.today()
    return ('<header class="chapter-head">\n  <div class="wrap">\n'
            '    <p class="chno">%s</p>\n    <h1>%s</h1>\n'
            '    <p class="updated">Last updated: <time datetime="%s">%s</time></p>\n'
            '  </div>\n</header>' % (html.escape(kicker), html.escape(title),
                                     today.isoformat(), today.strftime('%-d %B %Y')))


def swap_head(head, title, desc, url, image=OG_SURVEY):
    def sub(pat, val, s):
        return re.sub(pat, lambda m: m.group(1) + val + m.group(2), s, count=1)
    head = re.sub(r'<title>.*?</title>',
                  lambda _m: '<title>%s | Learn to Upholster</title>' % html.escape(title),
                  head, count=1, flags=re.S)
    for attr, val in (('name="description"', html.escape(desc)),
                      ('property="og:title"', html.escape(title)),
                      ('property="og:description"', html.escape(desc)),
                      ('property="og:url"', url),
                      ('property="og:image"', image),
                      ('name="twitter:image"', image),
                      ('name="twitter:card"', 'summary_large_image')):
        head = sub(r'(<meta\s+' + attr + r'\s+content=")(?:[^"]*)(")', val, head)
    head = sub(r'(<link\s+rel="canonical"\s+href=")(?:[^"]*)(")', url, head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', '', head, flags=re.S)
    return head


def render_form():
    out = ['<form class="sv-form" id="svForm" novalidate>']
    out.append('<div class="sv-hp" aria-hidden="true">'
               '<label>Leave this empty<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>')
    for name, label, kind, opts, required, hint in QUESTIONS:
        req = ' <span class="sv-req">*</span>' if required else ''
        out.append('<div class="sv-q">')
        out.append('<label for="f_%s">%s%s</label>' % (name, html.escape(label), req))
        if hint:
            out.append('<span class="hint">%s</span>' % html.escape(hint))
        if kind == 'select':
            o = ['<option value="">\u2014 choose \u2014</option>']
            o += ['<option value="%s">%s</option>' % (v, html.escape(t)) for v, t in opts]
            out.append('<select id="f_%s" name="%s"%s>%s</select>'
                       % (name, name, ' required' if required else '', ''.join(o)))
        else:
            out.append('<input type="number" id="f_%s" name="%s" step="0.5" min="0" inputmode="decimal">'
                       % (name, name))
        out.append('</div>')
    out.append('<button type="submit" class="sv-submit" id="svBtn">Send my answers</button>')
    out.append('<div class="sv-msg" id="svMsg" role="status"></div>')
    out.append('</form>')
    return '\n    '.join(out)


FORM_JS = """<script>
(function(){
  var f=document.getElementById('svForm'),b=document.getElementById('svBtn'),m=document.getElementById('svMsg');
  if(!f) return;
  f.addEventListener('submit',function(e){
    e.preventDefault();
    var d={},ok=true;
    Array.prototype.forEach.call(f.elements,function(el){
      if(!el.name) return;
      var v=el.value.trim();
      if(el.hasAttribute('required')&&!v){ok=false;el.style.borderColor='#B5552D';}
      else if(el.style){el.style.borderColor='';}
      if(v) d[el.name]=v;
    });
    if(!ok){m.className='sv-msg err';m.textContent='A couple of the required questions are still blank.';return;}
    b.disabled=true;b.textContent='Sending\\u2026';
    fetch('%API%',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)})
      .then(function(r){return r.json();})
      .then(function(j){
        if(j.error){m.className='sv-msg err';m.textContent=j.error;b.disabled=false;b.textContent='Send my answers';return;}
        f.style.display='none';m.className='sv-msg ok';
        if(j.recorded===false&&j.reason==='already-submitted'){
          m.textContent='It looks like you have already taken part \\u2014 thank you.';
        }else{
          m.innerHTML='<strong>Thank you.</strong> That is one more real workshop in the numbers.'+
            (j.total?(' '+j.total+' upholsterers have taken part so far.'):'')+
            ' Results are published at <a href="/state-of-the-trade/">State of the Trade</a>.';
        }
      })
      .catch(function(){m.className='sv-msg err';m.textContent='That did not send. Please try again in a moment.';
        b.disabled=false;b.textContent='Send my answers';});
  });
})();
</script>""".replace('%API%', API)

RESULTS_JS = """<script>
(function(){
  var el=document.getElementById('svResults'); if(!el) return;
  var LABEL={'<2':'Under 2 years','2-5':'2 to 5 years','6-10':'6 to 10 years','11-20':'11 to 20 years',
    '21-30':'21 to 30 years','30+':'Over 30 years','sole-trader':'Sole trader','partnership':'Partnership',
    'limited':'Limited company','employed':'Employed','part-time':'Part-time','hobby':'Hobby to professional',
    'home':'Home workshop','rented-unit':'Rented unit','shared':'Shared workshop','shop-frontage':'Shop frontage',
    'mobile':'Mobile','hourly':'Hours \\u00d7 rate','per-job':'Judged per job','per-piece-type':'Set piece prices',
    'mixed':'A mix','none':'No markup','under-25':'Under 25%','25-50':'25 to 50%','50-100':'50 to 100%',
    'over-100':'Over 100%','customer-supplies':'Customer supplies','under-2':'Under 2 weeks','2-4':'2 to 4 weeks',
    '5-8':'5 to 8 weeks','9-16':'9 to 16 weeks','over-16':'Over 16 weeks','domestic-recover':'Domestic recovers',
    'traditional-restoration':'Traditional restoration','contract':'Contract and commercial',
    'caravan-marine':'Caravan and marine','teaching':'Teaching','soft-furnishings':'Soft furnishings',
    'antiques-trade':'Antiques trade','often':'Often','sometimes':'Sometimes','never':'Never'};
  var NAMES={GB:'United Kingdom',US:'United States',CA:'Canada',AU:'Australia',NZ:'New Zealand',IE:'Ireland',
    ZA:'South Africa',FR:'France',DE:'Germany',NL:'Netherlands',BE:'Belgium',ES:'Spain',IT:'Italy',PT:'Portugal',
    SE:'Sweden',NO:'Norway',DK:'Denmark',FI:'Finland',PL:'Poland',CH:'Switzerland',AT:'Austria',IN:'India',
    JP:'Japan',SG:'Singapore',AE:'United Arab Emirates',BR:'Brazil',MX:'Mexico',XX:'Elsewhere'};
  var lab=function(v){return LABEL[v]||v;};
  var esc=function(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML;};
  function dist(title,rows){
    if(!rows||!rows.length) return '';
    var h='<h3>'+esc(title)+'</h3><table class="sv-table"><tbody>';
    rows.forEach(function(r){
      h+='<tr><td>'+esc(lab(r.value))+'<div class="sv-bar"><i style="width:'+r.pct+'%"></i></div></td>'+
         '<td class="n">'+r.pct+'%</td></tr>';
    });
    return h+'</tbody></table>';
  }
  fetch('%API%').then(function(r){return r.json();}).then(function(j){
    if(!j.published){
      var pct=Math.round((j.responses||0)/j.min_to_publish*100);
      el.innerHTML='<div class="sv-progress"><p><strong>'+(j.responses||0)+' of '+j.min_to_publish+
        ' responses.</strong> '+esc(j.note||'')+'</p><div class="sv-bar"><i style="width:'+pct+'%"></i></div></div>'+
        '<p>Nothing is published until there are enough answers to mean something. A median drawn from '+
        'six workshops would be quoted back for years and would be wrong.</p>'+
        '<p><a class="sv-submit" style="display:inline-block;text-decoration:none" href="/state-of-the-trade/take-part">Take part \\u2014 about three minutes</a></p>';
      return;
    }
    var o=j.overall,h='';
    h+='<div class="sv-stat"><div><b>'+j.responses+'</b><span>upholsterers</span></div>'+
       '<div><b>'+(j.by_country?j.by_country.length:0)+'</b><span>countries with enough data</span></div>'+
       '<div><b>'+(o.median_hours_wingback||'\\u2014')+'</b><span>median hours, traditional wing-back</span></div>'+
       '<div><b>'+(o.median_hours_wingback_modern||'\\u2014')+'</b><span>median hours, modern re-cover</span></div></div>';
    if(o.traditional_vs_modern_multiplier){
      h+='<p class="sv-progress"><strong>A traditional rebuild takes '+o.traditional_vs_modern_multiplier+
         '\\u00d7 as long as a modern re-cover</strong> on the same chair. Measured per workshop, '+
         'from the '+o.traditional_vs_modern_pairs+' upholsterers who gave both figures \\u2014 not by '+
         'comparing one group\\u2019s answers against another\\u2019s.</p>';
    }
    if(j.by_country&&j.by_country.length){
      h+='<h3>Rates by country</h3><table class="sv-table"><thead><tr><th>Country</th><th class="n">Median rate</th>'+
         '<th class="n">Wing-back (trad)</th><th class="n">Wing-back (modern)</th><th class="n">Responses</th></tr></thead><tbody>';
      j.by_country.forEach(function(c){
        h+='<tr><td>'+esc(NAMES[c.country]||c.country)+'</td>'+
           '<td class="n">'+(c.median_hourly_rate!=null?(c.median_hourly_rate+' '+(c.currency||'')):'\\u2014')+'</td>'+
           '<td class="n">'+(c.median_hours_wingback!=null?c.median_hours_wingback+' h':'\\u2014')+'</td>'+
           '<td class="n">'+(c.median_hours_wingback_modern!=null?c.median_hours_wingback_modern+' h':'\\u2014')+'</td>'+
           '<td class="n">'+c.responses+'</td></tr>';
      });
      h+='</tbody></table><p class="hint">'+esc(j.note||'')+'</p>';
    }
    h+=dist('Most profitable work',o.most_profitable_work);
    h+=dist('How jobs are priced',o.pricing_method);
    h+=dist('Fabric markup',o.fabric_markup);
    h+=dist('Current lead times',o.lead_time);
    h+=dist('Where upholsterers work from',o.premises);
    h+=dist('Years in the trade',o.years_in_trade);
    h+=dist('Turning work away for lack of capacity',o.turning_work_away);
    // The ask should get stronger once there are figures to show, not weaker.
    // "Here is what N workshops reported, add yours" beats "help us reach 30".
    h+='<div class="sv-progress"><p><strong>These figures update as more workshops respond.</strong> '+
       'Every answer makes them more useful \u2014 including to you, next time you are pricing a job. '+
       'Anonymous, three minutes, no name or email.</p>'+
       '<p><a class="sv-submit" style="display:inline-block;text-decoration:none" '+
       'href="/state-of-the-trade/take-part">Add your workshop to the data</a></p></div>';
    h+='<p>Last updated '+esc(j.updated)+'. '+esc(j.licence)+'</p>';
    el.innerHTML=h;
  }).catch(function(){
    el.innerHTML='<p>The results could not be loaded just now. Please try again shortly.</p>';
  });
})();
</script>""".replace('%API%', API)


def schema_dataset():
    return ('<script type="application/ld+json">\n'
            '{"@context":"https://schema.org","@type":"Dataset",'
            '"@id":"%s/state-of-the-trade#dataset",'
            '"name":"State of the Upholstery Trade",'
            '"description":"An open survey of working upholsterers worldwide: shop rates, bench hours by piece, '
            'fabric markup, lead times and which work pays. Medians by country, updated as responses arrive.",'
            '"url":"%s/state-of-the-trade","license":"https://creativecommons.org/licenses/by/4.0/",'
            '"creator":{"@type":"Person","@id":"%s/about#shaun","name":"Shaun Greenwood"},'
            '"publisher":{"@type":"Organization","@id":"%s#org","name":"Learn to Upholster"},'
            '"isAccessibleForFree":true,"inLanguage":"en",'
            '"distribution":{"@type":"DataDownload","encodingFormat":"application/json",'
            '"contentUrl":"%s%s"}}\n</script>' % (SITE, SITE, SITE, SITE, SITE, API))


def main():
    pre, mid, tail = get_chrome()
    os.makedirs(OUT_DIR, exist_ok=True)

    # ---- results page
    r_desc = ('Open survey data from working upholsterers worldwide: shop rates, bench hours by '
              'piece, fabric markup, lead times and which work actually pays.')
    body = (
        '<article class="article wrap read">\n'
        '  <p><a class="sv-submit sv-big" style="display:inline-block;text-decoration:none" '
        'href="/state-of-the-trade/take-part">Take the survey \u2014 three minutes, anonymous</a></p>\n'
        '  <p class="lede">There is no reliable public data on what upholstery work is worth. '
        'Rates get passed around as rumour, and new workshops price from guesswork. '
        'This is an attempt to fix that with numbers from actual benches.</p>\n'
        '  <p>Anonymous, free to read, and free to cite. No names, no email addresses, '
        'nothing that identifies a respondent \u2014 just the figures, aggregated.</p>\n'
        '  <div id="svResults"><p>Loading the latest figures\u2026</p></div>\n'
        '  <h2>Take part</h2>\n'
        '  <p>Thirteen questions, about three minutes, and the more workshops that answer the '
        'more useful it becomes for everyone \u2014 including you, next time you set a price.</p>\n'
        '  <p><a class="sv-submit" style="display:inline-block;text-decoration:none" '
        'href="/state-of-the-trade/take-part">Take part in the survey</a></p>\n'
        '</article>')
    page = swap_head(pre, 'State of the Upholstery Trade', r_desc, SITE + '/state-of-the-trade')
    page = page.replace('</head>', CSS + '\n' + schema_dataset() + '\n</head>', 1)
    page += page_header('State of the Upholstery Trade', 'Open survey data \u00b7 updated live')
    open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8').write(
        page + mid + body + RESULTS_JS + tail)

    # ---- form page
    f_desc = ('Add your workshop to the State of the Upholstery Trade survey. Anonymous, thirteen '
              'questions, about three minutes.')
    form_body = (
        '<article class="article wrap read">\n'
        '  <p class="lede">Thirteen questions about how your workshop actually runs. '
        'About three minutes.</p>\n'
        '  <p>Anonymous. No name, no email address, nothing that identifies you or your business. '
        'Answer what you are comfortable with \u2014 only the first five are required, and a partial '
        'answer is still useful.</p>\n'
        '  <p>Results are published at <a href="/state-of-the-trade/">State of the Trade</a> and are '
        'free for anyone to cite.</p>\n'
        '  %s\n</article>' % render_form())
    page = swap_head(pre, 'Take part in the survey', f_desc, SITE + '/state-of-the-trade/take-part')
    page = page.replace('</head>', CSS + '\n<meta name="robots" content="index,follow">\n</head>', 1)
    page += page_header('Take part', 'State of the Upholstery Trade')
    open(os.path.join(OUT_DIR, 'take-part.html'), 'w', encoding='utf-8').write(
        page + mid + form_body + FORM_JS + tail)

    print('State of the Trade built:')
    print('   %s/index.html      (live results, %d questions surveyed)' % (OUT_DIR, len(QUESTIONS)))
    print('   %s/take-part.html  (form)' % OUT_DIR)
    print('   API: %s  \u2014 needs the SURVEY_DB binding' % API)


if __name__ == '__main__':
    main()
