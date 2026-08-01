# SEO/GEO fixes for the new pages

Audit of the eight new pages (workshop forms, six Business Hub articles, survey).
Most of it was clean: descriptions all in range, one `<h1>` each, canonicals
correct, JSON-LD valid everywhere it existed. Three real problems.

## 1. `/workshop-forms` was invisible to AI

In the sitemap, but **not in llms.txt or llms-full.txt** and no markdown variant.
Cause: `build-md.py` is root-only and doesn't know about it, and
`build-md-extra.py` only walked subdirectories.

Fixed by adding a `ROOT_PAGES` list to `build-md-extra.py`. Any future root page
that `build-md.py` misses goes in that list.

## 2. The hub pages were published under URLs that redirect

`llms.txt` and `llms-full.txt` listed:

```
https://www.learntoupholster.com/business/index
https://www.learntoupholster.com/projects/index
https://www.learntoupholster.com/state-of-the-trade/index
```

Those 308-redirect to the real URLs, so not fatal — but an AI citing a redirect
is a weaker citation than one citing the page, and it contradicts the canonical
the page itself declares. My bug, from building URLs out of file paths.

`build-llms.py` now reads each page's own `<link rel="canonical">` and uses that,
falling back to a constructed URL only when there isn't one. Directory indexes
now publish as `/business/` and so on.

## 3. The Business Hub had no structured data at all

Every article had Article + FAQPage + BreadcrumbList. The hub itself had nothing.

Added a `CollectionPage` with an `ItemList` of all 15 articles in section order,
plus a `BreadcrumbList`. That tells a crawler the page is an index and what is in
it, which is what it actually is.

## Still outstanding

`/state-of-the-trade/take-part` has no structured data. Low priority — it is a
form, and the results page it points at already carries the `Dataset` markup that
matters. Worth adding a `WebApplication` block eventually.

## Deploy

```bash
python3 build-forms.py && python3 build-business.py && \
python3 build-md-extra.py && python3 build-llms.py && \
python3 update-sitemap.py && python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

## Verify

```bash
curl -s https://www.learntoupholster.com/llms.txt | grep -c workshop-forms        # 1
curl -s https://www.learntoupholster.com/llms.txt | grep -c '/index)'             # 0
curl -s https://www.learntoupholster.com/business/ | grep -c CollectionPage       # 1
```
