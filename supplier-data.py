#!/usr/bin/env python3
"""
supplier-data.py — the verified supplier list.

Every entry below was found by search and then checked by fetching the site.
`verified` is the date the website was confirmed live and trading-looking. It is
not a statement that the company is solvent — no one can check that from outside
— and the directory page says so plainly.

`status` values:
    live      site fetched and read
    blocked   site is up but refuses automated requests (403 or a bot check).
              That is evidence of an actively managed site, NOT a dead one.
              The re-checker must never delete these.

To add a supplier: append to SUPPLIERS, run check-suppliers.py to verify it,
then build-suppliers.py. Keep the list alphabetical within country.

Categories, kept short so the filter stays usable:
    traditional  jute webbing, hair, scrim, twine, coil springs, tacks
    foam         foam, cut-to-size, wadding, fibre
    fabric       upholstery cloth, vinyl, leather
    tools        hand tools, staple guns, machines
    sundries     zips, threads, adhesives, trim, nails, legs
    auto         automotive, marine and campervan materials
    fabrichouse  the fabric brands and mills themselves, as opposed to shops

Entries carry `kind`:

    supplier    sells materials — the default, and what the directory is for
    specialist  does not sell materials, but does museum-standard conservation
                work and takes commissions. Listed separately and only where the
                institutional work can be verified from public record.

Entries may carry `disclosure`. Anything the author has a commercial interest in
must have one, and the page prints it prominently. A directory presenting itself
as independent has to say when a listing is its own.
"""

VERIFIED = '2026-08-01'

