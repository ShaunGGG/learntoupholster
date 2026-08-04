# Supplier outreach

```bash
python3 build-suppliers.py && python3 build-outreach.py
```

Writes `outreach/supplier-outreach.md` — **58 individual messages**, one per
listed supplier, grouped by country, each linking to that supplier's own anchor
on the directory page. Bodella is skipped; you do not need to write to yourself.

Nothing is sent. These are drafts to work through by hand.

## Why this is the highest-value thing on the list

Fifty-eight businesses are in a free, verified, editorially compiled directory
on a site written by an AMUSF-accredited upholsterer, and none of them knows.

Some will link to it from a stockists or press page. Those are editorial links —
given freely, from relevant industry domains — and they are exactly the kind
that count and cannot be bought. This is the payoff for having built the
directory, and it is the most direct route to the authority problem that has
capped the site since the start.

## Two rules built into the wording

**It asks for nothing.** No link, no mention, no reply requested. That is
deliberate. Asking for a link in exchange for a listing turns it into an
exchange, and "requiring links as part of an agreement" is precisely what Google
names as a link scheme. Anything that comes back from a message that asked for
nothing is genuinely editorial.

**One message at a time, to a named business, about their own entry.** A BCC
blast to fifty-eight addresses is spam however politely written.

## Practical

- Most have a contact form rather than a published address. Use it. Do not hunt for personal emails.
- Start with the UK general suppliers — likeliest to care about a British reference site, quickest to reply.
- Fabric houses are larger and slower. Leave those until you have the hang of it.
- A handful a night is plenty. There is no deadline.
- If anyone asks to be removed, remove them that day and thank them. A directory people trust is worth more than one more entry.

## Also in this bundle

`build-suppliers.py` now gives every listing an anchor — `#s-ross-fabrics` and so
on — so each message can point at that supplier's own entry rather than the top
of a page of fifty-nine.

## After you deploy

```bash
python3 build-suppliers.py && python3 build-md-extra.py && python3 build-llms.py && \
python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

Then generate the drafts. The anchors need to be live before you send anything,
or the links in the emails will land at the top of the page instead of the entry.
