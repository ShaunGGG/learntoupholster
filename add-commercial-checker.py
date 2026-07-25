#!/usr/bin/env python3
"""
add-commercial-checker.py
-------------------------
Adds a contract / commercial branch to /fire-safety-checker without removing
anything that is already on the page.

It inserts three blocks:
  1. A self-contained BS 7176 hazard-category checker + specification record,
     placed immediately before the international section.
  2. A "commercial work overseas" addendum, placed after the international
     section's closing note.
  3. A limitation-of-liability notice, placed at the end of the main content.

Safe to re-run: if the markers are already present it reports and exits without
changing the file. Writes fire-safety-checker.html.bak before touching anything.
"""

import re
import shutil
import sys
from pathlib import Path

PAGE = Path("fire-safety-checker.html")
MARKER = 'id="cc-checker"'

# ---------------------------------------------------------------------------
# BLOCK 1 — the contract checker
# ---------------------------------------------------------------------------

CHECKER = r"""
<hr class="stitch">

<section id="cc-checker" class="cc">
<style>
.cc{margin:2.5rem 0}
.cc .cc-lede{margin-bottom:1.4rem}
.cc fieldset{border:0;border-top:1px dashed var(--gold,#C19A4B);margin:0 0 1.3rem;padding:1.1rem 0 0}
.cc legend{font-family:var(--display,Georgia,serif);font-size:.82rem;letter-spacing:.08em;text-transform:uppercase;color:var(--green,#2F4A3A);padding:0 .6rem 0 0}
.cc label.cc-opt{display:block;margin:.45rem 0;cursor:pointer;line-height:1.45}
.cc label.cc-opt input{margin-right:.55rem}
.cc-out{margin-top:1.6rem;padding:1.3rem 1.4rem;background:rgba(47,74,58,.055);border-left:3px solid var(--green,#2F4A3A);border-radius:2px}
.cc-out[hidden]{display:none}
.cc-cat{font-family:var(--display,Georgia,serif);font-size:1.28rem;line-height:1.25;color:var(--green,#2F4A3A);margin:0 0 .2rem}
.cc-sub{font-size:.9rem;color:var(--sage,#7C8C5D);margin:0 0 1rem;letter-spacing:.02em}
.cc-out h4{font-family:var(--display,Georgia,serif);font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:var(--green,#2F4A3A);margin:1.2rem 0 .4rem}
.cc-out ul{margin:.3rem 0 .8rem;padding-left:1.1rem}
.cc-out li{margin:.3rem 0}
.cc-flag{border-left:3px solid var(--terracotta,#B5552D);background:rgba(181,85,45,.06);padding:.85rem 1rem;margin:1rem 0;border-radius:2px}
.cc-flag strong{color:var(--terracotta,#B5552D)}
.cc-rec{margin-top:2rem;padding-top:1.4rem;border-top:1px dashed var(--gold,#C19A4B)}
.cc-rec .cc-grid{display:grid;grid-template-columns:1fr 1fr;gap:.75rem 1.1rem}
@media(max-width:640px){.cc-rec .cc-grid{grid-template-columns:1fr}}
.cc-rec label{display:block;font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;color:var(--sage,#7C8C5D);font-family:var(--display,Georgia,serif)}
.cc-rec input,.cc-rec textarea{width:100%;margin-top:.25rem;padding:.5rem .6rem;border:1px solid rgba(42,38,34,.25);border-radius:2px;background:#fff;font-family:inherit;font-size:.95rem;color:var(--ink,#2A2622)}
.cc-rec textarea{min-height:4.5rem;resize:vertical}
.cc-btns{margin-top:1.1rem;display:flex;gap:.6rem;flex-wrap:wrap}
.cc-btns button{font-family:var(--display,Georgia,serif);font-size:.82rem;letter-spacing:.07em;text-transform:uppercase;padding:.6rem 1.1rem;border-radius:2px;cursor:pointer;border:1px solid var(--green,#2F4A3A)}
.cc-btns .cc-primary{background:var(--green,#2F4A3A);color:var(--cream,#FBF6ED)}
.cc-btns .cc-ghost{background:transparent;color:var(--green,#2F4A3A)}
.cc-btns button:focus-visible{outline:2px solid var(--gold,#C19A4B);outline-offset:2px}
.cc-opt input:focus-visible{outline:2px solid var(--gold,#C19A4B);outline-offset:2px}
#cc-record-out[hidden]{display:none}
#cc-record-out{margin-top:1.3rem;padding:1.3rem;border:1px solid rgba(42,38,34,.2);background:#fff;border-radius:2px}
#cc-record-out h4{margin:0 0 .3rem;font-family:var(--display,Georgia,serif);color:var(--green,#2F4A3A)}
#cc-record-out dl{display:grid;grid-template-columns:auto 1fr;gap:.35rem .9rem;margin:.9rem 0 0;font-size:.92rem}
#cc-record-out dt{font-weight:600;color:var(--sage,#7C8C5D)}
#cc-record-out dd{margin:0}
@media print{.cc fieldset,.cc-btns,.cc-lede,.cc-rec .cc-grid{display:none}#cc-record-out{border:0}}
</style>

<h2>Contract &amp; commercial seating &mdash; which hazard category?</h2>

<p class="cc-lede">The checker above covers <strong>domestic</strong> work, where the Furniture and Furnishings (Fire) (Safety) Regulations 1988 apply. Seating destined for a pub, hotel, care home, office or any other non-domestic premises is a different regime: <strong>BS&nbsp;7176</strong>, which sorts seating into four hazard categories according to where it is going. Answer four questions and you get the category, the tests it calls for, and a specification record for the job file.</p>

<fieldset>
<legend>1. Where is the seating going?</legend>
<label class="cc-opt"><input type="radio" name="ccq1" value="low"> Office, school, college, museum or exhibition space</label>
<label class="cc-opt"><input type="radio" name="ccq1" value="med_public"> Pub, bar, restaurant, caf&eacute;, shop, cinema, theatre, village hall or hotel public area</label>
<label class="cc-opt"><input type="radio" name="ccq1" value="med_care"> Care home, hospital, clinic, or a GP / dental waiting room</label>
<label class="cc-opt"><input type="radio" name="ccq1" value="med_sleep"> Hotel or B&amp;B bedroom, hostel, or student accommodation</label>
<label class="cc-opt"><input type="radio" name="ccq1" value="high"> Offshore installation, or a higher-dependency hospital ward</label>
<label class="cc-opt"><input type="radio" name="ccq1" value="vhigh"> Prison cell, custody suite or locked psychiatric accommodation</label>
<label class="cc-opt"><input type="radio" name="ccq1" value="unknown"> Something else, or I don&rsquo;t know yet</label>
</fieldset>

<fieldset>
<legend>2. Is it in a room used for sleeping?</legend>
<label class="cc-opt"><input type="radio" name="ccq2" value="no"> No &mdash; a day room, bar, office or public space</label>
<label class="cc-opt"><input type="radio" name="ccq2" value="yes"> Yes &mdash; a bedroom, dormitory or overnight accommodation</label>
</fieldset>

<fieldset>
<legend>3. Has the client given you a written specification?</legend>
<label class="cc-opt"><input type="radio" name="ccq3" value="yes"> Yes &mdash; it names a hazard category or a crib level</label>
<label class="cc-opt"><input type="radio" name="ccq3" value="verbal"> Only verbally, or it just says &ldquo;must be fire retardant&rdquo;</label>
<label class="cc-opt"><input type="radio" name="ccq3" value="no"> No specification at all</label>
</fieldset>

<fieldset>
<legend>4. The cover fabric</legend>
<label class="cc-opt"><input type="radio" name="ccq4" value="composite"> Contract fabric, certificated <em>as a composite</em> with the filling I&rsquo;m using</label>
<label class="cc-opt"><input type="radio" name="ccq4" value="alone"> Contract fabric with its own certificate, but not tested with my filling</label>
<label class="cc-opt"><input type="radio" name="ccq4" value="vinyl"> Contract vinyl or FR-treated leather</label>
<label class="cc-opt"><input type="radio" name="ccq4" value="unknown"> Customer&rsquo;s own fabric, or compliance unknown</label>
</fieldset>

<div class="cc-out" id="cc-out" hidden></div>

<div class="cc-rec">
<h3>Specification record for your files</h3>
<p>This records <strong>what you supplied and to which standard</strong>. It is not a compliance certificate for the premises &mdash; under the Regulatory Reform (Fire Safety) Order 2005 that duty sits with the responsible person for the building, through their fire risk assessment. Print two: one for the job sheet, one for the client.</p>
<div class="cc-grid">
<label>Your business<input id="cc-biz" autocomplete="organization"></label>
<label>Job reference<input id="cc-ref"></label>
<label>Client / premises<input id="cc-client"></label>
<label>Date<input id="cc-date" type="date"></label>
<label>Item(s) and quantity<input id="cc-item"></label>
<label>Hazard category applied<input id="cc-cat" placeholder="e.g. BS 7176 medium hazard"></label>
<label>Cover fabric &mdash; supplier &amp; certificate ref<input id="cc-cover"></label>
<label>Interliner / barrier &mdash; certificate ref<input id="cc-inter"></label>
<label>Fillings &mdash; supplier &amp; certificate ref<input id="cc-fill"></label>
<label>Specification supplied by client<input id="cc-spec" placeholder="e.g. tender doc ref, or 'none'"></label>
</div>
<label style="margin-top:.75rem;display:block">Notes and limitations<textarea id="cc-notes"></textarea></label>
<div class="cc-btns">
<button type="button" class="cc-primary" id="cc-make">Create the record</button>
<button type="button" class="cc-ghost" id="cc-print" hidden>Print it</button>
</div>
<div id="cc-record-out" hidden></div>
</div>
</section>

<script>
(function(){
  var CATS = {
    low: {
      name: "Low hazard",
      crib: null,
      tests: [
        "BS EN 1021-1 &mdash; smouldering cigarette, applied to the cover and filling composite",
        "BS EN 1021-2 &mdash; match flame equivalent, applied to the composite"
      ],
      examples: "Offices, schools, museums and exhibition spaces."
    },
    medium: {
      name: "Medium hazard",
      crib: "crib 5",
      tests: [
        "BS EN 1021-1 &mdash; smouldering cigarette, on the composite",
        "BS EN 1021-2 &mdash; match flame equivalent, on the composite",
        "BS 5852 ignition source 5 (<strong>crib 5</strong>) &mdash; on the cover and filling <em>together</em>"
      ],
      examples: "Hotels, restaurants, pubs, hospitals, care homes and most public premises. This is the level most contract work lands on."
    },
    high: {
      name: "High hazard",
      crib: "crib 7",
      tests: [
        "BS EN 1021-1 &mdash; smouldering cigarette, on the composite",
        "BS EN 1021-2 &mdash; match flame equivalent, on the composite",
        "BS 5852 ignition source 7 (<strong>crib 7</strong>) &mdash; on the composite. Source 7 replaces source 5 here rather than being added to it"
      ],
      examples: "Offshore installations and certain hospital wards."
    },
    vhigh: {
      name: "Very high hazard",
      crib: "crib 7",
      tests: [
        "Everything required at high hazard, as the minimum",
        "Additional requirements set at the specifier&rsquo;s discretion",
        "Testing of a complete item is available as an option here, and a fire officer or purchaser may ask for it"
      ],
      examples: "Locked psychiatric accommodation and prison cells."
    }
  };

  function q(name){
    var el = document.querySelector('input[name="'+name+'"]:checked');
    return el ? el.value : null;
  }

  function render(){
    var a1 = q('ccq1'), a2 = q('ccq2'), a3 = q('ccq3'), a4 = q('ccq4');
    var out = document.getElementById('cc-out');
    if(!a1 || !a2 || !a3 || !a4){ out.hidden = true; return; }

    var key, uplift = false, unknown = false;
    if(a1 === 'low'){ key = 'low'; }
    else if(a1 === 'med_public' || a1 === 'med_care' || a1 === 'med_sleep'){ key = 'medium'; }
    else if(a1 === 'high'){ key = 'high'; }
    else if(a1 === 'vhigh'){ key = 'vhigh'; }
    else { key = 'medium'; unknown = true; }

    if(key === 'low' && a2 === 'yes'){ uplift = true; }

    var c = CATS[key];
    var h = '';

    h += '<p class="cc-cat">' + (unknown ? 'Start at medium hazard &mdash; then confirm' : 'BS 7176 &mdash; ' + c.name) + '</p>';
    h += '<p class="cc-sub">' + c.examples + '</p>';

    if(unknown){
      h += '<div class="cc-flag"><strong>You need the category in writing.</strong> BS 7176 sets the level according to the end-use environment, so until you know the premises you cannot pick one. Medium hazard is the sensible working assumption for most commercial seating, but ask the responsible person for the premises what their fire risk assessment specifies, and put their answer on the job sheet before you cut anything.</div>';
    }

    h += '<h4>What the category calls for</h4><ul>';
    for(var i=0;i<c.tests.length;i++){ h += '<li>' + c.tests[i] + '</li>'; }
    h += '</ul>';

    h += '<div class="cc-flag"><strong>Your fillings still fall under the 1988 Regulations.</strong> At every hazard category, BS 7176 requires all filling materials to pass the relevant test in the Furniture and Furnishings (Fire) (Safety) Regulations 1988 as amended. Contract work does not take you outside those Regulations for foam and wadding &mdash; it adds to them. Buy CMHR foam and compliant waddings, and keep the supplier certificates.</div>';

    if(uplift){
      h += '<div class="cc-flag"><strong>Sleeping accommodation &mdash; consider going up a level.</strong> BS 7176&rsquo;s own guidance says that where premises in the low hazard category are also used for sleeping, a higher performance level should be considered. In practice that usually means specifying medium hazard (crib 5). Raise it with the client and record what they decide.</div>';
    }

    if(a1 === 'med_care'){
      h += '<div class="cc-flag"><strong>Healthcare varies by ward.</strong> Medium hazard is the general level for care homes and hospitals, but a risk assessment for a psychiatric or higher-dependency setting may push individual areas to high hazard. Do not assume one category covers a whole building.</div>';
    }

    h += '<h4>The cover fabric</h4>';
    if(a4 === 'composite'){
      h += '<p>This is the position you want to be in. ' + (c.crib
        ? 'The ' + c.crib + ' test is run on the cover and the filling <em>as a composite</em>, not on the fabric on its own, '
        : 'The cigarette and match tests are run on the cover and filling <em>as a composite</em>, not on the fabric on its own, ')
        + 'so a certificate covering the exact combination you are fitting is what actually evidences the category. Record the certificate number and the filling it was tested with &mdash; if you later change foam, the certificate no longer describes what you built.</p>';
    } else if(a4 === 'alone'){
      h += '<div class="cc-flag"><strong>A fabric certificate on its own does not evidence the category.</strong> ' + (c.crib
        ? 'The ' + c.crib + ' test is run on the cover and filling together. '
        : 'The tests for this category are run on the cover and filling together. ')
        + 'A fabric that passes in one composite may fail in another. Three ways out: fit the filling the fabric was certificated with; fit a certificated FR barrier / interliner system designed to bring the composite up to the required source; or have the actual composite tested. Whichever you choose, write it on the record.</div>';
    } else if(a4 === 'vinyl'){
      h += '<p>Contract vinyl and FR-treated leather are the usual route to ' + (c.crib || 'the required level') + ' on heavy-use seating, and they clean well, which is why hospitals and restaurants favour them. The same caution applies: the certificate needs to cover the composite you are actually building, not the face material alone. Note also that FR treatments applied to a fabric can lose effectiveness with washing, so for anything that will be laundered, inherently FR materials are the safer specification.</p>';
    } else {
      h += '<div class="cc-flag"><strong>Highest-risk case &mdash; do not claim a category.</strong> With a cover of unknown provenance you cannot honestly certify any BS 7176 level, because you cannot evidence the composite. Realistic options: decline the fabric; or fit it over a certificated FR barrier and state <em>in writing</em> that no hazard-category claim is made for the finished piece, with the client&rsquo;s written acknowledgement on file. On contract work, the second option still leaves the premises non-compliant if their assessment demands a category &mdash; so get the specifier to accept it before you start, not after.</div>';
    }

    h += '<h4>Getting the specification straight</h4>';
    if(a3 === 'yes'){
      h += '<p>Good. On contract work the written specification is effectively the law of the job. Quote its reference on your record, build to it, and if you think it is wrong &mdash; a low-hazard spec for a bedroom, say &mdash; put your concern in writing rather than quietly building to a different level.</p>';
    } else if(a3 === 'verbal'){
      h += '<div class="cc-flag"><strong>&ldquo;Fire retardant&rdquo; is not a specification.</strong> It names no category, no ignition source and no test. Go back with something concrete: <em>&ldquo;Please confirm in writing the BS 7176 hazard category required by your fire risk assessment for this area.&rdquo;</em> That single sentence moves the decision to the person who actually holds the duty, and gives you the document you will want if it is ever questioned.</div>';
    } else {
      h += '<div class="cc-flag"><strong>Get one before you start.</strong> Ask the responsible person for the premises: <em>&ldquo;Please confirm in writing the BS 7176 hazard category required by your fire risk assessment for this area.&rdquo;</em> Under the Regulatory Reform (Fire Safety) Order 2005 they must have a fire risk assessment, so the answer exists &mdash; someone just has to look it up. Building without it means guessing at another party&rsquo;s legal duty.</div>';
    }

    h += '<h4>Before it leaves the workshop</h4><ul>';
    h += '<li>Keep every supplier certificate for covers, barriers and fillings, filed against the job reference.</li>';
    h += '<li>If you are claiming compliance with BS 7176, the standard prescribes the design of the label &mdash; use the correct one rather than an improvised tag.</li>';
    h += '<li>Fill in the specification record below and give the client a copy. It is the document that shows what you supplied, and to which standard.</li>';
    h += '</ul>';

    out.innerHTML = h;
    out.hidden = false;
  }

  var names = ['ccq1','ccq2','ccq3','ccq4'];
  for(var n=0;n<names.length;n++){
    var els = document.querySelectorAll('input[name="'+names[n]+'"]');
    for(var i=0;i<els.length;i++){ els[i].addEventListener('change', render); }
  }

  function esc(s){
    return String(s||'').replace(/[&<>"]/g, function(m){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m];
    });
  }

  var mk = document.getElementById('cc-make');
  if(mk){
    mk.addEventListener('click', function(){
      var f = function(id){ var e = document.getElementById(id); return e ? e.value.trim() : ''; };
      var rows = [
        ['Job reference', f('cc-ref')],
        ['Client / premises', f('cc-client')],
        ['Date', f('cc-date')],
        ['Item(s)', f('cc-item')],
        ['Hazard category applied', f('cc-cat')],
        ['Cover fabric', f('cc-cover')],
        ['Interliner / barrier', f('cc-inter')],
        ['Fillings', f('cc-fill')],
        ['Client specification', f('cc-spec')],
        ['Notes and limitations', f('cc-notes')]
      ];
      var h = '<h4>' + (esc(f('cc-biz')) || 'Specification record') + '</h4>';
      h += '<p style="margin:0;font-size:.85rem;color:#7C8C5D">Record of materials supplied and the standard applied</p><dl>';
      for(var i=0;i<rows.length;i++){
        if(rows[i][1]){ h += '<dt>' + esc(rows[i][0]) + '</dt><dd>' + esc(rows[i][1]) + '</dd>'; }
      }
      h += '</dl>';
      h += '<p style="margin-top:1rem;font-size:.82rem;line-height:1.5;color:#2A2622">This record describes the materials supplied by the above business and the standard to which they were specified. It is not a fire risk assessment and does not certify the compliance of the premises, which remains the responsibility of the responsible person under the Regulatory Reform (Fire Safety) Order 2005.</p>';
      h += '<p style="margin-top:1.2rem;font-size:.85rem">Signed &hellip;&hellip;&hellip;&hellip;&hellip;&hellip;&hellip;&hellip;&hellip;&hellip;&hellip;&hellip;&hellip;&hellip;&hellip;&hellip;&nbsp;&nbsp;&nbsp;Date &hellip;&hellip;&hellip;&hellip;&hellip;&hellip;&hellip;&hellip;&hellip;</p>';
      var o = document.getElementById('cc-record-out');
      o.innerHTML = h;
      o.hidden = false;
      var p = document.getElementById('cc-print');
      if(p){ p.hidden = false; }
    });
  }

  var pr = document.getElementById('cc-print');
  if(pr){ pr.addEventListener('click', function(){ window.print(); }); }
})();
</script>
"""

