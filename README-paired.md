# Survey: fix the traditional-vs-modern comparison

**Deploy this soon — the current figure on your site is wrong.**

```bash
python3 build-survey.py && npx wrangler pages deploy --branch=production
```

## What was wrong

The survey published at 30 responses with:

> A traditional rebuild takes **1.4×** as long as a modern re-cover

and a United States row reading traditional 16 hours, modern 20 — modern taking
*longer*, which is nonsense.

My bug. I took the median of every traditional answer and, separately, the
median of every modern answer — **from different groups of people**. Seven
respondents answered only the modern question, with high figures (20, 50, 24,
25), which pulled the modern median up while the traditional median came from an
entirely different set.

## The correct figure

Comparing each respondent against themselves, from the 16 who answered both:

| | |
|---|---|
| pairs | 16 |
| median traditional | 25.5 h |
| median modern | 10.5 h |
| **multiplier** | **1.9×** |

Which is consistent with the two-to-three times your pricing chapter asserts,
and with your own 20 / 9.5.

## The fix

The multiplier is now the **median of per-workshop ratios**, not a ratio of two
medians. Wing-back medians — overall and per country — are also computed from
paired respondents only, so the two figures always describe the same people and
can honestly be set side by side. Both need at least five pairs before they
appear at all.

The page now says so:

> A traditional rebuild takes 1.9× as long as a modern re-cover on the same
> chair. Measured per workshop, from the 16 upholsterers who gave both figures —
> not by comparing one group's answers against another's.

## Why this matters more than the arithmetic

This is the number most likely to be quoted, and it is the one thing on the site
that nobody else has. If it had gone out at 1.4 and someone had checked it
against the underlying data, the whole dataset's credibility would have gone
with it.

Worth remembering as more responses arrive: every published figure needs to be
one you could defend if a sceptical upholsterer asked how it was calculated.
