#!/usr/bin/env python3
"""Structured-data gap fill (idempotent):
  A. buy-the-book: Product -> Book with all four format offers, + BreadcrumbList
  B. index: WebSite (+SearchAction) + Organization
  C. about: ProfilePage + Person (AMUSF, Greenwood Upholstery, sameAs) + BreadcrumbList
  D. the-workshop: FAQPage (2 Qs)   E. deep-buttoning-calculator: FAQPage (1 Q)
  F. projects/parker-knoll: HowTo   G. tools + contents: CollectionPage + BreadcrumbList
"""
import json, re
from lxml import html as lx

BASE = 'https://www.learntoupholster.com'
PERSON = {"@type": "Person", "name": "Shaun Greenwood",
          "jobTitle": "Master Upholsterer",
          "description": "AMUSF-accredited master upholsterer with 30+ years at the bench; owner of Greenwood Upholstery, Hebden Bridge.",
          "url": "https://www.greenwoodupholstery.com/"}

def ld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False) + '\n</script>\n'

def crumb(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u}
                                 for i, (n, u) in enumerate(items)]}

def add_head(fname, blocks, guard):
    c = open(fname).read()
    if guard in c:
        print(f'{fname}: already done'); return
    c = c.replace('</head>', ''.join(blocks) + '</head>', 1)
    open(fname, 'w').write(c)
    print(f'{fname}: {len(blocks)} block(s) added')

# ---- A. buy-the-book: Book with four offers --------------------------------
c = open('buy-the-book.html').read()
if '"@type": "Book"' not in c and '"@type":"Book"' not in c:
    amazon = 'https://www.amazon.co.uk/dp/B0H8M7NDV8'
    ship = {"@type": "OfferShippingDetails",
            "shippingRate": {"@type": "MonetaryAmount", "value": "0", "currency": "GBP"},
            "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "GB"}}
    def ed(name, fmt, price, url, extra=None):
        o = {"@type": "Offer", "url": url, "priceCurrency": "GBP", "price": price,
             "availability": "https://schema.org/InStock"}
        if extra: o.update(extra)
        return {"@type": "Book", "name": name, "bookFormat": "https://schema.org/" + fmt,
                "inLanguage": "en-GB", "offers": o}
    book = {"@context": "https://schema.org", "@type": "Book",
            "name": "The Working Upholsterer's Bible (Second Edition)",
            "author": PERSON,
            "publisher": {"@type": "Organization", "name": "Learn to Upholster", "url": BASE + '/'},
            "url": BASE + "/buy-the-book",
            "image": BASE + "/images/book-cover-green.jpg",
            "inLanguage": "en-GB",
            "genre": "Crafts & Hobbies",
            "description": "The complete craft of upholstery, traditional and modern: 35 chapters and 72 figures covering materials, every technique, seven full projects and the working workshop.",
            "workExample": [
                ed("Wiro-Bound A4 Workshop Edition", "Paperback", "44.99",
                   BASE + "/buy-the-book",
                   {"seller": {"@type": "Organization", "name": "Learn to Upholster"},
                    "shippingDetails": ship}),
                ed("Hardback Edition", "Hardcover", "39.99", amazon,
                   {"seller": {"@type": "Organization", "name": "Amazon"}}),
                ed("Paperback Edition", "Paperback", "24.99", amazon,
                   {"seller": {"@type": "Organization", "name": "Amazon"}}),
                ed("Kindle Edition", "EBook", "9.99", amazon,
                   {"seller": {"@type": "Organization", "name": "Amazon"}}),
            ]}
    # replace the old Product block wholesale
    m = re.search(r'<script type="application/ld\+json">\s*\{[^<]*?"@type":\s*"Product".*?</script>\s*', c, re.S)
    assert m, 'Product block not found'
    c = c.replace(m.group(0), ld(book))
    if '"BreadcrumbList"' not in c:
        c = c.replace('</head>', ld(crumb([("Learn to Upholster", BASE + '/'),
                                           ("Buy the Book", BASE + '/buy-the-book')])) + '</head>', 1)
    open('buy-the-book.html', 'w').write(c)
    print('buy-the-book: Book schema with 4 offers + breadcrumb')
else:
    print('buy-the-book: already done')

# ---- B. homepage: WebSite + Organization -----------------------------------
site = {"@context": "https://schema.org", "@type": "WebSite",
        "name": "Learn to Upholster", "url": BASE + '/',
        "description": "A free, in-depth upholstery reference from a master upholsterer with thirty years at the bench.",
        "publisher": {"@type": "Organization", "name": "Learn to Upholster", "url": BASE + '/',
                      "logo": {"@type": "ImageObject", "url": BASE + "/icon-512.png"},
                      "founder": PERSON},
        "potentialAction": {"@type": "SearchAction",
                            "target": {"@type": "EntryPoint",
                                       "urlTemplate": BASE + "/search?q={search_term_string}"},
                            "query-input": "required name=search_term_string"}}
add_head('index.html', [ld(site)], '"SearchAction"')

# ---- C. about: ProfilePage + Person ----------------------------------------
person = dict(PERSON)
person.update({
    "@context": "https://schema.org",
    "memberOf": {"@type": "Organization",
                 "name": "Association of Master Upholsterers and Soft Furnishers (AMUSF)"},
    "worksFor": {"@type": "LocalBusiness", "name": "Greenwood Upholstery",
                 "url": "https://www.greenwoodupholstery.com/",
                 "address": {"@type": "PostalAddress", "addressLocality": "Hebden Bridge",
                             "addressRegion": "West Yorkshire", "addressCountry": "GB"}},
    "knowsAbout": ["Upholstery", "Traditional upholstery", "Modern upholstery",
                   "Furniture restoration", "Soft furnishings"],
    "sameAs": ["https://www.greenwoodupholstery.com/",
               "https://www.facebook.com/greenwood.upholstery",
               "https://www.instagram.com/greenwood.upholstery/"]})
profile = {"@context": "https://schema.org", "@type": "ProfilePage",
           "url": BASE + "/about", "name": "About Learn to Upholster",
           "mainEntity": person}
add_head('about.html', [ld(profile),
                        ld(crumb([("Learn to Upholster", BASE + '/'), ("About", BASE + '/about')]))],
         '"ProfilePage"')

# ---- D. the-workshop FAQ ---------------------------------------------------
faq_ws = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": "How much space does an upholstery workshop need?",
     "acceptedAnswer": {"@type": "Answer", "text":
      "Look first for three things rather than a floor area: natural light, headroom, and a wide door. A single-chair hobby bench fits in a garage; a working shop needs room to walk all the way around a sofa with a spring-loaded strip of webbing in your hands."}},
    {"@type": "Question", "name": "What height should an upholstery bench be?",
     "acceptedAnswer": {"@type": "Answer", "text":
      "The height of your wrist crease when you stand naturally with your arms at your sides — for most adults 85–90 cm, typically close to 88 cm. The standard 32-inch (81 cm) British workshop bench is right for cabinet-making and too low for upholstery, where you stand over the work; a too-low bench means leaning forward all day, and that ends careers."}}]}
