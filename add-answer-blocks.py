#!/usr/bin/env python3
"""
add-answer-blocks.py — put a short canonical answer at the top of each chapter.

The long-form writing is the asset and none of it is touched. This adds a
90-word direct answer above it: the bit a model lifts when someone asks the
plain question, and the bit a reader in a hurry wants anyway.

Each block also emits a DefinedTerm, which is the start of the glossary
ontology — one canonical URL owning one subject.

Run from ~/learntoupholster. Idempotent: run it twice, nothing doubles up.
"""

import os, re, sys, shutil, datetime, html

MARK = 'ltu-answer-block'

CSS = """
/* Canonical answer block — short direct answer above the chapter proper. */
.ltu-answer{background:#fff;border:1px solid var(--rule);border-left:4px solid var(--green);
  padding:1.1rem 1.3rem;margin:0 0 1.8rem;border-radius:3px}
.ltu-answer h2{font-family:var(--display);font-size:1.24rem;line-height:1.3;margin:0 0 .5rem;
  color:var(--green-deep);font-weight:600}
.ltu-answer p{margin:0;font-size:1.06rem;line-height:1.55}
@media print{.ltu-answer{border-left-color:#000;break-inside:avoid}}
"""

# slug: (question, answer, term, term definition)
BLOCKS = {

'webbing': (
 'What is upholstery webbing?',
 'Upholstery webbing is a woven strip stretched taut across a furniture frame to carry everything built '
 'on top of it \u2014 springs, stuffing, cushions and the person sitting down. '
 'The trade standard for traditional work is 10-strand English jute, 50 mm '
 'wide, interlaced over and under like a basket and tensioned with a webbing strainer. Each end takes '
 'five 13 mm improved tacks: three through a single layer, the web folded back, then two through the '
 'doubled fold. Modern furniture more often uses rubber or elasticated webbing, which stretches by design '
 'and gives a softer seat. Get the webbing wrong and the chair sags within a year, however good the work above it.',
 'Upholstery webbing',
 'The load-bearing woven layer stretched across a furniture frame to support springs, stuffing or cushions.'),

'foam-construction': (
 'What foam should I use for upholstery?',
 'For a seat cushion, use HR or Reflex foam at 35\u201350 kg/m\u00b3 density and around 140\u2013200 N '
 'hardness, typically 100\u2013150 mm thick. Density and hardness are different things and people constantly '
 'confuse them: density is how much foam is in the foam and decides how long it lasts, while hardness is '
 'only how it feels to sit on. A cheap cushion can feel firm in the showroom and be flat in eighteen months '
 'because it was hard but not dense. Backs go softer, around 24 kg/m\u00b3; contract seating goes to 45 kg/m\u00b3 '
 'and up. In the UK all of it must be CMHR grade.',
 'CMHR foam',
 'Combustion Modified High Resilience foam, the fire-retardant grade required for UK domestic upholstery.'),

'springing-traditional': (
 'How does traditional springing work?',
 'Traditional springing uses double-cone coil springs stood on the webbing, stitched down to it in three '
 'places with a spring needle and twine, then lashed to each other and to the frame with laid cord. The '
 'lashing is the part that matters: it holds each spring upright and slightly compressed so the seat works '
 'as one surface rather than a field of independent springs. Springs are sized by gauge and height \u2014 a '
 'dining chair might take 10 or 12 gauge at 100 mm, an armchair seat 9 gauge at 150 mm. Done properly a '
 'sprung seat lasts decades and can be reworked rather than replaced.',
 'Double-cone spring',
 'The traditional upholstery coil spring, waisted at the centre, stitched to webbing and lashed with laid cord.'),

'stuffing-and-stitched-edges': (
 'What is a stitched edge in upholstery?',
 'A stitched edge is a firm, shaped rim built into the first stuffing so the seat holds a defined line '
 'instead of collapsing into a dome. Hair or fibre is held under scrim, then worked with a double-ended '
 'needle and twine: blind stitches first, buried inside the stuffing to drag it forward and pack the edge, '
 'then top stitches worked along the roll to sharpen it. Two or three rows is usual. It is the slowest, '
 'most skilled part of traditional upholstery and the part that decides whether the finished chair looks '
 'crisp or soft. No modern foam edge reproduces it convincingly.',
 'Stitched edge',
 'A firm shaped rim formed in the first stuffing with blind and top stitches, giving a traditional seat its defined line.'),

'buttoning-and-tufting': (
 'What is deep buttoning?',
 'Deep buttoning is a pattern of buttons pulled down into the stuffing on twine, forming diamonds of '
 'fabric between them with folded pleats running corner to corner. The critical point is that the grid '
 'marked on the fabric must be larger than the grid marked on the base \u2014 typically 13 mm extra per '
 'diamond for shallow buttoning, 19 mm for medium and 32 mm for deep, in both directions. That surplus is '
 'what travels down into each button pull and forms the pleat. Mark the fabric with the base spacing and '
 'the cover will be tight, the pleats will not form, and the panel is scrap.',
 'Deep buttoning',
 'A buttoned upholstery treatment where buttons are pulled into the stuffing, forming pleated diamonds of surplus fabric.'),

'choosing-the-right-fabric': (
 'How do I choose upholstery fabric?',
 'Judge upholstery fabric on four things. Durability, measured by the Martindale rub test: 15,000 or more '
 'for light domestic use, 25,000 general domestic, 40,000 for heavy domestic or light contract, and 100,000 '
 'for severe contract. Fire performance, which in the UK means the cover must pass the match test as part '
 'of the composite it is fitted with, not on its own. Construction, since a loose weave snags and a tight '
 'weave wears. And the practical matter of width and pattern repeat, which decides how much you buy. '
 'Colour is the last decision, not the first.',
 'Martindale rub test',
 'The abrasion test used to rate upholstery fabric durability, quoted as a number of rubs.'),

'calico-wadding-and-top-cover': (
 'What is calico used for in upholstery?',
 'Calico \u2014 muslin in the United States \u2014 is a plain cotton cloth fitted over the stuffing before '
 'the top cover goes on. It does the work of consolidating the shape: pulled and tacked tight, it compresses '
 'the stuffing into its final form and holds it there, so the top cover only has to be dressed over an '
 'already finished shape rather than create one. Over the calico goes a layer of wadding, which stops the '
 'coarse fibres beneath working through the cover and softens the surface. Skip the calico and the top '
 'cover does two jobs badly.',
 'Calico',
 'Plain cotton cloth fitted over upholstery stuffing to consolidate its shape before the top cover.'),

'stripping-the-old-work': (
 'How do you strip an old chair?',
 'Work downwards in the reverse order the chair was built, taking off one layer at a time: top cover, '
 'wadding, calico, stuffing, hessian, springs, webbing. Use a ripping chisel and mallet, driving along the '
 'grain and never across it, or the rail splits. Photograph every layer before you remove it and keep the '
 'old covers \u2014 unpicked, they are the most accurate pattern you will ever have for the new ones. Note '
 'the tack positions and count the layers. Stripping is not demolition; it is the survey that tells you '
 'what the job actually is before you have quoted the customer a firm figure.',
 'Ripping chisel',
 'The chisel-shaped tool driven with a mallet to lever old tacks out of an upholstery frame.'),

'the-toolkit': (
 'What tools do you need to start upholstery?',
 'A beginner needs surprisingly little: a tack hammer (a magnetic one saves a lot of swearing), a ripping '
 'chisel and mallet for stripping, a good pair of shears kept only for fabric, a webbing strainer, a '
 'regulator for moving stuffing about under the cover, a skewer or two, and a staple gun or a tin of 13 mm '
 'improved tacks. That is enough to strip and rebuild a drop-in dining seat, which is where everybody '
 'should start. The specialist tools \u2014 double-ended needles, spring needles, buttoning needles, hide '
 'strainers \u2014 can wait until the job in front of you actually needs one.',
 'Regulator',
 'A long steel upholstery needle used to redistribute stuffing beneath a cover without opening it.'),

'pricing-and-quoting': (
 'How much does reupholstery cost?',
 'Price the labour hours first and add materials, never the other way round. As a guide at a workshop rate '
 'of \u00a380 an hour: a drop-in dining seat is well under an hour, a stuffover dining chair two to five '
 'hours depending on whether it is a modern re-cover or a traditional rebuild, a wing-back armchair eight '
 'hours modern or around twenty traditional, and a three-seat sofa twelve to thirty-four. Add fabric, '
 'sundries and roughly 12% contingency, because nobody knows what is under the cover until it comes off. '
 'Underquoting is the apprentice\u2019s mistake, and it is very hard to undo.',
 'Bench hours',
 'The labour time a piece takes at the bench, the primary basis for pricing an upholstery job.'),

'frame-repair-and-joint-reinforcement': (
 'How do you repair a chair frame?',
 'A loose frame must be repaired before any upholstery goes on it, because upholstery cannot hold a chair '
 'together. Knock the loose joints apart rather than gluing over the old work, clean every trace of dried '
 'glue from both faces, then re-glue with PVA and cramp until set \u2014 a joint glued over old glue will '
 'fail again within a year. Corner blocks are screwed and glued, not nailed. Broken rails are best replaced '
 'in matching timber; splits can be glued and dowelled if the grain runs right. Woodworm needs treating and '
 'assessing for structural loss before anything else happens.',
 'Corner block',
 'A triangular timber block glued and screwed into a chair frame corner to stiffen the joint.'),

'knots-and-stitches': (
 'What knots does an upholsterer need?',
 'Four will carry you through almost any job. The slip knot starts every run of twine and lets you set '
 'tension before locking it. The half hitch locks that tension off and is the workhorse of spring lashing '
 'and stitching. The lock stitch spaces a row of stitches evenly and stops each one loosening the last, '
 'which is what holds a stitched edge together. And the tailor\u2019s or bow knot ties off a button so it '
 'can be released later without cutting the cover. Learn them with twine in hand rather than from a '
 'diagram; the tension is half the knot.',
 'Slip knot',
 'The adjustable starting knot used to set tension in upholstery twine before locking it with a half hitch.'),

'loose-covers': (
 'What is a loose cover?',
 'A loose cover is a removable fitted cover made to the shape of a piece rather than tacked onto it \u2014 '
 'what the Americans call a slipcover. It is cut and pinned directly on the furniture, usually inside out, '
 'so the cover takes the exact shape of the piece, then seamed with piping at the joins and finished with '
 'a zip or ties. Allow generously for shrinkage if the cloth will be washed, and pre-wash cotton and linen '
 'before cutting. A good loose cover reads almost like upholstery; a poor one looks like a bedsheet, and '
 'the difference is entirely in the fitting.',
 'Loose cover',
 'A removable fitted furniture cover cut and pinned to shape rather than tacked to the frame; a slipcover.'),

'trimming-and-finishing': (
 'How is upholstery finished at the edges?',
 'The finish is what hides the tacks and the raw edge where the cover meets the frame, and it is the first '
 'thing anyone looks at. Options in rough order of formality: braid or gimp glued along the tack line, '
 'decorative nails driven at even spacing or run in a strip, double piping, or a close-nailed row on show '
 'wood. Bottom cloth goes on the underside last to keep dust out and to signal a finished job. Whichever '
 'you choose, the line must be dead straight and the spacing even \u2014 an uneven nail run is visible '
 'across a room and undoes good work beneath it.',
 'Gimp',
 'Narrow decorative braid glued over the tack line where an upholstery cover meets show wood.'),

'the-anatomy-of-an-upholstered-piece': (
 'What are the layers of an upholstered chair?',
 'A traditionally upholstered seat is built up in order and stripped down in reverse: frame, webbing, '
 'springs, hessian over the springs, first stuffing of hair or fibre, scrim with its stitched edge, second '
 'stuffing, calico, wadding, then the top cover and its trimming. A modern piece compresses the middle of '
 'that list into foam on rubber webbing or a sprung unit, with a wadding wrap under the cover. Knowing the '
 'order is the whole of diagnosis: when a chair sags, dips or goes lumpy, the symptom tells you which layer '
 'has failed before you have taken a single tack out.',
 'Second stuffing',
 'The softer layer of stuffing laid over the scrim and stitched edge to give the final surface its shape.'),
}


