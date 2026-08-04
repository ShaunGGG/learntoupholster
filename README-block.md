# Stop serving internal files

```bash
python3 patch-middleware-block.py && npx wrangler pages deploy --branch=production
```

## What I got wrong

I told you to add `outreach` to `.assetsignore`. **That file does nothing on
Cloudflare Pages** — it is a Workers-with-assets feature. I assumed it applied
here because the `.py` files were 404ing, and concluded the ignore file was
working.

It was not. Those 404s come from the block list at the top of
`functions/_middleware.js`, which you already had, and which blocks `*.py`,
root-level `*.md`, `/project-sources/` and dotfiles.

Everything not on that list is public. Which meant these were all live:

| | |
|---|---|
| `/wrangler.toml` | D1 and KV namespace IDs |
| `/business-sources/*.txt` | every article source |
| `/supplier-schema.sql` | table definitions |
| `/outreach/supplier-outreach.md` | the outreach drafts |

None of it is a credential — an ID is useless without an API token — but it is
internal detail with no reason to be published, and it can be indexed.

## The fix

Extends the existing block list rather than adding a second mechanism, so there
is still one place to look when something unexpectedly 404s:

```
*.py *.toml *.sql *.bak, root-level *.md,
/project-sources/, /business-sources/, /outreach/, dotfiles
```

Tested against eighteen paths: everything internal blocked, everything public
still served — including `/.well-known/`, `/md/*.md`, `/ask-index.json`,
`/llms-full.txt` and the supplier icons.

## After deploying

```bash
for u in /wrangler.toml /supplier-schema.sql /business-sources/the-physical-toll.txt \
         /outreach/supplier-outreach; do
  printf "%s %s\n" "$(curl -s -o /dev/null -w '%{http_code}' https://www.learntoupholster.com$u)" "$u"
done
```

All four should be 404. Then check the site still works: `/`, `/suppliers`,
`/business/`, `/md/webbing.md`.

## The `.assetsignore` file

Harmless either way. Delete it if you like — it has no effect on Pages, and
leaving it there implies a protection that does not exist.
