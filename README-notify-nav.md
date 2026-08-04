# Supplier notifications + Tools menu

## 1. You now get told about submissions

`/api/supplier-submit` emails you when someone sends a supplier in. Two secrets
needed — you already use Resend for the Greenwood quote worker, so the same
account works:

```bash
npx wrangler pages secret put RESEND_API_KEY --project-name=learntoupholster
npx wrangler pages secret put NOTIFY_EMAIL --project-name=learntoupholster
```

Optionally `NOTIFY_FROM` if you want it from your own verified domain rather
than Resend's default sender.

The email gives you the name, URL, country, categories, any note, and how many
are waiting — plus the exact command to mark it approved.

**The email is fire-and-forget.** If Resend is down or the key is missing, the
submission is still saved; you just do not get told. Losing a submission to a
failed email would be the worse outcome.

Without the secrets it works exactly as before, silently. To check by hand:

```bash
npx wrangler d1 execute ltu-survey --remote --command \
  "SELECT id, created_at, country, name, url, note FROM supplier_submissions WHERE status='pending'"
```

## 2. Tools menu

`patch-nav-tools.py` adds two entries that were unreachable from the navigation:

- **Supplier directory** — first in the sub-menu, above the calculators
- **Workshop forms** — after the invoice template

The directory goes at the top because "where do I buy this" is the question
people arrive with most often, and it is the only thing in that menu that
answers it.

Idempotent, walks every page, backs up first. Run before `build-inline.py`.

## Deploy

```bash
python3 patch-nav-tools.py && python3 build-inline.py && \
python3 build-inline-extra.py && npx wrangler pages deploy --branch=production
```
