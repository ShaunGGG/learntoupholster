# Entity schema — defining what the site already points at

## The problem

Twenty-four pages carry references like:

```json
"publisher": {"@type":"Organization","@id":"https://www.learntoupholster.com#org"}
"author":    {"@type":"Person","@id":"https://www.learntoupholster.com/about#shaun"}
```

**Neither @id was defined anywhere.** A consumer follows the reference and finds
nothing. The homepage had a decent Organization — logo, founder, description —
but with no `@id`, so nothing could link to it, and `/about` had a second Person
with no `@id` either. Two nodes describing the same man, no way to know they are
one person.

Most of those dangling references are mine, written into the Business Hub,
survey and glossary generators without ever defining the targets. This closes it.

## What it does

**Homepage** — defines `Organization #org`, `WebSite #website` and `Book #book`,
and removes the old un-@id'd WebSite so there are not two competing definitions
of the same site.

**/about** — defines `Person /about#shaun` in full: job title, AMUSF credential
as a proper `EducationalOccupationalCredential`, `worksFor` pointing back at the
Organization, and `knowsAbout`. The existing ProfilePage is rewritten so its
`mainEntity` points at that @id rather than describing a second Shaun.

Result: every reference across all 24 pages now resolves to a real node.

## Before you run it — SAME_AS

At the top of the script:

```python
SAME_AS = [
    'https://www.pinterest.co.uk/YOURHANDLE/',
]
```

**Put your Pinterest URL in.** `sameAs` is the machine-readable claim that an
account carrying your name is yours. It is how a search engine joins the site
and the accounts into one entity, and it is genuinely the most useful line in
the whole file.

It runs fine with the list empty and tells you it is empty. But an Organization
that claims no profiles is doing half a job.

Only list accounts you control.

## Run

```bash
python3 patch-entity-schema.py && python3 build-inline.py && \
python3 build-inline-extra.py && npx wrangler pages deploy --branch=production
```

Idempotent. Backs up to `~/ltu-backups/` first.

## On the hashtag

Worth being straight: none of this affects `#learntoupholster` on social. A
hashtag is not owned and cannot be claimed by markup — it goes to whoever posts
under it consistently. Kim's Upholstery is not holding a crown; as far as your
own site shows, Learn to Upholster has no social presence at all, so nobody else
is in the room.

What this schema does affect is how Google and AI systems understand the name:
whether "Learn to Upholster" is a phrase that appears in text, or an entity with
an identity, a publisher, a named accredited author and a set of profiles. That
is the part you can win with code. The hashtag is won by posting.
