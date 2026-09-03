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


# --- title length helper (added by fix-titles.py) ---------------------
import html as _html, re as _re

def brand_title(title, limit=60):
    """Append the brand suffix only when the result still fits in a SERP.

    Measured on the RENDERED length: &amp; is one character on screen even
    though it is five in source. Titles that are already long keep their
    own words and lose the suffix, which is the less useful half.
    """
    plain = _re.sub(r'<[^>]+>', '', _html.unescape(str(title)))
    if len(plain) + 21 <= limit:
        return "%s | Learn to Upholster" % title
    return title
# ----------------------------------------------------------------------


try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

SITE = "https://www.learntoupholster.com"
SRC_DIR = "project-sources"
OUT_DIR = "projects"
IMG_DIR = "images/projects"
# --- workshop gallery -------------------------------------------------------
# Forty-three finished pieces. Rendered into the projects hub by render_hub()
# so a rebuild can never drop it again. Assets live in /assets/gallery/ as
# NN.jpg (full), NN-t.jpg (thumb) and NN-t-s.jpg (400w). Width/height are the
# real thumb dimensions - they stop the masonry reflowing as images load.
GALLERY_ITEMS = [
    (1, 760, 570, "Mid-century open-arm settee, re-covered in a soft green wool."),
    (2, 760, 598, "A pair of Queen Anne-style wing chairs in antiqued tan leather."),
    (3, 570, 760, "Victorian open armchair, deep-buttoned in blue ticking stripe with stud detail."),
    (4, 570, 760, "Victorian carved spoon-back chair in a black floral tapestry."),
    (5, 570, 760, "Bedroom tub chair in olive wool with contrast buttons."),
    (6, 597, 760, "Small Victorian chair in a peacock-feather print, buttoned back."),
    (7, 570, 760, "Art Deco bentwood lounge chair in a Persian kilim print."),
    (8, 570, 760, "Victorian scroll-arm library chair in a red diamond weave."),
    (9, 570, 760, "Wing chair in green check tweed with burgundy cord piping."),
    (10, 570, 760, "Vintage side chair re-covered in green check wool."),
    (11, 628, 760, "Round button footstool in a peacock-feather print."),
    (12, 570, 760, "Bentwood stool in a cream-and-green ticking stripe."),
    (13, 570, 760, "Queen Anne-style wing chair in a blue basket weave."),
    (14, 760, 528, "Long bench footstool in a green diamond weave."),
    (15, 760, 633, "Deep ottoman footstool in a warm plaid chenille."),
    (16, 570, 760, "Tall wing-back armchair in green windowpane tweed with braid."),
    (17, 570, 760, "Carolean-style high-back carver in sage chenille."),
    (18, 760, 507, "A pair of mid-century lounge chairs in a soft stripe."),
    (19, 608, 760, "Art Deco bentwood armchair in a blue geometric weave."),
    (20, 570, 760, "Wing-back fireside chair in duck-egg blue."),
    (21, 570, 760, "Mid-century open-arm chair in a charcoal wool."),
    (22, 570, 760, "Mid-century armchair in teal velvet."),
    (23, 760, 570, "Upholstered headboard in a bold botanical print."),
    (24, 570, 760, "Deep-buttoned tub chair in raspberry wool."),
    (25, 570, 760, "Slipper chair in a blue-and-green stripe."),
    (26, 570, 760, "Caned berg\u00e8re chair in a Welsh tapestry weave."),
    (27, 760, 570, "Victorian mahogany chaise longue in a peacock print."),
    (28, 570, 760, "Deep-buttoned wing chair in a blue tartan check."),
    (29, 570, 760, "Victorian spindle-back tub chair in sage velvet."),
    (30, 760, 570, "Love-seat armchair in emerald velvet."),
    (31, 570, 760, "Bench footstool in a flame-stitch weave."),
    (32, 570, 760, "French fauteuil in navy velvet with an embroidered back."),
    (33, 760, 570, "Two-seater scroll-arm sofa in raspberry."),
    (34, 570, 760, "Curved tub chair in ochre velvet."),
    (35, 570, 760, "Wing-back armchair in grey herringbone."),
    (36, 760, 569, "Two-seater sofa in a sage Greek-key chenille."),
    (37, 569, 760, "Wing-back armchair in an autumn tartan."),
    (38, 760, 569, "Edwardian chaise longue in mustard velvet."),
    (39, 570, 760, "Mid-century open-arm chair in a geometric weave."),
    (40, 760, 570, "Wing-back chair and footstool in a floral sprig print."),
    (41, 570, 760, "Caned-back armchair with a blue wool cushion."),
    (42, 760, 652, "Snuggler armchair in green chenille with a flame-stitch footstool."),
    (43, 570, 760, "Painted stick-back chair with a charcoal wool seat."),
]

