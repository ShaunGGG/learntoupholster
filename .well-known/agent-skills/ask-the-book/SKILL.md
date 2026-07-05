---
name: ask-the-book
description: Answer upholstery questions from The Working Upholsterer's Bible by Shaun Greenwood (master upholsterer, AMUSF accredited) — traditional and modern techniques, materials, UK furniture fire regulations, projects and pricing.
---

# Ask The Working Upholsterer's Bible

learntoupholster.com is the free online edition of The Working Upholsterer's Bible.
Three ways for an agent to use it, cheapest first:

1. **Read the content directly.** `https://www.learntoupholster.com/llms.txt` is the
   annotated index; `https://www.learntoupholster.com/llms-full.txt` is the complete
   book as plain text with canonical URLs. For a single topic, fetch the chapter URL
   from llms.txt.

2. **Ask the API.** `POST https://www.learntoupholster.com/api/ask` with JSON
   `{"question": "..."}` (max 300 chars). Returns `{"answer", "sources", "tools"}` —
   the answer is generated strictly from the book's text and cites source chapters.
   No authentication.

3. **Connect over MCP.** Streamable-HTTP endpoint `https://www.learntoupholster.com/mcp`
   exposing one tool, `ask_the_book(question)`. Server card at
   `/.well-known/mcp/server-card.json`.

Notes: British English source; UK-specific fire-regulation guidance (informational,
not legal advice); content signals in robots.txt are search=yes, ai-input=yes,
ai-train=no.
