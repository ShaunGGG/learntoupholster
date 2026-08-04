# Dropdowns for Fire Regulations and Contents

```bash
python3 patch-nav-dropdowns.py && python3 build-inline.py && \
python3 build-inline-extra.py && npx wrangler pages deploy --branch=production
```

## What changes

**Fire Regulations** becomes a dropdown, the same as Tools:

- United Kingdom
- United States
- Canada
- Australia & New Zealand
- Ireland

**Contents** becomes a dropdown, and Start Here moves inside it:

- Full contents
- Start Here
- A\u2013Z glossary

The standalone Start Here item is removed, so the top-level menu loses an entry
rather than gaining one. I added the A\u2013Z glossary as well \u2014 a dropdown
holding a single item looks like a mistake, and the glossary belongs with the
contents rather than buried in Tools.

## Why it needs no other wiring

The dropdown is pure CSS on `.has-sub` \u2014 hover and `:focus-within` on desktop,
a stacked indented list under 880px. No JavaScript. New dropdowns work with
nothing else changed, on mobile as well as desktop.

## A bug worth recording

The first version inserted the Contents dropdown and then deleted the standalone
Start Here entry as a separate step. That deleted the wrong one: once the
dropdown exists, the first `/start-here` match in the file is the entry *inside*
it. The result was a Contents dropdown with Start Here missing and no way to
reach the page from the menu at all.

Contents and Start Here are now replaced together in one operation, which cannot
go wrong that way. Verified: Start Here appears exactly once in the nav, inside
the dropdown.

## Check after deploying

```bash
curl -s https://www.learntoupholster.com/ | grep -c 'class="has-sub"'   # 3
curl -s https://www.learntoupholster.com/ | grep -c '/start-here'       # 1 in the nav
```

Then hover Fire Regulations and Contents on the desktop menu, and check both
expand on a phone.
