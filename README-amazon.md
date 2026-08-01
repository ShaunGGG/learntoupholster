# Amazon affiliate redirect — fixed

## What was wrong

All 333 affiliate links on the site were unattributed. Each link passes
`u=https://www.amazon.co.uk/s?k=...&tag=842699-21`, but `/go/amazon` discarded
that parameter, rebuilt the URL from `q`, and sent every visitor to:

```
https://www.amazon.com/s?k=...
```

No tag, and the wrong store. Amazon cannot attribute a sale without a tag, so
every click since launch has been a free referral.

## What it does now

Routes the visitor to their own Amazon store using `cf-ipcountry`, and applies
the correct tag for that store.

| Visitor | Destination | Tagged |
| --- | --- | --- |
| UK | amazon.co.uk | yes |
| Ireland | amazon.co.uk | yes — same store, same tag |
| US | amazon.com | not yet |
| Germany / Austria | amazon.de | not yet |
| Canada, Australia, FR, IT, ES, NL, SE, PL, JP, IN | their own store | not yet |
| Anywhere unmapped | amazon.co.uk | yes |

Tags are keyed to the **store**, not the country. That matters: an Irish visitor
shops on amazon.co.uk where your UK tag is valid, and keying by country left them
untagged for no reason.

Also preserved from the old version: it will only ever redirect to an Amazon
domain. A `u` pointing anywhere else — including `amazon.co.uk.evil.com` — is
discarded and the link falls back to a search. That is what stopped it being an
open redirect, and it is worth keeping.

Product links work too. If a `u` contains `/dp/ASIN`, that path is carried across
to the visitor's store with the right tag rather than being flattened to a search.

## To earn on non-UK traffic

`842699-21` is a UK tag and is not valid on amazon.com. Amazon Associates is a
separate account per region — all free, and each gives you a tag for that store.

Given four of your first five survey responses were American, **Associates US is
the one worth doing.** Sign up, then put the tag in `STORE_TAGS` at the top of
the file:

```js
'www.amazon.com': 'yourtag-20',
```

Redeploy and US clicks start earning. Same pattern for CA, DE and AU if the
traffic justifies it.

Until a store has a tag, visitors still go to their own store untagged — which is
exactly what happens today. No revenue, but no worse an experience, and no reason
to send a US buyer to a UK shop to protect a tag they cannot use.

## Deploy

```bash
npx wrangler pages deploy --branch=production
```

## Verify

```bash
curl -s -o /dev/null -D - -H "CF-IPCountry: GB" \
  "https://www.learntoupholster.com/go/amazon?q=jute+webbing" | grep -i location
# expect: amazon.co.uk/s?k=jute+webbing&tag=842699-21
```

Then check a real link from `/the-toolkit` in a browser and confirm `tag=` is on
the URL you land on. Your Associates dashboard should start showing clicks that
are not yours within a day.

## One caveat

The redirect sends `Cache-Control: no-store`. Affiliate destinations vary by
visitor country, so allowing an edge cache to pin one country's redirect for
everyone would send UK buyers to amazon.com and lose the tag again.
