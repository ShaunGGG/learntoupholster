#!/usr/bin/env python3
"""
Adds the "how it works" explainers to the foam-cushion and deep-buttoning
calculators, and adds author (E-E-A-T) schema to all five calculator pages.
Safe to run repeatedly. Run from your project root:
    cd ~/learntoupholster && python3 add-calc-explainers.py
Preview only:
    python3 add-calc-explainers.py --dry-run
"""
import re, sys, json, pathlib

DRY  = "--dry-run" in sys.argv
args = [a for a in sys.argv[1:] if a != "--dry-run"]
ROOT = pathlib.Path(args[0] if args else ".")

AUTHOR = {
  "@type": "Person",
  "name": "Shaun Greenwood",
  "jobTitle": "Master Upholsterer",
  "description": "AMUSF-accredited master upholsterer with 30+ years at the bench; owner of Greenwood Upholstery, Hebden Bridge.",
  "url": "https://www.greenwoodupholstery.com/"
}
CALCS = ["fabric-yardage.html","reupholstery-cost-calculator.html",
         "deep-buttoning-calculator.html","foam-cushion-calculator.html",
         "leather-hide-calculator.html"]

FOAM_ARTICLE = r"""
<article class="article wrap read">
  <h2>How to choose the right foam density for a cushion</h2>
  <p>The single mistake I see more than any other is treating <strong>density</strong> and <strong>firmness</strong> as the same thing. They aren't — and getting them the wrong way round is the difference between a cushion that lasts ten years and one that's flat by next winter.</p>
  <p><strong>Density is the weight of the foam</strong> — how many kilograms a cubic metre of it weighs — and it's the best single clue to how long a cushion will last. A dense foam has more material packed into it, so it takes far longer to break down and go soft. <strong>Firmness is simply how hard it feels to sit on</strong>, measured in Newtons, and it's a separate property you choose for comfort. A cheap foam can be made to feel firm and still collapse within a year; a good dense foam can feel soft and still be holding its shape a decade later. UK foam carries both numbers together — a code like <em>RX38/150</em> means a density of 38&nbsp;kg/m³ and a hardness of about 150&nbsp;Newtons — so once you can read the code you buy on quality, not on the showroom squeeze.</p>
  <p>So the rule is simple: <strong>pick the density for how long you need it to last, then pick the firmness for how you want it to feel</strong> — and never let a soft, cheap, low-density foam into a seat just because it felt nice in the shop.</p>

  <h2>Matching foam to the job — a few rules from the bench</h2>
  <p><strong>A seat works harder than a back, so it needs more density.</strong> A sofa or armchair seat is the hardest-working cushion in the house; I won't drop below about 40&nbsp;kg/m³ on one, in an HR (high-resilience) or Reflex foam, at a medium-firm feel. A back is different — you lean on it, you don't sit on it — so it can go softer and lighter, around 24&nbsp;kg/m³, or be filled with hollowfibre for a loose, squashy look.</p>
  <p><strong>Thin pads must be dense, not thick.</strong> A dining or drop-in seat is shallow and sits close to a hard frame, so a soft foam just bottoms out and you feel the wood underneath. Here a firm, dense pad of around 33&nbsp;kg/m³ at 30–40&nbsp;mm beats a soft thick one every time — when there's a board under the cushion, density matters more than depth.</p>
  <p><strong>Anything commercial goes up a grade.</strong> A pub, café or waiting-room seat is sat on hundreds of times a day, and contract-grade foam of 45&nbsp;kg/m³ and up is the difference between a year and ten. Footstools and window seats sit in between — treat a footstool like a small seat, firm and dense, because it doubles as somewhere to perch.</p>
  <p><strong>Wrap the foam; don't leave it bare.</strong> A layer of polyester (Dacron) wadding over the foam softens the hard cut edge, stops the cover creasing straight onto bare foam, and gives the cushion a slight crown so it reads as full rather than boxy. And cut the foam a touch oversize for its cover, so it fills the corners and sits plump instead of hollow.</p>

  <h2>What about fire safety?</h2>
  <p>This one isn't optional in the UK. For domestic upholstery the foam must be <strong>CMHR</strong> — Combustion Modified High Resilience — to meet the Furniture and Furnishings (Fire) (Safety) Regulations. Most reputable foam sold for upholstery already is, but read the label rather than assume. Public and contract seating usually has to meet the stricter <strong>Crib 5</strong> standard (BS&nbsp;5852), and mattresses fall under their own rules (BS&nbsp;7177). On any commercial job, confirm the venue's requirement before you spec the foam — it's the one corner you can never cut. You can check what applies with the <a href="/fire-safety-checker">fire regulations checker</a>.</p>

  <h2>A worked example</h2>
  <p>Say you're rebuilding the seat cushions on a family sofa. The calculator points you at an HR/CMHR foam around <strong>40&nbsp;kg/m³</strong> for the density — so it survives a decade of daily use — a <strong>medium-firm</strong> feel of roughly 150&nbsp;Newtons, and about <strong>120&nbsp;mm</strong> finished thickness. You'd cut that foam a shade oversize for the covers, wrap each block in Dacron to soften the edges and crown the top, and you've a cushion that feels right on day one and still feels right years later. Swap to a firm 45&nbsp;kg/m³ contract foam and it would last even longer but feel harder; drop to a soft 28&nbsp;kg/m³ and it would feel lovely for a season, then sag. Same cushion, same size — the density decides the lifespan, the firmness decides the feel.</p>

  <div class="tools">
    <h4>Foam-working kit</h4>
    <ul>
      <li><a class="aff" href="https://www.amazon.co.uk/s?k=electric+foam+cutter+upholstery&tag=842699-21" target="_blank" rel="sponsored noopener">Electric foam cutter</a> <span class="paid">(paid link)</span></li>
      <li><a class="aff" href="https://www.amazon.co.uk/s?k=polyester+dacron+wadding+upholstery&tag=842699-21" target="_blank" rel="sponsored noopener">Polyester (Dacron) wadding</a> <span class="paid">(paid link)</span></li>
      <li><a class="aff" href="https://www.amazon.co.uk/s?k=spray+contact+adhesive+foam&tag=842699-21" target="_blank" rel="sponsored noopener">Spray contact adhesive for foam</a> <span class="paid">(paid link)</span></li>
      <li><a class="aff" href="https://www.amazon.co.uk/s?k=serrated+foam+saw+knife&tag=842699-21" target="_blank" rel="sponsored noopener">Serrated foam saw</a> <span class="paid">(paid link)</span></li>
    </ul>
  </div>

  <div class="related">
    <a href="/foam-construction"><span class="dir">Read next</span><span class="ttl">Foam Construction &#8594;</span></a>
    <a href="/modern-sofa-recover"><span class="dir">See it in a project</span><span class="ttl">Modern Sofa Re-cover &#8594;</span></a>
    <a href="/tools"><span class="dir">Browse</span><span class="ttl">All tools &#8594;</span></a>
  </div>
</article>
"""

