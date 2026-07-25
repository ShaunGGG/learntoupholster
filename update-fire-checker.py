#!/usr/bin/env python3
"""
update-fire-checker.py
----------------------
Follow-up fixes to /fire-safety-checker after the contract checker went live.

  A. Clean print — the record prints on its own instead of dragging the whole
     page with it. Uses a hidden iframe, so no popup blocker involvement.
  B. Title and meta description updated to cover contract work (BS 7176,
     crib 5) as well as domestic.
  C. Standfirst and intro copy corrected — it is no longer "four questions".
  D. A skip link to the contract checker, for people arriving from a link
     about commercial work.
  E. New commercial Q&As appended to the EXISTING FAQPage schema block
     (not a second, competing block). Skipped safely if none is found.

Each fix is independent: if one cannot find its anchor it reports and the
others still apply. Safe to re-run. Writes a .bak2 backup.
"""

import json
import re
import shutil
import sys
from pathlib import Path

PAGE = Path("fire-safety-checker.html")

done, skipped = [], []


# ---------------------------------------------------------------- A. printing
OLD_PRINT = """  var pr = document.getElementById('cc-print');
  if(pr){ pr.addEventListener('click', function(){ window.print(); }); }"""

NEW_PRINT = """  var pr = document.getElementById('cc-print');
  if(pr){ pr.addEventListener('click', function(){
    var root = document.documentElement;
    var clear = function(){ root.classList.remove('cc-printing'); };
    root.classList.add('cc-printing');
    if(window.matchMedia){
      var mql = window.matchMedia('print');
      if(mql.addEventListener){ mql.addEventListener('change', function(e){ if(!e.matches){ clear(); } }); }
    }
    window.addEventListener('afterprint', clear, { once: true });
    setTimeout(clear, 3000);
    window.print();
  }); }"""

PRINT_CSS = ("@media print{"
             "html.cc-printing body *{visibility:hidden!important}"
             "html.cc-printing #cc-record-out,html.cc-printing #cc-record-out *"
             "{visibility:visible!important}"
             "html.cc-printing #cc-record-out{position:absolute;left:0;top:0;width:100%;"
             "border:0!important;padding:0!important;margin:0!important}"
             "html.cc-printing #cc-record-out[hidden]{display:none!important}"
             "}")

OLD_CSS_TAIL = ("@media print{.cc fieldset,.cc-btns,.cc-lede,.cc-rec .cc-grid"
                "{display:none}#cc-record-out{border:0}}")


def fix_print(html):
    changed = False

    if OLD_PRINT in html:
        html = html.replace(OLD_PRINT, NEW_PRINT, 1)
        changed = True
    else:
        skipped.append("A. clean print — could not find the existing print handler")

    if PRINT_CSS in html:
        skipped.append("A. print stylesheet — already present")
    elif OLD_CSS_TAIL in html:
        html = html.replace(OLD_CSS_TAIL, PRINT_CSS, 1)
        changed = True
    else:
        # append the rule to the checker's own <style> block instead
        m = re.search(r'(#cc-record-out dd\{margin:0\})', html)
        if m:
            html = html[:m.end()] + PRINT_CSS + html[m.end():]
            changed = True
        else:
            skipped.append("A. clean print — could not place the print stylesheet")

    if changed:
        done.append("A. clean print — record prints on its own, page suppressed")
    return html


# ------------------------------------------------------------------- B. meta
NEW_TITLE = ("Upholstery Fire Regulations: Domestic &amp; BS 7176 Contract Checker "
             "| Learn to Upholster")
NEW_DESC = ("Which fire rules apply to your upholstery job? Free checker for UK domestic "
            "work and BS 7176 contract seating \u2014 crib 5, hazard categories and "
            "printable records.")
NEW_OGTITLE = "Fire regulations checker \u2014 domestic and contract upholstery"
NEW_OGDESC = ("The 1988 Regulations and BS 7176, turned into plain questions: what your "
              "job needs on covers, fillings, hazard categories and records.")