GALLERY_CSS = """<style>
.ltu-gal{columns:4 210px;column-gap:1.1rem;margin:1.4rem 0 0}
.ltu-gal figure{break-inside:avoid;margin:0 0 1.1rem;cursor:zoom-in;background:#fff;
  border:1px solid var(--rule);border-radius:12px;overflow:hidden}
.ltu-gal figure:hover,.ltu-gal figure:focus-within{box-shadow:0 8px 22px rgba(42,38,34,.14)}
.ltu-gal img{width:100%;height:auto;display:block}
.ltu-gal figcaption{font-family:var(--body);font-size:.93rem;color:#6b6357;
  padding:.55rem .8rem .7rem;line-height:1.35}
.ltu-gal figure:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
#ltu-lb{position:fixed;inset:0;z-index:200;background:rgba(20,17,14,.93);
  display:flex;align-items:center;justify-content:center;flex-direction:column;padding:1.5rem}
#ltu-lb img{max-width:min(92vw,1100px);max-height:80vh;width:auto;border-radius:6px}
#ltu-lb .cap{color:var(--cream);font-family:var(--body);font-size:1rem;
  margin-top:.9rem;text-align:center;max-width:44rem;opacity:.92}
#ltu-lb button{position:absolute;background:none;border:0;color:var(--cream);
  font-family:var(--display);cursor:pointer;padding:.6rem 1rem;opacity:.75}
#ltu-lb button:hover,#ltu-lb button:focus-visible{opacity:1}
#ltu-lb .x{top:.6rem;right:.9rem;font-size:2rem;line-height:1}
#ltu-lb .p,#ltu-lb .n{top:50%;transform:translateY(-50%);font-size:2.6rem;line-height:1}
#ltu-lb .p{left:.3rem} #ltu-lb .n{right:.3rem}
@media(max-width:640px){.ltu-gal{columns:2 140px;column-gap:.7rem}
  .ltu-gal figcaption{font-size:.86rem;padding:.45rem .6rem .55rem}}
</style>"""

GALLERY_JS = """<script>
(function(){
  var sec=document.getElementById('gallery'); if(!sec) return;
  var figs=[].slice.call(sec.querySelectorAll('figure[data-full]'));
  if(!figs.length) return;
  var box=null, idx=0;
  function close(){ if(!box) return; box.remove(); box=null;
    document.removeEventListener('keydown',key); figs[idx].focus(); }
  function key(e){ if(e.key==='Escape') close();
    else if(e.key==='ArrowRight') show(idx+1);
    else if(e.key==='ArrowLeft') show(idx-1); }
  function show(n){
    idx=(n+figs.length)%figs.length;
    var f=figs[idx], src=f.getAttribute('data-full');
    var cp=f.querySelector('figcaption'); cp=cp?cp.textContent:'';
    if(!box){
      box=document.createElement('div'); box.id='ltu-lb';
      box.setAttribute('role','dialog'); box.setAttribute('aria-modal','true');
      box.innerHTML='<button class="x" aria-label="Close">&#215;</button>'+
        '<button class="p" aria-label="Previous">&#8249;</button>'+
        '<button class="n" aria-label="Next">&#8250;</button>'+
        '<img alt=""><p class="cap"></p>';
      box.addEventListener('click',function(e){
        if(e.target===box) close();
        else if(e.target.className==='x') close();
        else if(e.target.className==='p') show(idx-1);
        else if(e.target.className==='n') show(idx+1); });
      document.body.appendChild(box);
      document.addEventListener('keydown',key);
      box.querySelector('.x').focus();
    }
    box.querySelector('img').src=src;
    box.querySelector('img').alt=cp;
    box.querySelector('.cap').textContent=cp;
  }
  figs.forEach(function(f,i){
    f.setAttribute('tabindex','0');
    f.setAttribute('role','button');
    f.addEventListener('click',function(){ show(i); });
    f.addEventListener('keydown',function(e){
      if(e.key==='Enter'||e.key===' '){ e.preventDefault(); show(i); } });
  });
})();
</script>"""


