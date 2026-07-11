#!/usr/bin/env python3
"""Adds an international section (US, Ireland, EU, Canada, Australia/NZ) to
/fire-safety-checker with country selector, comparison guidance and extended
FAQ schema; retitles the page for worldwide reach. Idempotent.
Run from repo root:  python3 patch-fire-intl.py"""
import json, re

F = 'fire-safety-checker.html'
t = open(F, encoding='utf-8').read()
orig = t
MARK = 'id="intl-fire"'

SECTION = '''<hr class="seam">
<section class="wrap read" id="intl-fire">
<h2>What are the fire regulations for upholstery in other countries?</h2>
<p>The UK rules above are the strictest general regime in the world &#8212; but if you work, sell or ship elsewhere, the ground changes completely. Pick the market:</p>
<div style="display:flex;gap:.5rem;flex-wrap:wrap;margin:1rem 0 1.4rem" id="intl-btns">
  <button data-c="us" class="btn btn-ghost" style="font-size:.95rem;padding:.5rem 1rem">United States</button>
  <button data-c="ie" class="btn btn-ghost" style="font-size:.95rem;padding:.5rem 1rem">Ireland</button>
  <button data-c="eu" class="btn btn-ghost" style="font-size:.95rem;padding:.5rem 1rem">EU</button>
  <button data-c="ca" class="btn btn-ghost" style="font-size:.95rem;padding:.5rem 1rem">Canada</button>
  <button data-c="anz" class="btn btn-ghost" style="font-size:.95rem;padding:.5rem 1rem">Australia &amp; NZ</button>
</div>

<div class="intl-panel" id="panel-us" style="display:none">
<h3>United States &#8212; 16 CFR Part 1640 (federal, since June 2021)</h3>
<p>The US now has a single federal standard: <strong>16 CFR Part 1640</strong>, which adopts California&#8217;s <strong>TB 117-2013</strong> nationwide. It is a <strong>smoulder (cigarette) resistance</strong> standard only &#8212; there is no open-flame test and <strong>no flame-retardant chemicals are required</strong>. Compliance is by component: a passing cover fabric over passing filling, or a passing <strong>barrier material fully encasing the filling</strong> (the barrier route means the piece complies even if other components would fail).</p>
<p><strong>For upholsterers, the crucial rule:</strong> furniture reupholstered <em>for sale</em> must comply and must carry the permanent label <em>&#8220;Complies with U.S. CPSC requirements for upholstered furniture flammability&#8221;</em> (required since June 2022). But furniture reupholstered <strong>for the customer&#8217;s own personal use is exempt</strong> &#8212; the opposite of the UK position, where trade reupholstery must comply regardless. California adds its own SB&#8202;1019 label stating whether the piece contains flame retardants.</p>
</div>

<div class="intl-panel" id="panel-ie" style="display:none">
<h3>Ireland &#8212; the UK&#8217;s close cousin</h3>
<p>Ireland runs its own regime (I.S. 419 and associated fire-safety requirements) which closely mirrors the UK approach: <strong>cigarette and match resistance</strong> for domestic upholstered furniture, based on the same BS 5852 test family, with labelling requirements. If a job passes the UK regulations above, it will generally meet the Irish requirements &#8212; but confirm labelling wording with your supplier or the CCPC before supplying at trade.</p>
</div>

<div class="intl-panel" id="panel-eu" style="display:none">
<h3>European Union &#8212; no single rule</h3>
<p>There is <strong>no EU-wide flammability law for domestic upholstered furniture</strong>. The reference tests are <strong>EN 1021-1 (cigarette)</strong> and <strong>EN 1021-2 (match)</strong>, but whether either is mandatory depends on the member state &#8212; most impose nothing for domestic furniture, while <strong>contract and public-space work</strong> (hotels, healthcare, transport) is specified per country and per contract, often at much tougher levels. Selling into the EU: check the destination country&#8217;s rules and put the required test level in writing on the job sheet. Ireland (left) is the strict exception.</p>
</div>

<div class="intl-panel" id="panel-ca" style="display:none">
<h3>Canada &#8212; mattresses regulated, furniture largely voluntary</h3>
<p>Canada regulates <strong>mattress</strong> flammability federally, but there is <strong>no general mandatory ignition-resistance standard for domestic upholstered furniture</strong>. Voluntary standards and provincial or contract requirements (particularly for public buildings) fill the gap. Reupholstering for Canadian customers: no federal furniture test applies, but confirm any contract specification and keep records.</p>
</div>

<div class="intl-panel" id="panel-anz" style="display:none">
<h3>Australia &amp; New Zealand &#8212; contract-driven</h3>
<p>Neither country imposes a general mandatory flammability standard on domestic upholstered furniture. <strong>Commercial and public work</strong> is where requirements bite: procurement typically specifies AS/NZS test standards, and healthcare or detention contracts set their own levels. For domestic work: no test required; for contract work: the specification is the law of the job &#8212; get it in writing.</p>
</div>

<p style="margin-top:1.2rem"><em>Regulations change and this page is guidance, not legal advice &#8212; for a specific job, confirm with the relevant national authority (CPSC in the US, CCPC in Ireland, local trading standards in the UK) or the contract specifier.</em></p>
</section>
<script>
(function(){var bs=document.querySelectorAll('#intl-btns button');bs.forEach(function(b){b.addEventListener('click',function(){document.querySelectorAll('.intl-panel').forEach(function(p){p.style.display='none'});bs.forEach(function(x){x.classList.remove('btn-primary');x.classList.add('btn-ghost')});document.getElementById('panel-'+b.dataset.c).style.display='block';b.classList.remove('btn-ghost');b.classList.add('btn-primary');});});bs[0].click();})();
</script>'''

