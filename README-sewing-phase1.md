# Sewing section, phase 1 — thread and needles

```bash
python3 build-sewing.py && python3 patch-nav-sewing.py && \
python3 build-md-extra.py && python3 build-llms.py && python3 update-sitemap.py && \
python3 prune-sitemap.py && python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

Three pages: `/sewing`, `/sewing-thread`, `/sewing-needles`. **Sewing** is a
top-level menu item with a dropdown, after Fire Regulations. `sewing-data.py`
holds the content; later phases are edits to that file.

## The re-check found four things wrong. All corrected.

**135\u00d716 and 135\u00d717 are the same system.** I had them as two systems. They
are interchangeable \u2014 identical shank and length, different point. 135\u00d716
is the leather point, 135\u00d717 the round point. Getting that wrong would have
sent people hunting for a system they already had.

**System 190 is Pfaff.** I had written "some cylinder-arm and heavier machines",
which was a guess dressed as a fact. It is 190R / MTX190, a 2.00 mm shank used in
Pfaff industrial machines.

**NM is measured above the scarf.** Schmetz specify the blade diameter is taken
above the scarf or short groove and *not* at any reinforced part \u2014 which is
why a reinforced needle can measure thicker than its number in places. Added,
along with the detail that the system was fixed in 1942 to replace some forty
competing ones.

**DB\u00d71 changes system above 110/18.** A genuine trap I had missed: the shank
is 1.63 mm up to 110/18, and larger sizes of the same needle are made on a
2.00 mm shank and become system 134. Now on the page.

## The Tex research found a real gap

**Ticket numbers were missing entirely, and they are what you actually buy by.**
Coats and Gütermann cones are marked Tkt 40, Tkt 20 — not Tex, not commercial
size. A British or European upholsterer reading a page that only gave American
numbering would have to convert before they could use it. The table now leads
with Tex and carries Commercial, Ticket and Government side by side.

The trap is worth stating plainly, and the page does: **ticket numbers run
backwards.** A higher ticket is a *finer* thread, the opposite of Tex.

Two other things the research explained that nobody sets out clearly:

**Why #69 and T70 are nearly but not quite the same number.** Both come from
denier, by different divisors. Three 210-denier plies is 630 denier: ÷ 9 gives
Tex 70, × 0.11 gives commercial 69. Same thread, two sums.

**Why you never see a T73.** Polyester at that ticket uses 220-denier plies,
which works out at Tex 73 — and is still sold as T70, because Tex sizes are
bracketed into fixed steps and anything between rounds to the nearest.

Both now on the page, with the worked figures.

## What the re-check confirmed

Thread sizing, the Tex definition, bonded construction and the Z-twist rule all
stand — the Tex definition now confirmed directly by Gütermann rather than
by retailers. The T70 needle range (100/16 \u2013 110/18) is confirmed by four independent
sources.

**Groz-Beckert strengthens the vinyl advice.** They describe their R point as
suiting woven fabrics, leather, *artificial leather and coated fabrics* alike \u2014
the manufacturer's own way of saying a round point is defensible on vinyl. That
is now quoted rather than asserted as workshop lore.

## Sources removed, and why that is defensible here

The citation lists are gone from all three pages, replaced by one practical line:
sizing is standardised so the numbers hold wherever you work, but manufacturers
vary at the margins and their own chart beats any general table.

That is a reasonable call for this material in a way it would not be for fire
regulations. Fire rules are law, they differ by country and they get amended —
so a reader needs to check the source and the date. Thread and needle sizing is
standardised engineering fact. It does not shift with jurisdiction and it does
not get repealed.

The sources are kept in `sewing-data.py` with a note explaining why they are no
longer printed. If anything is ever queried, they are there.

**One limitation worth you knowing even though it is not on the page.** The T70
needle pairing was confirmed by four independent sources. The larger sizes —
T135 and above — rest mainly on one published chart from a specialist
retailer rather than a needle maker. I could not find a manufacturer table
covering the coarse end. That is part of why the "your supplier's chart wins"
line stays.

## Written to be read anywhere

Nothing on these pages is country-specific, and the framing now says so. All four
numbering systems are given equal standing rather than one being treated as
normal and the others as foreign:

- Tex as the international standard
- Commercial size as North American but common worldwide
- Ticket numbers as what most upholsterers outside North America buy by
- Government sizes as a US legacy still printed on thread everywhere

Needle sizing is metric with the Singer equivalent, which is universal. The only
brand names are needle systems and thread makers, which are the same everywhere.

## Your Schmetz pack changed the needle page, for the better

You mentioned UK walking foot needles come as sizes 18, 20, 21, 23, 24. That sent
me back to check, and two things came out of it.

**The published charts disagree with each other.** The two most widely cited
differ by about one size step through the middle of the range — one gives
125/20 to 140/22 for T135, the other 140/22 to 180/24 for the same thread.
Neither is wrong; needle choice depends on the material as much as the thread. I
had been treating one chart as authoritative and flagging your figures against
it, which was the wrong frame.

The table now gives a **workable range spanning both charts**, plus the size most
people actually reach for. Your 130/21 for T135 sits inside it. Your 160/23 is
the usual choice for T210 on the coarser chart — so it was a real, sensible
figure, just filed one row up from where I was looking.

**Not every size is stocked everywhere**, and no chart mentions it. Packs sold as
Singer 18, 20, 21, 23, 24 are metric 110, 125, 130, 160, 180 — so a chart
telling you to fit a 140/22 or a 200/25 may be sending you after something your
supplier does not carry. The page now says: take the nearest stocked size within
the range and test on an offcut, which is what the band is for.

That is the sort of thing only someone buying needles would know, and it is not
written down anywhere else I could find.

## Still needs your eyes

The **"which thread for what"** table is your judgement, kept as you gave it,
with campervan and caravan rows added from your own work. Worth a read before it
is public.

**The "which thread for what" table is your judgement**, kept as you gave it,
with campervan and caravan rows added from your own work. Read it before it is
public.
