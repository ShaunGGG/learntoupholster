#!/usr/bin/env python3
"""
write-title-proposals.py — Learn to Upholster

Fills column 4 of title-proposals.tsv with hand-written titles, all under
60 characters, keyword-first, brand suffix dropped. Google truncates or
rewrites "| Learn to Upholster" anyway, and on a 97-character title it was
costing 40% of the visible space.

Review the TSV afterwards and change anything you disagree with. Setting a
row's column 4 equal to column 3 skips that row.

Usage:
    python3 write-title-proposals.py
    python3 write-title-proposals.py --apply
    then: python3 patch-seo-audit-sep26.py --apply --titles-apply
"""
import os, shutil, sys
from datetime import datetime, timezone

TSV = "title-proposals.tsv"
APPLY = "--apply" in sys.argv

TITLES = {
    "calico-wadding-and-top-cover.html": "Fitting the Top Cover: Calico, Wadding & Corner Pleats",
    "foam-construction.html": "Foam Cushion Construction: Cutting, Bonding & Dacron",
    "buttoning-and-tufting.html": "Deep Buttoning & Tufting: The Diamond Grid Explained",
    "trimming-and-finishing.html": "Upholstery Trimming: Gimp, Welt & Decorative Nails",
    "fire-safety-checker.html": "UK Upholstery Fire Regulations & BS 7176 Checker",
    "fabric-visualiser.html": "Free Fabric Visualiser: See Your Chair in Your Fabric",
    "historical-style-guide.html": "Identifying British Chair & Sofa Styles by Period",
    "customers-and-the-workshop-year.html": "Customers & the Upholstery Workshop Year",
    "stripping-the-old-work.html": "How to Strip a Chair for Reupholstery",
    "fabric-yardage.html": "Upholstery Fabric Yardage Calculator: Metric & Imperial",
    "loose-covers.html": "Loose Covers: Measuring, Calico Mock-Up & Seams",
    "stuffing-and-stitched-edges.html": "Stuffing & Stitched Edges: The Sprung-Edge Seat",
    "press-pack.html": "Press Pack \u2014 Greenwood Upholstery & Learn to Upholster",
    "frame-repair-and-joint-reinforcement.html": "Chair Frame Repair & Joint Reinforcement",
    "start-here.html": "Start Here: Your First Upholstery Project, Step by Step",
    "modern-sofa-recover.html": "Modern Sofa Re-Cover: Foam, Staple & Fixed-Price",
    "readers-bench.html": "The Reader's Bench: First Seats by Book Readers",
    "chesterfield-sofa.html": "Chesterfield Sofa: Deep-Buttoned Leather Restoration",
    "standards-regulations-and-bibliography.html": "UK Upholstery Standards, Regulations & Bibliography",
    "the-wing-back-that-wasnt-a-howard.html": "The Wing-Back That Wasn't a Howard: A Workshop Story",
    "projects/renault-twizy-seat-wrap.html": "Renault Twizy Seats in Diamond-Stitch Vinyl",
    "materials-reference-charts.html": "Upholstery Materials Reference Charts: Specs & Uses",
    "workshop-forms.html": "Free Printable Upholstery Workshop Forms",
    "drop-in-dining-seat.html": "Drop-In Dining Seat: A Complete Beginner's Project",
    "fire-regulations-australia-new-zealand.html": "Australia & New Zealand Upholstery Fire Regulations",
    "knots-and-stitches.html": "Upholstery Knots & Stitches: Illustrated Reference",
    "sewing-thread.html": "Upholstery Thread Guide: Sizes, Nylon vs Polyester",
    "the-family-sofa-from-heptonstall.html": "The Family Sofa from Heptonstall: A Workshop Story",
    "projects/jensen-s-v8-carpet-set.html": "Jensen S-V8: Fitting a New Car Carpet Set in Navy",
    "find-an-upholsterer.html": "Find an Upholsterer Near You: UK, US & Worldwide",
    "wing-back-armchair.html": "Wing-Back Armchair: Full Traditional Restoration",
    "invoice-template.html": "Free Upholstery Invoice & Quote Template (Excel)",
    "springing-traditional.html": "Traditional Springing: Hand-Tied Coil Springs",
    "projects/kawasaki-motorbike-seat.html": "Kawasaki Motorbike Seat in Diamond-Stitch Vinyl",
    "choosing-the-right-fabric.html": "Choosing the Right Upholstery Fabric: A Beginner's Guide",
    "leather-hide-calculator.html": "Leather Hide Calculator: Square Feet & Hides",
    "piping-calculator.html": "Upholstery Piping & Bias-Strip Calculator",
    "sewing-setup.html": "Sewing Machine Setup & Parts for Upholstery",
    "sewing-troubleshooting.html": "Sewing Machine Troubleshooting for Upholstery",
    "the-pair-of-nursing-chairs.html": "The Pair of Nursing Chairs: A Workshop Story",
    "pricing-and-quoting.html": "Pricing & Quoting for an Upholstery Workshop",
    "springing-modern.html": "Modern Springing: Zigzag & No-Sag Springs",
    "stool-pouffe.html": "Stool & Pouffe: Buttoned Drum Stool Project",
    "the-toolkit.html": "The Upholstery Toolkit: Tools for Beginners",
    "a-brief-opinionated-history-of-upholstery.html": "A Brief, Opinionated History of Upholstery",
    "buy-the-book.html": "Buy the Book: Wiro-Bound Workshop Edition",
    "index.html": "Learn to Upholster: Traditional & Modern Techniques",
    "stuffover-dining-chair.html": "Stuffover Dining Chair: A Step-Up Project",
    "fire-regulations-usa.html": "United States Upholstery Fire Regulations",
    "headboard.html": "Upholstered Headboard: A Complete Project Guide",
    "sewing-machines.html": "Industrial Sewing Machines for Upholstery",
    "sewing-selector.html": "Thread & Needle Selector for Upholstery",
    "foam-cushion-calculator.html": "Foam & Cushion Density Calculator by Project",
}

