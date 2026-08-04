#!/usr/bin/env python3
"""
build-sewing.py — Phase 1 of the sewing section.

Generates:
    sewing.html              hub
    sewing-thread.html       thread guide
    sewing-needles.html      needle guide

Content comes from sewing-data.py, where every figure is corroborated across at
least two independent trade sources. Page chrome is lifted from an existing page
at build time, so the section matches any restyling automatically \u2014 same
approach as build-fire.py and build-business.py.

Run before build-inline.py.
"""

import os, re, sys, html, datetime, importlib.util

SITE = 'https://www.learntoupholster.com'
CHROME_FROM = 'webbing.html'
OG = SITE + '/assets/og-card.jpg'


def load():
    spec = importlib.util.spec_from_file_location('sd', 'sewing-data.py')
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
             '    <a href="/sewing"><span class="dir">Sewing</span><br>'
             '<span class="ttl">Machines, thread and needles \u2192</span></a>\n'
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
.sw-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem;margin:1.6rem 0}
.sw-card{background:#fff;border:1px solid var(--rule);border-radius:3px;padding:1rem 1.2rem;
  text-decoration:none;display:block;color:var(--ink)}
.sw-card:hover{border-color:var(--green-deep)}
.sw-card h2{font-family:var(--display);font-size:1.14rem;margin:0 0 .3rem;color:var(--green-deep)}
.sw-card p{margin:0;font-size:.95rem}
.sw-card .soon{font-size:.82rem;background:var(--cream-deep);border-radius:2px;
  padding:.1rem .45rem;display:inline-block;margin-top:.5rem}
.sw-table{width:100%;border-collapse:collapse;margin:1rem 0;font-size:.94rem}
.sw-table th,.sw-table td{text-align:left;padding:.45rem .6rem;border-bottom:1px solid var(--rule);
  vertical-align:top}
.sw-table th{font-family:var(--display);color:var(--green-deep);white-space:nowrap}
.sw-table td.n{white-space:nowrap;font-variant-numeric:tabular-nums}
.sw-table tr.hi td{background:var(--cream-deep)}
@media(max-width:700px){
  /* Six columns will not fit a phone. Restack each row as its own labelled
     block rather than forcing a sideways scroll, which is unusable one-handed. */
  .sw-table,.sw-table tbody,.sw-table tr,.sw-table td{display:block;width:100%;box-sizing:border-box}
  .sw-table thead{position:absolute;left:-9999px}
  .sw-table tr{background:#fff;border:1px solid var(--rule);border-radius:3px;
    padding:.55rem .7rem;margin:0 0 .7rem}
  .sw-table tr.hi{background:var(--cream-deep)}
  .sw-table td{border:0;padding:.2rem 0;display:flex;gap:.6rem;align-items:baseline}
  .sw-table td::before{content:attr(data-l);flex:0 0 8.4rem;font-size:.8rem;font-weight:600;
    text-transform:uppercase;letter-spacing:.02em;color:var(--green-deep)}
  .sw-table td.n{white-space:normal}
  .sw-table tr.hi td{background:transparent}
}
.sw-note{background:var(--cream-deep);border-left:4px solid var(--gold);border-radius:3px;
  padding:.9rem 1.1rem;margin:1.3rem 0;font-size:.97rem}
.sw-warn{background:#fff;border-left:4px solid var(--terracotta);border-radius:3px;
  padding:.9rem 1.1rem;margin:1.3rem 0;font-size:.97rem}
