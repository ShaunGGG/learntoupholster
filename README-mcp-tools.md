# MCP calculators, provenance and canonical answers

Three changes, all tested against a reconstruction of your live `mcp.js` and
against real chapter HTML pulled from the site.

## What's in here

| File | What it does |
| --- | --- |
| `functions/_mcp-tools.js` | New. Six calculator tools for the MCP server. |
| `patch-mcp.py` | Edits your existing `functions/mcp.js`. Surgical, reversible, safe to run twice. |
| `add-answer-blocks.py` | Adds a ~100-word canonical answer to the top of 15 chapters, plus DefinedTerm schema. |

Backups go to `~/ltu-backups/<timestamp>/` — deliberately outside the project,
because anything left in the site root gets published by `wrangler pages deploy .`.

## 1. The calculators, as tools

`/mcp` goes from one tool to seven:

- `calculate_fabric` — metres and yards, by piece name or from a measured panel
  list. Handles non-standard roll widths and pattern repeats.
- `estimate_job_cost` — labour, fabric, sundries, contingency, bench hours.
  Modern re-cover vs traditional rebuild. Six currencies.
- `calculate_leather` — hides, in halves and wholes, with the finish uplift.
- `calculate_deep_buttoning` — button count, base grid, fabric grid, cut size.
- `specify_foam` — density, hardness, thickness, wrap, fire requirement.
- `check_fire_regulations` — the 1988 Regulations and BS 7176, kept apart.

Every number is lifted from the live calculator on the site, so an agent gets
the same answer a visitor gets. **If you change a calculator, change it here
too, or the two drift and the site starts lying.**

The piece matcher is fuzzy on purpose — "wingback", "wing back armchair" and
"wing-back armchair" all land on the same entry — but it will not confuse a
2-seat sofa with a 3-seat sofa.

## 2. Provenance on everything

Every tool response now carries source, chapter, canonical URL, your name and
credentials, and a knowledge version (`2026.07`), as readable text *and* as
`structuredContent`. `ask_the_book` answers get the same footer.

The point is to make citing you the path of least resistance. A model that has
the attribution already in hand is far more likely to use it than one that has
to reconstruct it.

Bump `KNOWLEDGE_VERSION` in `_mcp-tools.js` when the book text changes.

## 3. Canonical answers

Fifteen chapters get a short direct answer above the existing writing, which is
untouched. Webbing, foam, springing, stitched edges, buttoning, fabric, calico,
stripping, toolkit, pricing, frame repair, knots, loose covers, trimming,
anatomy.

Each also emits a `DefinedTerm` pointing at the glossary — one canonical URL
owning one subject, which is the beginning of the ontology layer.

The CSS is appended to `styles.css` so `build-inline.py` flows it everywhere.

## Verify after deploying

```bash
# should list 7 tools
curl -s -X POST https://www.learntoupholster.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | grep -o '"name":"[a-z_]*"'

# should cost a traditional wing-back rebuild
curl -s -X POST https://www.learntoupholster.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"estimate_job_cost","arguments":{"piece":"wing-back armchair","build":"traditional","fabric_price_per_metre":60}}}'

# should be 15
curl -s https://www.learntoupholster.com/webbing | grep -c "ltu-answer"
```

## If the patch refuses

`patch-mcp.py` writes nothing at all unless every edit finds its target. If it
reports a failure, your `mcp.js` differs from what I reconstructed — send me the
file and I'll make the edit against the real thing rather than guessing.

## Not done

The `/use-in-ai` page still describes one tool. It needs rewriting as developer
documentation now there are seven — send me the page source and that's a quick
job.