SUPPLIERS = [
    # ---------------- United Kingdom ----------------
    dict(country='GB', name='Advanced Upholstery',
         url='https://www.advancedupholstery.co.uk/',
         cats=['traditional', 'foam', 'fabric', 'tools', 'sundries'],
         note='Thousands of lines for trade and hobbyist. Free UK delivery over a threshold. East Lothian.',
         status='live'),
    dict(country='GB', name='Foam4U',
         url='https://foam4u.co.uk/',
         cats=['foam', 'traditional', 'sundries'],
         note='Full spring range including double cone, zigzag and Parker Knoll tension springs, plus jute, Pirelli and elasticated webbing.',
         status='live'),
    dict(country='GB', name='J A Milton Upholstery Supplies',
         url='https://www.jamiltonupholstery.co.uk/',
         cats=['traditional', 'foam', 'fabric', 'tools', 'sundries'],
         note='Long-established general supplier. Useful product notes on webbing weights.',
         status='live'),
    dict(country='GB', name='Livedale',
         url='https://livedale.co.uk/',
         cats=['traditional', 'sundries'],
         note='Jute webbing in several weights and widths, springs and narrow fabrics.',
         status='blocked'),
    dict(country='GB', name='The Millshop Online',
         url='https://www.the-millshop-online.co.uk/',
         cats=['fabric', 'traditional'],
         note='Fabric warehouse in Northamptonshire; upholstery and curtain cloth plus supplies.',
         status='live'),
    dict(country='GB', name='The Upholstery Shop',
         url='https://www.upholsteryshop.co.uk/',
         cats=['traditional', 'foam', 'fabric', 'tools', 'sundries'],
         note='Webbing, springs, rubberised hair, contract vinyls and tools. Sells by the metre in single lengths.',
         status='live'),
    dict(country='GB', name='Upholstery Supplier',
         url='https://upholsterysupplier.co.uk/',
         cats=['traditional', 'foam', 'fabric', 'tools', 'sundries'],
         note='Falkirk, Scotland. Trade accounts available. Stocks Ross, Moon, William Clark and J Brown fabrics.',
         status='live'),
    dict(country='GB', name='Upholstery Warehouse',
         url='https://upholsterywarehouse.co.uk/',
         cats=['traditional', 'foam', 'fabric', 'tools', 'sundries'],
         note='Large general range for upholstery and soft furnishings. Also runs courses.',
         status='live'),

    # ---------------- United States ----------------
    dict(country='US', name='Alan Richard Textiles',
         url='https://alanrichardtextiles.com/',
         cats=['fabric', 'tools', 'sundries', 'traditional'],
         note='C.S. Osborne tools, Conso trimmings, jute and elastic webbing. Tier pricing on many lines.',
         status='live'),
    dict(country='US', name='Fabric Wholesale Direct',
         url='https://fabricwholesaledirect.com/',
         cats=['fabric', 'sundries', 'tools'],
         note='Wholesale-priced cloth plus needles, threads, webbing and shears.',
         status='live'),
    dict(country='US', name='Midwest Fabrics',
         url='https://midwestfabrics.com/',
         cats=['fabric', 'foam', 'traditional', 'tools', 'sundries'],
         note='Wholesale and retail. Cording, foam, webbing, springs, staples and high-temp adhesive.',
         status='live'),
    dict(country='US', name='Philmore Upholstery Supply',
         url='https://philmoresupply.com/',
         cats=['foam', 'fabric', 'tools', 'sundries', 'auto'],
         note='Pinellas Park, Florida. Custom-cut foam, welt cord, marine and automotive materials.',
         status='live'),
    dict(country='US', name='Rochford Supply',
         url='https://rochfordsupply.com/',
         cats=['fabric', 'foam', 'traditional', 'sundries', 'auto'],
         note='Commercial upholstery, marine and outdoor textiles. Over 50 years trading. CushionCraft foam, batting, springs and webbing.',
         status='live'),
    dict(country='US', name='Upholster.com',
         url='https://store.upholster.com/',
         cats=['tools', 'traditional', 'foam', 'auto'],
         note='C.S. Osborne tools, walking foot machines, foam cutters. Ships internationally.',
         status='blocked'),
    dict(country='US', name='Upholstery Connection',
         url='https://www.upholsteryconnection.com/',
         cats=['traditional', 'tools', 'sundries'],
         note='Jute burlap, spring twine, edge roll, skewers and stripping tools. Strong on traditional consumables.',
         status='live'),
    dict(country='US', name='Upholstery Supplies of America',
         url='https://upholsterysupplyshop.com/',
         cats=['foam', 'fabric', 'sundries'],
         note='Wholesale supplier in the Southeast. Vinyl, foam, pillows and adhesives.',
         status='live'),
    dict(country='US', name='Upholstery Supply Online',
         url='https://www.upholsterysupplyonline.com/',
         cats=['auto', 'fabric', 'tools', 'sundries'],
         note='Strong automotive range — landau tops, headliner, welt cord, hog rings, button machines.',
         status='live'),
    dict(country='US', name='V&V Upholstery Supplies',
         url='https://vvupholsterysupply.com/',
         cats=['foam', 'fabric', 'auto', 'sundries'],
         note='Hollywood, Florida. Furniture, marine and automotive. Sunbrella, UV-rated threads, heat-resistant adhesives.',
         status='live'),

    # ---------------- Australia ----------------
    dict(country='AU', name='ACT Foam & Rubber',
         url='https://www.actfoam.com.au/',
         cats=['foam', 'traditional', 'sundries', 'auto'],
         note='Trade and retail. Springs, webbing and marine supplies.',
         status='live'),
    dict(country='AU', name='Holdfast Components',
         url='https://holdfastcomponents.com.au/',
         cats=['foam', 'sundries', 'traditional'],
         note='Components supplier: webbings and narrow tapes, spring pads, threads, zips, staples.',
         status='live'),
    dict(country='AU', name='Home Upholsterer',
         url='https://www.homeupholsterer.com.au/',
         cats=['foam', 'fabric', 'tools', 'sundries'],
         note='Chester Hill, Sydney. Foam cut to size, Australia-wide delivery, aimed at DIY as well as trade.',
         status='blocked'),
    dict(country='AU', name='Novafoam',
         url='https://novafoam.com.au/',
         cats=['foam', 'traditional', 'sundries', 'tools'],
         note='Foam, coil and zigzag springs, calico, dust covers, button moulds and twine.',
         status='live'),
    dict(country='AU', name='Oz Upholstery Supplies',
         url='https://ozupholsterysupplies.com.au/',
         cats=['foam', 'fabric', 'tools', 'sundries'],
         note='Melbourne parent company trading since 1974. Wholesale prices to trade and public, delivered Australia-wide.',
         status='live'),
    dict(country='AU', name='Sofa Rehab',
         url='https://sofarehab.com.au/',
         cats=['foam', 'traditional', 'sundries'],
         note='Seat foams, springs, webbing and lounge connectors. Flat-rate nationwide shipping. Good for small DIY orders.',
         status='live'),

    # ---------------- New Zealand ----------------
    dict(country='NZ', name='Furnco',
         url='https://www.furnco.co.nz/',
         cats=['foam', 'fabric', 'tools', 'sundries', 'traditional'],
         note='Trade, wholesale and DIY. Furniture components as well as upholstery supplies.',
         status='live'),
    dict(country='NZ', name='Reid & Twiname',
         url='https://www.retwine.co.nz/',
         cats=['foam', 'fabric', 'traditional', 'sundries'],
         note='Auckland and Christchurch. Calico, hessian, jute canvas and webbing, leathercloth, adhesives.',
         status='live'),
    dict(country='NZ', name='WT Distributors',
         url='https://webbing.co.nz/',
         cats=['traditional', 'auto', 'sundries'],
         note='NZ owned, 30+ years. Webbing and narrow fabrics for upholstery, automotive, marine and equestrian.',
         status='live'),

    # ---------------- Canada ----------------
    dict(country='CA', name='Ennis Fabrics',
         url='https://ennisfabrics.com/',
         cats=['fabric', 'foam', 'traditional', 'tools', 'sundries', 'auto'],
         note='Large distributor with foam stocked for both western and eastern Canada, plus US supply. Marine and automotive lines.',
         status='live'),
    dict(country='CA', name='Foamland',
         url='http://www.foamland.ca/',
         cats=['foam', 'traditional', 'sundries'],
         note='Hamilton, Ontario. Foam, webbing, burlap, ply grip, nail strip and basic tools.',
         status='live'),

    # ================= Fabric houses & mills =================
    # The brands rather than the shops. Most are trade-only and are ordered
    # through a local stockist or agent, so they are listed by where the house
    # is based — a good many supply worldwide.

    dict(country='GB', name='Abraham Moon & Sons', url='https://www.moons.co.uk/',
         cats=['fabrichouse', 'fabric'],
         note='Yorkshire woollen mill since 1837. Tweeds and wool upholstery cloth, still spun and woven on site.',
         status='live'),
    dict(country='GB', name='Andrew Muirhead', url='https://www.muirhead.co.uk/',
         cats=['fabrichouse', 'fabric'],
         note='Scottish leather tannery. Upholstery hides for furniture, aviation and rail.',
         status='live'),
    dict(country='GB', name='Bute Fabrics', url='https://www.butefabrics.com/',
         cats=['fabrichouse', 'fabric'],
         note='Isle of Bute mill. Wool cloth for contract and residential work.',
         status='live'),
    dict(country='GB', name='Camira', url='https://www.camirafabrics.com/',
         cats=['fabrichouse', 'fabric'],
         note='Contract and transport textiles, including wool and recycled ranges. Strong on commercial fire specification.',
         status='live'),
    dict(country='GB', name='Clarke & Clarke', url='https://www.clarke-clarke.com/',
         cats=['fabrichouse', 'fabric'],
         note='Part of Sanderson Design Group. Broad contemporary and classic ranges, widely stocked.',
         status='live'),
    dict(country='GB', name='Cristina Marrone', url='https://www.cristinamarrone.co.uk/',
         cats=['fabrichouse', 'fabric'],
         note='Textured weaves, stripes and checks. Classic and modern, useful for traditional pieces.',
         status='live'),
    dict(country='GB', name='Designers Guild', url='https://www.designersguild.com/',
         cats=['fabrichouse', 'fabric'],
         note='Colour-led designer ranges. Trade accounts available.',
         status='blocked'),
    dict(country='GB', name='Linwood', url='https://www.linwoodfabric.com/',
         cats=['fabrichouse', 'fabric'],
         note='British house with a wide upholstery and drapery range.',
         status='live'),
    dict(country='GB', name='Osborne & Little', url='https://www.osborneandlittle.com/',
         cats=['fabrichouse', 'fabric'],
         note='Long-established British designer house, sold through trade accounts.',
         status='live'),
    dict(country='GB', name='Panaz', url='https://www.panaz.com/',
         cats=['fabrichouse', 'fabric'],
         note='Contract textiles for hospitality and healthcare. Useful where crib 5 and cleanability are specified.',
         status='blocked'),
    dict(country='GB', name='Prestigious Textiles', url='https://www.prestigious.co.uk/',
         cats=['fabrichouse', 'fabric'],
         note='Large accessible range with matching wallpapers. Widely stocked by shops.',
         status='live'),
    dict(country='GB', name='Romo', url='https://www.romo.com/',
         cats=['fabrichouse', 'fabric'],
         note='Nottingham house trading since 1902, now a group including Zinc and Black Edition. Exports worldwide.',
         status='live'),
    dict(country='GB', name='Ross Fabrics', url='https://www.rossfabrics.co.uk/',
         cats=['fabrichouse', 'fabric'],
         note='Established 1933. Chenilles, flat weaves and velvets, plus AquaClean ranges. A trade staple for reupholstery.',
         status='live'),
    dict(country='GB', name='Sanderson Design Group', url='https://www.sandersondesigngroup.com/',
         cats=['fabrichouse', 'fabric'],
         note='Sanderson, Morris & Co, Zoffany, Harlequin and Scion under one group. Classic English design.',
         status='live'),
    dict(country='GB', name='Swaffer', url='https://www.swaffer.co.uk/',
         cats=['fabrichouse', 'fabric'],
         note='British house supplying upholstery and drapery cloth to the trade.',
         status='live'),
    dict(country='GB', name='Warwick Fabrics', url='https://www.warwick.co.uk/',
         cats=['fabrichouse', 'fabric'],
         note='International house supplying UK upholsterers for over thirty years. FibreGuard stain-resistant ranges.',
         status='live'),
    dict(country='GB', name='Wemyss', url='https://www.wemyssfabrics.com/',
         cats=['fabrichouse', 'fabric'],
         note='Scottish house. Rich textures and durable weaves, including FibreGuard ranges.',
         status='live'),
    dict(country='GB', name='Yarwood Leather', url='https://www.yarwoodleather.com/',
         cats=['fabrichouse', 'fabric'],
         note='Leeds-based leather supplier for commercial and residential interiors.',
         status='live'),

    dict(country='US', name='Greenhouse Fabrics', url='https://www.greenhousefabrics.com/',
         cats=['fabrichouse', 'fabric'],
         note='Large US supplier to workrooms and designers. Extensive upholstery range.',
         status='live'),
    dict(country='US', name='JF Fabrics', url='https://www.jffabrics.com/',
         cats=['fabrichouse', 'fabric'],
         note='North American house supplying upholstery and drapery cloth to the trade.',
         status='live'),
    dict(country='US', name='Kravet', url='https://www.kravet.com/',
         cats=['fabrichouse', 'fabric'],
         note='Major US trade house. Kravet, Lee Jofa, Brunschwig & Fils and GP & J Baker.',
         status='live'),
    dict(country='US', name='Pindler', url='https://www.pindler.com/',
         cats=['fabrichouse', 'fabric'],
         note='California house supplying the design trade across the US.',
         status='live'),
    dict(country='US', name='Sunbrella', url='https://www.sunbrella.com/',
         cats=['fabrichouse', 'fabric', 'auto'],
         note='Solution-dyed acrylic for outdoor, marine and heavy-use indoor work. The default for anything facing weather.',
         status='live'),

    dict(country='AU', name='Charles Parsons', url='https://www.charlesparsons.com/',
         cats=['fabrichouse', 'fabric'],
         note='Australian textile group supplying upholstery and commercial interiors.',
         status='live'),
    dict(country='AU', name='Instyle', url='https://instyle.com.au/',
         cats=['fabrichouse', 'fabric'],
         note='Australian house focused on commercial and contract textiles, with an environmental emphasis.',
         status='live'),
    dict(country='AU', name='Mokum Textiles', url='https://www.mokumtextiles.com/',
         cats=['fabrichouse', 'fabric'],
         note='Australian designer house, part of the James Dunlop group. Sold through trade accounts.',
         status='live'),
    dict(country='AU', name='Zepel Fabrics', url='https://www.zepelfabrics.com/',
         cats=['fabrichouse', 'fabric'],
         note='Australian house with a broad upholstery and drapery range.',
         status='live'),

    dict(country='CA', name='Telio', url='https://www.telio.com/',
         cats=['fabrichouse', 'fabric'],
         note='Montreal textile wholesaler. Broad fabric range including furnishing cloth.',
         status='live'),

    # ================= Disclosed interest =================
    dict(country='GB', name='Bodella', url='https://bodella.co.uk/',
         cats=['fabric'],
         note='Upholstery fabric shop selling by the metre, with samples available.',
         disclosure='Run by Shaun Greenwood, who writes this site. Listed for completeness '
                    'rather than as a recommendation over anything else here.',
         status='live'),
]

