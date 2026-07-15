#!/usr/bin/env python3
"""
Learn to Upholster — Projects builder
=====================================
Turns a short text file + a folder of photos into a finished project page,
rebuilds the /projects hub, and updates the sitemap. Run from the repo root:

    python3 build-projects.py

Input  : project-sources/<slug>.txt          (see _TEMPLATE.txt)
Photos : project-sources/photos/<slug>/*.jpg (any size, straight off the phone)
Output : projects/<slug>.html                -> /projects/<slug>
         projects/index.html                 -> /projects
         images/projects/<slug>/*.jpg        (resized, EXIF stripped)

Needs Pillow for photo resizing:  pip3 install Pillow
(without it, photos are copied at full size and a warning is printed)
"""
import glob, html, json, os, re, shutil, sys

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

SITE = "https://www.learntoupholster.com"
SRC_DIR = "project-sources"
OUT_DIR = "projects"
IMG_DIR = "images/projects"
CATEGORY_ORDER = ["Furniture", "Vehicles & Campervans", "Plant & Machinery",
                  "Curtains & Soft Furnishings", "Other"]

# ---------------------------------------------------------------- parsing
def parse(path):
    raw = open(path, encoding="utf-8").read()
    meta, stages, faqs = {}, [], []

    head, _, rest = raw.partition("--- STAGES ---")
    body, _, faq_block = rest.partition("--- FAQ ---")

    for line in head.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        k, _, v = line.partition(":")
        meta[k.strip().lower()] = v.strip()

    # stages: "# Heading", then optional photo:/caption:, then prose
    cur = None
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("# "):
            cur = {"heading": s[2:].strip(), "photo": "", "caption": "", "prose": []}
            stages.append(cur)
        elif cur is None:
            continue
        elif s.lower().startswith("photo:"):
            cur["photo"] = s.split(":", 1)[1].strip()
        elif s.lower().startswith("caption:"):
            cur["caption"] = s.split(":", 1)[1].strip()
        elif s:
            cur["prose"].append(s)

    q = None
    for line in faq_block.splitlines():
        s = line.strip()
        if s.upper().startswith("Q:"):
            q = s[2:].strip()
        elif s.upper().startswith("A:") and q:
            faqs.append((q, s[2:].strip()))
            q = None
    return meta, stages, faqs

def pairs(field):
    """'slug | Label, slug2 | Label2'  ->  [(slug,label), ...]"""
    out = []
    for chunk in field.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        slug, _, label = chunk.partition("|")
        out.append((slug.strip(), (label.strip() or slug.strip())))
    return out

# ---------------------------------------------------------------- photos
def process_photos(slug):
    src = os.path.join(SRC_DIR, "photos", slug)
    dst = os.path.join(IMG_DIR, slug)
    if not os.path.isdir(src):
        return {}
    os.makedirs(dst, exist_ok=True)
    made = {}
    for p in sorted(glob.glob(os.path.join(src, "*"))):
        name = os.path.basename(p)
        if not name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue
        out_name = os.path.splitext(name)[0] + ".jpg"
        out_path = os.path.join(dst, out_name)
        if HAVE_PIL:
            im = Image.open(p)
            im = im.convert("RGB")                     # also drops EXIF/GPS
            im.thumbnail((1400, 1400), Image.LANCZOS)  # full view
            im.save(out_path, "JPEG", quality=82, optimize=True, progressive=True)
            th = im.copy(); th.thumbnail((640, 640), Image.LANCZOS)
            th.save(os.path.join(dst, "thumb-" + out_name), "JPEG", quality=80, optimize=True)
        else:
            shutil.copy(p, out_path)
            shutil.copy(p, os.path.join(dst, "thumb-" + out_name))
        made[name] = out_name
    return made

# ---------------------------------------------------------------- chrome
def chrome():
    """Take head/nav/footer/scripts from the live homepage file in the repo."""
    h = open("index.html", encoding="utf-8").read()
    head = re.search(r"<head>.*?</head>", h, re.S).group(0)
    nav = re.search(r'<nav class="site-nav".*?</nav>', h, re.S).group(0)
    foot = re.search(r'<footer class="site-footer".*?</footer>', h, re.S).group(0)
    toggle = [s for s in re.findall(r"<script[^>]*>.*?</script>", h, re.S) if "nav-toggle" in s]
    return head, nav, foot, (toggle[0] if toggle else "")

