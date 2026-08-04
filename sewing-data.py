#!/usr/bin/env python3
"""
sewing-data.py — thread and needle reference.

Every number here is corroborated across at least two independent trade sources,
listed per page. Where the trade itself disagrees, the page says so rather than
picking a side quietly.

Researched 2 August 2026.

Note on the needle ranges: the two most-cited published charts disagree by about
one size step — The Thread Exchange runs finer, Techsew coarser. The ranges
here are the union of both, with `common` giving the size most people actually
reach for. That is more honest than picking a side, and the page says so.

Not every metric size is stocked everywhere. Walking foot packs are frequently
sold as Singer sizes 18, 20, 21, 23, 24 — metric 110, 125, 130, 160, 180 —
so 140/22 and 200/25 can be harder to find than a chart implies.

Old note on the needle table: published thread-maker charts give a *range* per thread
size, not a single needle. Ranges are used here. Anyone quoting one needle per
thread is simplifying, and at the coarse end the simplification goes wrong \u2014
Tex 270 is commonly listed as 180/24 to 220/26, so a 160/23 is too fine and the
thread will chafe in the eye.
"""

CHECKED = '2026-08-02'

# ---------------------------------------------------------------- thread sizes
# Commercial size, Tex, US government size, needle range, and what it is for.
THREAD_SIZES = [
    dict(commercial='#33',  tex='T35',  govt='A',  ticket='Tkt 80',  needle='80/12 \u2013 90/14',   common='90/14',
         use='Very light work, linings, fine detail. Rare in upholstery.'),
    dict(commercial='#46',  tex='T45',  govt='B',  ticket='Tkt 70',  needle='90/14 \u2013 100/16',  common='100/16',
         use='Light upholstery, thin leather, cushion interiors, delicate work.'),
    dict(commercial='#69',  tex='T70',  govt='E',  ticket='Tkt 40',  needle='100/16 \u2013 130/21',  common='110/18',
         use='The standard upholstery thread. Sofas, chairs, most seams. The '
             'heaviest most domestic machines will manage.'),
    dict(commercial='#92',  tex='T90',  govt='F',  ticket='Tkt 36',  needle='110/18 \u2013 140/22',  common='110/18 or 125/20',
         use='Automotive and vehicle trim, vinyl seating, heavier furniture. '
             'Needs an industrial machine.'),
    dict(commercial='#138', tex='T135', govt='FF', ticket='Tkt 20',  needle='125/20 \u2013 180/24',  common='130/21 or 140/22',
         use='Visible top stitching, leather, decorative seams where the stitch '
             'is meant to be seen.'),
    dict(commercial='#207', tex='T210', govt='3-cord', ticket='Tkt 15', needle='140/22 \u2013 200/25',  common='160/23',
         use='Heavy leather, bold contrast stitching, hard-use seating.'),
    dict(commercial='#277', tex='T270', govt='4-cord', ticket='Tkt 10', needle='180/24 \u2013 230/26',  common='180/24 or 200/25',
         use='Saddlery, very heavy leather, deliberate feature stitching.'),
    dict(commercial='#346', tex='T350', govt='5-cord', ticket='Tkt 8',  needle='220/26 \u2013 250/27',  common='230/26',
         use='Harness work. Beyond most upholstery machines.'),
]

