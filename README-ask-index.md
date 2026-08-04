# build-ask-index.py — now covers subdirectories

Drop-in replacement. Run it exactly as before:

```bash
python3 build-ask-index.py
```

## What was wrong

`glob.glob('*.html')` is root-only, so `ask_the_book` could not see the Business
Hub, the project write-ups or the supplier directory. Nineteen articles and six
projects were invisible to the one tool people actually ask questions through.

## Four fixes

**Recursive walk.** `**/*.html`, skipping `md/`, `functions/`, `assets/`,
`business-sources/`, `outreach/` and the rest.

**URLs for directory indexes.** A naive fix would have produced `/business/index`,
which redirects. `url_for()` returns `/business/` instead. Getting this wrong
would have had `ask_the_book` citing URLs that bounce.

**The content wrapper.** Your original matched `//section[@class="wrap"]` — an
exact attribute match. Project pages, the survey and the directory all use
`class="wrap read"`, so none of them matched. Now tests the class list properly.

**Interface furniture excluded.** Without this, the survey call-to-action at the
foot of all 19 Business Hub articles, the directory filters and the Visualiser Pro
block would all be indexed as though they were prose. Verified: zero leaked in.

Also skipped: `workshop-forms.html` and `take-part.html` (the text is field
labels, which makes noise not answers), `press-pack.html`, and anything carrying
a `noindex` robots tag.

## Tested

Against thirteen real pages pulled from the live site. Business Hub and project
chunks come out with the right URLs, titles and headings; the root behaves exactly
as before; every intended exclusion holds.

It now prints a breakdown so you can see at a glance that the subdirectories are
being picked up:

```
694 chunks written to ask-index.json
   (root)             315
   business           228
   projects           138
```

## One thing to be aware of

The index roughly doubles: **315 chunks / 385 KB → around 690 chunks / 850 KB.**

That is fine — it is served as a static asset and edge-cached, and more chunks
means better retrieval rather than worse. But it is a real jump, so if
`ask_the_book` ever feels slower, this is why and the file is where to look.

## Note on the survey

`/state-of-the-trade/` is not indexed, because its filename is `index.html` and
the results are rendered by JavaScript — there is little static prose to index.
That is the right outcome; the survey is not really "ask the book" material.

## Deploy

```bash
python3 build-ask-index.py && npx wrangler pages deploy --branch=production
```

Then try it:

```bash
curl -s -X POST https://www.learntoupholster.com/mcp -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"ask_the_book","arguments":{"question":"how do I turn down a job politely"}}}'
```

Before the patch that answered "the book doesn't cover it". It should now answer
from the Business Hub.
