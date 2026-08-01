# Business Hub: discovery, MCP and monetisation

## The bug this fixes

The Business Hub went live invisible. Not in `sitemap.xml`, not in `llms.txt`, not
in `llms-full.txt`, no markdown variant, and `ask_the_book` answered "the book
doesn't cover whether you should charge for estimates".

Cause: `build-md.py` and `build-ask-index.py` scan the site root only. Anything in
a subdirectory is skipped.

**This is not only the Business Hub.** Your six `/projects/` pages have the same
problem and always have — no markdown variants, and absent from `llms-full.txt`
since the day you built them.

## Hub layout

The hub now uses the same markup as `/contents`: `toc-part` blocks with a gold
part label, an `h2`, and a `toc-list` of links carrying a "Read now" badge. Those
classes are already in the sitewide stylesheet, so this needed no new CSS and will
follow any restyling of the contents page automatically.

The tax and insurance caveat is now a `sidenote` in the same style as the "First
time here?" box on `/contents`, and the calculators are a `toc-part` labelled
Tools rather than a card grid.

Visualiser Pro sits directly above Pricing & Profit — first thing after the intro,
ahead of the article list.

Article pages are unchanged; only the hub was restyled.

## Files

| File | What it does |
| --- | --- |
| `build-md-extra.py` | **New.** Markdown variants for subdirectory pages. Fixes `business/` and `projects/`. |
| `update-sitemap.py` | **New.** Walks the site, adds any page missing from `sitemap.xml`. Only ever adds. |
| `build-llms.py` | **v2.** Now walks `md/` recursively instead of globbing `md/*.md`. |
| `build-business.py` | **v3.** Emits MCP data, product blocks, affiliate support, robots rule. |
| `functions/_mcp-tools.js` | **Updated.** Adds `find_business_guidance`. |
| `functions/_business-data.js` | Generated. Regenerated every build, so MCP and the site cannot disagree. |

## Build order

```bash
python3 build-business.py && python3 patch-nav-footer.py && \
python3 build-ask-index.py && python3 build-md.py && python3 build-md-extra.py && \
python3 build-llms.py && python3 update-sitemap.py && python3 build-inline.py
```

`build-md-extra.py` goes after `build-md.py`; `update-sitemap.py` before
`build-inline.py`. Tested end to end against a mock built from your live pages:
13 pages into `llms-full.txt` — root, business and projects.

## MCP

`find_business_guidance` is tool number eight. No `mcp.js` patch needed — it lives
in `_mcp-tools.js`, which `mcp.js` already concatenates.

It returns the canonical short answer for each match plus the URL, or the whole
index with `list_all`. Deterministic, no model call, no API cost. Asked a craft
question it declines and points at `ask_the_book`, so the two don't compete.

`ask_the_book` still won't cover the Hub, because `build-ask-index.py` is root-only
and I don't have that file. Send it and I'll patch it — or leave it, since the
dedicated tool gives better answers for business questions anyway.

## Monetisation — what's already working

Checked on the live pages: **Mediavine (`grow.me` and `mv-sidebar`), GA4 and
canonicals all inherit correctly.** Ads are already running on the Business Hub.
Nothing to do.

## Monetisation — what I added

A `products:` front-matter field for your own products, which are the honest
earner here:

```
products: pro, book        # or bodella
```

Wired into the five articles where it genuinely fits — Visualiser Pro on the two
about losing quotes and winning customers, the book on the pricing pieces, Bodella
on customer's own fabric.

An `affiliate:` field also exists for Amazon:

```
affiliate: Magnetic tack hammer|magnetic upholstery hammer, Webbing strainer|upholstery webbing strainer
```

It builds `/go/amazon` links with tag `842699-21`, marks them `rel="sponsored
nofollow"`, and **automatically adds a disclosure**. Required by the ASA in the UK
and the FTC in the US, and not optional.

## Monetisation — the honest bit

I have deliberately not put Amazon links in any Business Hub article, and I would
think hard before you do.

Affiliate revenue works where someone is about to buy a physical thing — tools,
materials, kit. That is your craft content, and it is already doing it. Business
advice is different: someone reading "I'm busy but I'm not making money" is not
about to buy a staple gun, so the links earn almost nothing while quietly
undermining the one thing this section has going for it.

Your outline's real monetisation, in rough order of value:

1. **Ads** — already live, scales with traffic, costs you nothing to maintain.
2. **Your own products** — book, Visualiser Pro, Bodella, and the AMUSF courses when they run. High value, perfectly aligned, no disclosure problem.
3. **The benchmark survey** — data nobody else has. Not directly monetisable, but it is what earns the links and citations that make everything above worth more.
4. **Amazon** — real money in tool and material content. Marginal in business content.

The `affiliate:` field is there for the articles where it does fit — a future piece
on workshop equipment, say. Use it there.

## Verify after deploying

```bash
curl -s https://www.learntoupholster.com/sitemap.xml | grep -c '/business/'          # 10
curl -s https://www.learntoupholster.com/llms.txt | grep -c '/business/'             # 10
curl -s https://www.learntoupholster.com/llms-full.txt | grep -c '/projects/'        # 6
curl -s -o /dev/null -w '%{http_code}\n' https://www.learntoupholster.com/md/business/saying-no-to-a-job.md   # 200
curl -s -X POST https://www.learntoupholster.com/mcp -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | grep -o '"name":"[a-z_]*"'   # 8 tools
```