# ---------------------------------------------------------------- which thread
CHOICES = [
    dict(job='Sofas and armchairs', thread='Bonded nylon or polyester', size='T70',
         why='The everyday upholstery size. Strong enough for any domestic seam '
             'without the stitch becoming a feature.'),
    dict(job='Dining chairs, cushions, light work', thread='Bonded nylon or polyester',
         size='T45 \u2013 T70',
         why='T45 where the seam is short and the cloth light; T70 if in doubt.'),
    dict(job='Car and van seats', thread='Bonded nylon', size='T70 \u2013 T90',
         why='Around the sizes vehicle manufacturers use \u2014 strong, and the stitch '
             'stays discreet. Nylon\u2019s abrasion resistance suits a seat that is '
             'slid across daily.'),
    dict(job='Decorative top stitching on leather', thread='Bonded nylon or polyester',
         size='T135', why='Bold enough to read as a deliberate line rather than a seam.'),
    dict(job='Vinyl seating', thread='Bonded polyester', size='T90',
         why='Vinyl is usually a hard-use or wipe-clean situation. Polyester copes '
             'better with light and cleaning products.'),
    dict(job='Leather furniture', thread='Bonded nylon or polyester', size='T90',
         why='T135 where you want the stitching seen.'),
    dict(job='Marine and boat upholstery', thread='Bonded polyester', size='T90 \u2013 T135',
         why='<strong>Polyester, always.</strong> Sunlight is the thing that kills a '
             'marine seam, and nylon degrades in UV faster than polyester.'),
    dict(job='Motorcycle seats', thread='Bonded polyester', size='T90 \u2013 T135',
         why='Outdoors and uncovered most of its life. Same reasoning as marine.'),
    dict(job='Garden and outdoor furniture', thread='Bonded polyester', size='T70 \u2013 T90',
         why='Polyester for the UV. This is the one choice people get wrong most often.'),
    dict(job='Campervan interiors', thread='Bonded polyester', size='T70 \u2013 T90',
         why='Behind glass, in the sun, for years. A van interior gets far more '
             'light than a sofa in a front room.'),
    dict(job='Caravan and holiday-home seating', thread='Bonded polyester', size='T70',
         why='Hard use, strong light, and cleaned often.'),
]

# ---------------------------------------------------------------- nylon vs poly
FIBRES = [
    dict(name='Bonded nylon', best='Indoor work, vehicle interiors, leather',
         pros=['Highest tensile strength for its size',
               'Excellent abrasion resistance \u2014 suits seams that get slid across',
               'More elastic, so it gives rather than snapping under a sudden load',
               'Widest colour range in most suppliers\u2019 stock'],
         cons=['Degrades faster in ultraviolet light',
               'Absorbs a little moisture, which matters in damp conditions']),
    dict(name='Bonded polyester', best='Anything that sees sunlight',
         pros=['Far better UV resistance \u2014 the deciding property outdoors',
               'Low moisture absorption',
               'Resists most cleaning chemicals well',
               'Nearly as strong as nylon at the same size'],
         cons=['Slightly less abrasion resistant than nylon',
               'Slightly less elastic']),
]

# ---------------------------------------------------------------- sources
# No longer printed on the pages. Thread and needle sizing is standardised
# engineering fact rather than jurisdiction-specific law, so the citation
# apparatus the fire pages need is clutter here. Kept because these are what
# the figures were verified against, and worth having if anything is queried.
SOURCES_NEEDLE = [
    ('Schmetz \u2014 needle size designations (NM system)',
     'https://www.schmetzneedles.com/pages/needle-size-designations'),
    ('The Thread Exchange \u2014 thread to needle size chart',
     'https://www.thethreadexchange.com/miva/merchant.mvc?Screen=CTGY&Category_Code=needle-size-chart'),
    ('The Thread Exchange \u2014 needle buying guide and system equivalents',
     'https://www.thethreadexchange.com/miva/merchant.mvc?Screen=CTGY&Category_Code=needle-information'),
    ('Service Thread \u2014 how to interpret needle size',
     'https://www.servicethread.com/blog/how-to-interpret-needle-size'),
]

SOURCES_THREAD = [
    ('The Thread Exchange \u2014 thread sizes and needle chart',
     'https://www.thethreadexchange.com/miva/merchant.mvc?Screen=CTGY&Category_Code=needle-size-chart'),
    ('Superior Threads \u2014 bonded thread diameter guide',
     'https://www.superiorthreads.com/education/bonded-thread-diameter-guide'),
    ('Superior Threads \u2014 thread twist explained',
     'https://www.superiorthreads.com/education/thread-twist-explained'),
    ('Service Thread \u2014 left twist vs right twist industrial thread',
     'https://www.servicethread.com/blog/left-twist-vs.-right-twist-industrial-sewing-thread-differences-and-applications'),
    ('Trivantage \u2014 thread guide',
     'https://www.trivantage.com/thread-guide'),
    ('G\u00fctermann \u2014 textile unit calculator and numbering systems',
     'https://industry.guetermann.com/en/service-unlimited/textile-unit-calculator'),
    ('Service Thread \u2014 ticket size against tex size for bonded thread',
     'https://www.servicethread.com/blog/what-is-the-difference-between-ticket-size-and-tex-size-for-bonded-thread'),
    ('Textile Learner \u2014 sewing thread size numbering systems',
     'https://textilelearner.net/sewing-thread-size-numbering-system/'),
]


