# Removing "All tools" from the Contents menu

```bash
python3 patch-remove-all-tools.py && python3 build-inline.py && \
python3 build-inline-extra.py && npx wrangler pages deploy --branch=production
```

## What it was

A script on 88 pages, marked `/*ltuNav3*/`, takes the **first** dropdown in the
menu:

```js
document.querySelector(".nav-list .has-sub")
```

and inserts a link at the top of it:

```js
al.href = a.getAttribute("href");   // the parent's own href
al.textContent = "All tools";       // hardcoded label
```

Written when Tools was the only dropdown, so the label was right. Contents is now
first, so the item says "All tools" and goes to `/contents` \u2014 exactly what you
described.

Because it is injected at page load, the HTML source looked correct. That is why
I kept insisting it was browser cache across three rounds. It was not, and I
should have opened a rendered page rather than trusting the markup.

## What the patch does

Removes the six statements that create and insert the link. Nothing else.

The clean-up loop that strips previously injected copies is **kept** on purpose \u2014
it means any copy already sitting in a reader's cached page disappears next time
they load.

Your mobile toggle, the `collapsible` / `expanded` behaviour and the desktop
hover are all untouched, as asked.

## Verified

I ran the patched script against a stub DOM. It injects nothing, and the Contents
dropdown comes out with two items: Start Here and A\u2013Z glossary.

## After deploying

Hard refresh, then check Contents has two items and Tools still has eleven.