# ---------------------------------------------------------------------------
# BLOCK 2 — commercial work overseas
# ---------------------------------------------------------------------------

INTL = r"""
<h3 id="cc-intl">Commercial and contract work overseas</h3>

<p>One pattern holds almost everywhere: <strong>domestic furniture rules vary enormously, but contract work is governed by the specification</strong>. Most countries that impose nothing at all on a sofa sold to a household still expect tested seating in a hotel or a hospital &mdash; the requirement simply arrives through the building code, the insurer or the tender document rather than through consumer law. Wherever you are working, the practical instruction is the same as it is in Britain: get the required standard and test level in writing before you cut.</p>

<p><strong>United States.</strong> The federal standard, 16 CFR Part 1640, is a smoulder standard for residential upholstered furniture. Commercial seating sits outside it and is driven instead by the model building and life-safety codes adopted state by state, which for public occupancies have long looked to California Technical Bulletin 133 &mdash; a full-scale burn test of a finished chair rather than a composite test &mdash; alongside the NFPA test methods. Which applies depends on occupancy type and on the authority having jurisdiction, so the specifier and the local fire marshal, not the fabric supplier, are who you ask.</p>

<p><strong>Ireland.</strong> The domestic regime closely tracks the UK. For contract work, Irish specifiers commonly call up the British standards directly, so a BS 7176 category is usually the language of the job.</p>

<p><strong>European Union.</strong> There is no EU-wide flammability law for domestic furniture and no single contract standard either. EN 1021-1 and 1021-2 are the shared cigarette and match tests, but the contract levels above them are national: Germany typically works to the DIN 4102 building-material classes, France to its own classification for public buildings, and the Nordic countries to their own test regime. A German hotel specification and a French one will ask for different pieces of paper for the same chair.</p>

<p><strong>Canada.</strong> Mattresses are federally regulated; general domestic upholstered furniture is not. Contract seating is governed by the National Building Code as adopted provincially, together with whatever the contract specifies &mdash; which for public and healthcare buildings is often a full-scale test comparable to the US approach.</p>

<p><strong>Australia and New Zealand.</strong> Domestic furniture carries no general mandatory flammability standard. Commercial and public work is entirely specification-driven, with healthcare, aged care and detention procurement setting their own levels, frequently citing the British crib tests because they are the established international shorthand.</p>

<p><em>These are orientation notes, not a compliance route. For any actual overseas job, the test level in the contract document and the view of the local authority having jurisdiction are what govern.</em></p>
"""

