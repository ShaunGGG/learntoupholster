#!/usr/bin/env python3
"""AEO/GEO pass: FAQ blocks + FAQPage schema on the four workshop stories and
/buy-the-book; question-format headings on two core chapters. Idempotent.
Run from repo root:  python3 patch-aeo.py"""
import json, re

def faq_html(title, qas):
    s = ['<hr class="seam">', '<section class="wrap read">', f'<h2>{title}</h2>']
    for q, a in qas:
        s.append(f'<h3>{q}</h3>\n<p>{a}</p>')
    s.append('</section>')
    return '\n'.join(s)

def faq_ld(qas):
    strip = lambda x: re.sub('<[^>]+>', '', x)
    return ('<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": strip(q),
            "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qas]
    }, ensure_ascii=False) + '</script>\n</head>')

STORIES = {
 'the-pair-of-nursing-chairs.html': ("Questions this restoration answers", [
  ("How much does it cost to restore a Victorian nursing chair?",
   "In this 2024 restoration the labour was <strong>£850 per chair</strong>, plus fabric — three metres at £110 a metre across the pair, so a little over £2,000 for the two. Every chair differs with condition; the <a href=\"/reupholstery-cost-calculator\">cost estimator</a> gives a starting range, and a proper itemised quote follows an inspection."),
  ("Are old chairs from a loft worth reupholstering?",
   "Very often, yes. These two spent twenty-one years in a loft and the frames underneath were completely sound — dust is the easy part. A photograph is enough for an upholsterer to give a first opinion on whether a piece justifies restoration before you move anything."),
  ("How long does traditional reupholstery of a chair take?",
   "A full traditional rebuild of one of these nursing chairs took around <strong>twenty-four hours of bench time</strong>, with the pair completed a week apart. Traditional work — webbing, stuffing and stitching by hand — cannot honestly be rushed much below that."),
 ]),
 'the-family-sofa-from-heptonstall.html': ("Questions this job answers", [
  ("How much does it cost to re-cover a three-seater sofa?",
   "This 2019 three-seater cost <strong>£1,100 in labour plus £456 of fabric</strong> (twelve metres at £38 a metre) — £1,556 all in, against the £4,000 its owners were quoted for a like-for-like replacement. A sound frame and good foam are what make a re-cover this economical."),
  ("Is it cheaper to reupholster a sofa or buy a new one?",
   "When the frame and cushion interiors are sound, a professional re-cover typically lands at a third to a half of replacing the sofa with equivalent quality — and it keeps a perfectly good piece of furniture out of landfill."),
  ("How long does it take to re-cover a sofa?",
   "This one was quoted at three weeks and finished inside two: strip-down in an afternoon, the old cover panels kept as templates, and the body-cover fitting taking the best part of a week of drape, smooth and staple."),
 ]),
 'the-wing-back-that-wasnt-a-howard.html': ("Questions this restoration answers", [
  ("How much does it cost to reupholster a wing-back chair in leather?",
   "A full leather restoration of a quality wing-back runs <strong>£1,200–£1,800</strong> depending on the hides chosen. This one came in around £1,500, including two full hides at £420 each — the leather is usually the biggest single line on the bill. The <a href=\"/leather-hide-calculator\">leather hide calculator</a> shows how the footage adds up."),
  ("How do you tell a genuine Howard chair?",
   "Genuine Howard &amp; Sons chairs from the Berners Street workshop carry a brass tag on the underside, and the frame has structural fingerprints an upholsterer can verify once the bottoming cloth is opened. Be wary of attributions made by phone — an honest inspection protects you from paying a Howard price for a chair that isn't one."),
  ("How many leather hides does a wing-back chair need?",
   "This chair took <strong>two full hides</strong>, cut into eleven panels with the natural scarring placed where the deep buttoning would hide it. Leather is sold by the square foot and wastes more than cloth, which is why hide count — not metreage — is how the job is priced."),
 ]),
 'the-last-chair.html': ("Questions this chapter answers", [
  ("Is upholstery a dying trade?",
   "No — but it is a changing one. Individual careers taper rather than stop, while demand for honest repair and re-covering is growing as furniture prices rise and customers turn against throwaway pieces. New workshops are still opening; ours did in 2024."),
  ("How long does a properly upholstered chair last?",
   "Longer than the person who upholstered it. A traditionally rebuilt chair finished today, re-covered every few decades as fabrics wear, can reasonably be in use a century from now — the chair you finish at five o'clock on the day you retire is the chair somebody else will be sitting on in 2125."),
  ("How do you become an upholsterer?",
   "The traditional route is training under experienced hands — mine was the modern method with the traditional underneath it, followed by years across vehicle trim and furniture workshops. Today the AMUSF accredits courses and workshops across the UK, and this book exists to put the bench knowledge in one place."),
 ]),
}

