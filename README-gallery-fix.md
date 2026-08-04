# Gallery fixes: giant Facebook icon, and Gallery out of the menu

Re-run the merge \u2014 it now repairs the previous one rather than refusing.

```bash
python3 build-projects.py && \
python3 merge-gallery.py && \
python3 remove-our-work.py && \
python3 patch-nav-gallery.py && \
python3 optimise-project-images.py && \
python3 build-md-extra.py && python3 build-llms.py && python3 update-sitemap.py && \
python3 build-inline.py && python3 build-inline-extra.py && \
npx wrangler pages deploy --branch=production
```

## The Facebook logo

My fault. The `<div class="gallery-wrap">` on the old page holds three things
before the photographs: a promotional paragraph about Greenwood being insured, a
"share your before-and-afters in our Facebook group" callout with an inline SVG,
and a sidenote. I took the whole wrapper.

The callout's icon is sized by a `.ba-note svg` rule, and my CSS extraction only
carried rules matching `.gallery`, `.lightbox`, `figure` and `figcaption`. So the
SVG arrived with no width and rendered at whatever space it could take.

**Fixed by taking only the inner `<div class="gallery">`.** Just the 43 figures,
nothing else. That also drops the Greenwood promotional paragraph, which read
oddly on a page about documenting work anyway.

Two smaller things caught while fixing it:

- The gallery div already carries `id="gallery"`, and my heading was adding a second one. Duplicate IDs are invalid HTML and break anchor links. Removed.
- The script now **repairs a previous merge** instead of printing "already merged" and leaving the page wrong. Verified stable over three consecutive runs: 43 figures every time, no accumulation.

If you want the Facebook group link on the projects page, that is worth adding
deliberately with its own styling rather than smuggled in with the photographs.

## Gallery out of the menu

Removed entirely. It pointed at a section of a page already in the menu, and the
menu had grown long. Handles both the original `/our-work` entry and the
`/projects/#gallery` version the earlier patch left.

## Check after deploying

```bash
curl -s https://www.learntoupholster.com/projects/ | grep -c "<figure"     # 43
curl -s https://www.learntoupholster.com/projects/ | grep -c "ba-note"     # 0
curl -s https://www.learntoupholster.com/ | grep -c ">Gallery<"            # 0
curl -s -o /dev/null -w "%{http_code} -> %{redirect_url}\n" \
  https://www.learntoupholster.com/our-work                                # 301
```
