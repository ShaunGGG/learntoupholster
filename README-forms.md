# Workshop forms

A new page at `/workshop-forms`: four printable forms that carry a job through the
workshop.

## Why print-ready HTML and not another spreadsheet

The quote and invoice are already covered by the .xlsx on `/invoice-template`, and
that is the right format for those — they do arithmetic.

These four do not. They are paperwork you fill in with a biro at a customer's
house or on the bench, so a download is friction rather than help:

- Nothing to open, no software to own
- Works on a phone standing in someone's front room
- Fill on screen and print, or print blank and write on it
- Your workshop name and contact save locally and appear on all four

## The forms

**Customer enquiry** — taken on the first call. Source of enquiry, the piece, what
they want, fabric supplied by whom, deadline, budget, next action. Stops the
"what did they actually say?" problem a week later.

**Furniture condition report** — completed *before* work starts, ideally at
collection with the customer present, with a signature line. This is the form that
prevents arguments about damage. Frame, upholstery, existing marks, photographs
taken.

**Job sheet** — travels with the piece. Scope checklist, materials, metreage,
batch or dye lot, foam spec, **fire certificate references**, estimated versus
actual hours, quoted price and balance.

**Collection & delivery note** — signed at handover. Two copies, one each.

## Details worth knowing

**Actual hours are on the job sheet on purpose.** Most workshops never record them,
which is why their estimates never improve. The form asks for estimated and actual
side by side.

**Fire compliance has its own block**, because the certificate references are the
thing people lose. It links back to the fire regulations checker.

**Written for use anywhere.** No currency symbols baked in, no country-specific
legal wording, and where fire certificates come up the page points at the checker
for the UK position rather than assuming it.

**Print behaviour:** each form prints on its own A4 page. "Print this form" prints
just that one; "Print all four" prints the set. The nav, footer, ads, intro and
index are all hidden in print, and input boxes become ruled lines.

## Build order

`build-forms.py` goes before `build-inline.py`, same as the other generators:

```bash
python3 build-forms.py && python3 build-business.py && \
python3 build-md-extra.py && python3 build-llms.py && \
python3 update-sitemap.py && python3 build-inline.py && python3 build-inline-extra.py
```

`update-sitemap.py` will pick the page up automatically.

## Worth doing next

Link it from the Business Hub tool grid — it belongs alongside the calculators.
Add `('/workshop-forms', 'Workshop forms', 'Enquiry, condition report, job sheet
and delivery note. Print-ready.')` to the `TOOLS` list at the top of
`build-business.py` and rebuild.
