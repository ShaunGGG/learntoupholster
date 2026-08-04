# Sewing phase 5 — setup and parts. Section complete.

```bash
python3 build-sewing.py && python3 build-sewing-selector.py && python3 patch-nav-sewing.py && \
python3 build-md-extra.py && python3 build-llms.py && python3 update-sitemap.py && \
python3 prune-sitemap.py && python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

Final page at `/sewing-setup`. Six pages, all cross-linked, all in the dropdown.

| | |
|---|---|
| `/sewing` | hub |
| `/sewing-selector` | three questions, full specification |
| `/sewing-machines` | feed types and bed types |
| `/sewing-troubleshooting` | six symptoms, 28 checks |
| `/sewing-thread` | sizes, fibres, four numbering systems |
| `/sewing-needles` | pairing, systems, points |
| `/sewing-setup` | motors, reducers, feet, tension |

## The motor is the headline

**Changing a clutch motor for a servo is the single best thing you can do to an
older industrial machine**, and the upholsterers are close to unanimous on it.

A clutch motor runs continuously and is controlled by slipping the clutch \u2014 a
narrow usable range that is genuinely hard to learn, and the reason so many
people describe an industrial machine as bolting away from them. A servo only
turns when you press, follows the pedal, and most have a dial to cap the top
speed while you learn. Bolt-on job, less than a set of feet and a few cones of
thread.

**Speed reducers get an honest warning.** A reducer slows the machine *and*
multiplies punching power by the same ratio, which is the real answer for very
thick leather where a servo loses torque at the bottom of its range. But fit one
early and the machine becomes slow enough to be maddening once you are quicker
and want to get through the work. Servo first; reducer only if still short of
power at low speed.

## Two practical details worth having

**Walking foot feet come as sets** \u2014 inner and outer together. You cannot
swap one. Not obvious until you have ordered the wrong thing.

**Welting feet are sized to the cord**: 1/8, 5/32, 3/16, 1/4, 5/16 and 3/8 inch.
The groove has to match or the stitching will not pull tight against the piping.

And the choice nobody explains: **toothed feet or smooth**. Teeth grip and feed
better through thick assemblies; smooth does not mark. On any face that will be
seen, especially leather, smooth is worth the poorer grip.

## The tension section is an order, not a list

Rethread with the foot **up** so the discs are open \u2192 leave the bobbin alone
\u2192 test on an offcut of the actual material \u2192 read which side is losing
\u2192 adjust the top only, a little at a time.

Almost every tension problem is solved on top, and almost every one made worse
was made worse by starting at the bobbin.

## Needle-change interval corrected

You called out the "every eight hours" figure and you were right — that came
from a domestic and quilting source, where a machine runs all day on fine cloth
and a slightly blunt point shows at once. Upholstery is not that. You sew a seam
and go back to the bench, and the needle is a heavier thing to start with.

All three pages that carried it now say the same thing instead: **change it when
the work tells you to**, not on a schedule —

- skipped stitches appear
- the sound changes
- snagging or pulled threads in the face
- straight after the needle has met a tack, a staple or the plate
- and a fresh one before a job you cannot afford to mark

The needle page keeps the hour-count but explains why it does not apply here,
since anyone who has read it elsewhere will wonder.

## A small bug caught in the final check

Two pages missed the link to the new setup page because their cross-link wording
differed slightly from the others. Caught by counting links per page rather than
assuming the edit applied. All seven pages now link to all their siblings.