def _swap_meta(html, pattern, newval, label):
    m = re.search(pattern, html, re.I | re.S)
    if not m:
        skipped.append(f"B. {label} — not found")
        return html
    if newval in m.group(0):
        skipped.append(f"B. {label} — already updated")
        return html
    start, end = m.span(1)
    done.append(f"B. {label} — updated")
    return html[:start] + newval + html[end:]


def fix_meta(html):
    html = _swap_meta(html, r"<title>(.*?)</title>", NEW_TITLE, "title")
    html = _swap_meta(
        html,
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']',
        NEW_DESC, "meta description")
    html = _swap_meta(
        html,
        r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\'](.*?)["\']',
        NEW_OGTITLE, "og:title")
    html = _swap_meta(
        html,
        r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\'](.*?)["\']',
        NEW_OGDESC, "og:description")
    return html


# ------------------------------------------------------------------- C. copy
COPY_SWAPS = [
    ("turned into four plain questions",
     "turned into plain questions, for domestic work and for contract seating"),
    ("Answer the four questions and the checker sets out",
     "Answer the questions and the checker sets out"),
]


def fix_copy(html):
    for old, new in COPY_SWAPS:
        if new in html:
            skipped.append(f"C. copy — already updated ({old[:32]}…)")
            continue
        if old not in html:
            skipped.append(f"C. copy — not found ({old[:32]}…)")
            continue
        html = html.replace(old, new, 1)
        done.append(f"C. copy — updated ({old[:32]}…)")
    return html


# -------------------------------------------------------------- D. skip link
SKIPLINK = ('\n<p class="cc-skip" style="margin:.9rem 0 0;font-size:.95rem">'
            '<strong>Working on contract seating?</strong> '
            '<a href="#cc-checker">Skip to the BS&nbsp;7176 checker for pubs, hotels, '
            'care homes and offices &rarr;</a></p>\n')


def fix_skiplink(html):
    if 'class="cc-skip"' in html:
        skipped.append("D. skip link — already present")
        return html
    m = re.search(r'printable compliance record for your files\.?\s*</p>', html, re.I)
    if not m:
        m = re.search(r'a printable compliance record.*?</p>', html, re.I | re.S)
    if not m:
        skipped.append("D. skip link — could not find the standfirst")
        return html
    done.append("D. skip link — added under the standfirst")
    return html[:m.end()] + SKIPLINK + html[m.end():]


# ------------------------------------------------------------------ E. schema
NEW_FAQS = [
    ("Do commercial upholstery jobs follow the same fire regulations as domestic?",
     "No. Domestic upholstered furniture falls under the Furniture and Furnishings "
     "(Fire) (Safety) Regulations 1988 as amended. Seating for non-domestic premises "
     "such as pubs, hotels, offices and care homes falls under BS 7176, which sets four "
     "hazard categories according to the end-use environment. The two are not "
     "alternatives: BS 7176 requires all filling materials to pass the relevant tests in "
     "the 1988 Regulations at every hazard category, so contract work adds requirements "
     "rather than replacing them."),
    ("What is BS 7176 medium hazard and when does crib 5 apply?",
     "Medium hazard is the BS 7176 category that covers most commercial premises, "
     "including hotels, restaurants, pubs, hospitals and care homes. It requires the "
     "cigarette test (BS EN 1021-1), the match test (BS EN 1021-2), and ignition source "
     "5 — crib 5 — from BS 5852. Crib 5 is applied to the cover and filling together as "
     "a composite, so a certificate for the fabric alone does not evidence that the "
     "finished piece meets the category."),
    ("Who is responsible for fire compliance of upholstery in commercial premises?",
     "Responsibility for the fire safety of premises rests with the responsible person "
     "for those premises under the Regulatory Reform (Fire Safety) Order 2005, through "
     "their fire risk assessment. The upholsterer's role is to build to the hazard "
     "category that assessment specifies and to record the materials supplied. Ask for "
     "the required BS 7176 hazard category in writing before starting work — "
     "'fire retardant' on its own names no category, no ignition source and no test."),
]


