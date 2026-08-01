# Full site audit — 1 August 2026

85 pages crawled live.

## Clean

| Check | Result |
| --- | --- |
| Pages returning 200 | 85 / 85 |
| Broken internal links | 0 |
| Internal links hitting a redirect | 0 |
| Pages accidentally noindexed | 0 |
| Missing or mismatched canonical | 0 |
| Missing / duplicate `<h1>` | 0 |
| Missing meta description | 0 |
| Invalid JSON-LD | 0 |
| Missing `og:image` | 0 |
| Duplicate titles | 0 |
| Missing image alt text | 0 |

The one link flagged as broken (`/go/amazon`) is a crawler artefact — my checker
strips query strings, and that route needs them. It works.

## GEO layer

All five surfaces live: `robots.txt`, `llms.txt`, `llms-full.txt`, `sitemap.xml`,
`/.well-known/mcp/server-card.json`. MCP serving 8 tools. Markdown content
negotiation working on root, business and the new forms page.

`robots.txt` carries a Content-Signal line (`search=yes, ai-input=yes,
ai-train=no`), which is the right posture for a free reference that does not want
its book text used as training data.

Coverage: sitemap 85, llms 82. The four missing are the legal pages, excluded
deliberately — they teach a model nothing about upholstery.

## One fix in this bundle

`/press-pack` is `noindex` but was being published in `llms-full.txt`. A page kept
out of search should be kept out of the AI corpus too; feeding it to one and not
the other is an inconsistency an AI has no way to detect.

`build-llms.py` now reads each page's robots meta and skips noindexed pages,
reporting the count so it is visible rather than silent.

## Performance

Every page under 21 KB over the wire, all served brotli, all responding in under
0.1s. Viewport and `lang` correct. Nothing to do.

## Deploy

```bash
python3 build-llms.py && python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

## Verify

```bash
curl -s https://www.learntoupholster.com/llms-full.txt | grep -c press-pack   # 0
```

## The honest conclusion

The technical layer is as close to complete as it is worth taking it. Everything
that can be fixed by markup has been fixed.

Search still brought 7 visitors last month. That number will not move because of
anything in this audit — it moves when other sites link to this one. The survey
and the Business Hub are the two assets that can earn those links, and both need
promoting to people rather than optimising for machines.