FAQ_QAS = [
 ("Do US upholsterers have to meet fire regulations?",
  "Yes, when reupholstering for sale: 16 CFR Part 1640 (which adopts California TB 117-2013 federally) applies to furniture manufactured, imported or reupholstered for sale, and requires a permanent compliance label. Furniture reupholstered for the customer's own personal use is exempt in the US - unlike the UK, where trade reupholstery must comply regardless."),
 ("Is TB 117 required outside California?",
  "Yes. Since June 2021, California TB 117-2013 has been the federal standard for the whole United States under 16 CFR Part 1640. It is a smoulder-resistance (cigarette) standard; no flame-retardant chemicals are required."),
 ("Are UK fire regulations stricter than US regulations?",
  "Yes. The UK requires both cigarette and open-flame (match) resistance for domestic upholstered furniture, with Crib 5 levels for contract work. The US federal standard tests smoulder resistance only, with no open-flame requirement."),
 ("Does the EU have fire regulations for upholstered furniture?",
  "There is no EU-wide flammability law for domestic upholstered furniture. EN 1021-1 (cigarette) and EN 1021-2 (match) are the reference tests, applied country by country and contract by contract. Ireland is the strict exception, closely mirroring the UK regime."),
]

if MARK not in t:
    # insert before footer
    t = t.replace('<footer class="site-footer">', SECTION + '\n<footer class="site-footer">', 1)
    # extend existing FAQPage mainEntity
    add = ''.join(json.dumps({"@type":"Question","name":q,
        "acceptedAnswer":{"@type":"Answer","text":a}}, ensure_ascii=False)+',' for q,a in FAQ_QAS)
    t = re.sub(r'("mainEntity":\s*\[)', r'\1' + add.replace('\\', '\\\\'), t, count=1)
    # retitle for worldwide scope
    t = t.replace('<title>UK Fire Regulations Checker for Upholstery | Learn to Upholster</title>',
        '<title>Fire Regulations for Upholstery: UK, US &amp; Worldwide Checker | Learn to Upholster</title>')
    t = t.replace('What do the UK furniture fire regulations require of your upholstery job? Four questions, plain-English guidance, and a printable compliance record.',
        'What fire regulations apply to your upholstery job? UK checker with printable compliance record, plus US (TB 117-2013 / 16 CFR 1640), EU, Ireland, Canada and Australia at a glance.')
    open(F, 'w', encoding='utf-8').write(t)
    print("fire-safety-checker.html patched")
else:
    print("already patched")