def die(m):
    print(f"\n  ABORT: {m}\n  Nothing was changed.\n"); sys.exit(1)

if not os.path.isfile(TSV):
    die(f"{TSV} not found. Run --titles-propose first.")
lines = open(TSV, encoding="utf-8").read().splitlines()
if not lines or not lines[0].startswith("file\t"):
    die("unexpected TSV header — refusing to rewrite.")

out = [lines[0]]
filled = skipped = 0
unseen = set(TITLES)
for line in lines[1:]:
    p = line.split("\t")
    if len(p) != 4:
        out.append(line); continue
    f, old_len, cur, _ = p
    unseen.discard(f)
    new = TITLES.get(f)
    if new is None:
        out.append("\t".join([f, old_len, cur, cur])); skipped += 1
        print(f"     no title written for {f} — row set to skip")
    else:
        out.append("\t".join([f, old_len, cur, new])); filled += 1

print(f"  mode   : {'APPLY' if APPLY else 'DRY RUN (nothing written)'}")
print(f"  filled : {filled}    left to skip: {skipped}")
if unseen:
    print(f"  NOTE: {len(unseen)} titles had no matching TSV row (page renamed?):")
    for u in sorted(unseen): print(f"     {u}")
bad = [(f, t) for f, t in TITLES.items() if len(t) > 60]
if bad:
    die(f"{len(bad)} written titles exceed 60 chars — fix before applying.")
print("  all written titles are 60 chars or under")

if not APPLY:
    print("\n  Dry run only. Re-run with --apply.\n"); sys.exit(0)

ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
bdir = os.path.expanduser(f"~/ltu-backups/title-proposals-{ts}")
os.makedirs(bdir, exist_ok=True)
shutil.copy2(TSV, os.path.join(bdir, TSV))
open(TSV, "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"  backup : {bdir}")
print(f"  written: {TSV}")
print("\n  Review it, then:")
print("    python3 patch-seo-audit-sep26.py --apply --titles-apply\n")