# ---------------------------------------------------------------- selector
# Stitch length is the one figure in the selector that is not simply looked up.
# It turns on a contradiction that most guidance glosses over:
#
#   On woven fabric, more stitches make a stronger seam. A&E publish the
#   relationship as seam strength = SPI x thread breaking strength x 1.5.
#
#   On leather and vinyl, more stitches make a WEAKER one. Each hole is
#   permanent, and punching them closer together perforates the material along
#   a line until it tears like a stamp edge.
#
# So the same question has opposite answers depending on the material, which is
# exactly what a table cannot express and a selector can.
#
# SPI to millimetres is 25.4 / SPI. Cross-checked against Fine Leatherworking's
# published pairing of 12 SPI with 2.1 mm.

STITCH = {
    'woven':   dict(spi='7\u201310', mm='2.5\u20133.6 mm',
                    why='On woven cloth the thread passes between the yarns rather than '
                        'cutting them, so more stitches genuinely means a stronger seam. '
                        'A&amp;E give it as seam strength = stitches per inch \u00d7 thread '
                        'strength \u00d7 1.5. Go to the finer end on lighter cloth and the '
                        'longer end on heavy chenilles and weaves.'),
    'vinyl':   dict(spi='6\u20138', mm='3.2\u20134.2 mm',
                    why='Every stitch is a permanent hole. Crowding them perforates the '
                        'vinyl along a line and the seam tears like a stamp edge. Longer '
                        'stitches, fewer holes, stronger seam \u2014 the opposite of cloth.'),
    'leather': dict(spi='6\u20137', mm='3.6\u20134.2 mm',
                    why='Same reasoning as vinyl and more so. Leather is strong until you '
                        'perforate it, and its strength falls away quickly as the holes get '
                        'closer. Resist the urge to go finer for neatness.'),
}

POINT = {
    'woven':   ('Round point (R)',
                'Pushes between the yarns without cutting them. A leather point here would '
                'sever the weave along the whole seam and weaken it.'),
    'vinyl':   ('Round point (R)',
                'Vinyl feels like leather but is usually backed with a woven scrim, and a '
                'cutting point severs that backing. Groz-Beckert list their R point as '
                'suiting coated fabrics for this reason. Test on an offcut.'),
    'leather': ('Leather point (LR)',
                'A cutting point that slices a small clean incision rather than punching a '
                'hole. LR is the general-purpose grind and lays the stitches at a slight '
                'angle to the seam.'),
}


# A visible top stitch is specified differently from a seam that only has to
# hold. Heavier thread needs more room between stitches or the line crowds and
# looks muddled, and the whole point is that the individual stitches read.
STITCH_TOPSTITCH = dict(
    spi='6\u20137', mm='3.6\u20134.2 mm',
    why='Longer than a construction seam, for two reasons. The heavier thread needs room '
        'or the stitches crowd into a line you cannot read, and a decorative stitch is '
        'meant to be seen individually. On leather and vinyl it has the same advantage as '
        'always \u2014 fewer holes.')


# ---------------------------------------------------------------- machines
# Feed mechanisms, in order of how much of the work they do for you.
#
# The terminology is genuinely muddled in the trade and the sources contradict
# each other. One supplier calls unison feed "also known as walking foot feed";
# another says needle feed "is more appropriately termed compound"; a third
# lists compound, needle and triple feed as synonyms for one thing. They are
# not synonyms.
#
# There is a clean test, and the page gives it: does the needle move forward
# with the material? If it does, the machine is compound feed. If only the top
# foot walks, it is a walking foot machine and nothing more.