# ---------------------------------------------------------------------------
# BLOCK 3 — limitation of liability
# ---------------------------------------------------------------------------

DISCLAIMER = r"""
<hr class="stitch">

<section id="cc-disclaimer" class="cc-disc">
<style>
.cc-disc{margin:2.5rem 0 1rem;padding:1.4rem 1.5rem;border:1px solid rgba(42,38,34,.22);border-radius:2px;background:rgba(42,38,34,.03)}
.cc-disc h2{font-family:var(--display,Georgia,serif);font-size:1.05rem;letter-spacing:.04em;text-transform:uppercase;color:var(--green,#2F4A3A);margin:0 0 .8rem}
.cc-disc p{font-size:.92rem;line-height:1.6;margin:0 0 .8rem}
.cc-disc p:last-child{margin-bottom:0}
</style>
<h2>Important &mdash; the limits of this page</h2>

<p><strong>This is general information for the upholstery trade, not legal, regulatory or fire-safety advice, and no professional relationship is created by your use of it.</strong> It is written by a working upholsterer, not by a lawyer, a fire engineer or a testing house.</p>

<p>Fire safety law and the standards beneath it change, are amended, and are interpreted by courts and enforcing authorities in ways this page cannot anticipate. The UK Regulations are under active reform at the time of writing. Standards including BS 7176, BS 7177 and BS 5852 are copyright documents that are revised periodically; the summaries here are plain-English orientation and are not a substitute for reading the current standard or for the advice of an accredited testing house.</p>

<p><strong>Every job is different.</strong> The checkers on this page cannot see your materials, your client&rsquo;s premises, their fire risk assessment or their contract. Nothing here determines what any particular job legally requires. The categories suggested are starting points for a conversation with the person who holds the duty &mdash; not findings you can rely on.</p>

<p><strong>The records this page generates are your own documents.</strong> They record what you say you supplied. They are not certificates, they are not test evidence, they carry no accreditation, and they do not certify that any premises complies with anything. Under the Regulatory Reform (Fire Safety) Order 2005 responsibility for the fire safety of premises rests with the responsible person for those premises.</p>

<p>To the fullest extent permitted by law, Greenwood Upholstery and the author accept no liability for any loss, damage, cost, penalty or claim arising from reliance on this page, including where the information is incomplete, out of date or wrong. If you need a decision you can rely on, take it from your local Trading Standards service, an accredited testing house, the specifier for the job, or a suitably qualified professional.</p>

<p>Spotted something inaccurate? <a href="/contact">Tell us</a> and it will be corrected.</p>
</section>
"""


