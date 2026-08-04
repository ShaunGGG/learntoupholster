# Sewing section audit

```bash
python3 patch-ask-numbers.py && python3 build-ask-index.py && \
python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

## What was already right

All seven pages live and returning 200. Every one in the sitemap, in `llms.txt`
and with a markdown variant. Descriptions 106\u2013144 characters, single `<h1>`,
canonicals correct, valid JSON-LD on every page \u2014 CollectionPage on the hub,
Article plus FAQPage plus BreadcrumbList on the guides, WebApplication on the
selector. `og:image` everywhere. All seven cross-linked.

## Three real problems, all mine

**1. The sewing pages were not in `ask_the_book` at all.** 621 chunks in the
index, zero from `/sewing`. Cause: `build-ask-index.py` is not in any of the
deploy commands I have been giving you. It should be. The corrected chain is at
the foot of this file.

**2. Tables were invisible to the index.** The indexer reads paragraphs, list
items and headings \u2014 not table cells. So the thread size chart, the needle
pairing table, the which-thread-for-what table and the US fire regulations
occupancy table, which are the actual reference data on those pages, could not
be retrieved at all.

`build-ask-index.py` now flattens each table row into a readable line using the
`data-l` labels already there for the mobile card layout: *"Tex: T90; Commercial:
#92; Ticket: Tkt 36; Usual needle: 110/18 or 125/20."*

**3. The retrieval discarded every number on the site.** The tokeniser was
`/[a-z][a-z'-]{1,}/g` \u2014 a token had to start with a letter and contain only
letters. So "Tex 90" searched as "tex". "BS 7176" searched as "bs". "110/18"
vanished entirely.

Survivable when the content was prose. Not now: the sewing section is built on
thread sizes, needle sizes and ticket numbers, and the fire pages turn on crib 5
and BS 7176.

`patch-ask-numbers.py` fixes both halves of it:

- numbers and mixed tokens are kept, and mixed tokens also emit their parts, so `T70` answers to `70` and `110/18` answers to `110` or `18`
- a bare number matches an optional letter prefix, because `\bBB90` would never match `T90` \u2014 both sides are word characters

Tested: *"What size needle for Tex 90?"* now yields `[size, needle, tex, 90]` and
the `90` matches `T90` in the table. *"commercial 92"* matches `#92`.
*"needle 110"* matches `110/18`.

This improves retrieval across the whole site, not just sewing.

## The corrected deploy chain

I have been leaving `build-ask-index.py` out. It belongs after the page
generators and before the inline step:

```bash
python3 build-sewing.py && python3 build-sewing-selector.py && \
python3 patch-nav-sewing.py && python3 build-ask-index.py && \
python3 build-md-extra.py && python3 build-llms.py && \
python3 update-sitemap.py && python3 prune-sitemap.py && \
python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

## Check after deploying

```bash
curl -s https://www.learntoupholster.com/ask-index.json | grep -c '"/sewing'
```

Then ask it something numeric:

```bash
curl -s -X POST https://www.learntoupholster.com/mcp -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"ask_the_book","arguments":{"question":"What size needle for Tex 90 thread?"}}}'
```

Before this it answered "the book does not cover it".
