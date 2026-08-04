# Fire regulations by country

A new top-level section. Five countries, domestic and commercial on every page,
every claim sourced and dated.

## Deploy

```bash
python3 build-fire.py && python3 patch-fire-uk.py && python3 patch-nav-fire.py && \
python3 build-md-extra.py && python3 build-llms.py && python3 update-sitemap.py && \
python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

## What it creates

| Page | Domestic | Commercial |
|---|---|---|
| `/fire-regulations` | hub | |
| `/fire-safety-checker` (existing, kept) | UK — required by law | required by law |
| `/fire-regulations-usa` | required by law | depends on the building |
| `/fire-regulations-canada` | **no standard at all** | depends on the building |
| `/fire-regulations-australia-new-zealand` | **voluntary only** | depends on the building |
| `/fire-regulations-ireland` | required by law | depends on the building |

**Fire Regulations is now its own menu item**, after Business Hub, and the fire
checkers have been removed from the Tools sub-menu. It is a section of six pages,
not a tool, and appearing in both places was noise.

The UK keeps its URL. `/fire-safety-checker` has years of search history behind
it and moving it would throw that away. The hub links to it.

## The findings worth having

These are the reasons the section is worth existing, and none of them is written
down clearly anywhere else:

**United States.** The federal standard explicitly names *reupholstery* — but
CPSC confirmed to the National Upholstery Association that it does not apply
where the piece keeps the same owner. A customer's own chair coming back to them
is outside it; something you reupholster and sell is inside it. Almost no American
upholsterer knows this.

Also: TB 117-2013 tests **smoulder resistance only**. No match test at federal
level. That will surprise anyone trained to British rules.

And **California TB 133 has been repealed** — the open-flame test the trade
quoted for decades. Open-flame testing survives through NFPA 101 for
unsprinklered buildings in specific occupancies, and the page carries the full
occupancy table.

**Canada has no upholstery fire standard at all.** Ontario repealed its scheme in
2019, Manitoba in 2020, Quebec in 2021. Registration as a renovator is gone
nationwide. Most guidance still online describes the old gold, blue and white
label system as current; it has not been for years.

**Australia and New Zealand: AS/NZS 4088.1 is voluntary.** No mandatory domestic
flammability standard in either country.

**Ireland is not the UK.** S.I. No. 316/1995 and IS 419, tested to EN 1021. A
piece compliant in Britain is not automatically compliant in Ireland — and
Northern Ireland follows the UK regulations, so if you work across the border
those are two regimes.

## Honesty built into every page

Each carries, prominently: written by a British upholsterer, informational rather
than legal advice, sources listed at the foot, last-checked date printed, and the
instruction to get the requirement in writing from whoever is responsible for the
premises.

That last point is the one rule that holds in every country, and the hub says so:
**on commercial work the requirement belongs to the building, not the furniture.**

## Maintenance

`fire-data.py` holds all the content. Change a rule there and rebuild — no HTML
to edit. `CHECKED = '2026-08-02'` at the top prints on every page; update it when
you re-verify.

Worth a diary note to re-check annually. The Irish regulations are under review,
and the UK amended its regulations in 2025.

## One thing left by hand

The UK page still carries a short passage on other countries' rules, written when
it was the only page. Now each country has its own sourced page, that passage
would be better as a link to `/fire-regulations`. I have not automated that edit
because the passage is woven into hand-written prose and a script would make a
mess of it.
