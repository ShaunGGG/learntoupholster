# Internal graph — chapter and cluster links

Google is crawling the chrome and ignoring most of the book. Technique
chapters dead-end on Amazon and `/find-an-upholsterer`. New blog posts
have almost no in-article inbound from pages Google already has.

This patch does not add nav. It puts 3–4 contextual links *inside*
`<article>` on the weak chapters, rewrites blog RELATED clusters so
leather and money posts point at each other, and drops the 404
`/outreach/supplier-outreach` out of `sitemap.xml`.

Idempotent. Marker `<!-- internal-graph -->`. `--dry-run` prints the plan.

Unzip so `patch-internal-graph.py` lands in `~/learntoupholster`, then run
the terminal block in the chat.
