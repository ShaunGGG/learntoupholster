# Glossary ontology

Closes the inconsistency shipped with the answer blocks: the 15 chapter
`DefinedTerm` nodes each declared membership of a `DefinedTermSet` at
`/a-z-glossary`, and that page had no `DefinedTerm` markup at all. They pointed
at a set that did not exist.

## What it does

Reads the live glossary markup and emits a single `DefinedTermSet` containing
every term, then rewrites the 15 chapter blocks to reference it by `@id` rather
than loosely by name and URL. Two disconnected graphs become one.

- **127 canonical terms**, each with `@id`, name and description
- **8 aliases folded in as `alternateName`** — entries like "Tack hammer. See
  Hammer, magnetic." have no definition of their own. Emitting them would create
  empty nodes; dropping them would lose real synonyms. Attached to their target
  they stay searchable, which is the point of them. 127 + 8 = the 135 in the source.
- **19 terms carry `subjectOf`** pointing at the chapter that treats them properly

Terms are parsed from the page rather than listed in the script, so editing the
glossary is enough — the schema follows on the next run.

## Cost

+28 KB raw, but **+2.6 KB gzipped**, and Cloudflare serves brotli. The structure
repeats heavily so it compresses to almost nothing. Not a page-weight concern.

## Running it

Before `build-inline.py`:

```bash
python3 patch-glossary-schema.py
```

Idempotent, and refreshes rather than duplicating if run again. Backs up to
`~/ltu-backups/`. Refuses to write if it parses fewer than 50 terms, on the basis
that something has changed and a human should look.

## Verify

```bash
curl -s https://www.learntoupholster.com/a-z-glossary | grep -c 'DefinedTermSet'   # 1
curl -s https://www.learntoupholster.com/webbing | grep -o '"inDefinedTermSet":{[^}]*}'
# expect: {"@id":"https://www.learntoupholster.com/a-z-glossary#termset"}
```
