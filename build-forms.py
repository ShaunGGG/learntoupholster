#!/usr/bin/env python3
"""
build-forms.py — the printable workshop forms page.

Four forms that travel with a job: enquiry, condition report, job sheet, and
collection/delivery note. The quote and invoice are already covered by the
spreadsheet on /invoice-template, so these are deliberately the other half — the
paperwork that lives in the workshop rather than going to the customer.

Built as print-ready HTML rather than a download on purpose:

  - no file to open, no software to own, works on a phone at a customer's house
  - fill on screen and print, or print blank and fill in biro at the bench
  - your details save locally and prefill all four

Page chrome is lifted from an existing chapter page at build time, same as
build-business.py, so it follows any restyling of the site.

Run before build-inline.py.
"""

import os, re, sys, html, datetime

CHROME_FROM = 'webbing.html'
OUT = 'workshop-forms.html'
SITE = 'https://www.learntoupholster.com'
OG = SITE + '/assets/og-card.jpg'


# ---------------------------------------------------------------- chrome

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
             '    <a href="/invoice-template"><span class="dir">Also free</span><br>'
             '<span class="ttl">Quote &amp; invoice template \u2192</span></a>\n'
             '    <a href="/business/"><span class="dir">Business Hub</span><br>'
             '<span class="ttl">Making a living from upholstery \u2192</span></a>\n  </div>')
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


# ---------------------------------------------------------------- styles

CSS = """<style>
.wf-intro{margin-bottom:1.6rem}
.wf-setup{background:var(--cream-deep);border-left:4px solid var(--gold);border-radius:3px;
  padding:1rem 1.2rem;margin:1.4rem 0 2rem}
.wf-setup h2{font-family:var(--display);font-size:1.1rem;margin:0 0 .5rem;color:var(--green-deep)}
.wf-setup .row{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:.7rem}
.wf-setup label{display:block;font-size:.88rem;margin-bottom:.15rem}
.wf-setup input{width:100%;padding:.45rem .5rem;border:1px solid var(--rule);border-radius:3px;
  font:inherit;font-size:.95rem;background:#fff}
.wf-note{font-size:.87rem;margin:.7rem 0 0}

.wf-index{list-style:none;padding:0;margin:0 0 2rem}
.wf-index li{padding:.6rem 0;border-bottom:1px solid var(--rule)}
.wf-index a{font-weight:600;text-decoration:none}
.wf-index p{margin:.2rem 0 0;font-size:.95rem}

.wf-sheet{background:#fff;border:1px solid var(--rule);border-radius:3px;
  padding:1.6rem 1.8rem;margin:0 0 2.2rem}
.wf-sheet-head{display:flex;justify-content:space-between;align-items:flex-start;
  border-bottom:2px solid var(--green-deep);padding-bottom:.6rem;margin-bottom:1.1rem;gap:1rem}
.wf-sheet-head h2{font-family:var(--display);font-size:1.35rem;margin:0;color:var(--green-deep)}
.wf-biz{text-align:right;font-size:.9rem;line-height:1.35}
.wf-biz b{display:block;font-family:var(--display);font-size:1.05rem}
.wf-print{background:var(--green-deep);color:var(--cream);border:0;border-radius:3px;
  padding:.4rem .9rem;font:inherit;font-size:.88rem;font-weight:600;cursor:pointer;white-space:nowrap}

.wf-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:.8rem 1.2rem}
.wf-f{margin:0 0 .75rem}
.wf-f label{display:block;font-size:.82rem;font-weight:600;color:var(--green-deep);
  text-transform:uppercase;letter-spacing:.02em;margin-bottom:.2rem}
.wf-f input,.wf-f textarea,.wf-f select{width:100%;padding:.42rem .5rem;border:1px solid #C9C2B4;
  border-radius:2px;font:inherit;font-size:.95rem;background:#fff;box-sizing:border-box}
.wf-f textarea{min-height:4.5rem;resize:vertical}
.wf-f.tall textarea{min-height:7rem}
.wf-full{grid-column:1/-1}
.wf-sub{font-family:var(--display);font-size:1rem;color:var(--green-deep);margin:1.3rem 0 .6rem;
  border-bottom:1px solid var(--rule);padding-bottom:.25rem}
.wf-check{display:flex;flex-wrap:wrap;gap:.5rem 1.2rem;margin:.3rem 0 .6rem}
.wf-check label{display:flex;align-items:center;gap:.35rem;font-size:.93rem;font-weight:400;
  text-transform:none;letter-spacing:0}
.wf-check input{width:auto}
.wf-sign{display:grid;grid-template-columns:2fr 1fr;gap:1.2rem;margin-top:1.2rem;
  border-top:1px solid var(--rule);padding-top:1rem}
.wf-rule{border:0;border-top:1px solid #C9C2B4;margin:1.4rem 0 .3rem}
.wf-small{font-size:.82rem;margin:.4rem 0 0}

@media print{
  body{background:#fff}
  .site-nav,.site-footer,.wf-intro,.wf-setup,.wf-index,.wf-print,.chapter-head,
  .ad-rail,.related,.seam,.bookblock,#grow-me,.capture{display:none!important}
  .wrap,.page-cols,.article{max-width:none!important;width:auto!important;margin:0!important;padding:0!important}
  .wf-sheet{border:0;padding:0;margin:0;page-break-after:always;break-after:page}
  .wf-sheet:last-of-type{page-break-after:auto;break-after:auto}
  .wf-sheet-head{border-bottom:2px solid #000}
  .wf-f input,.wf-f textarea,.wf-f select{border:0;border-bottom:1px solid #555;border-radius:0;
    padding:.15rem 0}
  .wf-f textarea{border:1px solid #555;padding:.3rem}
  .wf-f label{color:#000}
  .wf-sheet-head h2{color:#000}
  .wf-sub{color:#000}
  @page{size:A4 portrait;margin:14mm}
}
</style>"""


