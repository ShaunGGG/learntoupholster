# Supplier icons

Every listing now carries the supplier's own site icon at 40px, with the text
beside it.

## Run

```bash
python3 fetch-supplier-icons.py && python3 build-suppliers.py
```

The icons are in the bundle already, so you only need to run the fetcher after
adding a new supplier. It skips anything already downloaded.

## Results

- **44 of 59** fetched from the supplier's own site
- **15** fall back to a generated lettermark — initials in the site palette

The fallbacks are not failures on my side. Eight of those sites declare no icon
at all, three block automated requests, and three serve an HTML page in response
to their own declared icon URL. Nothing recoverable there.

A lettermark looks deliberate rather than broken, which matters — a directory
where half the rows have an image and half have a gap looks unfinished.

**Bodella is one of the fallbacks**, because it publishes only `favicon.svg` and
Pillow cannot rasterise SVG. If you add a `favicon.png` or `apple-touch-icon.png`
to the Bodella site, delete `assets/supplier-icons/bodella.png` and re-run the
fetcher and it will pick it up.

## Two decisions worth knowing

**Self-hosted, not hot-linked.** It would have been one line to point at Google's
favicon service. That sends every visitor's browsing history to a third party and
breaks whenever they change it. These are fetched once at build time and served
from your own domain — 138 KB for all 59.

**Site icons, not brand logos.** A favicon is what a company publishes as its own
identifying mark, and using one to identify the company you are linking to is
ordinary directory practice. Scraping fifty-nine companies' full brand logos is a
murkier thing to do with other people's trademarks, and they would be
inconsistent shapes anyway.

## On adding logo upload to the submit form

I would not build that, and the reason is not effort.

A file upload endpoint means R2 storage, MIME and size validation, a malware
surface, and moderating every uploaded image — on a public form, on your domain,
for a directory that has had no submissions yet. That is a meaningful attack
surface bought for very little.

And it is unnecessary: `fetch-supplier-icons.py` gets the icon from the URL the
submitter gives you, which is better data anyway because it is guaranteed to
match the real site rather than being whatever file someone chose to upload.

The workflow is already complete without it:

1. Submission arrives, you get the email
2. You check the site is real and add it to `supplier-data.py`
3. `python3 fetch-supplier-icons.py` collects the icon automatically
4. `python3 build-suppliers.py`

If a supplier ever wants a specific image used, they can email it and you drop it
into `assets/supplier-icons/<slug>.png` by hand. That is the same outcome with
none of the risk.
