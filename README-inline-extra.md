# build-inline-extra.py

## The problem it fixes

`build-inline.py` reports "inlined into 62 pages". The site has 80. It works on
the site root only, so anything under `business/`, `projects/` or
`state-of-the-trade/` keeps whatever stylesheet was current when that page was
generated — and silently drifts from then on.

The white tile behind the AMUSF crest is what exposed it. Root pages got it;
`/business/` and `/projects/` did not. `/state-of-the-trade/` did, but only by
luck: it was generated after the crest CSS landed, so it lifted a fresh copy.

This is the same root-only limitation `build-md.py` had, which is why
`build-md-extra.py` exists. Same shape of fix.

## What it does

Reads the canonical `:root` stylesheet out of a freshly-inlined root page and
replaces the stale copy in every subdirectory page.

Scoped blocks that don't start with `:root` are left alone — the `.biz-*` rules
on Business Hub pages and the `.sv-*` rules on the survey belong to those pages
and must survive. Verified: block counts are unchanged, only the `:root` block
is swapped.

**Must run after `build-inline.py`**, or it copies a stale stylesheet.

## The full chain, in order

```bash
python3 build-business.py && \
python3 build-survey.py && \
python3 patch-nav-footer.py && \
python3 build-ask-index.py && \
python3 build-md.py && \
python3 build-md-extra.py && \
python3 build-llms.py && \
python3 update-sitemap.py && \
python3 build-inline.py && \
python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

Generators first, then indexes, then CSS inlining, then the subdirectory catch-up.

## Verify

```bash
curl -s https://www.learntoupholster.com/business/ | grep -o '\.foot-crest[^{]*{[^}]*}' | grep -c 'inline-flex'
# expect 1, not 0
```

## Worth knowing

Any future change to `styles.css` has this same failure mode. As long as
`build-inline-extra.py` stays at the end of the chain it's handled, but if you
ever run `build-inline.py` on its own to push a quick CSS change, run this
straight after it.
