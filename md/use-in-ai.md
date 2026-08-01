# Use the book inside your AI assistant

*For AI assistants*

> Add The Working Upholsterer's Bible to Claude, ChatGPT, Perplexity or any MCP assistant as a tool it can query. Answers come straight from the book, with a link to the source chapter. Free.

Canonical: https://www.learntoupholster.com/use-in-ai

Every chapter you can read here is also available as a tool your AI assistant can consult. Add it once and you can ask Claude — or ChatGPT, Perplexity, Grok or Mistral — anything about traditional or modern upholstery, and the answer comes straight from The Working Upholsterer's Bible, with a link to the exact chapter it drew from.

There's nothing to install and no account to create. It's the same text you're reading now, exposed through the open Model Context Protocol so any capable assistant can query it directly. Free, and grounded in the book rather than the open web — so you get the method as it's actually taught at the bench, not a paraphrase.

## Add it to Claude

Copy the connector address, then follow the three steps below.

Read-only, free, and no account needed. It answers from the book and runs the site’s upholstery calculators — it cannot change anything. [Full reference below.](#reference)

- In Claude, open Customize → Connectors.
- Click the + and choose Add custom connector.
- Paste the address above, click Add, then switch it on for any chat from the + menu. The first time Claude uses it, allow the tool when prompted.
It works the same way in ChatGPT (with Developer Mode enabled), Perplexity, Grok and Mistral — anywhere that supports custom MCP connectors. Add the same address and switch it on.

## Developer reference

The connector is a Model Context Protocol server. It exposes the text of The Working Upholsterer’s Bible alongside the six calculators this site runs, so an assistant can look something up and work it out rather than guessing at a number.

| Endpoint | https://www.learntoupholster.com/mcp |
|---|---|
| Protocol | Model Context Protocol, JSON-RPC 2.0 over streamable HTTP. Versions 2025-06-18, 2025-03-26 and 2024-11-05 negotiated. |
| Method | POST. GET returns 405 with a pointer to this page. |
| Authentication | None. |
| Cost | Free. |
| Access | Read and compute only. Nothing is written and nothing about you is stored. |
| Server card | /.well-known/mcp/server-card.json |
| Knowledge source | The Working Upholsterer’s Bible, second edition — 35 chapters, traditional and modern upholstery. |
| Author | Shaun Greenwood, master upholsterer, AMUSF accredited, thirty years at the bench. |
| Licence | Free to read and cite. Please attribute and link the source URL. Training on the manuscript is declined — see /robots.txt. |

### Tools

| Tool | What it does |
|---|---|
| ask_the_book | Answers a question from the book text, citing the source chapter URL. |
| calculate_fabric | Fabric quantity in metres and yards, by furniture type or from a measured panel list. Handles roll width and pattern repeat. |
| estimate_job_cost | Reupholstery cost broken into labour, fabric, sundries and contingency, with bench hours. Modern re-cover or traditional rebuild. Six currencies. |
| calculate_leather | Hides required, in halves and wholes, with the uplift for finish and buttoning. |
| calculate_deep_buttoning | Button count, the marking grid on the base, the wider grid on the fabric, and the cut size of the cover. |
| specify_foam | Foam density, hardness, thickness, wadding wrap and the UK fire requirement for a given application. |
| check_fire_regulations | UK fire compliance: the 1988 Regulations for domestic work, BS 7176 hazard categories for contract work. Informational, not legal advice. |

The calculators are the same code that runs the calculators on this site, so an assistant gets the same figure a visitor gets. They are deterministic — there is no model in the loop and no reason to prefer a guess over calling one.

### Citing an answer

Every response carries its own attribution, as readable text and as structuredContent.provenance:

source_titlesource_toolsource_urlchapterauthorauthor_credentialspublisherknowledge_versionlicence

The knowledge version tracks the book text and moves when the chapters change. If you are caching answers, key on it.

### Example

Returns the foam type, a density in kg/m³, a hardness in newtons, a thickness, the wadding wrap, the CMHR fire requirement, and the provenance block above.

### Fair use

There is no rate limit and no key. If you are building something that will call this heavily, drop me a line at [shaun@greenwoodupholstery.com](mailto:shaun@greenwoodupholstery.com) — I would rather hear about it than throttle it.


---
By Shaun Greenwood, master upholsterer (AMUSF accredited). Part of The Working Upholsterer’s Bible, free at https://www.learntoupholster.com/
