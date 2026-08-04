# Retiring /our-work

## Deploy, in this order

```bash
python3 build-projects.py && \
python3 merge-gallery.py && \
python3 remove-our-work.py && \
python3 patch-nav-gallery.py && \
python3 optimise-project-images.py && \
python3 build-md-extra.py && python3 build-llms.py && python3 update-sitemap.py && \
python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

Order matters. `merge-gallery.py` must run before `remove-our-work.py`, and the
removal script checks \u2014 it refuses to delete anything until the gallery is
actually on `/projects/`, so the forty-three photographs cannot vanish by
mistake.

## What it does

**Adds a 301 redirect** to `functions/_middleware.js`:

```
/our-work  ->  /projects/#gallery
```

Straight to the photographs rather than the top of the page.

The redirect goes in the middleware rather than a `_redirects` file because the
middleware demonstrably runs on this site, and I could not verify from outside
whether `_redirects` fires underneath a root middleware. Guessing about a
redirect is how you discover weeks later that it never worked.

**Deletes** `our-work.html` and `md/our-work.md`, so the photographs are not
sitting on two URLs as near-duplicate content.

**Backs both up** to `~/ltu-backups/` first.

## Why redirect rather than just delete

`/our-work` has been live, linked from the main menu on every page, and indexed.
Deleting it outright turns every inbound link, bookmark and search result into a
404 and throws away whatever authority the URL has accumulated. A 301 passes that
onto `/projects/`, which is now the stronger page.

## Verify after deploying

```bash
curl -s -o /dev/null -w "%{http_code} -> %{redirect_url}\n" \
  https://www.learntoupholster.com/our-work
```

Expect `301 -> https://www.learntoupholster.com/projects/#gallery`.

Then check the photographs actually arrived:

```bash
curl -s https://www.learntoupholster.com/projects/ | grep -c "<figure"
```

Expect 43.

If the redirect returns 200 instead of 301, the middleware edit did not take \u2014
tell me and I will look at it rather than leaving it half done.