FEEDS = [
    dict(name='Drop feed', also='Regular feed',
         how='Feed dogs under the material do all the work, moving it while the needle is '
             'out of the fabric. The presser foot only holds down.',
         good='Single layers of cloth. Every domestic machine and the lighter industrials.',
         bad='Anything thick, layered, or slippery. The top layer creeps and you finish a '
             'long seam with the two pieces out of register \u2014 the classic result of '
             'sewing upholstery on the wrong machine.',
         verdict='not upholstery'),
    dict(name='Needle feed', also='',
         how='The needle moves with the feed dogs rather than straight up and down, so it '
             'carries the material forward while it is still through it.',
         good='Thicker seams than drop feed will manage. Keeps layers in register better.',
         bad='Still nothing gripping the top surface, so slippery materials can drift.',
         verdict='better'),
    dict(name='Walking foot', also='Top feed',
         how='An alternating pair of feet. The outer foot holds while the inner foot lifts, '
             'moves forward, drops and grips \u2014 so the top of the material is driven as '
             'well as the bottom.',
         good='Vinyl, coated cloth, single-layer leather, most upholstery panels. Stops the '
              'top layer drifting.',
         bad='The needle still does not move with the material, so heavy multi-layer '
             'assemblies can shift at the point where you turn a corner.',
         verdict='good'),
    dict(name='Compound feed', also='Unison feed \u00b7 triple feed \u00b7 compound walking foot',
         how='Feed dogs, inner foot and <strong>needle</strong> all move together while the '
             'outer foot holds. Three things driving the material in step instead of one.',
         good='This is the upholstery machine. Thick multi-layer work, leather, heavy '
              'weaves, anything where the layers must stay in register through a curve.',
         bad='Poor on very light cloth \u2014 the feed can mark delicate material. Less '
             'forgiving to set up than a drop feed, and it takes practice to get the '
             'settings right for a new material.',
         verdict='what you want'),
]

BEDS = [
    dict(name='Flat bed',
         what='The familiar shape: a flat table with the needle in the middle.',
         good='Long straight seams over big panels. Everything flat, which in upholstery is '
              'most things. The workhorse, and the machine to buy first.',
         bad='Useless on anything tubular or three-dimensional. You cannot get inside a '
             'finished cushion cover or round a headrest.'),
    dict(name='Cylinder arm',
         what='The bed is a narrow horizontal cylinder rather than a table, so work can be '
              'fed round it.',
         good='Tubular and three-dimensional work \u2014 headrests, bolsters, finished '
              'covers, awkward corners a flat bed cannot reach.',
         bad='Long flat seams are harder to keep straight with no table to rest on. '
             'Flat-bed attachments exist to convert one, which is worth knowing before you '
             'buy two machines.'),
    dict(name='Post bed',
         what='The needle sits on top of a raised vertical post.',
         good='Visibility and control on small, detailed, three-dimensional pieces. '
              'Precision top stitching where you need to see exactly where the needle lands.',
         bad='A specialist. Very few upholstery jobs actually need one.'),
    dict(name='Long arm',
         what='A flat bed stretched \u2014 more room to the right of the needle.',
         good='Large panels, awnings, tarpaulins, marine covers. Anything where the bulk of '
              'the work has to pass through the throat.',
         bad='Takes up a great deal of bench. Only worth it if you regularly handle pieces '
             'big enough to fight a standard machine.'),
]


# ---------------------------------------------------------------- troubleshooting
# Ordered so the cheap checks come first. A machine shop's own account is that
# most machines brought in for skipped stitches sew perfectly once a new needle
# is fitted \u2014 a slightly bent needle throws the needle-to-hook clearance out,
# and it is invisible to the eye.
#
# Bernina's own guidance: remember TNT \u2014 Threading, Needle, Tension \u2014
# because roughly four times out of five the fault is not the machine.

