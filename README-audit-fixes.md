# Audit fixes before the sewing section

```bash
python3 patch-nav-dropdowns.py && python3 update-sitemap.py && python3 prune-sitemap.py && \
python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

## The audit

97 pages crawled. Everything is healthy:

| | |
|---|---|
| Pages returning 200 | 97 / 97 |
| Genuinely broken links | 0 |
| Internal links hitting a redirect | 0 |
| Missing or mismatched canonicals | 0 |
| Missing / duplicate `<h1>` | 0 |
| Missing descriptions | 0 |
| Invalid JSON-LD | 0 |
| Missing `og:image` | 0 |
| MCP tools responding | 8 / 8 |
| GEO surfaces live | 6 / 6 |

**The gallery merge worked**: 43 figures on `/projects/`, the Facebook callout
gone, `/our-work` returning a clean 301 to `/projects/#gallery`.

**MCP is unaffected.** All eight tools tested with real calls \u2014 `ask_the_book`
answering from the Business Hub, the fire checker, the fabric calculator. Every
new page is in `sitemap.xml` and `llms.txt`.

The one link the crawler flagged, `/go/amazon`, is an artefact of my checker
stripping query strings. It works.

## Two things to fix

**1. The sitemap listed two dead URLs.** `/our-work` (now a 301) and
`/outreach/supplier-outreach` (now blocked). `update-sitemap.py` adds pages it
finds but never removes ones that have gone, so the file accumulates stale
entries.

`prune-sitemap.py` checks every entry against the files on disk and removes the
ones with nothing behind them. It adds nothing \u2014 that is still
`update-sitemap.py`'s job \u2014 so run it straight after. Function-served routes
like `/mcp` are kept deliberately.

Worth adding to the standard build chain permanently.

**2. The deployed dropdowns are the first version.** They still carry "All
countries" and "Full contents" \u2014 the parent links repeated inside their own
dropdown, which you spotted.

The patch was idempotent, so re-running it saw a dropdown and stopped. It now
tidies an existing one instead: tested against your live markup, it removes the
two redundant entries and leaves everything else alone.

After this the three dropdowns read:

- **Contents** \u2014 Start Here, A\u2013Z glossary
- **Fire Regulations** \u2014 United Kingdom, United States, Canada, Australia & New Zealand, Ireland
- **Tools** \u2014 Supplier directory, calculators, workshop forms, visualiser

None repeats its own parent.

## Then you are clear for the sewing section
