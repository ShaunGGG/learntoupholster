# Project image optimisation

Run after `build-projects.py`, before `build-inline.py`. Idempotent.

```bash
python3 optimise-project-images.py
```

Needs Pillow: `sudo apt install python3-pil`

## What it does

**Adds `width` and `height` to every project photo**, read from the actual file
on disk. This is the fix that matters. Without dimensions the browser cannot
reserve space, so the text jumps as each photo loads — Google measures that as
Cumulative Layout Shift and it is one of the cheapest Core Web Vitals wins there
is. Your chapter pages already have dimensions; the project pages never did
(20 of 21 images missing on Parker Knoll).

**Generates a webp alongside each jpeg and wraps the img in a `<picture>`.**
Browsers take the webp, anything old falls back to the jpeg. The AMUSF crest
already used this pattern, so it is consistent with the rest of the site.

**Adds `loading="lazy"` and `decoding="async"`** where missing.

## Honest numbers

I told you earlier that webp would cut the image weight by about two thirds.
**That was wrong** and I should correct it: measured on the Jensen page it is
**22%** — 1.57 MB down to 1.22 MB.

Your JPEGs are already well compressed. One of them (`02c.jpg`) produces a webp
*larger* than the original, so the script checks and discards it rather than
shipping a worse file.

It is also worth saying that the 1.6 MB figure overstates the problem, because
lazy loading is already in place. A visitor loads the HTML plus the first image —
about 130 KB — and the rest arrive as they scroll. The page was never as heavy in
practice as the total suggests.

So: the dimensions fix is genuinely worth doing. The webp is a modest
improvement worth having because it is free once the script exists.

The photos are 1400px on the long edge, which is right for a high-DPI screen at
your column width. They are not oversized and should not be shrunk.

## Settings

At the top of the file:

- `QUALITY = 82` — visually indistinguishable from the jpeg. Below about 75 you
  start to see it on fabric texture, which is the worst possible thing to lose
  on an upholstery site.
- `MAX_WIDTH = 1600` — only resizes if something is larger than that.
- `SKIP` — filename fragments to leave alone (crest, logo, icon).

## Also worth knowing

The new project page was not in `llms-full.txt` because `build-md-extra.py` had
not run since you added it. Nothing wrong with the page — just the build order.
The full chain after adding a project:

```bash
python3 build-projects.py && python3 optimise-project-images.py && \
python3 build-md-extra.py && python3 build-llms.py && python3 update-sitemap.py && \
python3 build-inline.py && python3 build-inline-extra.py
```