def gallery_band():
    """The gallery section, dropped into the projects hub below the projects."""
    figs = []
    for num, w, h, cap in GALLERY_ITEMS:
        n = "%02d" % num
        c = html.escape(cap)
        figs.append(
            '<figure data-full="/assets/gallery/%s.jpg">'
            '<img loading="lazy" decoding="async" src="/assets/gallery/%s-t.jpg" '
            'alt="%s" width="%d" height="%d" '
            'srcset="/assets/gallery/%s-t-s.jpg 400w, /assets/gallery/%s-t.jpg %dw" '
            'sizes="(max-width:640px) 45vw, 210px">'
            '<figcaption>%s</figcaption></figure>' % (n, n, c, w, h, n, n, w, c))

    return ('<hr class="seam">\n'
            '<section id="gallery" style="scroll-margin-top:5rem">\n'
            '<p class="eyebrow">From our workshop</p>\n'
            '<h2 style="margin-top:.2rem">The gallery</h2>\n'
            '<p>The projects above are documented stage by stage. These are the '
            'finished pieces &#8212; forty-three of them, reupholstered by hand at '
            'Greenwood Upholstery in West Yorkshire. Victorian show-frames and Queen '
            'Anne wing chairs, mid-century settees, chaises, footstools and stools. '
            'Tap any photograph to see it larger.</p>\n'
            '<p>This page is our work &#8212; but there is a wall for yours too. '
            '<a href="/readers-bench">The Reader&#8217;s Bench</a> is where readers&#8217; '
            'first seats go up: send a photograph of your first drop-in and get '
            'featured.</p>\n'
            '<div class="ltu-gal">\n' + "\n".join(figs) + '\n</div>\n'
            '</section>\n' + GALLERY_CSS + '\n' + GALLERY_JS)


def gallery_schema():
    """ImageGallery structured data for the forty-three photographs."""
    return {
        "@context": "https://schema.org",
        "@type": "ImageGallery",
        "name": "Greenwood Upholstery \u2014 our work",
        "url": SITE + "/" + OUT_DIR + "/#gallery",
        "description": ("Finished upholstery from a working AMUSF workshop in "
                        "West Yorkshire: wing chairs, Victorian show-frames, "
                        "mid-century settees, chaises and footstools."),
        "image": [SITE + "/assets/gallery/%02d.jpg" % n
                  for n, _w, _h, _c in GALLERY_ITEMS],
    }
# --- end workshop gallery ---------------------------------------------------

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

def clip(text, limit=180):
    """Meta description: cut at a sentence end if there is one, else a word
    boundary. Never mid-word, which is what a bare [:180] slice gives you."""
    t = " ".join((text or "").split())
    if len(t) <= limit:
        return t
    window = t[:limit]
    cut = max(window.rfind(". "), window.rfind("? "), window.rfind("! "))
    if cut >= 90:                       # a sentence end worth stopping on
        return window[:cut + 1]
    cut = window.rfind(" ")
    return (window[:cut] if cut > 0 else window).rstrip(",;:—- ") + "…"

def og_dims(url_path):
    """Pixel size of a built image, for og:image:width/height. ('' if unknown)."""
    if not (HAVE_PIL and url_path):
        return None
    p = url_path.lstrip("/")
    if not os.path.exists(p):
        return None
    try:
        return Image.open(p).size
    except Exception:
        return None