# Removed 1 August 2026: Provincial Upholstery (Southern Highlands, NSW).
# Listed originally on the strength of an archived "upholstery supplies" page
# offering trade access to horsehair. Those pages are now 404, the site presents
# as conservation consultancy and heritage commissions, and the owner confirmed
# in writing that the horsehair stock is held "exclusively to service our
# institutional museum and blue-chip colonial commissions". Holding materials
# for your own work is not supplying them. A directory of where to buy things
# has to mean it.

SPECIALISTS = [

# ================= Heritage & conservation specialists =================
# Not suppliers. Workshops taking commissions on pieces that matter, where the
# institutional record is publicly verifiable. Listed because upholsterers are
# regularly asked "who can I trust with this?" and there is nowhere to look.

    dict(kind='specialist', country='AU', name='Provincial Upholstery',
         url='https://www.provincialupholstery.com/',
         cats=['conservation', 'traditional'],
         note='Welby / Bowral, Southern Highlands, NSW. Carlos Rodrigues, trained from '
              'age 14 in Sintra, Portugal. Traditional hand-stitched horsehair work and '
              'independent structural diagnosis. Commissions include Government House '
              'Sydney, Vaucluse House and Sydney Living Museums, and work approved by the '
              'Historic Houses Trust of New South Wales. Holds archival horsehair and '
              'European flax twine for its own conservation commissions.',
         status='live'),

]

COUNTRIES = {
    'GB': 'United Kingdom',
    'US': 'United States',
    'AU': 'Australia',
    'NZ': 'New Zealand',
    'CA': 'Canada',
    'IE': 'Ireland',
    'ZA': 'South Africa',
    'OTHER': 'Elsewhere',
}

CATEGORIES = [
    ('traditional', 'Traditional materials',
     'Jute webbing, hair, scrim, twine, coil springs, tacks'),
    ('foam', 'Foam & fillings',
     'Foam, cut-to-size, wadding, fibre'),
    ('fabric', 'Fabric, vinyl & leather', 'Cover materials'),
    ('tools', 'Tools & machines',
     'Hand tools, staple guns, sewing machines'),
    ('sundries', 'Sundries',
     'Zips, threads, adhesives, trim, nails, legs'),
    ('auto', 'Automotive & marine',
     'Vehicle, campervan, boat and outdoor materials'),
    ('fabrichouse', 'Fabric houses & mills',
     'The brands themselves — usually trade accounts, ordered via a stockist'),
]
