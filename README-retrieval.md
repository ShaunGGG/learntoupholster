# ask_the_book retrieval — BM25

Two changes that fix the failure you found.

```bash
python3 patch-ask.py && python3 build-ask-index.py && \
npx wrangler pages deploy --branch=production
```

## What was wrong

The scorer summed raw term frequency:

```js
s += tf;                          // "upholstery" ×6 = 6 points
if (head.includes(w)) s += 4;     // "carpal" ×2   = 2 points
```

No inverse document frequency, so a word in four hundred chunks counted the same
as one in two. That is why:

- `carpal tunnel` → worked
- `carpal tunnel upholstery` → failed

Adding one common word buried the distinctive one. `indexOf` also matched
without word boundaries, so "tan" matched "important".

Doubling the index this morning made it worse, because there are now twice as
many chunks containing common words competing for the same query.

## Two fixes

**BM25 scoring** in `ask.js`. Rare terms weighted by rarity, term frequency
saturates instead of growing without limit, long chunks no longer win on length
alone, and word boundaries on matching. The heading bonus is kept but scaled by
how distinctive the word is.

**Per-supplier chunking** in `build-ask-index.py`. All 59 directory listings were
running together into a handful of 2000-character blocks, so a search for
"horsehair" was competing against four unrelated companies in the same chunk.
Each listing is now its own chunk.

## Measured on your real index

Twelve questions, checking whether the right page reaches the model at all — not
just whether it ranks first, since eight chunks are sent:

| | old | new |
|---|---|---|
| right page retrieved | 10 / 12 | **12 / 12** |

Specifically fixed: `carpal tunnel upholstery` (was nothing), and
`where can I buy horsehair` (now rank 1, pointing at Provincial Upholstery).
Improved: stitched edges, fire regulations, campervan work — all now send more
relevant chunks. Nothing got worse.

## Cost

BM25 does two passes over the index per query rather than one. At ~620 chunks
that is a few milliseconds, against a Claude call taking two seconds. The
lower-casing that used to happen per request now happens once when the index
loads.

## Note

`patch-ask.py` only replaces `retrieve()` and the index-loading line. The
affiliate tool matching, the system prompt and the API call are untouched. It
writes nothing if either target is missing, and backs up first.
