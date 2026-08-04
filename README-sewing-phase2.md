# Sewing phase 2 — the thread and needle selector

```bash
python3 build-sewing.py && python3 build-sewing-selector.py && python3 patch-nav-sewing.py && \
python3 build-md-extra.py && python3 build-llms.py && python3 update-sitemap.py && \
python3 prune-sitemap.py && python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

New page at `/sewing-selector`, added to the Sewing dropdown and the hub. This
bundle also contains the phase 1 pages, so it supersedes the earlier one.

## What it does

Three questions \u2014 material, where it will live, construction or top stitch \u2014
returning thread fibre, Tex size with the commercial and ticket equivalents,
needle size and range, point type, and stitch length. With the reasoning for
each, so you can judge whether it fits the job rather than taking it on trust.

Deterministic and runs in the browser. No API call, nothing to fail, works
offline once loaded. It reads from `sewing-data.py`, so the selector and the
guide pages cannot drift apart.

**All 18 combinations tested by running the actual logic.** Every one returns a
complete and coherent specification.

## The research produced one genuinely good finding

**Stitch length works in opposite directions depending on the material**, and
most guidance never mentions it.

On woven cloth, more stitches make a *stronger* seam \u2014 the thread passes
between the yarns rather than cutting them, and each stitch adds holding power.
A&E publish it as seam strength = stitches per inch \u00d7 thread strength \u00d7 1.5.

On leather and vinyl, more stitches make a *weaker* one. Every stitch is a
permanent hole, and crowding them perforates the material along a line until the
seam tears the way a stamp does.

So the instinct to sew finer for neatness is right on cloth and wrong on hide.
That is exactly what a table cannot express and a selector can, and it is why
the first question is what you are sewing.

SPI to millimetres is 25.4 \u00f7 SPI, cross-checked against a published pairing
of 12 SPI with 2.1 mm.

## Two things running the logic caught

**Top stitching was getting the same stitch length as a construction seam.** It
should be longer: the heavier thread needs room or the line crowds into
something you cannot read, and the whole point of a decorative stitch is that
the individual stitches show. Now 6\u20137 SPI whatever the material.

**My woven range was too fine.** I had 8\u201310 SPI. Published guidance puts
heavyweight cloth \u2014 which upholstery fabric is \u2014 at 6\u20138. Widened to
7\u201310 with a note to go finer on light cloth and longer on heavy weaves.

## Honest limitation

Most published stitch-length guidance is written for garment manufacture or hand
leatherwork. Upholstery-specific machine figures are thinner on the ground, so
the ranges are inferred from heavyweight-fabric and leather guidance rather than
lifted from an upholstery standard. The page says to test on an offcut, which is
the right instruction regardless.

Worth your eye on the stitch lengths in particular \u2014 that is bench knowledge
and you will know immediately if a figure looks wrong.
