# Upholstery supplier directory

New page at `/suppliers`. **30 suppliers across 5 countries**, every one found by
search and then verified by fetching the site on 1 August 2026.

| | |
|---|---|
| United Kingdom | 9 |
| United States | 10 |
| Australia | 6 |
| New Zealand | 3 |
| Canada | 2 |

Filterable by country and by what they supply — traditional materials, foam,
fabric, tools, sundries, automotive. Filters tested across every combination.

## Setup — once

```bash
npx wrangler d1 execute ltu-survey --remote --file=supplier-schema.sql
```

Reuses the existing `ltu-survey` database, so no new binding is needed. The
submit endpoint accepts `SURVEY_DB`, `ltu_survey` or `DB`.

## Build order

```bash
python3 build-suppliers.py && python3 build-business.py && \
python3 build-md-extra.py && python3 build-llms.py && python3 update-sitemap.py && \
python3 build-inline.py && python3 build-inline-extra.py
```

## How verification is worded — this matters

The page says the website *"was fetched and read on [date]"*, not that the
company is trading. Nobody can check solvency from outside, and claiming
otherwise would be the one thing that could make this directory a liability
rather than an asset.

Four suppliers return 403 or a bot-check page. **They are live and defending
themselves, not dead.** They are listed with "site blocks automated checks,
verified by hand", and `check-suppliers.py` never treats that as a failure.

## Re-checking every six months

```bash
python3 check-suppliers.py
```

Fetches every listed site and reports:

- **GONE** — parked or for-sale domain
- **CHECK** — unreachable, 404, or the page no longer reads like a supplier
- **blocked** — up but refusing automation (fine, no action)
- **live** — read successfully

**It changes nothing automatically.** A directory is an editorial product and
removing a supplier should be a decision, not the side effect of a timeout.
Deal with anything flagged, update `VERIFIED` in `supplier-data.py`, rebuild.

Put a reminder in the diary for **1 February 2027**.

## Submissions

`/suppliers` has a form at the bottom. Submissions go to D1 with status
`pending` — nothing appears publicly until you add it to `supplier-data.py` by
hand. Honeypot field, and a duplicate check on both the host and the submitter.

To see what has come in:

```bash
npx wrangler d1 execute ltu-survey --remote --command \
  "SELECT id, created_at, country, name, url, cats, note FROM supplier_submissions WHERE status='pending' ORDER BY id"
```

Then mark them off:

```bash
npx wrangler d1 execute ltu-survey --remote --command \
  "UPDATE supplier_submissions SET status='added' WHERE id=1"
```

## Two decisions worth keeping

**No paid listings, no affiliate links.** Every outbound link is
`rel="noopener nofollow"`. The moment it becomes pay-to-list it stops being a
recommendation and becomes a directory nobody trusts — and the trust is what
makes suppliers want to be in it, which is what earns the links.

**The list is compiled, not crowd-dumped.** Moderation is the product.

## Where it is thin

Ireland, South Africa and mainland Europe have nothing at all, and Canada has
only two. The submission form says so explicitly and asks for those first.

This is the natural next Facebook post, and a better one than the survey:
"where do you buy your webbing?" is a question upholsterers enjoy answering and
there is nothing sensitive about it. Every reply is a directory entry, and it is
the only way to get coverage you cannot research from Yorkshire.
