# PROMPT — paste this to Claude, then follow its questions

I'm Shaun, Greenwood Upholstery. Publish a new project on learntoupholster.com
using my existing Projects system — the finished page must match the live
Parker Knoll project (learntoupholster.com/projects/parker-knoll-wing-chair)
in structure: fact box, stage headings with numbered photos and captions,
methods cross-links, four FAQs, and the workshop block. My build system does
all of that automatically. Everything you need is in this kit
(moto_seat_project_kit.zip): the finished project text file
`project-sources/kawasaki-motorbike-seat.txt` and a photo-prep script
`prep-moto-photos.py`. Do not rewrite the project text — it's approved.

THE JOB
A Kawasaki motorbike dual seat: stripped, foam rebuilt FLAT (customer's
request), patterned with the shrink-wrap method, cut with 1/2 inch seam
allowance, sewn in double-diamond vinyl with red piping, refitted. Nine
photos tell the story, renamed 01.jpg–09.jpg like the Parker Knoll set.

THE NINE PHOTOS (verify each by LOOKING at it, don't trust filenames blindly):
  01  PXL_20260716_111621*  old seat, black ribbed vinyl, split at the nose
  02  PXL_20260716_111650*  stripped seat, new white foam cut flat, yellow foam at tail
  03  PXL_20260716_114159*  seat wrapped in shrink wrap, marker seam lines + hatching
  04  PXL_20260720_075245*  the wrap cut into flat pattern pieces, labelled Front/Back/Piping
  05  PXL_20260716_160522*  diamond-stitch cover under the sewing machine
  06  PXL_20260720_121018*  finished covered seat on the bench, red piping
  07  IMG*WA0002*           PORTRAIT shot of seat on the bike from behind the bars
  08  IMG*WA0001*           close-up of the fitted seat on the bike, tank in shot
  09  IMG*WA0003*           full side-on shot of the whole bike  << HUB THUMBNAIL

STEPS
1. Copy `kawasaki-motorbike-seat.txt` into `project-sources/` of the
   learntoupholster repo. Copy `prep-moto-photos.py` to the repo root.

2. Compare my new txt against `project-sources/parker-knoll-wing-chair.txt`
   in the repo. If the Parker Knoll file has any extra fields my new file
   lacks (for example a field that feeds the "Tools & materials used on this
   job" Amazon box), add the same field to the motorbike file with
   job-appropriate items: marine/automotive vinyl, vinyl piping cord, contact
   spray adhesive, upholstery shears. Match the Parker Knoll format exactly.

3. Run:  python3 prep-moto-photos.py <folder-with-the-9-photos>
   It renames the photos to 01.jpg–09.jpg in
   `project-sources/photos/kawasaki-motorbike-seat/`, bakes orientation,
   strips ALL EXIF/GPS, and blurs the number plate (reads "YBJ 198X") in
   photos 07, 08 and 09.

4. CRITICAL — verify the blur. View every image in `plate-checks/` AND the
   three full images 07/08/09 in the photos folder. The plate must be
   unreadable at full zoom in ALL THREE (07: bottom edge of the portrait
   frame; 08: right edge; 09: mid-right of frame). If any character is
   legible, widen that photo's box in BLUR_BOXES inside the script and
   re-run. Never proceed with a readable plate.

5. Ask me THREE questions before building, then edit the txt with my answers:
   a) hours:  (fact box — currently blank)
   b) price:  (currently blank; leave out if I say so)
   c) exact bike model (e.g. Z650). If I give one, rename the slug to match
      (e.g. kawasaki-z650-seat): rename the .txt file AND the photos folder,
      and update title/subtitle/piece/intro to name the model.

6. Build:  python3 build-projects.py && python3 patch-projects-nav.py
   Expect this project's line to say 9 stages, 9 photos, 4 FAQs. Open the
   generated projects/<slug>.html and check: stages run 01→09 with their
   headings, captions match the photos, the methods block links to
   Foam Construction and Stripping the Old Work, and the /projects hub card
   uses the FULL BIKE shot (09) as its thumbnail.

7. Deploy:
   npx wrangler pages deploy . --project-name=learntoupholster --branch=production \
     && git add -A \
     && git commit -m "Project: Kawasaki motorbike seat — flat re-shape and re-cover" \
     && git push
   Then give me the live URL to check.

RULES
- Never commit or deploy any photo with a readable number plate.
- Don't modify build-projects.py or patch-projects-nav.py.
- Don't rewrite my project text beyond steps 2 and 5.
- If any photo doesn't match its description above, stop and show me.

(If you're Claude on claude.ai with the nine photos attached instead of
Claude Code in the repo: do steps 3–5 in your sandbox — uploads land in
/mnt/user-data/uploads — then hand me a zip of the finished project-sources/
tree plus the exact build+deploy commands above, and I'll run them locally.)
