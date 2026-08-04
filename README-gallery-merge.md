# Gallery merged into Projects

## Deploy

```bash
python3 build-projects.py && python3 merge-gallery.py && python3 patch-nav-gallery.py && \
python3 optimise-project-images.py && python3 build-md-extra.py && python3 build-llms.py && \
python3 update-sitemap.py && python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

`merge-gallery.py` runs **after** `build-projects.py`, since it post-processes
the hub the generator produces. Same pattern as `optimise-project-images.py`.

## What changed

The two pages were doing halves of the same job. `/projects/` documented six jobs
stage by stage; `/our-work` held forty-three photographs of finished pieces with
no write-up.

Split like that, the documented work looked thin and the gallery looked like
advertising. Together they read properly: here is how the work is done, and here
is a great deal more of it from the same bench.

Section order on `/projects/` is now:

1. Furniture — documented jobs
2. Vehicles & Campervans — documented jobs
3. **More from the bench** — the 43 gallery photographs
4. Why we document every job

The lightbox script and gallery CSS were carried across, so the photographs still
open large and look the same.

**"Gallery" stays in the menu** but now points at `/projects/#gallery`. It is the
word people look for, so removing it would cost you wayfinding for no gain.

## One decision left, and it matters

`our-work.html` is **untouched**, which means those forty-three figures — same
images, same alt text, same captions — now exist on two pages. That is
near-duplicate content and Google will pick one to show, possibly the wrong one.

Pick one of these:

**Redirect it.** Cleanest, and consolidates everything onto the stronger page.
Create a `_redirects` file in the project root containing:

```
/our-work  /projects/  301
```

Then delete `our-work.html`. Test after deploying — you have a root
`functions/_middleware.js` and I have not been able to verify from here that
`_redirects` fires underneath it. If `/our-work` still serves the old page,
fall back to the option below.

**Or point it.** Keep the file, strip the gallery block out of it by hand, and
leave a short page saying the work now lives on `/projects/`. Slower, but it
cannot break and it keeps the URL alive.

I would take the redirect. `/projects/` is the better page for an international
reference site — it teaches, where the gallery only shows — and one strong page
beats two thin ones.

## Worth knowing

`/our-work` currently reads as Greenwood's portfolio: "chairs, settees and stools
we've reupholstered at Greenwood Upholstery in West Yorkshire". On a free
international reference that framing is slightly off-key. Inside `/projects/` the
same photographs work harder, because there they are evidence that the person
teaching the craft does it for a living rather than a pitch for a Yorkshire
workshop.