add_head('the-workshop.html', [ld(faq_ws)], '"FAQPage"')

# ---- E. deep-buttoning-calculator FAQ --------------------------------------
faq_db = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": "How much extra fabric does deep buttoning need?",
     "acceptedAnswer": {"@type": "Answer", "text":
      "The fabric must be cut much fuller than the finished panel because it pleats inward at every button. The extra is called the fullness or take-up, added to every diamond in both directions: as a starting point allow about half an inch per diamond for shallow buttoning, three-quarters of an inch for medium, and one and a quarter inches for deep — each way. It grows with the depth of the buttoning, the thickness of the stuffing and the stretch of the cloth."}}]}
add_head('deep-buttoning-calculator.html', [ld(faq_db)], '"FAQPage"')

# ---- F. Parker Knoll HowTo -------------------------------------------------
f = 'projects/parker-knoll-wing-chair.html'
c = open(f).read()
if '"HowTo"' not in c:
    t = lx.fromstring(c)
    stages = ["Stripping the old cover", "The first new wing", "The second wing",
              "The inside arms", "The inside back", "Piping the wings",
              "The outside arms and back", "The cushion ready to sew", "The finishing touch"]
    steps = []
    for name in stages:
        txt = ''
        for h in t.xpath('//h2'):
            if ' '.join(''.join(h.itertext()).split()) == name:
                el = h.getnext()
                while el is not None and not txt:
                    words = ' '.join(' '.join(el.itertext()).split())
                    if el.tag in ('p', 'figure') and len(words) > 40:
                        txt = words[:280].rsplit(' ', 1)[0]
                    el = el.getnext()
                break
        steps.append({"@type": "HowToStep", "name": name,
                      "text": txt or name})
    howto = {"@context": "https://schema.org", "@type": "HowTo",
             "name": "How a Parker Knoll wing chair is reupholstered",
             "description": "The full re-cover of a Parker Knoll wing chair (model PK 720/745/1013) in teal velvet, documented stage by stage from a working AMUSF workshop: 5.5 hours at the bench.",
             "totalTime": "PT5H30M",
             "step": steps}
    c = c.replace('</head>', ld(howto) + '</head>', 1)
    open(f, 'w').write(c)
    print(f'{f}: HowTo with {len(steps)} steps')
else:
    print(f'{f}: already done')

# ---- G. tools + contents CollectionPage ------------------------------------
tools_cp = {"@context": "https://schema.org", "@type": "CollectionPage",
            "name": "Free Upholstery Tools & Calculators", "url": BASE + "/tools",
            "description": "Nine free upholstery tools: fabric yardage, reupholstery cost, deep buttoning, foam and cushion spec, leather hides, box cushions, piping, an AI fabric visualiser and a UK fire regulations checker.",
            "isPartOf": {"@type": "WebSite", "name": "Learn to Upholster", "url": BASE + '/'}}
add_head('tools.html', [ld(tools_cp),
                        ld(crumb([("Learn to Upholster", BASE + '/'), ("Tools", BASE + '/tools')]))],
         '"CollectionPage"')

contents_cp = {"@context": "https://schema.org", "@type": "CollectionPage",
               "name": "Contents — The Working Upholsterer's Bible",
               "url": BASE + "/contents",
               "description": "Every chapter of the free online upholstery reference: foundations, techniques, seven complete projects, the working workshop, reference charts and workshop stories.",
               "isPartOf": {"@type": "WebSite", "name": "Learn to Upholster", "url": BASE + '/'},
               "author": PERSON}
add_head('contents.html', [ld(contents_cp),
                           ld(crumb([("Learn to Upholster", BASE + '/'), ("Contents", BASE + '/contents')]))],
         '"CollectionPage"')
