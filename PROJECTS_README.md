# Projects — how to add a job

One-time setup (once only):

    pip3 install Pillow

## For every new job

**1. Photos.** Straight off the phone, no editing needed. Put them in:

    project-sources/photos/<slug>/

Name them in order: `01-before.jpg`, `02-strip.jpg`, `03-frame.jpg`, etc.
The script resizes them, strips EXIF/GPS, and makes thumbnails automatically.

**2. Text.** Copy `project-sources/_TEMPLATE.txt` to `project-sources/<slug>.txt`
and fill it in. The slug becomes the URL:

    jcb-digger-seat.txt  ->  learntoupholster.com/projects/jcb-digger-seat

**3. Build and deploy.**

    python3 build-projects.py
    python3 patch-projects-nav.py
    npx wrangler pages deploy . --project-name=learntoupholster --branch=production
    git add -A && git commit -m "Project: JCB digger seat" && git push

That's it. The page, the hub, the schema and the sitemap all update themselves.

## What gets built

- `/projects/<slug>` — the project page (Article + BreadcrumbList + FAQPage schema)
- `/projects` — the hub, cards grouped by category, rebuilt every run
- `images/projects/<slug>/` — web-sized photos + thumbnails

## At the bench — what to capture

- **Same angle before and after.** Mark the spot. That pairing is the shareable shot.
- Every layer coming off, in order.
- **The problems**: rot, woodworm, previous bodges. The honest bits are what make it credible.
- Wide shot + close shot at each stage.
- **Write the numbers down**: bench hours, metres of fabric, materials, what you'd quote.
  These become the fact box and the FAQ — and they're the data nobody else publishes.

## Categories

Use one of these in the `category:` field so the hub groups properly:

    Furniture
    Vehicles & Campervans
    Plant & Machinery
    Curtains & Soft Furnishings
    Other

## Cross-links

`chapters:` and `tools:` link the job back to the book and calculators. Format:

    chapters: the-wing-back-chair | The Wing-Back Chair, webbing | Webbing
    tools: fabric-yardage | Work out your own fabric

This is what makes Google see the site as one connected body of expertise
rather than a pile of separate pages — worth the twenty seconds.