.sw-cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.1rem;margin:1.2rem 0}
.sw-fib{background:#fff;border:1px solid var(--rule);border-radius:3px;padding:1rem 1.2rem}
.sw-fib h3{font-family:var(--display);font-size:1.1rem;margin:0 0 .2rem;color:var(--green-deep)}
.sw-fib .best{font-size:.9rem;margin:0 0 .6rem}
.sw-fib ul{margin:.2rem 0 .7rem;padding-left:1.1rem;font-size:.95rem}
.sw-fib .h{font-weight:600;font-size:.88rem;color:var(--green-deep);margin:.4rem 0 .1rem}
.sw-fib .also{font-family:var(--body);font-size:.8rem;font-weight:400;color:var(--ink);display:block}
.fr-tags{margin:0 0 .5rem}
.fr-tag{display:inline-block;border-radius:2px;padding:.12rem .5rem;font-size:.8rem;font-weight:600}
.v-no{background:var(--terracotta);color:#fff}
.v-mid{background:var(--cream-deep);color:var(--ink);border:1px solid var(--rule)}
.v-ok{background:var(--gold);color:#22382C}
.v-yes{background:var(--green-deep);color:var(--cream)}
.tr-nav{list-style:none;padding:0;margin:0 0 1.8rem;display:flex;flex-wrap:wrap;gap:.5rem}
.tr-nav a{display:block;background:#fff;border:1px solid var(--rule);border-radius:99px;
  padding:.35rem .85rem;text-decoration:none;font-size:.93rem}
.tr-nav a:hover{border-color:var(--green-deep)}
.tr-sym{background:#fff;border:1px solid var(--rule);border-left:4px solid var(--green-deep);
  border-radius:3px;padding:1.1rem 1.3rem;margin:0 0 1.3rem}
.tr-sym h2{font-family:var(--display);font-size:1.25rem;margin:0 0 .3rem;color:var(--green-deep)}
.tr-what{font-size:.96rem;margin:0 0 .8rem}
.tr-checks{margin:0;padding-left:1.3rem}
.tr-checks li{margin:0 0 .7rem;font-size:.96rem}
.sw-src{font-size:.88rem;border-top:1px solid var(--rule);margin-top:1.8rem;padding-top:.9rem}
.sw-src ul{margin:.3rem 0 .7rem;padding-left:1.1rem}
</style>"""


def sources_block(sources, checked):
    """A practical note rather than a citation list.

    Thread and needle sizing is standardised engineering fact \u2014 it does not
    shift with jurisdiction or get amended the way fire regulations do, so the
    citation apparatus those pages need would only be clutter here. What does
    matter is that manufacturers vary at the margins, which is the point worth
    making instead.
    """
    return ('<div class="sw-src">\n'
            '  <p>Sizing is standardised, so these numbers hold wherever you work. '
            'Manufacturers do vary slightly at the margins, though \u2014 if your thread '
            'supplier publishes a chart for their own product, it beats any general table '
            'including this one.</p>\n</div>')


def build_thread(pre, mid, tail, d):
    rows = ''.join(
        '<tr%s><td class="n" data-l="Tex"><strong>%s</strong></td>'
        '<td class="n" data-l="Commercial">%s</td><td class="n" data-l="Ticket">%s</td>'
        '<td class="n" data-l="Govt.">%s</td><td class="n" data-l="Usual needle">%s</td>'
        '<td data-l="For">%s</td></tr>'
        % (' class="hi"' if s['tex'] == 'T70' else '', s['tex'], s['commercial'], s['ticket'],
           s['govt'], s['common'], html.escape(s['use']))
        for s in d.THREAD_SIZES)

    choices = ''.join(
        '<tr><td data-l="Job"><strong>%s</strong></td><td data-l="Thread">%s</td>'
        '<td class="n" data-l="Size">%s</td><td data-l="Why">%s</td></tr>'
        % (html.escape(c['job']), html.escape(c['thread']), c['size'], c['why'])
        for c in d.CHOICES)

    fibres = ''.join(
        '<div class="sw-fib"><h3>%s</h3><p class="best">Best for: %s</p>'
        '<p class="h">In its favour</p><ul>%s</ul>'
        '<p class="h">Against it</p><ul>%s</ul></div>'
        % (html.escape(f['name']), html.escape(f['best']),
           ''.join('<li>%s</li>' % p for p in f['pros']),
           ''.join('<li>%s</li>' % c for c in f['cons']))
        for f in d.FIBRES)

    body = (
        '<article class="article wrap read">\n'
        '  <p class="lede">Which thread for which job, what the three numbering systems mean, '
        'and the one property that decides nylon or polyester.</p>\n\n'

        '  <div class="sw-note"><p><strong>If you read nothing else:</strong> use bonded '
        '<strong>polyester</strong> for anything that will see sunlight \u2014 marine, motorcycle, '
        'garden, campervan, caravan \u2014 and bonded <strong>nylon</strong> for indoor work and '
        'vehicle interiors. <strong>T70</strong> is the everyday upholstery size. Most people who '
        'get this wrong put nylon somewhere sunny.</p></div>\n\n'

        '  <h2>Four numbering systems, one thread</h2>\n'
        '  <p>The same cone is sold under four sets of numbers depending on who made it and where '
        'you are, which is most of why this is confusing.</p>\n'
        '  <ul>\n'
        '    <li><strong>Tex</strong> \u2014 the international standard, and the one worth '
        'learning. It is the weight in grams of 1,000 metres, so a higher number is a thicker '
        'thread. T70 weighs 70 g per kilometre.</li>\n'
        '    <li><strong>Commercial size</strong> (#69, #92) \u2014 the North American trade standard, '
        'derived from denier. Common worldwide because so much bonded thread is made to it.</li>\n'
        '    <li><strong>Ticket number</strong> (Tkt 40, Tkt 20) \u2014 what is printed on Coats and '
        'G\u00fctermann cones, so it is what a great many upholsterers outside North America '
        'actually buy by. <strong>It runs backwards:</strong> a higher ticket number is a '
        '<em>finer</em> thread.</li>\n'
        '    <li><strong>Government size</strong> (E, F, FF) \u2014 a US military legacy, still '
        'printed on a good deal of thread wherever it is sold.</li>\n'
        '  </ul>\n'
        '  <p>They line up like this. The needle column gives the size most people reach for; there is '
        'a workable range either side of it, set out on the <a href="/sewing-needles">needle '
        'page</a>.</p>\n'
        '  <table class="sw-table"><thead><tr><th>Tex</th><th>Commercial</th><th>Ticket</th>'
        '<th>Govt.</th><th>Usual needle</th><th>What it is for</th></tr></thead><tbody>%s</tbody></table>\n'
        '  <p class="fine">T70 is highlighted because it is the size you will use most, and the '
        'heaviest a domestic machine will generally manage. Ticket equivalents are the nearest '
        'standard ticket to (1,000 \u00f7 Tex) \u00d7 3, so treat them as close rather than exact.</p>\n\n'

        '  <div class="sw-note"><p><strong>Why #69 and T70 are nearly but not quite the same '
        'number.</strong> Both are calculated from denier, the weight in grams of 9,000 metres, but '
        'by different divisors. A bonded nylon of three 210-denier plies is 630 denier: divide by 9 '
        'and you get Tex 70; multiply by 0.11 and you get commercial size 69. The same thread, two '
        'sums. Polyester at the same ticket uses 220-denier plies, which works out at Tex 73 \u2014 '
        'and is still sold as T70, because Tex sizes are bracketed into fixed steps and anything '
        'between them rounds to the nearest. That is why you never see a T73.</p></div>\n\n'

        '  <h2>Nylon or polyester</h2>\n'
        '  <p>Both are bonded, both are strong, and for most indoor work either will do. The '
        'difference that actually decides it is ultraviolet light.</p>\n'
        '  <div class="sw-cols">%s</div>\n'
        '  <div class="sw-warn"><p><strong>The mistake worth avoiding.</strong> Nylon is the '
        'stronger, more abrasion-resistant thread, so it feels like the better choice \u2014 and '
        'people reach for it out of habit. Put it in a boat, a motorcycle seat or a campervan and '
        'the sun will have it long before the seam wears out. In sunlight, polyester wins on the '
        'only property that matters there.</p></div>\n\n'

        '  <h2>What is bonded thread?</h2>\n'
        '  <p>A resin coating applied after twisting. It binds the plies together so the thread '
        'resists untwisting as it runs through the machine, reduces friction at the needle, and '
        'stops the end fraying when you thread up. For any upholstery work at speed, bonded is '
        'what you want \u2014 unbonded thread of the same size will fray and snarl.</p>\n\n'

        '  <h2>Which thread for what</h2>\n'
        '  <table class="sw-table"><thead><tr><th>Job</th><th>Thread</th><th>Size</th>'
        '<th>Why</th></tr></thead><tbody>%s</tbody></table>\n\n'

        '  <h2>S twist and Z twist \u2014 and why the trade contradicts itself</h2>\n'
        '  <p>Plied thread is twisted in one of two directions, described as <strong>S</strong> or '
        '<strong>Z</strong>. Sewing machines are built around one of them, and using the wrong one '
        'makes the thread untwist as it runs, which shows up as fraying, snarling and broken '
        'thread that no amount of tension adjustment will fix.</p>\n'
        '  <p><strong>Machine sewing thread should have a final Z twist.</strong> That is true for '
        'domestic, industrial and longarm machines alike, and for every major brand. S twist is '
        'for hand sewing, and for the outside needle of certain twin-needle machines built for it.</p>\n'
        '  <div class="sw-warn"><p><strong>Ignore \u201cleft twist\u201d and \u201cright twist\u201d.</strong> '
        'The trade uses those terms inconsistently. One large supplier\u2019s thread guide calls Z twist '
        'the left twist while their own blog describes S twist as clockwise; another supplier '
        'reverses the pair entirely. The S and Z labels are unambiguous and the left/right ones are '
        'not, so buy on S or Z and disregard the rest.</p></div>\n\n'

        '  <h2>Can a domestic machine sew upholstery thread?</h2>\n'
        '  <p>Up to <strong>T70</strong>, usually yes \u2014 that is the recognised ceiling for '
        'domestic machines, and it is enough for a great deal of furniture work. Above it you need '
        'an industrial machine: T90 and up want a larger needle, a bigger hook and more thread path '
        'than a domestic head is built for. Forcing it produces skipped stitches and, eventually, '
        'a timing problem.</p>\n\n'

        '  <div class="sw-note"><p><strong>Want this worked out for you?</strong> The '
        '<a href="/sewing-selector">thread and needle selector</a> takes three questions and '
        'returns the thread, size, needle, point and stitch length for the job, with the reasoning '
        'for each.</p></div>\n'
        '  <p>Also in this section: <a href="/sewing-needles">needles</a> \u00b7 '
        '<a href="/sewing-machines">machines</a> \u00b7 '
        '<a href="/sewing-troubleshooting">troubleshooting</a> \u00b7 '
        '<a href="/sewing-setup">setup</a> \u00b7 '
        '<a href="/sewing">everything</a>.</p>\n\n  %s\n</article>'
        % (rows, fibres, choices, sources_block(d.SOURCES_THREAD, d.CHECKED)))

    desc = ('Which upholstery thread for which job: bonded nylon or polyester, Tex sizes, '
            'commercial and government numbering, and needle pairing.')
    url = SITE + '/sewing-thread'
    page = swap_head(pre, 'Upholstery thread guide \u2014 sizes, nylon vs polyester', desc, url)
    page = page.replace('</head>', CSS + '\n' + thread_schema(url) + '\n</head>', 1)
    page += header('Sewing \u00b7 Thread', 'Upholstery thread guide')
    open('sewing-thread.html', 'w', encoding='utf-8').write(page + mid + body + tail)


def build_needles(pre, mid, tail, d):
    rows = ''.join(
        '<tr%s><td class="n" data-l="Thread"><strong>%s</strong></td>'
        '<td class="n" data-l="Commercial">%s</td><td class="n" data-l="Range">%s</td>'
        '<td class="n" data-l="Usual"><strong>%s</strong></td>'
        '<td data-l="Typical work">%s</td></tr>'
        % (' class="hi"' if s['tex'] == 'T70' else '', s['tex'], s['commercial'],
           s['needle'], s['common'], html.escape(s['use']))
        for s in d.THREAD_SIZES)

    body = (
        '<article class="article wrap read">\n'
        '  <p class="lede">Needle size follows thread size. Get the pairing wrong and no amount '
        'of tension adjustment will save the seam.</p>\n\n'

        '  <div class="sw-note"><p><strong>The principle.</strong> The needle has to make a hole '
        'big enough for the thread to pass through twice \u2014 down and back \u2014 without '
        'chafing, but no bigger than it needs to be. Too fine and the thread frays and breaks. '
        'Too coarse and you leave visible holes and a weak seam.</p></div>\n\n'

        '  <h2>Thread to needle</h2>\n'
        '  <p>Published as ranges, because that is how the thread makers give them. Within a '
        'range, go finer for a tight weave and coarser for something dense or layered.</p>\n'
        '  <table class="sw-table"><thead><tr><th>Thread (Tex)</th><th>Commercial</th>'
        '<th>Workable range</th><th>Usual choice</th><th>Typical work</th></tr></thead>'
        '<tbody>%s</tbody></table>\n\n'

        '  <div class="sw-warn"><p><strong>Published charts do not agree with each other.</strong> '
        'The two most widely cited differ by roughly one size step across the middle of the range '
        '\u2014 one recommends 125/20 to 140/22 for T135, the other 140/22 to 180/24 for the same '
        'thread. Neither is wrong. Needle choice depends on the material as much as the thread, so '
        'there is a workable band rather than a single correct answer. The ranges above span both '
        'charts; the usual column is where most people land.</p></div>\n\n'

        '  <div class="sw-note"><p><strong>And not every size is stocked everywhere.</strong> '
        'Walking foot needles are often sold in packs of Singer sizes 18, 20, 21, 23 and 24 \u2014 '
        'metric 110, 125, 130, 160 and 180. So a chart telling you to fit a 140/22 or a 200/25 may '
        'be sending you after something your usual supplier does not carry. Where that happens, '
        'take the nearest stocked size within the range and test on an offcut. The band exists for '
        'exactly this reason.</p></div>\n\n'

        '  <h2>Reading needle sizes</h2>\n'
        '  <p>Needles carry two numbers, such as <strong>110/18</strong>. They are two names for '
        'one needle, not two measurements.</p>\n'
        '  <p>The first is <strong>NM</strong>, the metric number: the blade diameter in hundredths '
        'of a millimetre, so 110 means 1.10 mm. Schmetz specify that it is measured above the scarf '
        'or the short groove, and not at any reinforced part of the blade \u2014 which is why a '
        'reinforced needle can measure thicker than its number in places. The system was fixed in '
        '1942 to replace some forty competing ones.</p>\n'
        '  <p>The second is the older American, or Singer, size. It is an arbitrary scale rather '
        'than a measurement, but it maps consistently: NM 110 is always an 18.</p>\n\n'

        '  <h2>Needle systems</h2>\n'
        '  <p>A system is a shank diameter and a length. It has nothing to do with size. A needle '
        'of the right size in the wrong system will not fit, or will not time correctly.</p>\n'
        '  <ul>\n'
        '    <li><strong>135\u00d716 and 135\u00d717</strong> \u2014 the walking foot system, and '
        'the one most upholsterers use. The two are <em>interchangeable</em>: same shank, same '
        'length, different point. 135\u00d716 is the leather point, 135\u00d717 the round point '
        'for cloth. Also sold as DP\u00d716 and DP\u00d717.</li>\n'
        '    <li><strong>134</strong> \u2014 many flat-bed lockstitch machines. Also sold as '
        '135\u00d75, 135\u00d77 and DP\u00d75.</li>\n'
        '    <li><strong>DB\u00d71</strong> \u2014 common on lighter industrial lockstitch heads. '
        'Watch this one: the shank is 1.63 mm up to 110/18, and above that size the same needle is '
        'made on a 2.00 mm shank and becomes system 134. To stay on the narrow shank at larger '
        'sizes you need system 1738A.</li>\n'
        '    <li><strong>190</strong> (190R, MTX190) \u2014 Pfaff and Pfaff-pattern industrial '
        'machines. 2.00 mm shank.</li>\n'
        '    <li><strong>130/705H</strong> \u2014 domestic machines, identifiable by the flat on '
        'the shank. Also sold as HA\u00d71 and 15\u00d71.</li>\n'
        '  </ul>\n'
        '  <p>Your machine\u2019s manual states its system. Failing that, it is usually stamped on '
        'the packet of whatever is in the machine now.</p>\n\n'

        '  <h2>Round point or leather point</h2>\n'
        '  <p>This matters more than most people expect.</p>\n'
        '  <p>A <strong>round point</strong> (R) pushes between the yarns of a woven cloth without '
        'cutting them. Use it on anything woven. Put a leather point through woven cloth and you '
        'cut the yarns, which weakens the seam along its whole length.</p>\n'
        '  <p>A <strong>leather point</strong> is a cutting point, ground to slice a small clean '
        'incision rather than punch a hole. The grind determines which way the cut lies and '
        'therefore how the stitches sit \u2014 LR is the common general-purpose leather point and '
        'gives a neat line slightly angled to the seam.</p>\n'
        '  <div class="sw-note"><p><strong>Vinyl is the awkward one.</strong> It behaves like '
        'leather to the needle but is usually backed with a woven scrim, and a leather point cuts '
        'that backing. Groz-Beckert describe their R point as suiting woven fabrics, leather, '
        '<em>artificial leather and coated fabrics</em> alike, which is the manufacturer\u2019s way '
        'of saying a round point is a defensible choice on vinyl. Many trimmers use one for exactly '
        'that reason. Test on an offcut of the actual material before committing on a '
        'customer\u2019s job.</p></div>\n\n'

        '  <h2>Change needles more often than you think</h2>\n'
        '  <p>A needle blunts long before it looks blunt. A blunted point pushes material down '
        'rather than piercing it, which is a common cause of skipped stitches and puckering that '
        'gets blamed on tension. If a machine that was sewing well starts misbehaving, put a new '
        'needle in before you touch anything else. It is the cheapest thing in the workshop and '
        'the most frequent culprit.</p>\n'
        '  <p>You will see hour-counts quoted for this \u2014 change it every eight hours and so '
        'on. Those come from garment production, where a machine runs all day on fine cloth and a '
        'slightly blunt point shows at once. Upholstery is not that. You sew a seam and go back to '
        'the bench, and the needle is a heavier thing to begin with. Change it when the work tells '
        'you: skipped stitches, a change in the sound, snagging in the face, or straight after it '
        'has met a tack, a staple or the plate.</p>\n\n'

        '  <div class="sw-note"><p><strong>Want this worked out for you?</strong> The '
        '<a href="/sewing-selector">thread and needle selector</a> pairs the thread, needle, point '
        'and stitch length in three questions.</p></div>\n'
        '  <p>Also in this section: <a href="/sewing-thread">thread</a> \u00b7 '
        '<a href="/sewing-machines">machines</a> \u00b7 '
        '<a href="/sewing-troubleshooting">troubleshooting</a> \u00b7 '
        '<a href="/sewing-setup">setup</a> \u00b7 '
        '<a href="/sewing">everything</a>.</p>\n\n'
        '  %s\n</article>'
        % (rows, sources_block(d.SOURCES_NEEDLE, d.CHECKED)))

    desc = ('Upholstery needle sizes by thread size, needle systems, round and leather points, '
            'and why a blunt needle causes skipped stitches.')
    url = SITE + '/sewing-needles'
    page = swap_head(pre, 'Sewing machine needles for upholstery', desc, url)
    page = page.replace('</head>', CSS + '\n' + needle_schema(url) + '\n</head>', 1)
    page += header('Sewing \u00b7 Needles', 'Needles for upholstery')
    open('sewing-needles.html', 'w', encoding='utf-8').write(page + mid + body + tail)



def build_machines(pre, mid, tail, d):
    verdict_cls = {'not upholstery': 'v-no', 'better': 'v-mid',
                   'good': 'v-ok', 'what you want': 'v-yes'}
    feeds = ''.join(
        '<div class="sw-fib"><h3>%s%s</h3>'
        '<p class="fr-tags"><span class="fr-tag %s">%s</span></p>'
        '<p class="h">How it works</p><p>%s</p>'
        '<p class="h">Good for</p><p>%s</p>'
        '<p class="h">Where it falls down</p><p>%s</p></div>'
        % (html.escape(f['name']),
           ' <span class="also">%s</span>' % html.escape(f['also']) if f['also'] else '',
           verdict_cls[f['verdict']], html.escape(f['verdict']),
           f['how'], html.escape(f['good']), html.escape(f['bad']))
        for f in d.FEEDS)

    beds = ''.join(
        '<div class="sw-fib"><h3>%s</h3><p class="best">%s</p>'
        '<p class="h">Good for</p><p>%s</p>'
        '<p class="h">Where it falls down</p><p>%s</p></div>'
        % (html.escape(b['name']), html.escape(b['what']),
           html.escape(b['good']), html.escape(b['bad']))
        for b in d.BEDS)

    body = (
        '<article class="article wrap read">\n'
        '  <p class="lede">Two things describe a machine: how it moves the material, and what '
        'shape the bed is. The first matters far more than the second, and it is the one most '
        'buying guides skate over.</p>\n\n'

        '  <div class="sw-note"><p><strong>The short version.</strong> For upholstery you want a '
        '<strong>compound feed</strong> machine on a <strong>flat bed</strong>. Everything else on '
        'this page is either a step down from that or a specialist you will use a handful of times '
        'a year.</p></div>\n\n'

        '  <h2>Feed \u2014 how the material is moved</h2>\n'
        '  <p>A machine has to move two surfaces of the material at the same rate. If it only '
        'drives the underside, the top creeps, and on a long seam you finish with the two pieces '
        'out of register. That is the single most common reason upholstery sewn on the wrong '
        'machine looks wrong.</p>\n'
        '  <div class="sw-cols">%s</div>\n\n'

        '  <div class="sw-warn"><p><strong>The names are used inconsistently, so here is a test '
        'that settles it.</strong> One supplier calls unison feed \u201calso known as walking foot '
        'feed\u201d. Another says needle feed \u201cis more appropriately termed compound\u201d. '
        'A third lists compound, needle and triple feed as three names for one thing. They are not '
        'the same thing.</p>'
        '<p>Watch the needle as the machine sews. <strong>If the needle moves forward with the '
        'material, it is compound feed.</strong> If the needle only goes up and down while the top '
        'foot walks, it is a walking foot machine and nothing more. That is checkable in ten '
        'seconds and it beats arguing about the label on the box.</p></div>\n\n'

        '  <h2>Bed \u2014 what shape the machine is</h2>\n'
        '  <p>The bed decides what you can physically get under the needle. It has nothing to do '
        'with how well the machine sews.</p>\n'
        '  <div class="sw-cols">%s</div>\n\n'

        '  <h2>The overlocker</h2>\n'
        '  <p>Worth its own mention because it does a job the walking foot machine cannot, and '
        'because a lot of upholsterers do not realise how much use it gets.</p>\n'
        '  <p>An overlocker sews, trims and wraps the raw edge in one pass, using loopers instead '
        'of a bobbin. In upholstery it is edge protection: it stops a cut edge unravelling before '
        'you have got the piece together.</p>\n'
        '  <p><strong>Only on cloth that actually frays.</strong> Plenty of upholstery weaves are '
        'stable enough at the cut edge that overlocking them is time spent for nothing. It earns '
        'its keep on loose weaves, nubby textures, linens and anything destined for a loose cover '
        'that will be taken off and washed.</p>\n'
        '  <div class="sw-note"><p><strong>The order that works.</strong> Overlock the cut pieces '
        'first, then straight stitch them together on the walking foot machine.</p>'
        '<p>Doing it that way you are running flat single layers through the overlocker, which is '
        'quick and accurate. Leave it until after the seam is sewn and you are feeding a bulky '
        'folded allowance through instead, on a curve, with the piece already assembled. Both '
        'methods are used, but the first is easier on every count.</p></div>\n'
        '  <div class="sw-warn"><p><strong>The overlock is not the seam.</strong> On woven cloth, '
        'an overlocked join on its own can fray along with the edge or sit oddly on the face side. '
        'The straight stitch is what holds the piece together; the overlock only protects the raw '
        'edge. A five-thread overlocker does both in one pass \u2014 a four-thread does '
        'not.</p></div>\n\n'

        '  <h2>What to actually buy</h2>\n'
        '  <p><strong>One compound feed flat bed machine will do almost everything.</strong> Long '
        'seams, panels, cushions, covers, leather, vinyl, heavy weaves. If you buy one machine, '
        'buy that.</p>\n'

        '  <div class="sw-note"><p><strong>What is actually in my workshop, after thirty-four '
        'years.</strong> Two walking foot machines \u2014 a Jack kept for the thick work and a '
        'Juki for everything else \u2014 plus an overlocker, and a second Jack that lives in the '
        'van for on-site repairs. No cylinder arm. No post bed.</p>'
        '<p>That is worth saying plainly because every buying guide points you at a specialist bed '
        'as the second machine. In practice the second machine that earns its keep is <em>another '
        'flat bed</em>, because what you are really buying is a second setup: one threaded heavy '
        'with a big needle, one ready for ordinary work, and no stopping to change over.</p></div>\n'

        '  <p>The forums say the same thing from the other direction. Upholsterers who do own '
        'cylinder and post bed machines report they make small curved work easier but only on a '
        'few seams, and not often \u2014 one trimmer noting it is less trouble to top stitch on '
        'the flat bed already threaded than to swap thread over to the cylinder for two runs. '
        'Flat-bed attachments exist for cylinder machines, so if the awkward work is occasional '
        'there is a cheaper way round it than a second head.</p>\n'
        '  <p>The exception is genuinely three-dimensional work most days \u2014 a lot of '
        'headrests, bolsters or finished covers going round the arm. Then a cylinder arm stops '
        'being a luxury. For most furniture upholstery it never quite gets there.</p>\n\n'

        '  <p>Also in this section: <a href="/sewing-selector">selector</a> \u00b7 '
        '<a href="/sewing-thread">thread</a> \u00b7 <a href="/sewing-needles">needles</a> '
        '\u00b7 <a href="/sewing-troubleshooting">troubleshooting</a> \u00b7 '
        '<a href="/sewing-setup">setup</a> \u00b7 '
        '<a href="/sewing">everything</a>.</p>\n\n  %s\n</article>'
        % (feeds, beds, sources_block(None, d.CHECKED)))

    desc = ('Industrial sewing machines for upholstery: drop, needle, walking foot and compound '
            'feed explained, plus flat, cylinder, post and long arm beds.')
    url = SITE + '/sewing-machines'
    page = swap_head(pre, 'Industrial sewing machines for upholstery', desc, url)
    page = page.replace('</head>', CSS + '\n' + machines_schema(url) + '\n</head>', 1)
    page += header('Sewing \u00b7 Machines', 'Sewing machines for upholstery')
    open('sewing-machines.html', 'w', encoding='utf-8').write(page + mid + body + tail)


def machines_schema(url):
    return _base(url, 'Industrial sewing machines for upholstery',
                 'Feed mechanisms and bed types explained for upholstery work.',
                 [('What is the difference between a walking foot and a compound feed machine?',
                   'A walking foot machine drives the top of the material with an alternating '
                   'foot as well as the bottom with feed dogs. A compound feed machine adds the '
                   'needle, which moves forward with the material rather than only up and down. '
                   'The test is to watch the needle while the machine sews: if it travels forward '
                   'with the work it is compound feed, and if it only rises and falls it is a '
                   'walking foot machine. The names are used loosely in the trade, so the test is '
                   'more reliable than the label.'),
                  ('What sewing machine do I need for upholstery?',
                   'A compound feed machine on a flat bed will do almost everything in upholstery: '
                   'long seams, panels, cushions, covers, leather, vinyl and heavy weaves. Cylinder '
                   'arm and post bed machines make small three-dimensional work easier but are '
                   'used far less often than people expect, and flat-bed attachments exist for '
                   'cylinder machines.'),
                  ('Do I need a cylinder arm or post bed machine for upholstery?',
                   'Usually not. Upholsterers who own them report they help on small curved work '
                   'but only on a few seams and not often, and flat-bed attachments exist for '
                   'cylinder machines. In practice the second machine that earns its keep is '
                   'another flat bed, because what you are buying is a second setup \u2014 one '
                   'threaded heavy, one ready for ordinary work, with no stopping to change over. '
                   'A cylinder arm becomes worthwhile only if genuinely three-dimensional work is '
                   'a daily part of what you do.'),
                  ('Can I sew upholstery on a domestic sewing machine?',
                   'Light work, sometimes. A domestic machine uses drop feed, where only the feed '
                   'dogs move the material, so the top layer creeps on anything thick or slippery '
                   'and a long seam finishes out of register. Domestic machines also top out at '
                   'around T70 thread. For anything structural you want compound feed.')])



def build_trouble(pre, mid, tail, d):
    blocks = []
    for i, t in enumerate(d.TROUBLE, 1):
        checks = ''.join(
            '<li><strong>%s</strong><br>%s</li>' % (html.escape(a), b) for a, b in t['checks'])
        blocks.append(
            '<div class="tr-sym" id="s%d">\n  <h2>%s</h2>\n  <p class="tr-what">%s</p>\n'
            '  <ol class="tr-checks">%s</ol>\n</div>'
            % (i, html.escape(t['symptom']), html.escape(t['what']), checks))

    nav = ''.join('<li><a href="#s%d">%s</a></li>' % (i, html.escape(t['symptom']))
                  for i, t in enumerate(d.TROUBLE, 1))

    body = (
        '<article class="article wrap read">\n'
        '  <p class="lede">Something has gone wrong and there is a job waiting. Find the '
        'symptom, work down the list in order \u2014 the cheap checks are first for a '
        'reason.</p>\n\n'

        '  <div class="sw-warn"><p><strong>Before anything else: change the needle.</strong> '
        'It is the cheapest thing in the workshop and the most frequent culprit. A needle bends '
        'long before it looks bent, and a bend of a fraction of a millimetre moves it out of the '
        'hook\u2019s path. Machine shops report a great many machines brought in for skipped '
        'stitches that sew perfectly the moment a new needle goes in.</p>'
        '<p>Then remember the order: <strong>threading, needle, tension</strong>. Roughly four '
        'times out of five the fault is one of those three and not the machine.</p></div>\n\n'

        '  <ul class="tr-nav">%s</ul>\n\n'
        '  %s\n\n'

        '  <h2>When it is worth stopping</h2>\n'
        '  <p>Timing, hook clearance and a bent needle bar are real faults and they do happen. '
        'But they are the last things to suspect, not the first, and they need tools and someone '
        'who knows the machine. If you have worked through the list for a symptom and nothing has '
        'changed, that is the point to stop guessing and get it looked at \u2014 rather than '
        'three hours in, having moved every adjustment on the machine and lost your starting '
        'point.</p>\n'
        '  <div class="sw-note"><p><strong>Write down what you change.</strong> The single most '
        'useful habit in machine troubleshooting. Move one thing at a time, note it, and test. '
        'Half the machines that end up genuinely out of adjustment got there during an attempt to '
        'fix something else.</p></div>\n\n'

        '  <p>Also in this section: <a href="/sewing-selector">selector</a> \u00b7 '
        '<a href="/sewing-thread">thread</a> \u00b7 <a href="/sewing-needles">needles</a> '
        '\u00b7 <a href="/sewing-machines">machines</a> \u00b7 '
        '<a href="/sewing-setup">setup</a> \u00b7 '
        '<a href="/sewing">everything</a>.</p>\n</article>' % (nav, '\n\n  '.join(blocks)))

    desc = ('Upholstery sewing machine troubleshooting: skipped stitches, thread breaking, '
            'puckering, tension and feed problems, in the order worth checking.')
    url = SITE + '/sewing-troubleshooting'
    page = swap_head(pre, 'Sewing machine troubleshooting for upholstery', desc, url)
    page = page.replace('</head>', CSS + '\n' + trouble_schema(url, d) + '\n</head>', 1)
    page += header('Sewing \u00b7 Troubleshooting', 'When the machine misbehaves')
    open('sewing-troubleshooting.html', 'w', encoding='utf-8').write(page + mid + body + tail)


def trouble_schema(url, d):
    esc = lambda t: re.sub(r'<[^>]+>', '', t).replace('\\', '\\\\').replace('"', '\\"')
    faqs = [
        ('Why is my sewing machine skipping stitches?',
         'Most often a blunt or slightly bent needle. For a stitch to form the hook must pass '
         'through the loop of thread at the needle eye, and a bend of a fraction of a millimetre '
         'moves the needle out of the hook\u2019s path. Change the needle first. After that, '
         'check it is fitted the right way round and fully home, that its size suits the thread, '
         'and rethread with the presser foot raised so the tension discs are open.'),
        ('Why does my thread keep breaking?',
         'Usually the needle is too fine for the thread, so the eye files the thread away as it '
         'passes through twice on every stitch. Go up a size within the range for that thread. '
         'Otherwise look for a burr on the needle, hook or throat plate, back off the top tension, '
         'and check the thread has a final Z twist \u2014 S twist untwists as it runs and frays '
         'for no other reason.'),
        ('Why do I get a nest of thread at the start of a seam?',
         'The fabric is being pushed down into the needle plate hole before the stitches have '
         'anything to grip. Hold both thread tails behind the presser foot for the first three or '
         'four stitches and it stops. If it happens on every seam from the very first stitch, the '
         'upper thread is probably outside the tension discs \u2014 rethread with the foot up.'),
        ('Why are my seams puckering?',
         'Usually top tension too tight, drawing the seam in after it is sewn. It can also be a '
         'blunt needle displacing the material, a stitch too short for a heavy weave, or a drop '
         'feed machine being asked to do work that needs compound feed, where the top layer '
         'creeps and gathers.'),
    ]
    q = ','.join('{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}'
                 % (esc(a), esc(b)) for a, b in faqs)
    return ('<script type="application/ld+json">\n'
            '{"@context":"https://schema.org","@graph":['
            '{"@type":"Article","@id":"%s#article","headline":"Sewing machine troubleshooting for '
            'upholstery","url":"%s","inLanguage":"en","dateModified":"%s",'
            '"author":{"@id":"%s/about#shaun"},"publisher":{"@id":"%s#org"},'
            '"isPartOf":{"@type":"WebPage","@id":"%s/sewing#hub"}},'
            '{"@type":"FAQPage","@id":"%s#faq","mainEntity":[%s]},'
            '{"@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
            '{"@type":"ListItem","position":2,"name":"Sewing","item":"%s/sewing"},'
            '{"@type":"ListItem","position":3,"name":"Troubleshooting","item":"%s"}]}]}\n</script>'
            % (url, url, datetime.date.today().isoformat(), SITE, SITE, SITE, url, q,
               SITE, SITE, url))



def build_setup(pre, mid, tail, d):
    motors = ''.join(
        '<div class="sw-fib"><h3>%s</h3>'
        '<p class="fr-tags"><span class="fr-tag %s">%s</span></p>'
        '<p class="h">How it works</p><p>%s</p>'
        '<p class="h">In its favour</p><ul>%s</ul>'
        '<p class="h">Against it</p><ul>%s</ul></div>'
        % (html.escape(m['name']),
           'v-mid' if m['verdict'] == 'what came with it' else 'v-yes',
           html.escape(m['verdict']), html.escape(m['how']),
           ''.join('<li>%s</li>' % html.escape(x) for x in m['pros']),
           ''.join('<li>%s</li>' % x for x in m['cons']))
        for m in d.MOTORS)

    feet = ''.join(
        '<div class="tr-sym"><h2>%s</h2><p class="tr-what">%s</p><p>%s</p></div>'
        % (html.escape(f['name']), html.escape(f['use']), f['note'])
        for f in d.FEET)

    body = (
        '<article class="article wrap read">\n'
        '  <p class="lede">The motor, the feet and the order you set the tension in. None of it '
        'is glamorous and all of it decides whether the machine is a pleasure or a fight.</p>\n\n'

        '  <h2>The motor</h2>\n'
        '  <p>If a machine feels uncontrollable, this is usually why, and it is the cheapest '
        'thing on the machine to put right.</p>\n'
        '  <div class="sw-cols">%s</div>\n'
        '  <div class="sw-note"><p><strong>Changing a clutch motor for a servo is the single '
        'best thing you can do to an older industrial machine.</strong> It is a bolt-on job, it '
        'costs less than a set of feet and a few cones of thread, and it turns a machine that '
        'bolts away from you into one you can walk a stitch at a time. Upholsterers who have done '
        'it are close to unanimous.</p></div>\n\n'

        '  <h2>Slowing it down further</h2>\n'
        '  <p>Two ways, and they are not the same.</p>\n'
        '  <p><strong>A smaller pulley on the motor</strong> is the cheap one. It slows the '
        'machine and costs a few pounds.</p>\n'
        '  <p><strong>A speed reducer</strong> is a second pulley stage between motor and '
        'machine. It slows the machine <em>and multiplies the punching power by the same '
        'ratio</em>, which is why it is the answer for very thick leather where a servo starts '
        'losing torque at the bottom of its range. Fitting one may mean drilling the table for '
        'the bracket and buying two new belts.</p>\n'
        '  <div class="sw-warn"><p><strong>Do not fit one before you need it.</strong> A reducer '
        'makes the machine very slow indeed, and upholsterers who fitted one early report finding '
        'it maddening once they got quicker and wanted to actually get through the work. Fit a '
        'servo first. Add a reducer only if you are still short of power at low speed on genuinely '
        'thick assemblies.</p></div>\n\n'

        '  <h2>Presser feet</h2>\n'
        '  <p>The foot is doing two jobs at once: holding the material down, and staying out of '
        'the way of whatever you are sewing next to.</p>\n'
        '  %s\n\n'

        '  <h2>Setting the tension, in the right order</h2>\n'
        '  <p>Almost every tension problem is solved on top, and almost every tension problem '
        'made worse is made worse by starting at the bobbin.</p>\n'
        '  <ol class="tr-checks">\n'
        '    <li><strong>Rethread with the presser foot up.</strong> The discs only open when the '
        'foot is raised. Thread it with the foot down and the thread sits outside them, and no '
        'setting will fix that.</li>\n'
        '    <li><strong>Leave the bobbin alone.</strong> Bobbin tension is set and rarely wants '
        'moving. If you have already been turning that screw, put it back to where a full bobbin '
        'case just holds its own weight when you dangle it by the thread and gives line with a '
        'small jerk.</li>\n'
        '    <li><strong>Sew a test seam on an offcut of the actual material.</strong> Two layers, '
        'same thread, same needle. Not a scrap of something else.</li>\n'
        '    <li><strong>Read which side is losing.</strong> Loops underneath mean the top tension '
        'is too loose. Loops on top mean it is too tight.</li>\n'
        '    <li><strong>Adjust the top only, a little at a time</strong>, and re-test after each '
        'change.</li>\n'
        '  </ol>\n\n'

        '  <h2>The maintenance that actually matters</h2>\n'
        '  <ul>\n'
        '    <li><strong>Oil it.</strong> Industrial machines are built to be oiled and they will '
        'wear out fast if they are not. Follow the plate on the machine; most want it daily in '
        'regular use.</li>\n'
        '    <li><strong>Brush the lint out of the bobbin case and race.</strong> Lint under the '
        'bobbin tension spring changes the tension noticeably, and it is the cause of a great many '
        'faults blamed on the machine.</li>\n'
        '    <li><strong>Never blow compressed air into it.</strong> It drives lint further in, '
        'past bearings, where a brush cannot reach.</li>\n'
        '    <li><strong>Change the needle when the work tells you to</strong>, not on a '
        'schedule. Skipped stitches, a change in the sound, snagging in the face, or straight '
        'after it has met a tack or a staple. Cheapest insurance in the workshop.</li>\n'
        '  </ul>\n\n'

        '  <p>Also in this section: <a href="/sewing-selector">selector</a> \u00b7 '
        '<a href="/sewing-thread">thread</a> \u00b7 <a href="/sewing-needles">needles</a> '
        '\u00b7 <a href="/sewing-machines">machines</a> \u00b7 '
        '<a href="/sewing-troubleshooting">troubleshooting</a> \u00b7 '
        '<a href="/sewing-setup">setup</a> \u00b7 '
        '<a href="/sewing">everything</a>.</p>\n</article>' % (motors, feet))

    desc = ('Servo against clutch motors, speed reducers, presser feet for upholstery, and the '
            'order to set tension in.')
    url = SITE + '/sewing-setup'
    page = swap_head(pre, 'Sewing machine setup and parts for upholstery', desc, url)
    page = page.replace('</head>', CSS + '\n' + setup_schema(url) + '\n</head>', 1)
    page += header('Sewing \u00b7 Setup', 'Setup and parts')
    open('sewing-setup.html', 'w', encoding='utf-8').write(page + mid + body + tail)


def setup_schema(url):
    return _base(url, 'Sewing machine setup and parts for upholstery',
                 'Motors, speed reducers, presser feet and tension setting.',
                 [('Should I fit a servo motor or keep the clutch motor?',
                   'Fit a servo. A clutch motor runs continuously and is controlled by slipping '
                   'the clutch, which gives a narrow usable range and is genuinely hard to learn. '
                   'A servo only turns when you press the pedal, follows the pedal for speed, and '
                   'usually has a dial to cap the top speed. It is a bolt-on change, costs less '
                   'than a set of feet and some thread, and is the single best improvement you can '
                   'make to an older industrial machine.'),
                  ('What does a speed reducer do?',
                   'It is a second pulley stage between the motor and the machine. It slows the '
                   'machine down and multiplies the punching power by the same ratio, which is why '
                   'it helps on very thick leather where a servo motor loses torque at the bottom '
                   'of its range. Fit a servo first and add a reducer only if you are still short '
                   'of power at low speed \u2014 fitted early, the resulting speed is slow enough '
                   'to be frustrating once you are quicker.'),
                  ('How do I set the tension on an industrial sewing machine?',
                   'Rethread with the presser foot raised so the tension discs are open, leave the '
                   'bobbin tension alone, sew a test seam on an offcut of the actual material, and '
                   'read which side is losing: loops underneath mean the top tension is too loose, '
                   'loops on top mean it is too tight. Adjust only the top tension, a little at a '
                   'time, testing after each change.')])


def build_hub(pre, mid, tail, d):
    cards = [
        ('/sewing-thread', 'Thread',
         'Bonded nylon or polyester, Tex sizes and the three numbering systems, '
         'which thread for which job, and the twist question.', None),
        ('/sewing-needles', 'Needles',
         'Needle size by thread size, needle systems, round and leather points, '
         'and why a blunt needle causes skipped stitches.', None),
        ('/sewing-selector', 'Thread &amp; needle selector',
         'Three questions and you get the thread, size, needle, point and stitch '
         'length \u2014 with the reasoning for each.', None),
        ('/sewing-machines', 'Machines',
         'Drop, needle, walking foot and compound feed; flat, cylinder, post and '
         'long arm beds. What to buy, and what you would rarely use.', None),
        ('/sewing-troubleshooting', 'Troubleshooting',
         'Skipped stitches, thread breaking, puckering, tension and feed problems \u2014 '
         'in the order worth checking.', None),
        ('/sewing-setup', 'Setup &amp; parts',
         'Servo against clutch motors, speed reducers, presser feet, and the order '
         'to set tension in.', None),
    ]
    out = []
    for href, title, blurb, tag in cards:
        badge = '<span class="soon">%s</span>' % tag if tag else ''
        if href:
            out.append('<a class="sw-card" href="%s"><h2>%s</h2><p>%s</p>%s</a>'
                       % (href, title, blurb, badge))
        else:
            out.append('<div class="sw-card"><h2>%s</h2><p>%s</p>%s</div>'
                       % (title, blurb, badge))

    body = (
        '<article class="article wrap read">\n'
        '  <p class="lede">Industrial sewing explained for upholsterers. Most of what is written '
        'about these machines is aimed at sailmakers, leatherworkers or garment factories \u2014 '
        'this is the same ground from an upholstery bench.</p>\n\n'
        '  <div class="sw-grid">\n    %s\n  </div>\n\n'
        '  <div class="sw-note"><p><strong>Where to start.</strong> If something is going wrong at '
        'the machine, it is thread or needle far more often than tension. The two guides above '
        'answer most of it, and the pairing between them answers most of the rest.</p></div>\n\n'
        '  <p>Six pages, and the section is complete.</p>\n</article>' % '\n    '.join(out))

    desc = ('Industrial sewing for upholsterers: thread, needles, machines and troubleshooting, '
            'explained from an upholstery bench rather than a sail loft.')
    url = SITE + '/sewing'
    page = swap_head(pre, 'Industrial sewing for upholsterers', desc, url)
    page = page.replace('</head>', CSS + '\n' + hub_schema(url) + '\n</head>', 1)
    page += header('Free resource', 'Sewing')
    open('sewing.html', 'w', encoding='utf-8').write(page + mid + body + tail)


def header(kicker, h1):
    t = datetime.date.today()
    return ('<header class="chapter-head">\n  <div class="wrap">\n'
            '    <p class="chno">%s</p>\n    <h1>%s</h1>\n'
            '    <p class="updated">Last updated: <time datetime="%s">%s</time></p>\n'
            '  </div>\n</header>' % (html.escape(kicker), html.escape(h1),
                                     t.isoformat(), t.strftime('%-d %B %Y')))


def _base(url, name, desc, faqs):
    q = ','.join('{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}'
                 % (a, b) for a, b in faqs)
    return ('<script type="application/ld+json">\n'
            '{"@context":"https://schema.org","@graph":['
            '{"@type":"Article","@id":"%s#article","headline":"%s","description":"%s","url":"%s",'
            '"inLanguage":"en","dateModified":"%s","author":{"@id":"%s/about#shaun"},'
            '"publisher":{"@id":"%s#org"},"isPartOf":{"@type":"WebPage","@id":"%s/sewing#hub"}},'
            '{"@type":"FAQPage","@id":"%s#faq","mainEntity":[%s]},'
            '{"@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
            '{"@type":"ListItem","position":2,"name":"Sewing","item":"%s/sewing"},'
            '{"@type":"ListItem","position":3,"name":"%s","item":"%s"}]}]}\n</script>'
            % (url, name, desc, url, datetime.date.today().isoformat(), SITE, SITE, SITE,
               url, q, SITE, SITE, name, url))


def thread_schema(url):
    return _base(url, 'Upholstery thread guide',
                 'Thread sizes, bonded nylon against polyester, and which thread for which job.',
                 [('Is bonded nylon stronger than polyester?',
                   'Nylon has slightly higher tensile strength and better abrasion resistance at '
                   'the same size. Polyester has far better resistance to ultraviolet light. For '
                   'anything that sees sunlight \\u2014 marine, motorcycle, garden or campervan '
                   'work \\u2014 polyester is the correct choice despite nylon being marginally '
                   'stronger, because UV degradation will destroy a nylon seam long before it '
                   'wears out.'),
                  ('What thread should I use for car seats?',
                   'Bonded nylon in T70 to T90. That is around the range vehicle manufacturers '
                   'use: strong enough for the seat, with a stitch that stays discreet. Nylon\\u2019s '
                   'abrasion resistance suits a seat that is slid across every day. For decorative '
                   'top stitching, T135.'),
                  ('Can a domestic sewing machine handle upholstery thread?',
                   'Up to T70, usually yes \\u2014 that is the recognised ceiling for domestic '
                   'machines and enough for much furniture work. T90 and above need an industrial '
                   'machine: a larger needle, a bigger hook and more thread path than a domestic '
                   'head provides.'),
                  ('What is bonded thread?',
                   'Thread given a resin coating after twisting. The coating binds the plies so '
                   'the thread resists untwisting as it runs through the machine, reduces friction '
                   'at the needle and stops the end fraying. Unbonded thread of the same size will '
                   'fray and snarl at upholstery speeds.')])


def needle_schema(url):
    return _base(url, 'Sewing machine needles for upholstery',
                 'Needle size by thread size, needle systems and point types.',
                 [('What size needle for Tex 90 thread?',
                   'Thread makers publish 110/18 to 125/20 for T90, which is commercial size 92. '
                   'Within that range use the finer needle for a tight weave and the coarser one '
                   'for dense or layered work.'),
                  ('Why does my machine skip stitches?',
                   'A blunt needle is the most frequent cause and it blunts long before it looks '
                   'blunt. A blunted point pushes the material down rather than piercing it, so '
                   'the hook misses the loop. Change the needle before adjusting anything else. '
                   'After that, check the needle size suits the thread and that the system is '
                   'correct for the machine.'),
                  ('Should I use a leather point needle on vinyl?',
                   'Often not. Vinyl behaves like leather to the needle but is usually backed with '
                   'a woven scrim, and a leather point cuts that backing. Many trimmers use a '
                   'round point on vinyl for that reason. Test on an offcut of the actual material '
                   'before committing on a customer\\u2019s job.')])


def hub_schema(url):
    items = ','.join('{"@type":"ListItem","position":%d,"name":"%s","url":"%s%s"}' % (i, n, SITE, u)
                     for i, (n, u) in enumerate([('Thread', '/sewing-thread'),
                                                 ('Needles', '/sewing-needles'),
                                                 ('Selector', '/sewing-selector'),
                                                 ('Machines', '/sewing-machines'),
                                                 ('Troubleshooting', '/sewing-troubleshooting'),
                                                 ('Setup', '/sewing-setup')], 1))
    return ('<script type="application/ld+json">\n'
            '{"@context":"https://schema.org","@graph":['
            '{"@type":"CollectionPage","@id":"%s#hub","name":"Industrial sewing for upholsterers",'
            '"url":"%s","inLanguage":"en",'
            '"description":"Thread, needles, machines and troubleshooting, explained from an '
            'upholstery bench.","author":{"@id":"%s/about#shaun"},"publisher":{"@id":"%s#org"},'
            '"mainEntity":{"@type":"ItemList","numberOfItems":6,"itemListElement":[%s]}},'
            '{"@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
            '{"@type":"ListItem","position":2,"name":"Sewing","item":"%s/sewing"}]}]}\n</script>'
            % (url, url, SITE, SITE, items, SITE, SITE))


def main():
    if not os.path.exists('sewing-data.py'):
        sys.exit('sewing-data.py not found. Run this from ~/learntoupholster.')
    d = load()
    pre, mid, tail = get_chrome()
    build_hub(pre, mid, tail, d)
    build_machines(pre, mid, tail, d)
    build_trouble(pre, mid, tail, d)
    build_setup(pre, mid, tail, d)
    build_thread(pre, mid, tail, d)
    build_needles(pre, mid, tail, d)
    print('Sewing section, phase 1:')
    print('   sewing.html            hub')
    print('   sewing-thread.html     %d thread sizes, %d job recommendations'
          % (len(d.THREAD_SIZES), len(d.CHOICES)))
    print('   sewing-needles.html    needle pairing, systems, point types')
    print('   sewing-machines.html   %d feed types, %d bed types' % (len(d.FEEDS), len(d.BEDS)))
    print('   sewing-troubleshooting.html  %d symptoms, %d checks'
          % (len(d.TROUBLE), sum(len(t['checks']) for t in d.TROUBLE)))
    print('   sewing-setup.html      motors, speed reducers, %d feet, tension' % len(d.FEET))


if __name__ == '__main__':
    main()
