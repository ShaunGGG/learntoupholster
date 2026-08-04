# Sewing phase 3 — machines

```bash
python3 build-sewing.py && python3 build-sewing-selector.py && python3 patch-nav-sewing.py && \
python3 build-md-extra.py && python3 build-llms.py && python3 update-sitemap.py && \
python3 prune-sitemap.py && python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

New page at `/sewing-machines`, added to the hub and the dropdown. Contains
phases 1 and 2 as well, so this supersedes the earlier bundle.

## The terminology is genuinely broken, and the page fixes it

Checking this properly turned up the same shape of problem as the thread twist
question. The sources contradict each other:

- One supplier: unison feed is "also known as walking foot feed"
- Another: needle feed "is more appropriately termed compound"
- A third lists compound, needle and triple feed as three names for one thing

They are not the same thing, and someone buying a machine on those descriptions
could easily pay for a walking foot and think they had bought compound feed.

**There is a clean test and the page gives it:** watch the needle while the
machine sews. If the needle travels forward with the material, it is compound
feed. If it only rises and falls while the top foot walks, it is a walking foot
machine and nothing more. Ten seconds, and it beats arguing about the label.

That framing came from an upholstery workshop's own account rather than a
manufacturer's, which is why it is the clearest one out there.

## The four feeds, in order

| | |
|---|---|
| Drop feed | not upholstery \u2014 only the underside is driven, so the top layer creeps |
| Needle feed | better \u2014 needle carries the work, but nothing grips the top |
| Walking foot | good \u2014 top and bottom driven, but the needle does not travel |
| **Compound feed** | **what you want** \u2014 feed dogs, inner foot and needle all in step |

## The buying advice is honest rather than aspirational

Every guide I read wants to sell a second machine. The upholsterers say something
different, and the page says it too: cylinder and post bed machines make small
curved work easier **but only on a few seams, and not often**. One trimmer put it
that on many jobs it is less trouble to top stitch on the flat bed already
threaded than to swap thread over to the cylinder for two runs.

So the page recommends one compound feed flat bed, mentions that flat-bed
attachments exist for cylinder machines, and names the one case where a cylinder
arm stops being a luxury \u2014 genuinely three-dimensional work most days.

## A bug caught in testing

The menu patch used one variable name for two different things and crashed on its
summary line after correctly updating the menu. Fixed, and the top-up logic is
now generic: it adds whichever dropdown entries are missing rather than checking
for one specific page. Later phases will not need it changed again.

Both paths tested \u2014 inserting the menu fresh, and topping up a dropdown
deployed before these pages existed. Identical result, idempotent.

## Still worth your eye

The mechanics are well sourced and cross-checked. The **buying judgement** is
where your experience beats my reading \u2014 particularly whether a cylinder arm
is as occasional as the forums suggest, given you do vehicle and campervan work
where three-dimensional pieces are more common than in furniture.