# ---------------------------------------------------------------------------
# Anchor logic
# ---------------------------------------------------------------------------

def find_intl_heading(html):
    """Locate the <h2> that opens the international section."""
    pat = re.compile(
        r'<h2[^>]*>\s*What are the fire regulations for upholstery in other countries\?',
        re.I)
    m = pat.search(html)
    if m:
        return m.start()
    # looser fallback
    pat2 = re.compile(r'<h2[^>]*>[^<]*other countries[^<]*</h2>', re.I)
    m2 = pat2.search(html)
    return m2.start() if m2 else None


def back_up_over_stitch(html, idx):
    """If a <hr> divider sits immediately before idx, insert before it instead."""
    head = html[:idx]
    m = re.search(r'<hr[^>]*>\s*$', head, re.I)
    return m.start() if m else idx


def find_intl_close(html):
    """Locate the end of the international closing note."""
    pat = re.compile(
        r'Regulations change and this page is guidance.*?</p>', re.I | re.S)
    m = pat.search(html)
    if m:
        return m.end()
    pat2 = re.compile(r'confirm with the relevant national authority.*?</p>', re.I | re.S)
    m2 = pat2.search(html)
    return m2.end() if m2 else None


def find_main_close(html):
    for pat in (r'</main>', r'<section[^>]*class="[^"]*newsletter', r'<footer', r'</body>'):
        m = re.search(pat, html, re.I)
        if m:
            return m.start()
    return None