def make_head(head, title, desc, canon, schema_blocks):
    hd = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", head, flags=re.S)
    hd = re.sub(r'<meta name="description" content=".*?"',
                f'<meta name="description" content="{desc}"', hd, flags=re.S)
    hd = re.sub(r'<link rel="canonical" href=".*?"',
                f'<link rel="canonical" href="{canon}"', hd)
    hd = re.sub(r'<script type="application/ld\+json">.*?</script>', "", hd, flags=re.S)
    ld = "".join('<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False)
                 + "</script>\n" for b in schema_blocks)
    return hd.replace("</head>", ld + "</head>")

# ---------------------------------------------------------------- render
def render_project(slug, meta, stages, faqs, photos, head, nav, foot, toggle):
    esc = html.escape
    title = meta.get("title", slug)
    subtitle = meta.get("subtitle", "")
    cat = meta.get("category", "Other")
    piece = meta.get("piece", "")
    hero = next((s["photo"] for s in stages if s["photo"]), "")
    hero_url = f"/{IMG_DIR}/{slug}/{photos.get(hero, hero)}" if hero else ""

    facts = [("Piece", piece), ("Category", cat), ("Bench hours", meta.get("hours", "")),
             ("Fabric", meta.get("fabric", "")), ("Materials", meta.get("materials", "")),
             ("Typical price", ("£" + meta["price"]) if meta.get("price") else "")]
    facts = [(k, v) for k, v in facts if v]

    body = [f'''<header class="chapter-head"><div class="wrap">
<p class="chno">Projects &#183; {esc(cat)}</p>
<h1>{esc(title)}</h1>
{f'<p class="epigraph">{esc(subtitle)}</p>' if subtitle else ''}
</div></header>
<hr class="seam">
<section class="wrap read">''']

    if meta.get("intro"):
        body.append(f"<p><strong>{esc(meta['intro'])}</strong></p>")

    # fact box
    if facts:
        rows = "".join(
            f'<tr><td style="padding:.45rem .7rem;border-bottom:1px solid var(--rule);'
            f'font-weight:600;white-space:nowrap">{esc(k)}</td>'
            f'<td style="padding:.45rem .7rem;border-bottom:1px solid var(--rule)">{esc(v)}</td></tr>'
            for k, v in facts)
        body.append(
            '<div style="background:#fff;border:1px solid var(--rule);border-left:4px solid var(--gold);'
            'border-radius:5px;padding:.6rem .4rem;margin:1.2rem 0;max-width:38rem">'
            f'<table style="width:100%;border-collapse:collapse;font-size:1.02rem">{rows}</table></div>')

    # stages
    for st in stages:
        body.append(f"<h2>{esc(st['heading'])}</h2>")
        if st["photo"]:
            fn = photos.get(st["photo"], st["photo"])
            body.append(
                f'<figure style="margin:1rem 0">'
                f'<img src="/{IMG_DIR}/{slug}/{fn}" alt="{esc(st["caption"] or st["heading"])}" '
                f'loading="lazy" style="width:100%;border-radius:4px;'
                f'box-shadow:0 6px 20px rgba(42,38,34,.13)">'
                + (f'<figcaption style="font-size:.95rem;color:#6b6459;margin-top:.4rem;'
                   f'font-style:italic">{esc(st["caption"])}</figcaption>' if st["caption"] else "")
                + "</figure>")
        for para in " ".join(st["prose"]).split("  "):
            if para.strip():
                body.append(f"<p>{esc(para.strip())}</p>")

    # cross-links
    links = []
    for s, label in pairs(meta.get("chapters", "")):
        links.append(f'<li><a href="/{s}">{esc(label)}</a></li>')
    for s, label in pairs(meta.get("tools", "")):
        links.append(f'<li><a href="/{s}">{esc(label)}</a></li>')
    if links:
        body.append("<hr class=\"seam\"><h2>The methods behind this job</h2>"
                    "<p>Every technique used here is set out in full in the book:</p>"
                    f"<ul>{''.join(links)}</ul>")

    # FAQ
    if faqs:
        body.append("<hr class=\"seam\"><h2>Questions about this job</h2>")
        for q, a in faqs:
            body.append(f"<h3>{esc(q)}</h3>\n<p>{esc(a)}</p>")

    # CTA
    body.append('''<hr class="seam">
<p style="text-align:center;margin:1.4rem 0">
<a href="/buy-the-book" style="display:inline-block;background:#B5552D;color:#FBF6ED;padding:.7rem 1.7rem;
border-radius:3px;text-decoration:none;font-family:Fraunces,serif;font-weight:600">Learn to do this &#8212; the book</a>
&nbsp;
<a href="/projects" style="display:inline-block;padding:.7rem 1.5rem;border:1.5px solid var(--green);
border-radius:3px;color:var(--green);text-decoration:none;font-family:Fraunces,serif;font-weight:600">More projects</a>
</p></section>''')

    canon = f"{SITE}/{OUT_DIR}/{slug}"
    desc = meta.get("intro", subtitle or title)[:180]
    schema = [{
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "description": desc,
        "image": (SITE + hero_url) if hero_url else "",
        "author": {"@type": "Person", "name": "Shaun Greenwood",
                   "jobTitle": "Master Upholsterer, AMUSF accredited"},
        "publisher": {"@type": "Organization", "name": "Learn to Upholster"},
        "datePublished": meta.get("year", "2026"), "mainEntityOfPage": canon,
    }, {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Projects", "item": f"{SITE}/{OUT_DIR}"},
            {"@type": "ListItem", "position": 3, "name": title, "item": canon}]}]
    if faqs:
        schema.append({"@context": "https://schema.org", "@type": "FAQPage",
                       "mainEntity": [{"@type": "Question", "name": q,
                                       "acceptedAnswer": {"@type": "Answer", "text": a}}
                                      for q, a in faqs]})

    page_title = f"{title} &#8212; Upholstery Project | Learn to Upholster"
    hd = make_head(head, page_title, esc(desc), canon, schema)
    return (f"<!DOCTYPE html>\n<html lang=\"en\">\n{hd}\n<body>\n{nav}\n"
            + "\n".join(body) + f"\n{foot}\n{toggle}\n</body>\n</html>")