def fix_schema(html):
    blocks = list(re.finditer(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.I | re.S))
    if not blocks:
        skipped.append("E. FAQ schema — no JSON-LD blocks on the page")
        return html

    for b in blocks:
        raw = b.group(1).strip()
        try:
            data = json.loads(raw)
        except Exception:
            continue
        nodes = data if isinstance(data, list) else [data]
        if isinstance(data, dict) and "@graph" in data:
            nodes = data["@graph"]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            if str(node.get("@type", "")).lower() != "faqpage":
                continue
            entities = node.setdefault("mainEntity", [])
            if not isinstance(entities, list):
                entities = [entities]
                node["mainEntity"] = entities
            existing = {str(e.get("name", "")) for e in entities if isinstance(e, dict)}
            added = 0
            for q, a in NEW_FAQS:
                if q in existing:
                    continue
                entities.append({
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a},
                })
                added += 1
            if added == 0:
                skipped.append("E. FAQ schema — entries already present")
                return html
            new_json = json.dumps(data, indent=2, ensure_ascii=False)
            done.append(f"E. FAQ schema — {added} Q&As appended to the existing FAQPage")
            return html[:b.start(1)] + "\n" + new_json + "\n" + html[b.end(1):]

    skipped.append("E. FAQ schema — no FAQPage block found (nothing added, "
                   "to avoid a competing block)")
    return html


# ------------------------------------------------- F. print button always shown
CANON_PRINT = """  var pr = document.getElementById('cc-print');
  if(pr){ pr.hidden = false; pr.addEventListener('click', function(){
    var rec = document.getElementById('cc-record-out');
    if(!rec || rec.hidden || !rec.innerHTML.trim()){
      var mk2 = document.getElementById('cc-make');
      if(mk2){ mk2.click(); }
      rec = document.getElementById('cc-record-out');
    }
    if(!rec || rec.hidden){ return; }
    var root = document.documentElement;
    var clear = function(){ root.classList.remove('cc-printing'); };
    root.classList.add('cc-printing');
    window.addEventListener('afterprint', clear, { once: true });
    setTimeout(clear, 3000);
    window.print();
  }); }"""


def fix_print_button(html):
    changed = False

    # 1. the button itself should not start hidden
    m = re.search(r'(<button[^>]*id="cc-print"[^>]*)\s+hidden(\s*>)', html)
    if m:
        html = html[:m.start()] + m.group(1) + m.group(2) + html[m.end():]
        changed = True
    elif re.search(r'<button[^>]*id="cc-print"', html):
        skipped.append("F. print button — already visible by default")
    else:
        skipped.append("F. print button — button not found")
        return html

    # 2. canonical handler: creates the record on demand, then prints
    if "if(mk2){ mk2.click(); }" in html:
        skipped.append("F. print handler — already creates the record on demand")
    else:
        pat = re.compile(
            r"  var pr = document\.getElementById\('cc-print'\);"
            r"[\s\S]*?window\.print\(\);\s*\}\);\s*\}")
        m2 = pat.search(html)
        if m2:
            html = html[:m2.start()] + CANON_PRINT + html[m2.end():]
            changed = True
        else:
            skipped.append("F. print handler — could not find the handler to replace")

    if changed:
        done.append("F. print button — always visible, creates the record if needed")
    return html


# ---------------------------------------------------------------------- main
def main():
    if not PAGE.exists():
        sys.exit("ERROR: fire-safety-checker.html not found. Run from the repo root.")

    original = PAGE.read_text(encoding="utf-8")
    if 'id="cc-checker"' not in original:
        sys.exit("ERROR: the contract checker isn't on this page yet. "
                 "Run add-commercial-checker.py first.")

    html = original
    for fn in (fix_print, fix_print_button, fix_meta, fix_copy, fix_skiplink, fix_schema):
        html = fn(html)

    if html == original:
        print("No changes needed — everything is already applied.")
    else:
        shutil.copy2(PAGE, PAGE.with_suffix(".html.bak2"))
        PAGE.write_text(html, encoding="utf-8")
        print(f"Updated fire-safety-checker.html "
              f"({len(original):,} → {len(html):,} chars)")
        print("Backup: fire-safety-checker.html.bak2\n")

    if done:
        print("Applied:")
        for d in done:
            print("  ✓", d)
    if skipped:
        print("\nSkipped:")
        for s in skipped:
            print("  ·", s)


if __name__ == "__main__":
    main()
