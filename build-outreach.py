#!/usr/bin/env python3
"""
build-outreach.py — one message per listed supplier, ready to send.

Writes outreach/supplier-outreach.md: a working checklist with an individual,
personalised message for every supplier in the directory, each linking to that
supplier's own anchor on the page.

Nothing is sent. This produces drafts for you to work through by hand.

    python3 build-outreach.py

Two rules built into the wording, both deliberate:

  It asks for nothing. Not a link, not a mention, not a reply. Telling a
  business they are listed in a free directory is useful information; asking
  for a link in return turns it into an exchange, and "requiring links as part
  of an agreement" is exactly what Google names as a link scheme. Any link that
  comes back from this is editorial, which is the only kind worth having.

  One message at a time, to a named business, about their own entry. A BCC
  blast to fifty-nine addresses is spam however politely it is written.
"""

import os, re, sys, html as H, textwrap, importlib.util, datetime
from urllib.parse import quote, urljoin

SITE = 'https://www.learntoupholster.com'
OUT_DIR = 'outreach'
OUT = os.path.join(OUT_DIR, 'supplier-outreach.md')
OUT_HTML = os.path.join(OUT_DIR, 'supplier-outreach.html')


def icon_slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def load():
    spec = importlib.util.spec_from_file_location('sd', 'supplier-data.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


SUBJECT_SHOP = "You're listed on Learn to Upholster's supplier directory"
SUBJECT_HOUSE = "{name} on the Learn to Upholster supplier directory"



def contact_guesses(url):
    """Likely contact pages. Not fetched — these are just links to try.

    Deliberately not scraped for email addresses. Harvesting business emails to
    bulk-mail them is the wrong side of PECR for sole traders and partnerships,
    and it is also how a sending domain gets flagged. Use the form.
    """
    return [urljoin(url, p) for p in ('/contact', '/contact-us', '/pages/contact')]


def mailto(subject, body, to=''):
    """A mailto: your own client opens, pre-filled. You still press send."""
    return 'mailto:%s?subject=%s&body=%s' % (
        quote(to), quote(subject, safe=''), quote(body, safe=''))


def body(entry, catnames, date):
    name = entry['name']
    anchor = '%s/suppliers#s-%s' % (SITE, icon_slug(name))
    cats = ', '.join(catnames.get(c, c).lower() for c in entry['cats'])
    house = 'fabrichouse' in entry['cats']

    what = ('one of the fabric houses upholsterers are pointed to when they are '
            'looking for cloth' if house else
            'a place to buy %s' % cats)

    intro = textwrap.fill(
        'I have put together a supplier directory so that upholsterers, particularly '
        'people starting out, can find out where to actually buy materials. '
        f'{name} is listed as {what}:', width=76)

    return f"""Hello,

I run learntoupholster.com — a free upholstery reference: the full text of my
book, calculators, and guidance for people working in the trade. I am an
AMUSF-accredited upholsterer with thirty years at the bench, and the site has no
paywall and takes no advertising from suppliers.

{intro}

{anchor}

There is nothing to do and nothing to pay. Nobody buys a listing and there are
no affiliate links on the page — I compiled it because "where do I get jute
webbing" is one of the most common questions I am asked and there was no decent
answer anywhere.

I checked your site was live on {date} and re-check the whole list every six
months. If anything in your entry is wrong, or you would rather not be listed at
all, tell me and I will change or remove it the same day.

Best wishes,

Shaun Greenwood
Master Upholsterer, AMUSF accredited
learntoupholster.com
"""



HTML_HEAD = """<!doctype html>
<meta charset="utf-8">
<title>Supplier outreach</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
 body{font:16px/1.55 system-ui,-apple-system,sans-serif;max-width:52rem;margin:2rem auto;
   padding:0 1.2rem;color:#2A2622;background:#FBF6ED}
 h1{font-size:1.6rem;margin:0 0 .3rem} h2{margin:2.4rem 0 .6rem;border-bottom:2px solid #22382C;
   padding-bottom:.25rem;color:#22382C}
 .note{background:#fff;border-left:4px solid #C19A4B;padding:.9rem 1.1rem;border-radius:3px;margin:1rem 0}
 .note ul{margin:.4rem 0 0;padding-left:1.1rem}
 .card{background:#fff;border:1px solid #E2DACB;border-radius:4px;padding:1rem 1.2rem;margin:0 0 1rem}
 .card.done{opacity:.45}
 .card h3{margin:0 0 .4rem;font-size:1.1rem;display:flex;align-items:center;gap:.5rem}
 .card h3 input{width:1.05rem;height:1.05rem}
 .links{font-size:.92rem;margin:.3rem 0 .7rem}
 .links a{margin-right:.9rem}
 .btn{display:inline-block;background:#22382C;color:#FBF6ED;padding:.42rem .9rem;border-radius:3px;
   text-decoration:none;font-weight:600;font-size:.92rem}
 pre{background:#F2EAD9;padding:.8rem .9rem;border-radius:3px;white-space:pre-wrap;
   font:13px/1.5 ui-monospace,monospace;margin:.5rem 0 0}
 details summary{cursor:pointer;font-size:.92rem;color:#22382C}
 .prog{position:sticky;top:0;background:#FBF6ED;padding:.6rem 0;font-weight:600;border-bottom:1px solid #E2DACB}
</style>
"""


def write_html(order, by_country, data, catnames, today):
    """A clickable version. The markdown is for reading; this is for working.

    Progress is kept in localStorage so ticking a box survives a page reload.
    Nothing leaves the browser and nothing is sent from here.
    """
    o = [HTML_HEAD, '<h1>Supplier outreach</h1>',
         '<p>One message per listed supplier. Nothing is sent from this page \u2014 '
         'the buttons open your own mail client with the message already written.</p>',
         '<div class="note"><strong>Before you start</strong><ul>'
         '<li>Send them one at a time, from your own address. Never BCC a batch.</li>'
         '<li>Most have a contact form rather than a published address \u2014 use it and paste the message in.</li>'
         '<li><strong>Do not bulk-send through Resend.</strong> That account also carries your quotes and '
         'order confirmations, and cold outreach is how a sending domain gets flagged.</li>'
         '<li>The message asks for nothing on purpose. Anything that comes back is then genuinely editorial.</li>'
         '<li>If anyone asks to be removed, remove them that day and thank them.</li>'
         '</ul></div>',
         '<p class="prog" id="prog"></p>']

    for c in order:
        o.append('<h2>%s</h2>' % H.escape(data.COUNTRIES.get(c, c)))
        for s in sorted(by_country[c], key=lambda x: ('fabrichouse' in x['cats'], x['name'].lower())):
            house = 'fabrichouse' in s['cats']
            subj = SUBJECT_HOUSE.format(name=s['name']) if house else SUBJECT_SHOP
            msg = body(s, catnames, today)
            anchor = '%s/suppliers#s-%s' % (SITE, icon_slug(s['name']))
            guesses = contact_guesses(s['url'])
            o.append(
                '<div class="card" data-k="%s">'
                '<h3><input type="checkbox"> %s</h3>'
                '<p class="links"><a href="%s" target="_blank" rel="noopener">their site</a>'
                '<a href="%s" target="_blank" rel="noopener">their entry</a>'
                '<a href="%s" target="_blank" rel="noopener">contact page?</a></p>'
                '<p><a class="btn" href="%s">Open a pre-filled email</a></p>'
                '<details><summary>Show the message</summary><pre>%s</pre></details>'
                '</div>'
                % (icon_slug(s['name']), H.escape(s['name']), H.escape(s['url']),
                   anchor, H.escape(guesses[0]), H.escape(mailto(subj, msg)), H.escape(msg)))

    o.append("""<script>
var K='ltu-outreach-done';
function load(){try{return JSON.parse(localStorage.getItem(K)||'{}');}catch(e){return {};}}
var done=load();
function updateProgress(){
  var cards=document.querySelectorAll('.card');
  var n=Object.keys(done).filter(function(k){return done[k];}).length;
  document.getElementById('prog').textContent=n+' of '+cards.length+' contacted';
}
document.querySelectorAll('.card').forEach(function(card){
  var k=card.getAttribute('data-k'), box=card.querySelector('input');
  if(done[k]){box.checked=true;card.classList.add('done');}
  box.addEventListener('change',function(){
    done[k]=box.checked; card.classList.toggle('done',box.checked);
    try{localStorage.setItem(K,JSON.stringify(done));}catch(e){}
    updateProgress();
  });
});
updateProgress();
</script>""")
    open(OUT_HTML, 'w', encoding='utf-8').write('\n'.join(o))


def main():
    if not os.path.exists('supplier-data.py'):
        sys.exit('Run this from ~/learntoupholster.')
    data = load()
    catnames = {k: l for k, l, _ in data.CATEGORIES}
    os.makedirs(OUT_DIR, exist_ok=True)

    by_country = {}
    for s in data.SUPPLIERS:
        if s.get('disclosure'):        # your own business; no letter needed
            continue
        by_country.setdefault(s['country'], []).append(s)

    order = [c for c in ('GB', 'US', 'CA', 'AU', 'NZ') if c in by_country]
    order += sorted(c for c in by_country if c not in order)

    n = sum(len(v) for v in by_country.values())
    out = [
        '# Supplier outreach',
        '',
        'One message per listed supplier. Nothing has been sent.',
        '',
        f'**{n} to contact.** Tick them off as you go. A handful a night is plenty —',
        'these go one at a time, to a named business, about their own entry.',
        '',
        '## Before you start',
        '',
        '- Each entry has an **Open a pre-filled email** link. Click it and your own mail client opens with the subject and message already written. Add the address, read it once, send. You send it, not a machine.',
        '- Most of these have a contact form rather than a published address. Use it, and paste the message in. Do not go hunting for personal emails to harvest.',
        '- **Do not bulk-send this through Resend or anything like it.** That account also sends your quotes and order confirmations, and cold outreach is how a sending domain gets flagged. Losing transactional email to save a fortnight of evenings is a bad trade.',
        '- **Do not ask for a link.** The message below deliberately asks for nothing. Anything that comes back is then genuinely editorial, which is the only kind of link worth having.',
        '- Send from your own address, individually. Never BCC a batch.',
        '- If someone asks to be removed, remove them that day and say thank you. A directory people trust is worth more than one more entry.',
        '',
        '## Priority',
        '',
        'Start with the UK general suppliers — they are the likeliest to care about a',
        'British reference site and the quickest to reply. Fabric houses are larger and',
        'slower; leave those until you have the hang of it.',
        '',
        '---',
        '',
    ]

    today = datetime.date.fromisoformat(data.VERIFIED).strftime('%-d %B %Y')

    for c in order:
        out.append('## %s' % data.COUNTRIES.get(c, c))
        out.append('')
        for s in sorted(by_country[c], key=lambda x: ('fabrichouse' in x['cats'], x['name'].lower())):
            house = 'fabrichouse' in s['cats']
            subj = SUBJECT_HOUSE.format(name=s['name']) if house else SUBJECT_SHOP
            out.append('### [ ] %s' % s['name'])
            out.append('')
            msg = body(s, catnames, today)
            guesses = contact_guesses(s['url'])
            out.append('Website: %s' % s['url'])
            out.append('Their entry: %s/suppliers#s-%s' % (SITE, icon_slug(s['name'])))
            out.append('')
            out.append('- [Open a pre-filled email](%s) \u2014 opens your mail client with '
                       'the subject and message already in it. Add their address and send.'
                       % mailto(subj, msg))
            out.append('- Contact page, most likely: %s' % ' \u00b7 '.join(
                '[%s](%s)' % (g.rsplit('/', 1)[-1] or 'contact', g) for g in guesses))
            out.append('')
            out.append('**Subject:** %s' % subj)
            out.append('')
            out.append('```')
            out.append(msg)
            out.append('```')
            out.append('')
        out.append('---')
        out.append('')

    open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
    write_html(order, by_country, data, catnames, today)
    print('%s written \u2014 %d messages' % (OUT, n))
    print('%s written \u2014 open this one in a browser and click through' % OUT_HTML)
    for c in order:
        print('   %-4s %d' % (c, len(by_country[c])))
    print('\nNothing sent. Work through it at your own pace.')


if __name__ == '__main__':
    main()