BUY = ("Questions buyers ask", [
  ("Why is the workshop edition wire-bound?",
   "Because a manual you use at the bench has to lie dead flat and fold back on itself one-handed — your other hand is holding the work. Wire-O binding does both; a paperback does neither. It's printed A4 in full colour on heavy 115gsm coated stock for the same reason."),
  ("How long does delivery take?",
   "Each copy is printed to order in the UK, usually within a few working days, then posted — UK orders typically arrive around a week from ordering. International orders ship worldwide from the same UK printer."),
  ("What's the difference between this and the Amazon editions?",
   "The words and figures are identical. The Amazon hardback, paperback and Kindle editions are made for reading; this wiro A4 edition is made for working from, and it is only sold here."),
  ("Is the book suitable for beginners?",
   "Yes — it starts from first principles and runs to full projects, but it's written at the working standard: the same methods, materials and honesty about costs that apply in a professional workshop, from an AMUSF-accredited master upholsterer with thirty years at the bench."),
])

RELATED_ANCHOR = '<p class="eyebrow read" style="text-align:center">Keep reading</p>'

changed = 0
for fname, (title, qas) in STORIES.items():
    t = open(fname, encoding='utf-8').read()
    if qas[0][0] in t:
        continue
    t = t.replace(RELATED_ANCHOR, faq_html(title, qas) + '\n<hr class="seam">\n' + RELATED_ANCHOR, 1)
    t = t.replace('</head>', faq_ld(qas), 1)
    open(fname, 'w', encoding='utf-8').write(t); changed += 1
    print("patched", fname)

# buy-the-book: insert before footer
t = open('buy-the-book.html', encoding='utf-8').read()
if BUY[1][0][0] not in t:
    t = t.replace('<footer class="site-footer">', faq_html(*BUY) + '\n<footer class="site-footer">', 1)
    t = t.replace('</head>', faq_ld(BUY[1]), 1)
    open('buy-the-book.html', 'w', encoding='utf-8').write(t); changed += 1
    print("patched buy-the-book.html")

# chapter heading rephrases (exact byte matches, voice preserved)
HEADS = {
 'the-anatomy-of-an-upholstered-piece.html': [
   ('<h2>Pass One — The outsides</h2>', '<h2>What can you see from the outside? — Pass One</h2>'),
   ('<h2>Pass Two — The insides</h2>', '<h2>What&#8217;s hidden inside an upholstered chair? — Pass Two</h2>'),
   ('<h2>Pass Three — The sequence</h2>', '<h2>What order do the layers go on? — Pass Three</h2>'),
 ],
 'the-workshop.html': [
   ('<h2>The room itself</h2>', '<h2>How much space does an upholstery workshop need?</h2>'),
   ('<h2>Light: three layers, never one</h2>', '<h2>How do you light an upholstery workshop? Three layers, never one</h2>'),
   ('<h2>Bench heights and the long-term back</h2>', '<h2>What height should an upholstery bench be?</h2>'),
 ],
}
for fname, pairs in HEADS.items():
    t = open(fname, encoding='utf-8').read(); o = t
    for old, new in pairs:
        t = t.replace(old, new, 1)
    if t != o:
        open(fname, 'w', encoding='utf-8').write(t); changed += 1
        print("patched", fname)

print(f"done — {changed} files changed")