# ---------------------------------------------------------------- fields

def f(label, name, kind='text', full=False, tall=False, placeholder=''):
    cls = 'wf-f' + (' wf-full' if full else '') + (' tall' if tall else '')
    ph = ' placeholder="%s"' % html.escape(placeholder) if placeholder else ''
    if kind == 'textarea':
        ctl = '<textarea name="%s"%s></textarea>' % (name, ph)
    else:
        ctl = '<input type="%s" name="%s"%s>' % (kind, name, ph)
    return '<div class="%s"><label>%s</label>%s</div>' % (cls, html.escape(label), ctl)


def checks(label, items):
    boxes = ''.join('<label><input type="checkbox"> %s</label>' % html.escape(i) for i in items)
    return ('<div class="wf-f wf-full"><label>%s</label><div class="wf-check">%s</div></div>'
            % (html.escape(label), boxes))


def sheet(id_, title, blocks):
    return (
        '<section class="wf-sheet" id="%s">\n'
        '  <div class="wf-sheet-head">\n'
        '    <h2>%s</h2>\n'
        '    <div>\n'
        '      <div class="wf-biz"><b data-biz="name">Your workshop</b>'
        '<span data-biz="contact"></span></div>\n'
        '    </div>\n'
        '    <button class="wf-print" data-print="%s" type="button">Print this form</button>\n'
        '  </div>\n%s\n</section>' % (id_, html.escape(title), id_, blocks))


# ---------------------------------------------------------------- forms

def form_enquiry():
    b = []
    b.append('<div class="wf-grid">')
    b.append(f('Date', 'date', 'date'))
    b.append(f('Enquiry ref', 'ref'))
    b.append(f('How did they find you?', 'source', placeholder='Recommendation, search, social, repeat'))
    b.append('</div>')
    b.append('<div class="wf-sub">Customer</div><div class="wf-grid">')
    b.append(f('Name', 'name'))
    b.append(f('Telephone', 'tel', 'tel'))
    b.append(f('Email', 'email', 'email'))
    b.append(f('Address', 'address', 'textarea', full=True))
    b.append('</div>')
    b.append('<div class="wf-sub">The piece</div><div class="wf-grid">')
    b.append(f('What is it?', 'piece', placeholder='Wing-back armchair, 3-seat sofa, dining chairs \u00d7 6'))
    b.append(f('Approximate age', 'age'))
    b.append(f('How many?', 'qty'))
    b.append(f('Current condition, in their words', 'condition', 'textarea', full=True))
    b.append('</div>')
    b.append('<div class="wf-sub">What they want</div>')
    b.append('<div class="wf-grid">')
    b.append(checks('Work requested', ['Full reupholstery', 'Recover only', 'Repair',
                                       'Loose covers', 'Cushions only', 'Frame repair',
                                       'Traditional rebuild', 'Not sure \u2014 advise']))
    b.append(f('Fabric \u2014 supplied by', 'fabricby', placeholder='Us / customer / undecided'))
    b.append(f('Fabric preference or budget per metre', 'fabricpref'))
    b.append(f('Timescale \u2014 any deadline?', 'deadline'))
    b.append(f('Budget discussed', 'budget'))
    b.append(f('Photographs received?', 'photos', placeholder='Yes / no / requested'))
    b.append('</div>')
    b.append('<div class="wf-sub">Notes and next action</div><div class="wf-grid">')
    b.append(f('Notes', 'notes', 'textarea', full=True, tall=True))
    b.append(f('Next action', 'next', placeholder='Quote by, visit arranged, awaiting photos'))
    b.append(f('Date promised', 'promised', 'date'))
    b.append('</div>')
    return sheet('enquiry', 'Customer enquiry', ''.join(b))