TROUBLE = [
    dict(
        symptom='Skipped stitches',
        what='For a stitch to form, the hook has to pass through the loop of thread that '
             'appears at the needle eye as the needle rises a few millimetres off its lowest '
             'point. Miss that loop and you get a gap. Everything below is a reason the hook '
             'and the loop failed to meet.',
        checks=[
            ('Change the needle. First, always.',
             'A needle bends long before it looks bent, and a bend of a fraction of a '
             'millimetre moves the needle out of the hook\u2019s path. Machine shops report '
             'that a great many machines brought in for skipped stitches sew perfectly on a '
             'new needle. Ignore the hour-counts you see quoted \u2014 those come from '
             'garment production, where the machine runs all day on fine cloth. Change it when '
             'the work tells you to: skipped stitches, a change in the sound, snagged or pulled '
             'threads in the face, or straight after the needle has met a tack, a staple or the '
             'plate. And put a fresh one in before a job you cannot afford to mark.'),
            ('Check the needle is in the right way round and fully home',
             'Pushed up short, or turned a few degrees, and the clearance goes. Worth ten '
             'seconds before anything else.'),
            ('Check the needle size against the thread',
             'Too large a needle with too fine a thread makes a loop too small for the hook '
             'to catch. There is a neat test for this: thread the needle, hold the thread at '
             'about 45 degrees and let the needle hang on it. A correctly matched needle '
             'slides down the thread under its own weight.'),
            ('Rethread the machine completely',
             'With the presser foot <em>up</em>, so the tension discs are open. Threading '
             'with the foot down leaves the thread sitting outside the discs and no amount '
             'of adjustment will fix it.'),
            ('Check the material is being held down',
             'If the cloth lifts with the needle \u2014 flagging \u2014 the loop never forms '
             'properly. On an industrial machine, check the inner presser foot is holding '
             'firmly on the needle\u2019s downward stroke.'),
            ('Check the throat plate',
             'The hole should be only slightly larger than the needle and thread together. '
             'An oversized or worn hole lets the material push down into it. Check it is '
             'not warped while you are there.'),
            ('Only then suspect timing',
             'If the hook passes below or too far above the needle eye it will miss the loop '
             'regardless. Timing genuinely does drift, and a hook tip that has been sharpened '
             'more than once or twice will have moved it. That is a job for someone with the '
             'tools.'),
        ]),
    dict(
        symptom='Thread breaking or shredding',
        what='Usually friction somewhere in the thread path, or a mismatch between thread and '
             'needle. The thread is telling you where it is being chafed.',
        checks=[
            ('Needle too fine for the thread',
             'The commonest cause. The thread has to pass through the eye twice on every '
             'stitch \u2014 down and back \u2014 and a tight eye files it away. Go up a needle '
             'size within the range for that thread.'),
            ('Burr on the needle, hook, throat plate or thread guides',
             'Run a finger over the thread path. A burr you can barely feel will shred thread '
             'at speed. The needle plate hole and the hook tip are the usual places.'),
            ('Top tension too tight',
             'Back it off and work up again rather than down from tight.'),
            ('Wrong twist',
             'Machine thread needs a final <strong>Z twist</strong>. S twist untwists as it '
             'runs through the machine and frays for no other reason. See the '
             '<a href="/sewing-thread">thread guide</a>.'),
            ('Unbonded thread',
             'At upholstery speeds unbonded thread of the same size will fluff and snarl. '
             'Bonded is not a luxury here.'),
            ('Thread coming off the cone badly',
             'It should feed straight up off the cone through the stand, not be dragged '
             'sideways. A cone sitting where the spool pin should be will twist the thread as '
             'it unwinds.'),
        ]),
    dict(
        symptom='A nest of thread under the fabric at the start of a seam',
        what='Almost never a tension fault, though it looks like one.',
        checks=[
            ('Hold both thread tails behind the foot as you start',
             'At the first stitch there is nothing holding the threads, so the fabric gets '
             'pushed down into the needle plate hole and the thread piles up underneath. '
             'Holding both tails for the first three or four stitches fixes it outright.'),
            ('Start a few millimetres in, then reverse back',
             'Rather than starting hard on the edge, where there is least to grip.'),
            ('Check the upper thread is actually in the tension discs',
             'If it looks like a nest every single time from the first stitch, this is why. '
             'Rethread with the presser foot up.'),
        ]),
    dict(
        symptom='Puckered seams',
        what='The two layers are arriving at the needle at different rates, or the thread is '
             'pulling the seam up after it is sewn.',
        checks=[
            ('Top tension too tight',
             'The most likely cause on a straight seam. The thread is drawing the seam in '
             'after it is stitched.'),
            ('Drop feed on a job that needs compound feed',
             'If only the underside is being driven, the top layer creeps and gathers. This '
             'is the classic sign of upholstery being sewn on the wrong machine \u2014 see '
             '<a href="/sewing-machines">machines</a>.'),
            ('Blunt needle',
             'A blunt point pushes the material down and forward rather than piercing it '
             'cleanly, and that displacement shows up as pucker.'),
            ('Stitch too short for the cloth',
             'Crowding stitches into a heavy weave gathers it. Lengthen and try again.'),
        ]),
    dict(
        symptom='Uneven or loose stitches on one side',
        what='Loops on the underside mean the top tension is losing; loops on top mean the '
             'bobbin is. The loose side is the side that is failing.',
        checks=[
            ('Rethread the top with the presser foot up',
             'Before touching a single dial. Thread outside the tension discs produces exactly '
             'this and is the most common cause by a distance.'),
            ('Check the bobbin case for lint',
             'Under the tension spring in the bobbin case is where lint collects, and a small '
             'amount changes the tension noticeably. Brush it out \u2014 never blow compressed '
             'air into a machine, it drives lint further in.'),
            ('Check the bobbin is wound evenly',
             'A bobbin wound loose or lumpy will not pay off at a steady rate however the '
             'tension is set.'),
            ('Adjust the top tension, not the bobbin',
             'The bobbin tension is set and rarely wants moving. Almost every tension problem '
             'is solved on top.'),
        ]),
    dict(
        symptom='Material not feeding evenly',
        what='Something is holding one surface back, or the feed is not gripping it.',
        checks=[
            ('Vinyl or coated cloth sticking to the foot',
             'A steel foot drags on a vinyl face. A roller foot or a Teflon foot solves it, '
             'and it is worth owning one before you need it.'),
            ('Feed dogs clogged or worn',
             'Lint packs between the teeth and they stop gripping. Worn teeth on an old '
             'machine do the same.'),
            ('Presser foot pressure wrong',
             'Too little and the material floats; too much and it drags. Adjust in small '
             'steps and test on an offcut.'),
            ('Wrong feed type for the work',
             'Layered or slippery assemblies need compound feed. No adjustment will make a '
             'drop feed machine handle them.'),
        ]),
]


