#!/usr/bin/env python3
"""Localises /reupholstery-cost-calculator: currency selector + editable local
hourly rate; labour uses the local rate, materials/fabric presets convert at
approximate FX. Adds FAQ entry. Idempotent. Run from repo root."""
import json, re

F = 'reupholstery-cost-calculator.html'
t = open(F, encoding='utf-8').read()
if 'id="ce-locale"' in t:
    print("already patched"); raise SystemExit

# --- 1. script surgery ---
t = t.replace("var RATE=80;",
  "var RATE=80;\n  var CE={sym:'\\u00a3',rate:80,fx:1};", 1)
t = t.replace("function gbp(n){ return '£'+Math.round(n).toLocaleString('en-GB'); }",
  "function gbp(n){ return CE.sym+Math.round(n).toLocaleString('en-GB'); }", 1)
t = t.replace("var hours=b.h, sundries=b.s;",
  "var hours=b.h, sundries=b.s*CE.fx;", 1)
t = t.replace("sundries+=30;", "sundries+=30*CE.fx;", 1)
t = t.replace("sundries+=25;", "sundries+=25*CE.fx;", 1)
t = t.replace("var pm = fabricCustom.value!=='' ? Math.max(0,parseFloat(fabricCustom.value)||0) : parseFloat(fabricSel.value);",
  "var pm = fabricCustom.value!=='' ? Math.max(0,parseFloat(fabricCustom.value)||0) : parseFloat(fabricSel.value)*CE.fx;", 1)
t = t.replace("var labour=hours*RATE;", "var labour=hours*CE.rate;", 1)
t = t.replace("' h × £80)', band(hL*RATE,hH*RATE,10)",
  "' h × '+CE.sym+CE.rate+')', band(hL*CE.rate,hH*CE.rate,10)", 1)
t = t.replace("' ('+p.yd+' m × £'+pm+'/m)'",
  "' ('+p.yd+' m × '+CE.sym+Math.round(pm)+'/m)'", 1)
t = t.replace("syncBuild(); calc();\n})();",
  "syncBuild(); calc();\n  window.CE_apply=function(sym,rate,fx){CE.sym=sym;CE.rate=Math.max(1,rate||CE.rate);CE.fx=fx;calc();};\n})();", 1)

# --- 2. locale UI, inserted just before the calculator script ---
anchor = re.search(r'<script>\s*\(function\(\)\{\s*var RATE=80;', t).group(0)
UI = '''<section class="wrap read" id="ce-locale" style="margin-top:1.6rem">
<div style="background:#fff;border:1px solid var(--rule);border-left:4px solid var(--gold);border-radius:5px;padding:1.1rem 1.3rem;max-width:44rem">
<h3 style="margin:.1rem 0 .5rem">Working outside the UK?</h3>
<p style="margin:0 0 .8rem;font-size:1.02rem">Pick your currency and put in your local workshop rate. Labour uses your rate; the hour counts stay the same (a wing-back takes the same time in Ohio as in Yorkshire); material and fabric presets convert at approximate exchange rates &#8212; enter your own fabric price for accuracy.</p>
<div style="display:flex;gap:.6rem;flex-wrap:wrap;align-items:center">
  <select id="ce-cur" style="font-size:1rem;padding:.45rem;border:1.5px solid var(--green);border-radius:3px">
    <option value="GBP" selected>&#163; GBP &#8212; UK</option>
    <option value="USD">$ USD &#8212; United States</option>
    <option value="EUR">&#8364; EUR &#8212; Europe</option>
    <option value="AUD">A$ AUD &#8212; Australia</option>
    <option value="CAD">C$ CAD &#8212; Canada</option>
    <option value="NZD">NZ$ NZD &#8212; New Zealand</option>
  </select>
  <label style="font-size:1rem">Workshop rate/hour
    <input id="ce-rate" type="number" min="1" step="5" value="80" style="width:6.5rem;font-size:1.05rem;padding:.4rem .5rem;margin-left:.4rem;border:1.5px solid var(--green);border-radius:3px">
  </label>
</div>
</div>
</section>
<script>
(function(){
 var D={GBP:{s:'\\u00a3',r:80,f:1},USD:{s:'$',r:100,f:1.35},EUR:{s:'\\u20ac',r:75,f:1.17},AUD:{s:'A$',r:110,f:2.05},CAD:{s:'C$',r:95,f:1.85},NZD:{s:'NZ$',r:105,f:2.25}};
 var cur=document.getElementById('ce-cur'), rate=document.getElementById('ce-rate');
 function go(){ var d=D[cur.value]; if(window.CE_apply) window.CE_apply(d.s, parseFloat(rate.value)||d.r, d.f); }
 cur.addEventListener('change', function(){ rate.value=D[cur.value].r; go(); });
 rate.addEventListener('input', go);
 window.addEventListener('load', go);
})();
</script>
'''
t = t.replace(anchor, UI + anchor, 1)

# --- 3. FAQ entry ---
QA = {"@type":"Question","name":"How much does reupholstery cost in the US or other countries?",
 "acceptedAnswer":{"@type":"Answer","text":"The bench hours are the same everywhere - a wing-back is a wing-back - so cost differences come almost entirely from the workshop's hourly rate. Typical US shop rates run $75-125 per hour against a UK benchmark of around 80 pounds. Set your currency and local rate in the calculator and the estimate localises; enter your local fabric price for the most accurate figure."}}
if '"mainEntity":[' in t:
    t = t.replace('"mainEntity":[', '"mainEntity":[' + json.dumps(QA, ensure_ascii=False) + ',', 1)
else:
    ld = '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[QA]}, ensure_ascii=False) + '</script>\n</head>'
    t = t.replace('</head>', ld, 1)

open(F, 'w', encoding='utf-8').write(t)
print("reupholstery-cost-calculator.html patched")
