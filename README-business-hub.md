# Business Hub — v2

Nine articles, all ten calculators, Visualiser Pro, and the template bug fixed.

## The heading bug

Generated pages were inheriting `<header class="chapter-head">` from the template
page, so every Business Hub article carried an `<h1>` reading **Webbing**, the
kicker "Part Two · Chapter Nine", and Bryan Mitchell's epigraph. The tail was
doing the same thing further down — every page ended with "Keep reading →
Springing, Traditional".

Both are fixed. The generator now excludes the chapter header from the inherited
chrome and builds its own (`Business Hub · <section>` + the article title), and it
rewrites the prev/next block to point back at the Hub and the Contents.

`og:image` was also still pointing at `webbing-birdseye.jpg`; it now uses the site
card, and `og:`/`twitter:` metadata is set per article.

## What's in it

**Nine articles** across five sections:

- *Pricing & Profit* — How much should an upholsterer charge?
- *Quoting Jobs* — Should I charge for estimates? · The chair is worse underneath than I expected
- *Getting Customers* — Getting your first customers
- *Dealing With Customers* — Explaining why upholstery costs what it does · Customer's own fabric
- *Problems Nobody Talks About* — I'm busy but I'm not making money · How do I say no? · Uncollected furniture

**All ten calculators** in a "Tools for the trade" grid on the hub, each with the
reason a working upholsterer opens it. Articles also carry a "Tools for this" box
driven by a `tools:` line in the front matter, so the calculators are reachable
from the article that creates the need for them.

**Visualiser Pro** appears in two places: a block on the hub, and inside the three
articles where it genuinely belongs — explaining cost, getting first customers, and
customer's own fabric. Placed where a customer is hesitating over a fabric choice,
which is the actual use case, rather than bolted onto every page.

## Adding an article

```
title: I'm busy but I'm not making money
question: Why am I fully booked and still broke?
answer: 60-110 words. Becomes the answer block and the hub summary.
section: Problems Nobody Talks About
order: 10
updated: 2026-07-31
related: /pricing-and-quoting
tools: /reupholstery-cost-calculator, /fabric-yardage

## First heading

Body text.
```

Drop it in `business-sources/` and re-run. Sections group automatically; add new
ones to `SECTION_ORDER` at the top of the script. Body markup: `##`/`###`,
paragraphs, `-` bullets, `1.` lists, `>` asides, `**bold**`, `*italic*`,
`[links](/url)`, `` `code` ``. Raw HTML passes through.

## Build order

```bash
python3 build-business.py && python3 patch-nav-footer.py && \
python3 build-ask-index.py && python3 build-md.py && \
python3 build-llms.py && python3 build-inline.py
```

`build-business.py` first so the pages exist before the nav patch runs; both before
`build-md.py` so every article lands in the markdown variants, `llms-full.txt` and
`ask_the_book` automatically.

## Verify after deploying

```bash
# should be 0 — no template bleed
curl -s https://www.learntoupholster.com/business/saying-no-to-a-job | grep -c "Chapter Nine\|springing-traditional"

# should be the article title, not "Webbing"
curl -s https://www.learntoupholster.com/business/saying-no-to-a-job | grep -o "<h1>[^<]*</h1>"

# should be 10
curl -s https://www.learntoupholster.com/business/ | grep -c 'biz-toolgrid\|<a href="/[a-z-]*"><strong>'
```
