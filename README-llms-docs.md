# llms.txt generator + /use-in-ai developer reference

Two fixes, both for problems found while verifying the last deploy rather than
from the audit's wishlist.

## 1. `build-llms.py` — new

`llms-full.txt` had drifted. The answer blocks went into the chapters, the HTML,
the markdown variants and the ask index — but not into `llms-full.txt`, because
whatever generated it in July was a one-off and never joined the build chain. A
333KB file that has to be remembered will eventually be forgotten.

This makes it derived output. Source of truth is `md/`, which `build-md.py` has
just regenerated, so the two cannot disagree.

**It must go into the chain, after `build-md.py`:**

```
python3 build-ask-index.py && python3 build-md.py && python3 build-llms.py && python3 build-inline.py
```

Regenerates both `llms.txt` and `llms-full.txt`. Reports page count, file sizes,
the change against the previous version, and a canary count of question-form
headings so a silent regression shows up.

Both files will change shape slightly from the July versions: cleaner heading
hierarchy, a knowledge version and generation date in the header, and a pointer
to the MCP endpoint. The content is the same corpus.

## 2. `patch-use-in-ai.py`

The page currently tells visitors the connector *"can answer questions from the
book, nothing more"*. True this morning, false since we shipped the calculators
— on the one page whose job is describing what the thing does.

The patch corrects that line, adds four calculator examples to "Try asking", and
appends a developer reference: endpoint facts, protocol versions, auth, cost,
licence, the seven tools, the provenance fields, and a working curl example.
That's the audit's section 19.

The existing copy-to-clipboard control and the Claude setup steps are untouched.
Writes nothing unless every target is found. Safe to run twice.

## Verify after deploying

```bash
# should be 15, not 0
curl -s https://www.learntoupholster.com/llms-full.txt | grep -c "^### What is\|^### How much\|^### What are"

# should list all seven
curl -s https://www.learntoupholster.com/use-in-ai | grep -c "check_fire_regulations"

# should be gone
curl -s https://www.learntoupholster.com/use-in-ai | grep -c "nothing more"
```

## Still not done

The A–Z glossary (~150 terms) is the obvious next structural piece — turning it
into a `DefinedTermSet` with each term linked to its chapter would finish the
ontology the 15 `DefinedTerm` blocks started. Worth doing, but it is not what is
capping your visibility.