def defined_term(slug, term, definition, question):
    url = 'https://www.learntoupholster.com/' + slug
    return (
'<script type="application/ld+json">\n'
'{"@context":"https://schema.org","@type":"DefinedTerm",'
'"@id":"%s#term","name":"%s","description":"%s","url":"%s",'
'"inDefinedTermSet":{"@type":"DefinedTermSet","name":"Upholstery Glossary",'
'"url":"https://www.learntoupholster.com/a-z-glossary"},'
'"subjectOf":{"@type":"Question","name":"%s",'
'"acceptedAnswer":{"@type":"Answer","url":"%s#answer"}}}\n'
'</script>' % (url, esc(term), esc(definition), url, esc(question), url))


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def block_html(question, answer):
    return (
'\n  <div class="ltu-answer" id="answer">\n'
'    <h2>%s</h2>\n'
'    <p>%s</p>\n'
'  </div>\n' % (html.escape(question), html.escape(answer)))


def find_file(slug):
    for cand in (slug + '.html', os.path.join(slug, 'index.html')):
        if os.path.exists(cand):
            return cand
    return None


def main():
    if not os.path.isdir('functions') and not os.path.exists('index.html'):
        sys.exit('Run this from ~/learntoupholster.')

    added, skipped, missing = [], [], []
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    # Backups live outside the project. A .backup file left in the site root
    # would be published by `wrangler pages deploy .` and could get indexed.
    bdir = os.path.join(os.path.expanduser('~'), 'ltu-backups', stamp)

    for slug, (q, a, term, definition) in BLOCKS.items():
        path = find_file(slug)
        if not path:
            missing.append(slug)
            continue
        src = open(path, encoding='utf-8').read()
        if MARK in src or 'class="ltu-answer"' in src:
            skipped.append(slug)
            continue

        m = re.search(r'<article class="article wrap read">', src)
        if not m:
            missing.append(slug + ' (no article tag)')
            continue

        new = src[:m.end()] + block_html(q, a) + src[m.end():]

        # DefinedTerm schema just before </head>
        schema = defined_term(slug, term, definition, q)
        hi = new.lower().rfind('</head>')
        if hi != -1:
            new = new[:hi] + '<!-- %s -->\n' % MARK + schema + '\n' + new[hi:]

        os.makedirs(bdir, exist_ok=True)
        shutil.copy2(path, os.path.join(bdir, os.path.basename(path)))
        open(path, 'w', encoding='utf-8').write(new)
        added.append(slug)

    # Styling: prefer styles.css so it flows everywhere through build-inline.py
    css_note = ''
    if os.path.exists('styles.css'):
        css = open('styles.css', encoding='utf-8').read()
        if '.ltu-answer' not in css:
            os.makedirs(bdir, exist_ok=True)
            shutil.copy2('styles.css', os.path.join(bdir, 'styles.css'))
            open('styles.css', 'a', encoding='utf-8').write('\n' + CSS)
            css_note = 'styles.css: answer-block CSS appended'
        else:
            css_note = 'styles.css: already has the CSS'
    else:
        css_note = 'styles.css not found \u2014 add the CSS from the top of this script by hand'

    print('Answer blocks added to %d chapters:' % len(added))
    for s in added:
        print('   + ' + s)
    if skipped:
        print('Already had one (left alone): ' + ', '.join(skipped))
    if missing:
        print('Could not find: ' + ', '.join(missing))
    print(css_note)
    if added:
        print('\nBackups: ~/ltu-backups/%s/' % stamp)


if __name__ == '__main__':
    main()
