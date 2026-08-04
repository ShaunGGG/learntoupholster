#!/usr/bin/env python3
"""
fire-data.py — upholstery fire regulations by country.

Every statement below is traceable to a source listed in that country's
`sources` block. Where a country has no requirement, the page says so plainly
rather than leaving a gap, because "there is no mandatory standard" is itself
the answer an upholsterer needs.

Researched 2 August 2026. Fire rules change; `checked` records when each
country was last verified, and the pages print it.

Structure per country:
    domestic   {status, headline, points, label}
    commercial {status, headline, points}
    sources    [(title, url)]

status is one of:
    mandatory   law, with a specific standard named
    partial     law exists but is narrower than people assume
    voluntary   a standard exists but nothing compels its use
    none        no upholstery-specific requirement
"""

CHECKED = '2026-08-02'

COUNTRIES = [

# ---------------------------------------------------------------- UNITED STATES
dict(
    code='usa', name='United States', flag='US',
    summary='Federal standard since 2021, and it names reupholstery \u2014 but not when '
            'the piece keeps the same owner.',
    domestic=dict(
        status='mandatory',
        headline='16 CFR Part 1640, adopting California TB 117-2013',
        points=[
            ('Reupholstery is in scope \u2014 with one exception',
             'The standard applies to upholstered furniture manufactured, imported or '
             '<strong>reupholstered</strong> on or after 25 June 2021. But CPSC confirmed to the '
             'National Upholstery Association that it does not apply where the furniture keeps '
             'the same owner through the work. A customer\u2019s own chair coming back to them is '
             'outside it; a piece you reupholster and sell is inside it. That single distinction '
             'decides most jobs and almost nobody knows about it.'),
            ('Smoulder resistance only',
             'This is the biggest difference from the British regime and it catches people who '
             'have worked to UK rules. TB 117-2013 tests resistance to a smouldering cigarette. '
             'There is <strong>no match or open-flame test</strong> at federal level for domestic '
             'furniture.'),
            ('Four components, tested separately',
             'Cover fabric, barrier material, resilient filling, and decking material where there '
             'is a loose cushion. Each passes or fails on its own.'),
            ('The barrier layer is the simple route',
             'Under TB 117-2013, <strong>if the barrier passes, the piece complies</strong> even '
             'where the cover and filling would fail on their own. Fitting a compliant barrier as '
             'standard practice solves the customer\u2019s-own-fabric problem outright \u2014 which '
             'is a cleaner answer than Britain has.'),
        ],
        label='Complies with U.S. CPSC requirements for upholstered furniture flammability.',
        label_notes=[
            'Required on covered furniture reupholstered on or after 25 June 2022',
            'Permanent label, front of the tag, in English',
            'White background, black text, black border',
            'State and city label rules sit on top of this \u2014 California has had its own since 2015',
        ],
    ),
    commercial=dict(
        status='partial',
        headline='NFPA 101 Life Safety Code, by occupancy and sprinklers',
        points=[
            ('California TB 133 has been repealed',
             'The open-flame test for public seating that the trade knew for decades is gone. '
             'Do not specify to it, and be wary of anyone still quoting it as current.'),
            ('But open-flame testing has not disappeared',
             'NFPA 101 still requires it in <strong>unsprinklered</strong> buildings for certain '
             'occupancies, via ASTM E1537 \u2014 a more general version of the old TB 133 procedure. '
             'Whether it applies turns on the building, not the furniture.'),
            ('It depends entirely on occupancy and sprinklers',
             'The table below is the whole of it. A great many occupancies require nothing at all.'),
            ('Ask the building, not the supplier',
             'The requirement comes from the premises\u2019 fire code and its sprinkler status. Get '
             'it in writing from whoever is responsible for the building before you cut anything.'),
        ],
        table=dict(
            head=['Occupancy', 'Sprinklered', 'Not sprinklered'],
            rows=[
                ['Ambulatory health care', 'NFPA 260 or 261', 'ASTM E1537'],
                ['Detention and correctional', 'NFPA 261', 'NFPA 261'],
                ['Dormitories', 'NFPA 260 or 261', 'ASTM E1537'],
                ['Health care', 'NFPA 260 or 261', 'ASTM E1537'],
                ['Hotel', 'NFPA 260 or 261', 'ASTM E1537'],
                ['Residential board and care', 'NFPA 260 or 261', 'ASTM E1537'],
                ['Assembly', 'None', 'None'],
                ['Business', 'None', 'None'],
                ['Day-care', 'None', 'None'],
                ['Educational', 'None', 'None'],
                ['Industrial', 'None', 'None'],
                ['Lodging and rooming houses', 'None', 'None'],
                ['Mercantile', 'None', 'None'],
                ['Storage', 'None', 'None'],
            ],
            note='NFPA 101 Life Safety Code occupancies and required tests. The International '
                 'Fire Code accepts either ASTM E1537 or the old California TB 133 where an '
                 'open-flame test is required.',
        ),
    ),
    sources=[
        ('16 CFR Part 1640 \u2014 eCFR',
         'https://www.ecfr.gov/current/title-16/chapter-II/subchapter-D/part-1640'),
        ('California TB 117-2013 \u2014 Department of Consumer Affairs',
         'https://bhgs.dca.ca.gov/about_us/tb117_2013.pdf'),
        ('CPSC direct final rule, 9 April 2021 \u2014 Federal Register',
         'https://www.federalregister.gov/documents/2021/04/09/2021-06977/standard-for-the-flammability-of-upholstered-furniture'),
        ('National Upholstery Association guidance, including their CPSC clarification on reupholstery',
         'https://nationalupholsteryassociation.org/Upholstered-Furniture-Flammability-Standard'),
        ('CPSC Small Business Ombudsman',
         'https://www.cpsc.gov/Newsroom/Small-Business-Resources'),
    ],
),

# ---------------------------------------------------------------- CANADA
dict(
    code='canada', name='Canada', flag='CA',
    summary='No flammability standard for upholstered furniture. All three provincial '
            'schemes were repealed between 2019 and 2021.',
    domestic=dict(
        status='none',
        headline='No upholstery flammability standard, federal or provincial',
        points=[
            ('The provincial schemes are all gone',
             'Ontario repealed its Upholstered and Stuffed Articles Regulation on 1 July 2019, '
             'Manitoba repealed its equivalent on 1 January 2020, and Quebec repealed the Act '
             'Respecting Stuffing and Upholstered and Stuffed Articles on 9 December 2021. '
             'Registration and licensing as a renovator are no longer required anywhere in Canada.'),
            ('Beware old guidance',
             'A great deal of what is still online describes the registration and gold, blue and '
             'white label system as though it were current. It is not, and has not been for years.'),
            ('Fibre content labelling still applies',
             'The federal <strong>Textile Labelling Act</strong> and its regulations still require '
             'accurate fibre content labelling on consumer textile articles, including upholstered '
             'furniture. That is a truth-in-labelling rule, not a fire rule.'),
            ('And the general duty still applies',
             'Under the Canada Consumer Product Safety Act you must not supply a product that is a '
             'danger to human health or safety. There is no prescribed upholstery fire test, but '
             '"no standard" is not the same as "no responsibility".'),
        ],
        label=None,
        label_notes=[],
    ),
    commercial=dict(
        status='partial',
        headline='Set by the building\u2019s fire code, not by furniture law',
        points=[
            ('No national contract standard for upholstery',
             'There is no Canadian equivalent of BS 7176. Requirements for public buildings come '
             'from the National Building Code, provincial fire codes and the authority having '
             'jurisdiction.'),
            ('North American practice fills the gap',
             'In the absence of a Canadian standard, contract specifications in Canada commonly '
             'call for <strong>NFPA 260 / UFAC</strong> or California TB 117-2013, because that is '
             'what the North American supply chain tests to.'),
            ('Ask the specifier',
             'On any commercial job, get the required standard in writing from whoever is '
             'responsible for the building. Do not assume, and do not let a client tell you '
             '"there\u2019s no standard in Canada" as a reason to fit anything.'),
        ],
    ),
    sources=[
        ('Federal labelling requirements for upholstered furniture \u2014 Competition Bureau Canada',
         'https://competition-bureau.canada.ca/en/federal-labelling-requirements-upholstered-furniture'),
        ('Guide to the labelling of stuffed or filled textile articles \u2014 Competition Bureau Canada',
         'https://competition-bureau.canada.ca/en/labelling/textile-labelling/guide-labelling-stuffed-or-filled-textile-articles'),
        ('Canada Consumer Product Safety Act \u2014 Health Canada',
         'https://laws-lois.justice.gc.ca/eng/acts/c-1.68/'),
    ],
),

# ---------------------------------------------------------------- AUSTRALIA / NZ
dict(
    code='australia-new-zealand', name='Australia & New Zealand', flag='AU',
    summary='The AS/NZS upholstery flammability standards are voluntary. There is no '
            'mandatory domestic requirement in either country.',
    domestic=dict(
        status='voluntary',
        headline='AS/NZS 4088.1 \u2014 a voluntary standard',
        points=[
            ('Nothing compels you to meet it',
             'AS/NZS 4088.1 sets ignitability requirements for covering and filling materials in '
             'domestic furniture, and AS/NZS 3744 provides the test methods \u2014 3744.1 for a '
             'smouldering cigarette, 3744.2 for match flame equivalent. Neither is mandatory for '
             'domestic upholstered furniture in Australia or New Zealand.'),
            ('Australian Consumer Law still applies',
             'Goods must be of acceptable quality and safe. Mandatory product safety standards do '
             'exist for various children\u2019s furniture. There is simply no mandatory flammability '
             'standard for ordinary domestic upholstery.'),
            ('Which makes it a professional judgement',
             'With no legal floor, the standard you work to is the one you choose. Specifying '
             'materials tested to AS/NZS 4088.1 costs little, and it is what you would want to be '
             'able to point at if a piece you built were ever involved in a fire.'),
            ('Tell the customer what you have done',
             'Where there is no legal requirement, a written record of the materials and their '
             'test evidence is worth more, not less. It is the only thing that distinguishes a '
             'considered specification from an accident.'),
        ],
        label=None,
        label_notes=[],
    ),
    commercial=dict(
        status='partial',
        headline='Building codes and the specifier, not furniture law',
        points=[
            ('Comes from the National Construction Code',
             'Fire requirements for public buildings in Australia flow from the NCC and the '
             'relevant state fire authority, not from an upholstery standard.'),
            ('AS/NZS 3744.2 is the usual match test',
             'Where a specification calls for open-flame performance, AS/NZS 3744.2 (match flame '
             'equivalent) is the local equivalent of BS EN 1021-2. Contract fabrics sold in '
             'Australia are commonly tested to it.'),
            ('British standards turn up in specifications',
             'Because much contract fabric is imported, BS 7176 and crib 5 appear in Australian '
             'and New Zealand specifications more often than you might expect. If a specifier asks '
             'for crib 5, they mean the British test.'),
            ('Get it in writing',
             'Same rule as everywhere: the requirement belongs to the building. Ask the person '
             'responsible for it, and record the answer.'),
        ],
    ),
    sources=[
        ('AS/NZS 4088.1 \u2014 Upholstery materials for domestic furniture: smouldering ignitability',
         'https://www.standards.org.au/'),
        ('AS/NZS 3744 series \u2014 Assessment of the ignitability of upholstered furniture',
         'https://www.standards.org.au/'),
        ('Product safety \u2014 Australian Competition and Consumer Commission',
         'https://www.productsafety.gov.au/'),
    ],
),

# ---------------------------------------------------------------- IRELAND
dict(
    code='ireland', name='Ireland', flag='IE',
    summary='Its own 1995 Order and Irish Standard, close to the British regime but a '
            'separate legal instrument.',
    domestic=dict(
        status='mandatory',
        headline='S.I. No. 316/1995 and Irish Standard IS 419',
        points=[
            ('A separate Irish instrument',
             'The Industrial Research and Standards (Fire Safety) (Domestic Furniture) Order 1995 '
             '(S.I. No. 316/1995), with Irish Standard <strong>IS 419</strong>, sets fire '
             'resistance levels for domestic upholstered furniture. It is not the British '
             'regulations, and a piece compliant in Britain is not automatically compliant here.'),
            ('European test methods',
             'The tests are the EN series familiar across Europe: <strong>EN 1021-1</strong> for a '
             'smouldering cigarette and <strong>EN 1021-2</strong> for match flame equivalent. '
             'These are the same tests British upholsterers know as BS EN 1021.'),
            ('Northern Ireland is different again',
             'Northern Ireland follows the UK Furniture and Furnishings (Fire) (Safety) Regulations, '
             'not the Irish Order, alongside EU General Product Safety requirements. If you work '
             'across the border, they are two regimes.'),
            ('Check the current position before you rely on it',
             'The Irish regulations have been under review, and the Department of Enterprise has '
             'consulted on amending them. Verify the current requirement rather than relying on '
             'this page alone.'),
        ],
        label=None,
        label_notes=[],
    ),
    commercial=dict(
        status='partial',
        headline='EN 1021 as the baseline, with the building setting the rest',
        points=[
            ('Public premises are specified more strictly',
             'Contract and public seating requirements come from the building\u2019s fire safety '
             'obligations rather than from the domestic furniture Order.'),
            ('BS 7176 is widely used',
             'Much contract fabric supplied into Ireland is tested and certificated to the British '
             'contract standard, so BS 7176 hazard categories and crib 5 appear routinely in Irish '
             'specifications.'),
            ('Ask the responsible person',
             'As everywhere: get the required category in writing before you cut anything.'),
        ],
    ),
    sources=[
        ('S.I. No. 316/1995 \u2014 Irish Statute Book',
         'https://www.irishstatutebook.ie/eli/1995/si/316/'),
        ('Furniture fire regulations consultation \u2014 Department of Enterprise, Tourism and Employment',
         'https://enterprise.gov.ie/en/consultations/furniture-fire-regulations-consultation.html'),
    ],
),

]

# The UK keeps its existing page and URL, which has years of search history behind
# it. The hub links to it rather than duplicating it.
UK = dict(
    code='uk', name='United Kingdom', flag='GB', url='/fire-safety-checker',
    summary='The strictest of the English-speaking regimes: cigarette and match tests, '
            'and a permanent label.',
    domestic_status='mandatory',
    commercial_status='mandatory',
)