def render_hub(projects, head, nav, foot, toggle):
    esc = html.escape
    by_cat = {}
    for p in projects:
        by_cat.setdefault(p["category"], []).append(p)

    body = ['''<header class="chapter-head"><div class="wrap">
<p class="chno">From the Workshop</p>
<h1>Projects</h1>
<p class="epigraph">Real jobs off a working bench &#8212; documented stage by stage. Furniture, vehicles, plant, soft furnishings: what came in, what we found, what it took.</p>
</div></header>
<hr class="seam">
<section class="wrap read">''']

    for cat in CATEGORY_ORDER + [c for c in by_cat if c not in CATEGORY_ORDER]:
        items = by_cat.get(cat)
        if not items:
            continue
        body.append(f"<h2>{esc(cat)}</h2>")
        body.append('<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));'
                    'gap:1.4rem;margin:1rem 0 2rem" class="proj-grid">')
        for p in items:
            img = (f'<img src="{p["thumb"]}" alt="{esc(p["title"])}" loading="lazy" '
                   f'style="width:100%;aspect-ratio:4/3;object-fit:cover;display:block">'
                   ) if p["thumb"] else ""
            meta_line = " &#183; ".join(x for x in [p.get("hours") and f'{p["hours"]} h at the bench',
                                                    p.get("fabric")] if x)
            body.append(
                f'<a href="/{OUT_DIR}/{p["slug"]}" style="text-decoration:none;color:inherit;'
                f'border:1px solid var(--rule);border-radius:6px;overflow:hidden;background:#fff;'
                f'display:flex;flex-direction:column">{img}'
                f'<div style="padding:.9rem 1rem">'
                f'<h3 style="margin:0 0 .3rem;font-size:1.15rem">{esc(p["title"])}</h3>'
                f'<p style="margin:0 0 .5rem;font-size:.95rem;color:#6b6459">{esc(p.get("piece",""))}</p>'
                f'<p style="margin:0;font-size:.92rem;color:var(--sage)">{meta_line}</p>'
                f'</div></a>')
        body.append("</div>")

    body.append('''<hr class="seam">
<h2>Why we document every job</h2>
<p>Textbooks show the ideal. A working bench shows the truth: the split rail nobody mentioned, the previous upholsterer&#8217;s shortcut, the frame that turned out to be worth saving after all. These pages record real work as it happened &#8212; the hours, the materials, the problems and the finish &#8212; from an AMUSF-accredited workshop in Hebden Bridge.</p>
<p>The full method behind every job is in <a href="/buy-the-book"><em>The Working Upholsterer&#8217;s Bible</em></a>.</p>
</section>
<style>@media(max-width:640px){.proj-grid{grid-template-columns:1fr !important}}</style>''')

    schema = [{
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": "Upholstery Projects", "url": f"{SITE}/{OUT_DIR}",
        "description": "Real upholstery jobs documented stage by stage from a working AMUSF workshop.",
        "hasPart": [{"@type": "Article", "headline": p["title"],
                     "url": f'{SITE}/{OUT_DIR}/{p["slug"]}'} for p in projects]
    }, {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Projects", "item": f"{SITE}/{OUT_DIR}"}]}]
    hd = make_head(head,
                   "Upholstery Projects &#8212; Real Jobs, Documented | Learn to Upholster",
                   "Real upholstery jobs documented stage by stage from a working AMUSF workshop: furniture, campervans, motorbike seats, plant machinery and soft furnishings.",
                   f"{SITE}/{OUT_DIR}", schema)
    return (f"<!DOCTYPE html>\n<html lang=\"en\">\n{hd}\n<body>\n{nav}\n"
            + "\n".join(body) + f"\n{foot}\n{toggle}\n</body>\n</html>")

# ---------------------------------------------------------------- sitemap
def update_sitemap(slugs):
    try:
        s = open("sitemap.xml", encoding="utf-8").read()
    except FileNotFoundError:
        print("  ! sitemap.xml not found — skipped"); return
    urls = [f"{SITE}/{OUT_DIR}"] + [f"{SITE}/{OUT_DIR}/{sl}" for sl in slugs]
    added = 0
    for u in urls:
        if f"<loc>{u}</loc>" not in s:
            s = s.replace("</urlset>",
                f"  <url><loc>{u}</loc><changefreq>monthly</changefreq>"
                f"<priority>0.8</priority></url>\n</urlset>")
            added += 1
    if added:
        open("sitemap.xml", "w", encoding="utf-8").write(s)
    print(f"  sitemap: {added} new entries")

# ---------------------------------------------------------------- main
def main():
    if not HAVE_PIL:
        print("! Pillow not installed — photos copied at full size.")
        print("  Fix with:  pip3 install Pillow\n")
    if not os.path.isdir(SRC_DIR):
        print(f"No {SRC_DIR}/ folder found."); sys.exit(1)

    head, nav, foot, toggle = chrome()
    os.makedirs(OUT_DIR, exist_ok=True)

    projects = []
    for path in sorted(glob.glob(os.path.join(SRC_DIR, "*.txt"))):
        slug = os.path.splitext(os.path.basename(path))[0]
        if slug.startswith("_"):
            continue
        meta, stages, faqs = parse(path)
        photos = process_photos(slug)
        page = render_project(slug, meta, stages, faqs, photos, head, nav, foot, toggle)
        open(os.path.join(OUT_DIR, slug + ".html"), "w", encoding="utf-8").write(page)

        hero = next((s["photo"] for s in stages if s["photo"]), "")
        thumb_src = meta.get("thumbnail", hero)
        thumb = f"/{IMG_DIR}/{slug}/thumb-{photos.get(thumb_src, thumb_src)}" if thumb_src else ""
        projects.append({"slug": slug, "title": meta.get("title", slug),
                         "category": meta.get("category", "Other"),
                         "piece": meta.get("piece", ""), "hours": meta.get("hours", ""),
                         "fabric": meta.get("fabric", ""), "thumb": thumb})
        print(f"  built /{OUT_DIR}/{slug}  ({len(stages)} stages, {len(photos)} photos, {len(faqs)} FAQs)")

    open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8").write(
        render_hub(projects, head, nav, foot, toggle))
    print(f"  built /{OUT_DIR} hub with {len(projects)} project(s)")
    update_sitemap([p["slug"] for p in projects])

if __name__ == "__main__":
    main()