BUTTON_ARTICLE = r"""
<article class="article wrap read">
  <h2>How deep buttoning works: two grids, not one</h2>
  <p>Deep buttoning looks like magic and is really just geometry done twice. There are <strong>two grids</strong>, not one, and keeping them straight in your head is most of the job. The buttons sit on a <strong>foundation grid</strong> — marked at the finished diamond size on the hessian, base or foam. The cover is marked on a <strong>second, larger grid</strong>, because every diamond swallows a little cloth as it folds. You pull the big grid down onto the small one, button by button, and the spare fabric becomes the pleats that run between the buttons. Get the two grids right and the folds fall into place on their own.</p>

  <h2>How to set out a diamond pattern</h2>
  <p><strong>The diamonds come from offsetting the rows.</strong> Every second row is shifted sideways by half a diamond, and that half-step is what turns a grid of squares into a field of diamonds. The <em>diamond width</em> is the spacing between buttons along a row; the <em>diamond height</em> is the spacing between every second row — so the rows themselves sit half that distance apart. Buttoning is traditionally set out a little taller than it is wide, which is why a diamond looks like a diamond and not a square.</p>
  <p><strong>Whole diamonds have to fit the space.</strong> You can't have three-and-a-bit diamonds across a chair back — it has to come out even. So the calculator nudges the diamond size slightly from the figure you type until a whole number fits the buttoned area cleanly, and shows you the "actual diamond" size you'll really be marking. Add a flat border between the outer buttons and the edge, and there's your foundation grid.</p>

  <h2>How much extra fabric does deep buttoning need?</h2>
  <p>This is the part that catches everybody, and the reason more buttoned jobs are ruined by a short cover than by anything else: <strong>the fabric has to be cut much fuller than the finished panel</strong>, because it pleats inward at every single button. Skimp here and you simply run out of cloth halfway across.</p>
  <p>The extra is called the <strong>fullness</strong>, or take-up, and you add it to every diamond, in both directions. As a starting point, allow about <strong>½&nbsp;inch per diamond for shallow buttoning, ¾&nbsp;inch for medium, and 1¼&nbsp;inch for deep</strong> — each way. It grows with the depth of the buttoning, the thickness of the stuffing and the stretch of the cloth; a thin cover over firm foam wants less. On top of the buttoned grid you still add a normal <strong>turning allowance</strong> all round — around 7&nbsp;cm — for pulling the cover through and fixing off, and on a buttoned job it pays to be generous.</p>
  <p><strong>On anything that matters, button a calico test panel first.</strong> Mark it, button it, and measure what you actually lose — then set the fullness to that figure, and every job after will be right first time. The numbers above get you close; your own hands and your own cloth get you exact.</p>

  <h2>A worked example</h2>
  <p>Take a chair back with a buttoned area of about 45&nbsp;cm each way, medium buttoning at a ¾-inch fullness. Once whole diamonds are fitted to the space you might land on a five-button-wide layout with offset rows. The calculator counts the buttons — but more usefully it works out the larger cover grid, adding the fullness to every diamond so you know exactly how much bigger to cut and mark the cloth. Add the turning all round and that's your cutting size. Mark the small grid on the base, the big grid on the back of the cover, line up the first row, and button your way across.</p>

  <div class="tools">
    <h4>Buttoning kit</h4>
    <ul>
      <li><a class="aff" href="https://www.amazon.co.uk/s?k=double+ended+mattress+buttoning+needle&tag=842699-21" target="_blank" rel="sponsored noopener">Long double-ended buttoning needle</a> <span class="paid">(paid link)</span></li>
      <li><a class="aff" href="https://www.amazon.co.uk/s?k=nylon+mattress+buttoning+twine&tag=842699-21" target="_blank" rel="sponsored noopener">Nylon buttoning twine</a> <span class="paid">(paid link)</span></li>
      <li><a class="aff" href="https://www.amazon.co.uk/s?k=self+cover+button+kit+upholstery&tag=842699-21" target="_blank" rel="sponsored noopener">Self-cover button kit</a> <span class="paid">(paid link)</span></li>
      <li><a class="aff" href="https://www.amazon.co.uk/s?k=upholstery+regulator+needle&tag=842699-21" target="_blank" rel="sponsored noopener">Upholstery regulator</a> <span class="paid">(paid link)</span></li>
    </ul>
  </div>

  <div class="related">
    <a href="/buttoning-and-tufting"><span class="dir">Read next</span><span class="ttl">Buttoning &amp; Tufting &#8594;</span></a>
    <a href="/chesterfield-sofa"><span class="dir">See it in a project</span><span class="ttl">The Chesterfield &#8594;</span></a>
    <a href="/tools"><span class="dir">Browse</span><span class="ttl">All tools &#8594;</span></a>
  </div>
</article>
"""