def form_condition():
    b = []
    b.append('<p class="wf-small">Complete <strong>before</strong> any work starts, ideally at '
             'collection with the customer present. Photograph everything noted here.</p>')
    b.append('<div class="wf-grid">')
    b.append(f('Date', 'date', 'date'))
    b.append(f('Job ref', 'ref'))
    b.append(f('Customer', 'customer'))
    b.append(f('Piece', 'piece'))
    b.append('</div>')
    b.append('<div class="wf-sub">Frame and structure</div><div class="wf-grid">')
    b.append(checks('Found on inspection', ['Loose joints', 'Broken rail', 'Previous repair',
                                            'Woodworm \u2014 old', 'Woodworm \u2014 active',
                                            'Split timber', 'Missing castor', 'Show wood damage',
                                            'Frame sound']))
    b.append(f('Detail', 'framedetail', 'textarea', full=True))
    b.append('</div>')
    b.append('<div class="wf-sub">Upholstery and cover</div><div class="wf-grid">')
    b.append(checks('Found on inspection', ['Webbing failed', 'Springs failed', 'Stuffing displaced',
                                            'Foam perished', 'Cover worn', 'Cover torn', 'Staining',
                                            'Odour', 'Pet damage', 'Previous re-cover over original',
                                            'Fire label present', 'No fire label']))
    b.append(f('Detail', 'covdetail', 'textarea', full=True))
    b.append('</div>')
    b.append('<div class="wf-sub">Existing damage and marks</div><div class="wf-grid">')
    b.append(f('Recorded damage \u2014 be specific about location', 'damage', 'textarea', full=True, tall=True))
    b.append(f('Photographs taken', 'photocount', placeholder='Number, and where stored'))
    b.append(f('Anything the customer pointed out', 'customersaid'))
    b.append('</div>')
    b.append('<hr class="wf-rule">')
    b.append('<p class="wf-small">The customer confirms the condition recorded above is an accurate '
             'description of the piece at the point of collection.</p>')
    b.append('<div class="wf-sign"><div class="wf-f"><label>Customer signature</label>'
             '<input type="text"></div><div class="wf-f"><label>Date</label>'
             '<input type="date"></div></div>')
    return sheet('condition', 'Furniture condition report', ''.join(b))


def form_jobsheet():
    b = []
    b.append('<p class="wf-small">Travels with the piece. One sheet per job.</p>')
    b.append('<div class="wf-grid">')
    b.append(f('Job ref', 'ref'))
    b.append(f('Date in', 'datein', 'date'))
    b.append(f('Promised', 'promised', 'date'))
    b.append(f('Customer', 'customer'))
    b.append(f('Telephone', 'tel', 'tel'))
    b.append(f('Piece', 'piece'))
    b.append('</div>')
    b.append('<div class="wf-sub">Work to be done</div><div class="wf-grid">')
    b.append(checks('Scope', ['Strip to frame', 'Frame repair', 'Re-web', 'Springs',
                              'First stuffing', 'Stitched edge', 'Second stuffing',
                              'New foam', 'Calico', 'Wadding', 'Top cover', 'Cushions',
                              'Buttoning', 'Piping', 'Trim / gimp', 'Nailing', 'Bottom cloth']))
    b.append(f('Detail and special instructions', 'scope', 'textarea', full=True, tall=True))
    b.append('</div>')
    b.append('<div class="wf-sub">Materials</div><div class="wf-grid">')
    b.append(f('Fabric \u2014 name and colour', 'fabric'))
    b.append(f('Supplier', 'supplier'))
    b.append(f('Metres required', 'metres'))
    b.append(f('Pattern repeat', 'repeat'))
    b.append(f('Order date / batch or dye lot', 'batch'))
    b.append(f('Customer\u2019s own material?', 'com', placeholder='Yes / no'))
    b.append(f('Foam spec', 'foam', placeholder='Density, hardness, thickness'))
    b.append(f('Other materials', 'othermat'))
    b.append('</div>')
    b.append('<div class="wf-sub">Compliance</div><div class="wf-grid">')
    b.append(checks('Fire evidence held', ['Cover certificate', 'Composite certificate',
                                           'FR interliner fitted', 'Filling certificates',
                                           'Contract spec required', 'Exempt \u2014 pre-1950',
                                           'Not applicable']))
    b.append(f('Certificate references \u2014 keep with the job record', 'certs', 'textarea', full=True))
    b.append('</div>')
    b.append('<div class="wf-sub">Time and progress</div><div class="wf-grid">')
    b.append(f('Estimated hours', 'esthours'))
    b.append(f('Actual hours', 'acthours'))
    b.append(f('Progress notes', 'progress', 'textarea', full=True))
    b.append(f('Quoted price', 'quoted'))
    b.append(f('Deposit taken', 'deposit'))
    b.append(f('Balance due', 'balance'))
    b.append('</div>')
    b.append('<p class="wf-small">Record actual hours even when the job is priced as a whole. '
             'It is the only way to find out whether your estimates are any good.</p>')
    return sheet('jobsheet', 'Job sheet', ''.join(b))


