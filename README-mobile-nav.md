# Two things

## 1. What you are seeing is a cached page

The live nav right now is:

```html
<li class="has-sub"><a href="/contents">Contents</a>
  <ul class="sub-menu">
    <li><a href="/start-here">Start Here</a></li>
    <li><a href="/a-z-glossary">A\u2013Z glossary</a></li>
  </ul>
```

There is no "All tools" anywhere in the navigation. `Ctrl+Shift+R` will show it.

## 2. A real problem I did cause

Adding dropdowns for Contents and Fire Regulations was free on desktop, where
they are hover menus. On mobile it was not, because the stylesheet force-expands
every sub-menu:

```css
@media(max-width:880px){ .sub-menu{position:static;display:block} }
```

Fine with one dropdown. Not fine with three. The burger menu became **26 items**
\u2014 eight top-level plus eighteen permanently open children, including all
eleven tools \u2014 so everything ran together as one undifferentiated list.

`patch-nav-mobile.py` adds a chevron beside each dropdown parent on mobile.
Sub-menus start closed and open one at a time. The parent link still navigates,
so tapping "Tools" goes to /tools exactly as before. Desktop hover is untouched,
and the chevrons are hidden above 880px.

**Mobile menu: 8 items instead of 26.**

Tested: three toggles created, all start closed, tapping opens and closes with
`aria-expanded` tracking correctly, and returning to a wide screen closes
anything left open.

## Deploy

```bash
python3 patch-nav-mobile.py && python3 update-sitemap.py && python3 prune-sitemap.py && \
python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

`prune-sitemap.py` is in this bundle too \u2014 the sitemap still lists `/our-work`
and `/outreach/supplier-outreach`, both of which are gone.

Then check on your phone: the menu should show eight items with chevrons, and
tapping one should open just that section.