def canonical(t):
    m = re.search(r'<link rel="canonical" href="([^"]+)"', t); return m.group(1) if m else ""
def title(t):
    m = re.search(r"<title>(.*?)</title>", t, re.S); return m.group(1).strip() if m else ""
def author_block(t):
    node = {"@context":"https://schema.org","@type":"WebPage","url":canonical(t),"name":title(t),
            "author":AUTHOR,
            "publisher":{"@type":"Organization","name":"Greenwood Upholstery","url":"https://www.greenwoodupholstery.com/"}}
    return '<!-- lu-author-schema -->\n<script type="application/ld+json">\n' + json.dumps(node, ensure_ascii=False) + '\n</script>\n'

FOOT = '<footer class="site-footer">'
changed = 0
for name in CALCS:
    p = ROOT / name
    if not p.exists():
        print(f"  ! not found: {name}"); continue
    t = orig = p.read_text(encoding="utf-8")
    acts = []

    if "lu-author-schema" not in t and "</head>" in t:
        t = t.replace("</head>", author_block(t) + "</head>", 1); acts.append("author-schema")

    if name == "foam-cushion-calculator.html":
        if "How to choose the right foam density" not in t and FOOT in t:
            t = t.replace(FOOT, '<hr class="seam">\n\n' + FOAM_ARTICLE + '\n\n' + FOOT, 1); acts.append("foam-explainer")

    if name == "deep-buttoning-calculator.html":
        t2 = re.sub(r'\s*<details class="note">\s*<summary>How it works[^<]*</summary>.*?</details>', '', t, count=1, flags=re.S)
        if t2 != t: t = t2; acts.append("removed-old-note")
        t2 = re.sub(r'\s*<p style="margin:1\.4rem 0 0"><a href="/buttoning-and-tufting">.*?</p>', '', t, count=1, flags=re.S)
        if t2 != t: t = t2; acts.append("removed-old-links")
        if "How deep buttoning works: two grids" not in t and FOOT in t:
            t = t.replace(FOOT, '<hr class="seam">\n\n' + BUTTON_ARTICLE + '\n\n' + FOOT, 1); acts.append("buttoning-explainer")

    if t != orig:
        if not DRY: p.write_text(t, encoding="utf-8")
        changed += 1; print(f"  {'(dry) ' if DRY else ''}+ {name}: {', '.join(acts)}")
    else:
        print(f"  = {name}: no change")

print(f"\n{'DRY RUN. ' if DRY else ''}{changed} file(s) {'would be ' if DRY else ''}updated.")
