# State of the Upholstery Trade — survey

Original data is the one asset an AI cannot reproduce and the thing most likely
to earn citations and inbound links. This is the machine for collecting it.

## What's here

| File | Purpose |
| --- | --- |
| `survey-schema.sql` | D1 table. No personal data by design. |
| `functions/api/survey.js` | POST records a response; GET returns public aggregates. |
| `build-survey.py` | Builds `/state-of-the-trade/` (live results) and `/state-of-the-trade/take-part` (form). |
| `build-md-extra.py` | Updated: now also covers `state-of-the-trade/`. |

## Setup — three steps, once

**1. Create the database**

```bash
npx wrangler d1 create ltu-survey
npx wrangler d1 execute ltu-survey --remote --file=survey-schema.sql
```

**2. Bind it to the Pages project**

Dashboard → Workers & Pages → **learntoupholster** → Settings → Functions →
**D1 database bindings** → add:

- Variable name: `SURVEY_DB`
- Database: `ltu-survey`

Add it to **Production** (and Preview if you want to test there).

**3. Add the hashing salt**

```bash
npx wrangler pages secret put SURVEY_SALT --project-name=learntoupholster
```

Paste any long random string. It salts the IP hash so the stored value can't be
brute-forced back to an address. Don't change it later — the duplicate check
depends on it staying constant.

## Build order

```bash
python3 build-survey.py && python3 build-md-extra.py && \
python3 build-llms.py && python3 update-sitemap.py && python3 build-inline.py
```

## Design decisions I made

**Live results, not an annual report.** A page that updates as responses arrive
is far more linkable than a PDF in 2027, and it gives people a reason to fill the
form in. The JSON at `/api/survey` is a citable endpoint in its own right and is
declared as a `Dataset` in schema.org markup, CC-BY.

**Nothing publishes below 30 responses.** A median shop rate drawn from six
workshops would get quoted back for years and would be wrong. Per-country figures
need 8 of their own before they appear. The results page shows progress toward
the threshold instead, which is itself a reason to take part.

**Medians, never means.** One person typing 900 for their hourly rate shouldn't
move a published figure.

**No personal data at all.** No names, no emails, no free text — every field is a
number or a value from a fixed list. The IP is stored only as a salted hash, only
to stop one person answering fifty times. There is nothing to leak, nothing to
delete on request, and no meaningful GDPR surface, which matters when respondents
are worldwide.

**Rates are never converted between currencies.** Comparing a UK rate to a US one
through an exchange rate says nothing useful about either. Each country's median
is shown in its own currency.

**Junk is rejected, not stored and cleaned later.** Values outside the allowed
lists and implausible numbers get a 400. A honeypot field catches basic bots.

## The part that isn't built

Distribution. The survey works; nobody knows it exists. It needs putting in front
of upholsterers — trade groups, the AMUSF, Facebook and Reddit upholstery
communities, suppliers' newsletters, your own LinkedIn. 30 responses is the first
hurdle and it is entirely a distribution problem, not a technical one.

I'd also add a line to the foot of the Business Hub articles pointing at it once
it's live, since that's where the right people already are.

## Verify after deploying

```bash
curl -s https://www.learntoupholster.com/api/survey | python3 -m json.tool
# expect: responses 0, published false, note about the threshold

curl -s -o /dev/null -w '%{http_code}\n' https://www.learntoupholster.com/state-of-the-trade/take-part
```