def form_delivery():
    b = []
    b.append('<p class="wf-small">Two copies \u2014 one for the customer, one for your file. '
             'Use the same form for collection and for delivery.</p>')
    b.append('<div class="wf-grid">')
    b.append(f('Date', 'date', 'date'))
    b.append(f('Job ref', 'ref'))
    b.append(f('Collection or delivery?', 'type', placeholder='Collection / delivery'))
    b.append(f('Customer', 'customer'))
    b.append(f('Address', 'address', 'textarea', full=True))
    b.append(f('Items', 'items', 'textarea', full=True))
    b.append('</div>')
    b.append('<div class="wf-sub">On handover</div><div class="wf-grid">')
    b.append(checks('Confirmed', ['Work as agreed', 'Customer has inspected',
                                  'Aftercare advice given', 'Fire label attached where required',
                                  'Offcuts returned', 'Balance settled', 'Balance outstanding']))
    b.append(f('Notes or anything raised', 'notes', 'textarea', full=True))
    b.append(f('Balance outstanding', 'balance'))
    b.append(f('Payment method', 'paymethod'))
    b.append('</div>')
    b.append('<hr class="wf-rule">')
    b.append('<div class="wf-sign"><div class="wf-f"><label>Received by</label>'
             '<input type="text"></div><div class="wf-f"><label>Date</label>'
             '<input type="date"></div></div>')
    return sheet('delivery', 'Collection & delivery note', ''.join(b))


JS = """<script>
(function(){
  var KEY='ltu-workshop-forms-biz';
  var ids=['bizName','bizContact'];
  function apply(){
    var n=(document.getElementById('bizName')||{}).value||'';
    var c=(document.getElementById('bizContact')||{}).value||'';
    Array.prototype.forEach.call(document.querySelectorAll('[data-biz="name"]'),function(el){
      el.textContent = n || 'Your workshop';
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-biz="contact"]'),function(el){
      el.textContent = c;
    });
  }
  function save(){
    try{
      localStorage.setItem(KEY, JSON.stringify({
        n:(document.getElementById('bizName')||{}).value||'',
        c:(document.getElementById('bizContact')||{}).value||''
      }));
    }catch(e){}
  }
  function load(){
    try{
      var d=JSON.parse(localStorage.getItem(KEY)||'{}');
      if(d.n && document.getElementById('bizName')) document.getElementById('bizName').value=d.n;
      if(d.c && document.getElementById('bizContact')) document.getElementById('bizContact').value=d.c;
    }catch(e){}
  }
  load(); apply();
  ids.forEach(function(id){
    var el=document.getElementById(id);
    if(el) el.addEventListener('input',function(){apply();save();});
  });

  // Print one form: hide the others for the duration of the print only.
  Array.prototype.forEach.call(document.querySelectorAll('[data-print]'),function(btn){
    btn.addEventListener('click',function(){
      var keep=btn.getAttribute('data-print');
      var sheets=document.querySelectorAll('.wf-sheet');
      var hidden=[];
      Array.prototype.forEach.call(sheets,function(s){
        if(s.id!==keep){ s.style.display='none'; hidden.push(s); }
      });
      window.print();
      setTimeout(function(){ hidden.forEach(function(s){ s.style.display=''; }); },300);
    });
  });
  var all=document.getElementById('wfPrintAll');
  if(all) all.addEventListener('click',function(){ window.print(); });
})();
</script>"""


