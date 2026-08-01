# Survey update — wing-back, traditional vs modern

## What changed

**Out:** "Bench hours: stuffover dining chair".

**In:** two wing-back questions instead of one —

- *Wing-back, full traditional rebuild* — hint sharpened to "Stripped to the frame
  and rebuilt — webbing, springs, hair, stitched edges. Not a re-cover."
- *Wing-back, modern re-cover* — "The same chair stripped and rebuilt in foam and
  modern materials."

Still 13 questions, so the wording in your Facebook post is still accurate.

## Why it's worth the swap

Asking both gives a figure nobody has published: how much longer a traditional
rebuild takes than a modern re-cover, on the same piece, across a real sample.
Your pricing chapter asserts two to three times. This evidences it.

The results page now shows both medians and a derived line:

> A traditional rebuild takes 2.1× as long as a modern re-cover on the same
> chair — from 40 upholsterers, rather than from anyone's rule of thumb.

Per-country columns show both figures too.

## Database

Already done via the connector, nothing to run:

- `hours_wingback_modern` column added
- Your own row corrected to 20 traditional / 9.5 modern

The `hours_dining` column is left in place rather than dropped — it holds your
original answer and destroying data to tidy a schema is a bad trade. It is simply
no longer written to or read from. `survey-schema.sql` omits it for fresh installs.

## Deploy

```bash
python3 build-survey.py && python3 build-md-extra.py && \
python3 build-llms.py && python3 build-inline.py && \
npx wrangler pages deploy --branch=production
```

## Note on the two responses already in

Neither answered the old dining-chair question, so nothing is lost. The US
response left all bench hours blank, which is exactly what the skip-anything
wording is for.