# ---------------------------------------------------------------- setup & parts
MOTORS = [
    dict(name='Clutch motor',
         how='The motor runs continuously at full speed whenever the machine is switched on. '
             'The pedal engages a clutch that connects it to the machine.',
         pros=['Robust, and they last',
               'Plenty of power for long continuous seams',
               'What most older industrial machines came with'],
         cons=['Speed control means slipping the clutch, and the usable range is narrow',
               'Genuinely hard to learn \u2014 the machine tends to take off',
               'Draws its full rated power whenever it is switched on, needle moving or not',
               'Hums constantly and gets warm',
               'Heavy, and some want three-phase or 220V'],
         verdict='what came with it'),
    dict(name='Servo motor',
         how='The motor only turns when you press the pedal, and its speed follows how far '
             'you press. Most have a dial to cap the top speed.',
         pros=['Fine control at low speed, which is what upholstery actually needs',
               'Silent when you are not sewing',
               'Uses power only while driving, so no heat and no hum',
               'Much lighter, and usually runs on ordinary single-phase mains',
               'You can set a top speed and simply not exceed it while learning'],
         cons=['Some lose torque at very low speed \u2014 the point at which a speed reducer '
               'starts to matter',
               'Cheaper analogue ones are less precise than digital'],
         verdict='fit one'),
]

FEET = [
    dict(name='Standard set', use='Everyday seams.',
         note='On a walking foot machine, feet come as <strong>sets</strong> \u2014 an inner '
              'and an outer that work together. You cannot swap one alone.'),
    dict(name='Welting or piping foot', use='Running piping, and sewing it in.',
         note='Sold in sizes matched to the cord: 1/8, 5/32, 3/16, 1/4, 5/16 and 3/8 inch are '
              'the usual set. The groove has to suit the cord or the stitching will not sit '
              'tight against it.'),
    dict(name='Zipper foot', use='Zips, and anything you must stitch close up against.',
         note='Comes as a single left toe or single right toe. Which you need depends on '
              'which side of the needle the obstruction is, so most people end up with both.'),
    dict(name='Roller foot', use='Leather, vinyl and coated cloth.',
         note='Rolls rather than slides, so it will not drag on a sticky face. A rubber '
              'roller also stops the foot marking soft leather, which matters more than the '
              'feeding on a show surface.'),
    dict(name='Teflon or non-stick foot', use='Vinyl, PVC, laminated cloth.',
         note='Cheaper answer to the same problem as a roller foot: a steel foot grips vinyl '
              'and stalls it, a non-stick face slides over it.'),
    dict(name='Feet with teeth, or smooth', use='A choice, not a type.',
         note='Toothed feet grip and feed better through thick assemblies. Smooth feet do '
              'not mark. On anything where the face will be seen \u2014 leather especially '
              '\u2014 smooth is worth the poorer grip.'),
    dict(name='Edge guide', use='Consistent seam allowance.',
         note='Either a foot with a guide built in, or a bar that bolts to the bed. Cheap, '
              'and it does more for the look of a seam than most things costing more.'),
]