def main():
    if not PAGE.exists():
        sys.exit(f"ERROR: {PAGE} not found. Run this from the repo root "
                 f"(the folder containing fire-safety-checker.html).")

    html = PAGE.read_text(encoding="utf-8")

    if MARKER in html:
        print("Already patched — the contract checker is present. Nothing to do.")
        return

    problems = []

    i_intl = find_intl_heading(html)
    if i_intl is None:
        problems.append("could not find the international section <h2>")

    i_close = find_intl_close(html)
    if i_close is None:
        problems.append("could not find the international closing note")

    i_main = find_main_close(html)
    if i_main is None:
        problems.append("could not find </main>, the newsletter block or <footer>")

    if problems:
        print("STOPPED — the page is not laid out the way this script expected:")
        for p in problems:
            print("  •", p)
        print("\nHeadings found in the file, to help fix the anchors:")
        for h in re.findall(r'<h[123][^>]*>(.*?)</h[123]>', html, re.S | re.I)[:40]:
            txt = re.sub(r'<[^>]+>', '', h).strip()
            if txt:
                print("   -", txt[:90])
        sys.exit(1)

    shutil.copy2(PAGE, PAGE.with_suffix(".html.bak"))

    # Insert from the bottom up so earlier offsets stay valid.
    out = html[:i_main] + DISCLAIMER + html[i_main:]
    out = out[:i_close] + INTL + out[i_close:]
    ins = back_up_over_stitch(out, i_intl)
    out = out[:ins] + CHECKER + out[ins:]

    PAGE.write_text(out, encoding="utf-8")

    print("Patched fire-safety-checker.html")
    print("  • contract checker inserted before the international section")
    print("  • overseas commercial notes added after it")
    print("  • limitation-of-liability notice added at the end")
    print("  • backup written to fire-safety-checker.html.bak")
    print(f"  • {len(html):,} chars → {len(out):,} chars (nothing removed)")


if __name__ == "__main__":
    main()
