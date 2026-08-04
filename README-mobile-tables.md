# Mobile tables

The thread table has six columns and the needle table five. On a phone they
overflowed and pushed the layout sideways. Desktop was fine, which is exactly why
I did not catch it.

## The fix

Rather than a sideways-scrolling table \u2014 unusable one-handed \u2014 each row
restacks as its own labelled card below 700px. The header row is moved off-screen
and every cell carries its column name, so a row reads:

```
TEX            T70
COMMERCIAL     #69
TICKET         Tkt 40
GOVT.          E
USUAL NEEDLE   110/18
FOR            The standard upholstery thread...
```

CSS only, no JavaScript. Desktop is untouched.

Applied to all four tables: thread sizes, which-thread-for-what, needle pairing,
and the US fire regulations occupancy table \u2014 which had the same problem and
which you would have hit next.

`build-fire.py` is included for that reason, so rebuild the fire pages too.

## Deploy

```bash
python3 build-sewing.py && python3 build-sewing-selector.py && python3 build-fire.py && \
python3 patch-nav-sewing.py && python3 build-md-extra.py && python3 build-llms.py && \
python3 update-sitemap.py && python3 prune-sitemap.py && \
python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

Then check on your phone: `/sewing-thread`, `/sewing-needles` and
`/fire-regulations-usa`.
