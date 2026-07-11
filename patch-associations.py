#!/usr/bin/env python3
"""Adds 'Upholstery trade associations worldwide' to /find-an-upholsterer,
plus the page's first FAQPage + BreadcrumbList schema and a widened title.
Idempotent. Run from repo root:  python3 patch-associations.py"""
import json

F = 'find-an-upholsterer.html'
t = open(F, encoding='utf-8').read()
if 'id="worldwide-bodies"' in t:
    print("already patched"); raise SystemExit

SECTION = '''<hr class="seam">
<section class="wrap read" id="worldwide-bodies">
<h2>What upholstery trade associations exist worldwide?</h2>
<p>Every country organises the trade differently &#8212; some through member associations like the AMUSF, others through formal craft qualifications with no guild at all. If you&#8217;re looking for an accredited professional (or training) outside the UK, start here:</p>

<h3>United Kingdom &#8212; AMUSF</h3>
<p>The <a href="https://amusf.org/" rel="noopener">Association of Master Upholsterers and Soft Furnishers</a> accredits training centres, maintains a member directory, and awards the Master Upholsterer title. It&#8217;s the gold standard this site&#8217;s author holds &#8212; if a UK upholsterer is AMUSF-accredited, their training has been independently verified.</p>

<h3>United States &amp; Canada &#8212; National Upholstery Association</h3>
<p>The <a href="https://nationalupholsteryassociation.org/" rel="noopener">National Upholstery Association</a> (founded 2019, non-profit) is North America&#8217;s trade body: it runs an upholsterers&#8217; directory, an educators&#8217; directory, a mentorship programme, webinars and the annual Custom Workroom Conference. If you&#8217;re in the US or Canada, their directory is the equivalent of the AMUSF&#8217;s member search.</p>

<h3>Germany &#8212; the Raumausstatter Meister system</h3>
<p>Germany folds upholstery into the <em>Raumausstatter</em> (interior fitter) craft under the Handwerk system &#8212; a formal apprenticeship route ending in the <strong>Meister</strong> qualification, arguably the closest structural equivalent to a Master Upholsterer accreditation anywhere. Look for &#8220;Raumausstattermeister&#8221; and check the local Handwerkskammer (chamber of crafts) register.</p>

<h3>France &#8212; the tapissier tradition</h3>
<p>French upholsterers are <em>tapissiers d&#8217;ameublement</em>, trained through the <strong>CAP Tapissier</strong> qualification and, at the elite end, the <a href="https://www.compagnons-du-devoir.com/" rel="noopener">Compagnons du Devoir</a> journeyman tradition. There is no single national member directory; the CAP and Compagnons background are the credentials to ask about.</p>

<h3>Australia &amp; New Zealand &#8212; qualification, not guild</h3>
<p>Neither country has a dedicated upholsterers&#8217; association. Training runs through TAFE&#8217;s <strong>Certificate III in Upholstery</strong> (Australia) and the equivalent NZ apprenticeship routes &#8212; ask a prospective upholsterer about their Cert III or time served, and look at their finished work.</p>

<p style="font-size:1rem"><em>Wherever you are: the questions in the guide above &#8212; and a look at photographs of work they&#8217;ve actually done &#8212; matter more than any badge.</em></p>
</section>'''

FAQ = [
 ("What is the American equivalent of the AMUSF?",
  "The National Upholstery Association (NUA), founded in 2019 - a non-profit trade body covering the US and Canada with an upholsterers' directory, educators' directory, mentorship programme and the annual Custom Workroom Conference. The AMUSF remains the UK's accrediting association."),
 ("Is there an upholstery trade association in Australia?",
  "No dedicated national association exists; the trade credential is TAFE's Certificate III in Upholstery. Ask a prospective upholsterer about their qualification or time served, and review their finished work."),
 ("What is a Raumausstattermeister?",
  "Germany's master craftsman qualification for the interior-fitting trade that includes upholstery, awarded through the Handwerk apprenticeship system - structurally the closest international equivalent to a UK Master Upholsterer."),
 ("How do I check if a UK upholsterer is properly qualified?",
  "Ask whether they are AMUSF-accredited or trained at an AMUSF Approved Training Centre, and look at photographs of comparable finished work. The AMUSF maintains a searchable member directory."),
]

t = t.replace('<footer class="site-footer">', SECTION + '\n<footer class="site-footer">', 1)

ld = ('<script type="application/ld+json">' + json.dumps({
    "@context":"https://schema.org","@type":"FAQPage",
    "mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]
}, ensure_ascii=False) + '</script>\n' +
'<script type="application/ld+json">' + json.dumps({
    "@context":"https://schema.org","@type":"BreadcrumbList",
    "itemListElement":[
      {"@type":"ListItem","position":1,"name":"Home","item":"https://www.learntoupholster.com/"},
      {"@type":"ListItem","position":2,"name":"Find an Upholsterer","item":"https://www.learntoupholster.com/find-an-upholsterer"}]
}, ensure_ascii=False) + '</script>\n</head>')
t = t.replace('</head>', ld, 1)

t = t.replace('<title>Find an Upholsterer Near You | Learn to Upholster</title>',
    '<title>Find an Upholsterer Near You &#8212; UK, US &amp; Worldwide | Learn to Upholster</title>')

open(F, 'w', encoding='utf-8').write(t)
print("find-an-upholsterer.html patched")
