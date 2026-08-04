# build-md-extra.py — finds orphan root pages automatically

## Why

`/suppliers` went live in the sitemap but absent from `llms.txt` and
`llms-full.txt`. Same cause as `/workshop-forms` before it, and the projects
pages before that: `build-md.py` only knows about the pages it was written for,
so anything new at the site root has no markdown variant and is therefore
invisible to the AI surfaces.

I fixed that last time by adding a `ROOT_PAGES = ['workshop-forms']` list. Which
worked, and then I forgot to update it. That is the fifth time this pattern has
bitten, so it is worth fixing properly rather than adding another name.

## What changed

`build-md-extra.py` now scans for the condition directly: **any root `.html`
page with no matching `md/<slug>.md` is a page missing from llms-full.txt.**

It reports what it found, so it is visible rather than silent:

```
root pages with no markdown variant: suppliers, workshop-forms
```

Excluded, because they are not content: `404`, `500`, `index`, `search`,
`press-pack`, and the legal boilerplate. Anything carrying a `noindex` robots
tag is skipped too — a page kept out of search should stay out of the AI corpus.

Tested against a mock with both cases present: it picked up `suppliers` and
`workshop-forms`, and correctly ignored `press-pack`, `privacy-policy` and the
two pages that already had variants.

## Result

Any page you add at the site root from now on lands in `llms.txt` and
`llms-full.txt` without anyone remembering to do anything.

## Deploy

```bash
python3 build-md-extra.py && python3 build-llms.py && \
python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```
