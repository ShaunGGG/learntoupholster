#!/usr/bin/env python3
"""International pass 2: (a) British vs American terminology section + FAQ on
/a-z-glossary; (b) UK-US foam grade converter + FAQPage on
/foam-cushion-calculator. Idempotent. Run from repo root."""
import json, re

# ---------- (a) GLOSSARY ----------
TERMS = [
 ("Hessian", "Burlap", "Same jute cloth, two names. Weights quoted in oz per yard both sides of the Atlantic."),
 ("Calico", "Muslin", "False friend: in the US, &#8220;calico&#8221; means printed cotton. The plain undercover cloth Britain calls calico is American muslin."),
 ("Wadding", "Batting", "Polyester wadding is often called &#8220;Dacron&#8221; in the US, after the trade name."),
 ("Deep buttoning", "Diamond tufting", "The showpiece technique. American suppliers list buttons and twine under &#8220;tufting.&#8221;"),
 ("Piping", "Welt / welting", "Piping cord becomes welt cord; double piping is &#8220;double welt.&#8221;"),
 ("Flies", "Stretchers / pull strips", "The cheap cloth extensions sewn to cover panels where they tuck away."),
 ("Bottoming cloth", "Dust cover / cambric", "The black lining under the seat. US suppliers sell it as &#8220;cambric.&#8221;"),
 ("Platform cloth", "Decking", "The hard-wearing cloth under loose seat cushions."),
 ("Tack roll", "Edge roll", "Pre-made paper-cored edging is &#8220;edge roll&#8221; or &#8220;dust border roll&#8221; in US catalogues."),
 ("Laid cord", "Spring twine", "The heavy cord for lashing springs; US suppliers also say &#8220;jute spring twine.&#8221;"),
 ("Chip foam / reconstituted foam", "Rebond foam", "The dense multicoloured recycled foam for bar seating and gym pads."),
 ("Upholstery skewers", "Upholstery pins", "The long steel pins holding covers in place for fitting."),
 ("Pouffe", "Ottoman / hassock", "Another false friend: a British ottoman is a lidded box, an American ottoman is a footstool."),
 ("Valance", "Skirt / dust ruffle", "The fabric drop hiding the legs on sofas and beds."),
 ("FR interliner", "Fire barrier / barrier fabric", "In the US the barrier is the standard route to TB 117-2013 compliance."),
 ("Settee", "Couch", "Sofa is understood everywhere; settee reads as distinctly British, couch as distinctly American."),
 ("Foam grades (kg/m&#179; + Newtons)", "Density (lb/ft&#179;) + ILD", "Entirely different grading systems &#8212; see the converter on the foam calculator."),
]

GLOSSARY_SECTION = ['<hr class="seam">',
'<section class="wrap read" id="uk-us-terms">',
'<h2>What are British upholstery terms called in America?</h2>',
'<p>The trade speaks two dialects. If you&#8217;re reading British instructions with an American supplier catalogue open (or the reverse), this is the translation table &#8212; including the false friends that catch people out.</p>',
'<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:1.02rem">',
'<thead><tr><th style="text-align:left;padding:.5rem .6rem;border-bottom:2px solid var(--gold)">British term</th><th style="text-align:left;padding:.5rem .6rem;border-bottom:2px solid var(--gold)">American term</th><th style="text-align:left;padding:.5rem .6rem;border-bottom:2px solid var(--gold)">Notes</th></tr></thead><tbody>']
for uk, us, note in TERMS:
    GLOSSARY_SECTION.append(f'<tr><td style="padding:.45rem .6rem;border-bottom:1px solid var(--rule)"><strong>{uk}</strong></td><td style="padding:.45rem .6rem;border-bottom:1px solid var(--rule)">{us}</td><td style="padding:.45rem .6rem;border-bottom:1px solid var(--rule)">{note}</td></tr>')
GLOSSARY_SECTION.append('</tbody></table></div></section>')
GLOSSARY_SECTION = '\n'.join(GLOSSARY_SECTION)

GLOSSARY_FAQ = [
 ("What is calico called in America?", "Muslin. Beware the false friend: American 'calico' means printed cotton fabric, not the plain undercover cloth British upholsterers mean."),
 ("What is deep buttoning called in the US?", "Diamond tufting. American suppliers list deep-buttoning materials under 'tufting'."),
 ("What is hessian called in America?", "Burlap - the same jute cloth under a different name."),
 ("What is the American equivalent of British foam grades?", "US foam is graded by density in pounds per cubic foot and hardness by ILD (indentation load deflection), rather than kg/m3 and Newtons. A UK 35-40 kg/m3 seat foam is roughly a US 2.2-2.5 lb foam; hardness conversion is approximate because the tests differ."),
]

