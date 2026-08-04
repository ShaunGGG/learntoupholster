# Sewing phase 4 — troubleshooting

```bash
python3 build-sewing.py && python3 build-sewing-selector.py && python3 patch-nav-sewing.py && \
python3 build-md-extra.py && python3 build-llms.py && python3 update-sitemap.py && \
python3 prune-sitemap.py && python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

New page at `/sewing-troubleshooting`. Six symptoms, 28 checks, ordered so the
cheap ones come first. Jump links at the top so someone with a machine in front
of them lands on their problem rather than scrolling.

Bundle contains phases 1\u20134.

## What the research established

**The mechanism, so the checks make sense rather than being a list.** A stitch
forms when the hook passes through the loop of thread appearing at the needle eye
as the needle rises a few millimetres off its lowest point. Every skipped-stitch
cause is a reason the hook and that loop failed to meet. Once that is stated, the
order of the checks is obvious instead of arbitrary.

**Change the needle first, always.** A machine shop's own account: a great many
machines brought in for skipped stitches sew perfectly the moment a new needle
goes in. A needle bends long before it looks bent, and a fraction of a millimetre
moves it out of the hook's path. Recommended interval is every eight hours of
sewing.

**Bernina's rule, worth repeating:** threading, needle, tension \u2014 roughly
four times out of five the fault is one of those three and not the machine.

**A test I had not seen before and have put on the page.** Thread the needle,
hold the thread at about 45 degrees, and let the needle hang on it. A correctly
matched needle slides down the thread under its own weight. That checks the
thread-to-needle pairing in five seconds with nothing but the two things in your
hand.

**The counterintuitive one:** too *large* a needle with too fine a thread causes
skipped stitches, because the loop formed is too small for the hook to catch.
Most people only think about needles being too small.

**Industrial-specific checks** most guidance omits, from a thread manufacturer's
own troubleshooting: the throat plate hole should be only slightly larger than
needle and thread together; the inner presser foot must hold on the needle's
downward stroke; a hook tip sharpened more than once or twice has moved the
timing.

## Two things on the page that are judgement rather than research

**When to stop.** Timing and hook clearance are real faults, but they are the
last things to suspect and they need tools. The page says: if you have worked the
list and nothing changed, stop guessing then \u2014 not three hours in with every
adjustment moved and no way back.

**Write down what you change.** One thing at a time, noted, then test. Half the
machines that end up genuinely out of adjustment got there during an attempt to
fix something else.

## This is the page your experience would improve most

Everything here is mechanically sound and sourced, but troubleshooting is
pattern recognition built from having fixed the same fault a hundred times.
Things I suspect you know that no source states:

- Which of these you actually hit most often on upholstery work
- Anything vinyl or leather specific that does not apply to cloth
- Faults tied to the heavy end \u2014 T135 and up, thick assemblies
- Whatever the Jack does that the Juki does not, or the reverse

Send me any of that and I will add it. It is the sort of thing that would make
this the best page of its kind rather than a good one.