def schema():
    return ('<script type="application/ld+json">\n'
            '{"@context":"https://schema.org","@graph":['
            '{"@type":"WebApplication","@id":"%s/workshop-forms#app",'
            '"name":"Upholstery workshop forms","applicationCategory":"BusinessApplication",'
            '"operatingSystem":"Any","url":"%s/workshop-forms",'
            '"description":"Four free printable forms for an upholstery workshop: customer enquiry, '
            'furniture condition report, job sheet, and collection and delivery note.",'
            '"offers":{"@type":"Offer","price":"0","priceCurrency":"GBP"},'
            '"author":{"@type":"Person","@id":"%s/about#shaun","name":"Shaun Greenwood"},'
            '"publisher":{"@type":"Organization","@id":"%s#org","name":"Learn to Upholster"}},'
            '{"@type":"FAQPage","@id":"%s/workshop-forms#faq","mainEntity":['
            '{"@type":"Question","name":"What paperwork does an upholstery workshop need?",'
            '"acceptedAnswer":{"@type":"Answer","text":"Four documents cover most jobs: an enquiry '
            'form to capture the first contact, a condition report recording the state of the piece '
            'before work starts, a job sheet that travels with the furniture through the workshop, '
            'and a collection and delivery note signed at handover. A quote and invoice sit '
            'alongside these."}}]}]}\n</script>' % (SITE, SITE, SITE, SITE, SITE))


def main():
    pre, mid, tail = get_chrome()
    today = datetime.date.today()

    intro = (
        '<p class="lede wf-intro">Four forms that carry a job through the workshop: the enquiry, '
        'the condition report, the job sheet, and the note that gets signed at handover. '
        'Free, no download and no account \u2014 fill them in on screen and print, or print '
        'them blank and fill them in at the bench.</p>\n'
        '  <div class="wf-setup">\n'
        '    <h2>Put your details on them</h2>\n'
        '    <div class="row">\n'
        '      <div><label for="bizName">Workshop name</label>'
        '<input id="bizName" type="text" placeholder="Your workshop"></div>\n'
        '      <div><label for="bizContact">Telephone, email or address</label>'
        '<input id="bizContact" type="text" placeholder="01234 567890 \u00b7 you@example.com"></div>\n'
        '    </div>\n'
        '    <p class="wf-note">Saved in this browser only, and never sent anywhere. '
        '<button class="wf-print" id="wfPrintAll" type="button">Print all four</button></p>\n'
        '  </div>\n'
        '  <ul class="wf-index">\n'
        '    <li><a href="#enquiry">Customer enquiry</a>'
        '<p>Taken on the first phone call or email, so nothing is forgotten before you quote.</p></li>\n'
        '    <li><a href="#condition">Furniture condition report</a>'
        '<p>Completed before you touch the piece. The form that prevents arguments about damage.</p></li>\n'
        '    <li><a href="#jobsheet">Job sheet</a>'
        '<p>Travels with the furniture: scope, materials, fire certificates, hours and progress.</p></li>\n'
        '    <li><a href="#delivery">Collection &amp; delivery note</a>'
        '<p>Signed at handover. Two copies, one each.</p></li>\n'
        '  </ul>\n'
        '  <p>The quote and invoice are covered separately by the free '
        '<a href="/invoice-template">quote and invoice spreadsheet</a>, which does the arithmetic. '
        'These four are the workshop half \u2014 the paper that stays with you.</p>\n'
        '  <p class="wf-small">Written for use anywhere. Where a form mentions fire certificates '
        'or labels, check what applies in your own country \u2014 the '
        '<a href="/fire-safety-checker">fire regulations checker</a> covers the UK position.</p>')

    body = ('<article class="article wrap read">\n  %s\n\n  %s\n  %s\n  %s\n  %s\n</article>'
            % (intro, form_enquiry(), form_condition(), form_jobsheet(), form_delivery()))

    desc = ('Four free printable forms for an upholstery workshop: customer enquiry, condition '
            'report, job sheet, and delivery note. No download, no account.')
    page = swap_head(pre, 'Workshop forms \u2014 free printable upholstery paperwork',
                     desc, SITE + '/workshop-forms')
    page = page.replace('</head>', CSS + '\n' + schema() + '\n</head>', 1)
    page += ('<header class="chapter-head">\n  <div class="wrap">\n'
             '    <p class="chno">Free tools</p>\n    <h1>Workshop forms</h1>\n'
             '    <p class="updated">Last updated: <time datetime="%s">%s</time></p>\n'
             '  </div>\n</header>' % (today.isoformat(), today.strftime('%-d %B %Y')))

    open(OUT, 'w', encoding='utf-8').write(page + mid + body + JS + tail)
    print('%s written \u2014 4 printable forms' % OUT)
    print('   enquiry, condition report, job sheet, collection & delivery note')


if __name__ == '__main__':
    main()