t = open('a-z-glossary.html', encoding='utf-8').read()
if 'id="uk-us-terms"' not in t:
    t = t.replace('<footer class="site-footer">', GLOSSARY_SECTION + '\n<footer class="site-footer">', 1)
    add = ''.join(json.dumps({"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}}, ensure_ascii=False)+',' for q,a in GLOSSARY_FAQ)
    t = t.replace('"mainEntity":[', '"mainEntity":[' + add, 1)
    open('a-z-glossary.html','w',encoding='utf-8').write(t)
    print("a-z-glossary.html patched")
else:
    print("glossary already patched")

# ---------- (b) FOAM CONVERTER ----------
FOAM_SECTION = '''<hr class="seam">
<section class="wrap read" id="foam-converter">
<h2>How do UK foam grades convert to US foam grades?</h2>
<p>Britain grades foam by <strong>density in kg/m&#179;</strong> and <strong>hardness in Newtons</strong>; America uses <strong>density in lb/ft&#179;</strong> and <strong>ILD</strong> (indentation load deflection, in pounds). Density converts exactly. Hardness does not &#8212; the tests use different indentation depths and rigs &#8212; so the ILD figure below is the <em>nearest equivalent band</em>, not a lab result. Confirm against the supplier&#8217;s data sheet before ordering.</p>
<div style="background:#fff;border:1px solid var(--rule);border-radius:6px;padding:1.3rem 1.4rem;max-width:34rem">
  <label style="display:block;margin-bottom:.7rem">Density
    <span style="display:flex;gap:.5rem;margin-top:.25rem">
      <input id="fc-den" type="number" step="0.1" value="39" style="flex:1;font-size:1.05rem;padding:.45rem .6rem;border:1.5px solid var(--green);border-radius:3px">
      <select id="fc-denu" style="font-size:1rem;padding:.45rem;border:1.5px solid var(--green);border-radius:3px"><option value="kg">kg/m&#179; (UK)</option><option value="lb">lb/ft&#179; (US)</option></select>
    </span></label>
  <label style="display:block;margin-bottom:.9rem">Hardness
    <span style="display:flex;gap:.5rem;margin-top:.25rem">
      <input id="fc-hard" type="number" step="5" value="200" style="flex:1;font-size:1.05rem;padding:.45rem .6rem;border:1.5px solid var(--green);border-radius:3px">
      <select id="fc-hardu" style="font-size:1rem;padding:.45rem;border:1.5px solid var(--green);border-radius:3px"><option value="n">Newtons (UK)</option><option value="ild">ILD (US)</option></select>
    </span></label>
  <div id="fc-out" style="background:var(--cream-deep);border-radius:5px;padding:.9rem 1rem;font-size:1.05rem"></div>
</div>
<p style="margin-top:1rem;font-size:1rem"><em>Rule of thumb: a British 35&#8211;40&#8202;kg/m&#179; seat foam at 180&#8211;200&#8202;N sits around an American 2.2&#8211;2.5&#8202;lb foam at 40&#8211;45&#8202;ILD &#8212; firm domestic seating in both dialects.</em></p>
</section>
<script>
(function(){
function cls(i){return i<25?'soft (light back cushions)':i<35?'medium (backs, light seats)':i<45?'medium-firm (domestic seats)':i<55?'firm (heavy-use seats)':'extra-firm (contract / bar seating)';}
function upd(){
 var d=parseFloat(document.getElementById('fc-den').value)||0,
     du=document.getElementById('fc-denu').value,
     h=parseFloat(document.getElementById('fc-hard').value)||0,
     hu=document.getElementById('fc-hardu').value, o='';
 if(du==='kg'){o+='<strong>'+(d*0.06243).toFixed(1)+' lb/ft&#179;</strong> density (US)';}
 else{o+='<strong>'+(d/0.06243).toFixed(0)+' kg/m&#179;</strong> density (UK)';}
 o+='<br>';
 if(hu==='n'){var ild=h*0.2248; o+='&#8776; <strong>'+Math.round(ild*0.85)+'&#8211;'+Math.round(ild*1.15)+' ILD</strong> (US, nearest band) &#8212; '+cls(ild);}
 else{var n=h/0.2248; o+='&#8776; <strong>'+Math.round(n*0.85)+'&#8211;'+Math.round(n*1.15)+' N</strong> (UK, nearest band) &#8212; '+cls(h);}
 document.getElementById('fc-out').innerHTML=o;
}
['fc-den','fc-denu','fc-hard','fc-hardu'].forEach(function(id){var e=document.getElementById(id);e.addEventListener('input',upd);e.addEventListener('change',upd);});
upd();})();
</script>'''

FOAM_FAQ = [
 ("What is ILD in foam?", "ILD (indentation load deflection) is the American hardness measure for foam: the pounds of force needed to compress a sample by 25%. Britain measures hardness in Newtons at 40% indentation instead, so conversions between the two are approximate."),
 ("How do I convert kg/m3 foam density to lb/ft3?", "Multiply by 0.06243. A British 39 kg/m3 seat foam is about 2.4 lb/ft3 in American terms. Density converts exactly; hardness does not."),
 ("What ILD is best for a seat cushion?", "For domestic seat cushions, roughly 40-45 ILD (the equivalent of a British 180-200 Newton foam) suits most sitters; heavy-use or contract seating runs firmer at 45-55 ILD."),
]

t = open('foam-cushion-calculator.html', encoding='utf-8').read()
if 'id="foam-converter"' not in t:
    t = t.replace('<footer class="site-footer">', FOAM_SECTION + '\n<footer class="site-footer">', 1)
    ld = '<script type="application/ld+json">' + json.dumps({
        "@context":"https://schema.org","@type":"FAQPage",
        "mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FOAM_FAQ]
    }, ensure_ascii=False) + '</script>\n</head>'
    t = t.replace('</head>', ld, 1)
    open('foam-cushion-calculator.html','w',encoding='utf-8').write(t)
    print("foam-cushion-calculator.html patched")
else:
    print("foam page already patched")