def make_head(head, title, desc, canon, schema_blocks,
              og_title=None, og_image=None, og_type="website"):
    hd = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", head, flags=re.S)
    hd = re.sub(r'<meta name="description" content=".*?"',
                f'<meta name="description" content="{desc}"', hd, flags=re.S)
    hd = re.sub(r'<link rel="canonical" href=".*?"',
                f'<link rel="canonical" href="{canon}"', hd)

    # --- Open Graph: make each page share as itself, not as the homepage ---
    hd = re.sub(r'<meta property="og:title" content=".*?"',
                f'<meta property="og:title" content="{og_title or title}"', hd, flags=re.S)
    hd = re.sub(r'<meta property="og:description" content=".*?"',
                f'<meta property="og:description" content="{desc}"', hd, flags=re.S)
    hd = re.sub(r'<meta property="og:type" content=".*?"',
                f'<meta property="og:type" content="{og_type}"', hd)
    hd = re.sub(r'<meta property="og:url" content=".*?"',
                f'<meta property="og:url" content="{canon}"', hd)
    if og_image:
        hd = re.sub(r'<meta property="og:image" content=".*?"',
                    f'<meta property="og:image" content="{SITE}{og_image}"', hd)
        wh = og_dims(og_image)
        if wh:
            hd = re.sub(r'<meta property="og:image:width" content=".*?"',
                        f'<meta property="og:image:width" content="{wh[0]}"', hd)
            hd = re.sub(r'<meta property="og:image:height" content=".*?"',
                        f'<meta property="og:image:height" content="{wh[1]}"', hd)

    # --- Twitter card (absent sitewide; large image so the photo leads) ---
    if 'name="twitter:card"' not in hd:
        hd = hd.replace("</head>",
                        '<meta name="twitter:card" content="summary_large_image">\n</head>')

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
    # the `thumbnail:` pick is the strongest shot of the job — share that one
    social = meta.get("thumbnail", "")
    social_url = f"/{IMG_DIR}/{slug}/{photos.get(social, social)}" if social else ""

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

    # close the main content section, then the "From the workshop" monetisation block
    body.append("</section>")
    body.append('''<hr class="seam">
<section class="wrap read" id="from-the-workshop" style="margin-top:1.4rem">''')

    # 1. quote CTA — the highest-value action on the page
    body.append('''<div style="background:var(--green);color:var(--cream);border-radius:6px;padding:1.3rem 1.5rem;margin-bottom:1.4rem;text-align:center">
<h2 style="color:var(--cream);margin:.1rem 0 .5rem">Have a piece like this?</h2>
<p style="margin:0 0 1rem;max-width:40rem;margin-left:auto;margin-right:auto">Find a professional upholsterer near you &#8212; UK, US and worldwide &#8212; to bring your own chair, sofa or piece back to life.</p>
<a href="/find-an-upholsterer" style="display:inline-block;background:var(--gold);color:var(--ink);padding:.7rem 1.9rem;border-radius:3px;text-decoration:none;font-family:Fraunces,serif;font-weight:700;font-size:1.1rem">Find an upholsterer near you</a>
</div>''')

    # 2. affiliate tools/materials box (only if the project lists them)
    aff = pairs(meta.get("affiliates", ""))
    if aff:
        items = "".join(
            f'<li style="margin-bottom:.5rem"><a class="aff" href="/go/amazon?q='
            + __import__("urllib.parse", fromlist=["quote_plus"]).quote_plus(term)
            + f'" target="_blank" rel="sponsored noopener">{esc(label)}</a> '
            f'<span class="paid" style="font-size:.85rem;color:#8a8577">(paid link)</span></li>'
            for term, label in aff)
        body.append(
            '''<div style="background:#fff;border:1px solid var(--rule);border-left:4px solid var(--gold);border-radius:5px;padding:1.1rem 1.4rem;margin-bottom:1.4rem">
<h2 style="margin:.1rem 0 .5rem">Tools &amp; materials used on this job</h2>
<p style="margin:0 0 .7rem;font-size:1rem;color:#6b6459">The kit that did this job, in case you want the same for yours:</p>
<ul style="margin:0">''' + items + "</ul></div>")

    # 3. book + visualiser + more projects
    body.append('''<p style="text-align:center;margin:1.2rem 0">
<a href="/buy-the-book" style="display:inline-block;background:#B5552D;color:#FBF6ED;padding:.7rem 1.7rem;margin:.3rem;border-radius:3px;text-decoration:none;font-family:Fraunces,serif;font-weight:600">Learn to do this &#8212; the book</a>
<a href="/fabric-visualiser" style="display:inline-block;padding:.7rem 1.5rem;margin:.3rem;border:1.5px solid var(--green);border-radius:3px;color:var(--green);text-decoration:none;font-family:Fraunces,serif;font-weight:600">See your chair in a new fabric</a>
<a href="/projects" style="display:inline-block;padding:.7rem 1.5rem;margin:.3rem;border:1.5px solid var(--green);border-radius:3px;color:var(--green);text-decoration:none;font-family:Fraunces,serif;font-weight:600">More projects</a>
</p>
</section>''')

    canon = f"{SITE}/{OUT_DIR}/{slug}"
    desc = clip(meta.get("intro", subtitle or title))
    schema = [{
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "description": desc,
        "image": (SITE + (social_url or hero_url)) if (social_url or hero_url) else "",
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

    page_title = brand_title(f"{title} &#8212; Upholstery Project")
    hd = make_head(head, page_title, esc(desc), canon, schema,
                   og_title=esc(title), og_image=(social_url or hero_url),
                   og_type="article")
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

    body.append(gallery_band())
    body.append('''<hr class="seam">
<h2>Why we document every job</h2>
<p>Textbooks show the ideal. A working bench shows the truth: the split rail nobody mentioned, the previous upholsterer&#8217;s shortcut, the frame that turned out to be worth saving after all. These pages record real work as it happened &#8212; the hours, the materials, the problems and the finish &#8212; from an AMUSF-accredited workshop in Hebden Bridge.</p>
<p>The full method behind every job is in <a href="/buy-the-book"><em>The Working Upholsterer&#8217;s Bible</em></a>.</p>
</section>
<style>@media(max-width:640px){.proj-grid{grid-template-columns:1fr !important}}</style>''')

    schema = [gallery_schema(), {
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
                   brand_title("Upholstery Projects &#8212; Real Jobs, Documented"),
                   "Real upholstery jobs documented stage by stage from a working AMUSF workshop: furniture, campervans, motorbike seats, plant machinery and soft furnishings.",
                   f"{SITE}/{OUT_DIR}/", schema,
                   og_title="Upholstery Projects &#8212; Real Jobs, Documented")
    return (f"<!DOCTYPE html>\n<html lang=\"en\">\n{hd}\n<body>\n{nav}\n"
            + "\n".join(body) + f"\n{foot}\n{toggle}\n</body>\n</html>")

# ---------------------------------------------------------------- llms.txt
LLMS_HEAD = "## Projects — real jobs from the workshop"

def update_llms(projects):
    """Rebuild the Projects section of llms.txt. Without this the project pages
    are invisible to the AI crawlers that read llms.txt, which is most of them."""
    try:
        s = open("llms.txt", encoding="utf-8").read()
    except FileNotFoundError:
        print("  ! llms.txt not found — skipped"); return

    lines = [LLMS_HEAD, "",
             "Documented jobs from Greenwood Upholstery, an AMUSF-accredited workshop "
             "in Hebden Bridge — what came in, what was found, the method and the finish.",
             ""]
    for p in sorted(projects, key=lambda x: x["title"]):
        lines.append(f"- [{html.unescape(p['title'])}]({SITE}/{OUT_DIR}/{p['slug']}): "
                     f"{html.unescape(p['desc'])}")
    section = "\n".join(lines) + "\n\n"

    pat = re.compile(re.escape(LLMS_HEAD) + r".*?(?=\n## |\Z)", re.S)
    if pat.search(s):
        s = pat.sub(section.rstrip("\n") + "\n", s, count=1)
    elif "## Tools" in s:
        s = s.replace("## Tools", section + "## Tools", 1)
    else:
        s = s.rstrip("\n") + "\n\n" + section
    open("llms.txt", "w", encoding="utf-8").write(s)
    print(f"  llms.txt: Projects section listing {len(projects)} page(s)")

# ---------------------------------------------------------------- sitemap
def update_sitemap(slugs):
    try:
        s = open("sitemap.xml", encoding="utf-8").read()
    except FileNotFoundError:
        print("  ! sitemap.xml not found — skipped"); return
    urls = [f"{SITE}/{OUT_DIR}/"] + [f"{SITE}/{OUT_DIR}/{sl}" for sl in slugs]
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
                         "fabric": meta.get("fabric", ""), "thumb": thumb,
                         "desc": clip(meta.get("intro", meta.get("subtitle", "")))})
        print(f"  built /{OUT_DIR}/{slug}  ({len(stages)} stages, {len(photos)} photos, {len(faqs)} FAQs)")

    open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8").write(
        render_hub(projects, head, nav, foot, toggle))
    print(f"  built /{OUT_DIR} hub with {len(projects)} project(s)")
    update_sitemap([p["slug"] for p in projects])
    update_llms(projects)

if __name__ == "__main__":
    main()
