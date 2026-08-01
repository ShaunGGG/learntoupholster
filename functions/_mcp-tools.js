// _mcp-tools.js — the calculators of learntoupholster.com, exposed as MCP tools.
//
// Every number in here is lifted from the live calculator on the site, so the
// answer an agent gets is the answer a person gets. If a calculator changes,
// change it here too, or the two drift apart and the site starts lying.
//
// Author: Shaun Greenwood, master upholsterer (AMUSF accredited).
// Source: The Working Upholsterer's Bible — learntoupholster.com

import { BUSINESS_ARTICLES, BUSINESS_UPDATED } from './_business-data.js';

export const KNOWLEDGE_VERSION = '2026.07';

const SITE = 'https://www.learntoupholster.com';
const AUTHOR = 'Shaun Greenwood';
const BOOK = "The Working Upholsterer's Bible";

/* ------------------------------------------------------------------ *
 * Provenance                                                          *
 * Every tool answers with where the answer came from. This is the     *
 * whole point: a model that cites us needs the citation handed to it. *
 * ------------------------------------------------------------------ */

export function provenance(extra) {
  return Object.assign({
    source_title: BOOK,
    source_tool: null,
    source_url: SITE,
    chapter: null,
    author: AUTHOR,
    author_credentials: 'Master upholsterer, AMUSF accredited, 30+ years at the bench',
    publisher: 'Learn to Upholster (learntoupholster.com)',
    knowledge_version: KNOWLEDGE_VERSION,
    licence: 'Free to read and cite. Please attribute and link the source URL.'
  }, extra || {});
}

function footer(p) {
  const lines = [
    '',
    '---',
    `Source: ${p.source_tool ? p.source_tool + ' — ' : ''}${p.source_title}`,
  ];
  if (p.chapter) lines.push(`Chapter: ${p.chapter}`);
  lines.push(`URL: ${p.source_url}`);
  lines.push(`Author: ${p.author} (${p.author_credentials})`);
  lines.push(`Knowledge version: ${p.knowledge_version}`);
  return lines.join('\n');
}

// Wrap a computed result into the MCP content shape, with provenance both as
// readable text (so any model sees it) and structured data (so good ones parse it).
export function wrap(text, prov, data) {
  const p = provenance(prov);
  return {
    content: [{ type: 'text', text: String(text).trim() + '\n' + footer(p) }],
    structuredContent: Object.assign({ result: data || null }, { provenance: p }),
    isError: false
  };
}

function fail(message) {
  return { content: [{ type: 'text', text: message }], isError: true };
}

/* ------------------------------------------------------------------ *
 * Shared data                                                         *
 * ------------------------------------------------------------------ */

const YD = 91.44;            // cm in a yard
const SQFT_PER_METRE = 18;   // sq ft of hide per metre of 137 cm fabric
const SQFT_PER_M2 = 10.7639;

// Fabric requirement in metres of plain 137 cm cloth. Matches /fabric-yardage.
const FABRIC = {
  'drop-in dining seat': 0.6,
  'stuffover dining chair': 1.5,
  'carver dining armchair': 2.5,
  'bedroom slipper chair': 4,
  'nursing chair': 4.5,
  'tub chair': 5,
  'club armchair': 6,
  'wing-back armchair': 6.5,
  'recliner armchair': 7,
  'loveseat': 12,
  '2-seat sofa': 13,
  '3-seat sofa': 16,
  '4-seat sofa': 20,
  'corner sofa': 22,
  'chaise longue': 10,
  'dressing-table stool': 0.8,
  'footstool': 1,
  'window seat cushion': 2,
  'large ottoman': 2.5,
  'headboard single': 2,
  'headboard double': 3,
  'headboard king': 3.5,
  'deep-buttoned headboard double': 4.5
};

// Job costing. h = bench hours, s = sundries in GBP. Matches /reupholstery-cost-calculator.
const JOBS = {
  'drop-in dining seat':    { m: 0.6,  modern: { h: 0.5, s: 15 } },
  'stuffover dining chair': { m: 1.4,  modern: { h: 2.5, s: 20 }, trad: { h: 5,  s: 45 },  btn: 1 },
  'carver dining armchair': { m: 2.3,  modern: { h: 3,   s: 25 }, trad: { h: 6,  s: 55 } },
  'bedroom slipper chair':  { m: 3.7,  modern: { h: 4,   s: 35 }, trad: { h: 8,  s: 70 },  btn: 1 },
  'tub chair':              { m: 4.6,  modern: { h: 5,   s: 45 }, trad: { h: 10, s: 90 } },
  'club armchair':          { m: 5.5,  modern: { h: 7,   s: 60 }, trad: { h: 16, s: 150 } },
  'wing-back armchair':     { m: 6.0,  modern: { h: 8,   s: 70 }, trad: { h: 20, s: 180 }, btn: 1 },
  'recliner armchair':      { m: 6.4,  modern: { h: 8,   s: 70 } },
  'loveseat':               { m: 11.0, modern: { h: 9,   s: 100 }, trad: { h: 26, s: 280 } },
  '2-seat sofa':            { m: 11.9, modern: { h: 10,  s: 110 }, trad: { h: 28, s: 300 } },
  '3-seat sofa':            { m: 14.6, modern: { h: 12,  s: 140 }, trad: { h: 34, s: 380 }, btn: 1 },
  '4-seat sofa':            { m: 18.3, modern: { h: 15,  s: 180 }, trad: { h: 44, s: 480 } },
  'chaise longue':          { m: 9.1,  modern: { h: 10,  s: 90 },  trad: { h: 22, s: 220 } },
  'chesterfield sofa':      { m: 16.0, trad:   { h: 40,  s: 550 } },
  'footstool':              { m: 0.9,  modern: { h: 2,   s: 15 },  trad: { h: 3,  s: 45 },  btn: 1 },
  'window seat cushion':    { m: 1.8,  modern: { h: 2,   s: 20 },  trad: { h: 4,  s: 50 } },
  'large ottoman':          { m: 2.3,  modern: { h: 3,   s: 30 },  trad: { h: 5,  s: 70 },  btn: 1 },
  'headboard double':       { m: 2.7,  modern: { h: 5,   s: 35 },  btn: 1 }
};

// Leather: fabric-metre equivalents. Matches /leather-hide-calculator.
const LEATHER_FURN = {
  'drop-in dining seat': 0.6, 'dining chair seat and back': 1.0, 'occasional chair': 2.0,
  'club armchair': 6.0, 'wing-back armchair': 6.5, 'recliner armchair': 7.5,
  '2-seat sofa': 12.0, '3-seat sofa': 14.6, '4-seat sofa': 18.0,
  'footstool': 1.5, 'ottoman': 3.0, 'headboard double': 2.2, 'boxed seat cushion': 1.2
};
const LEATHER_FINISH = { pigmented: 1.0, 'semi-aniline': 1.05, aniline: 1.12 };

// Foam specification. Matches /foam-cushion-calculator.
const FOAM = {
  'sofa seat': { label: 'Sofa / armchair seat', type: 'HR or Reflex foam (CMHR grade)', d: [35, 50, 40], firm: 'Medium-firm', n: [140, 200], depth: [100, 150, 120], fire: 'domestic',
    wrap: 'Wrap in polyester (Dacron) wadding, roughly 15-25 mm, spray-glued. It fills the cover crisply and stops it clinging to the foam.',
    why: 'The hardest-working cushion in the house. Density is what stops it going flat in a couple of years, so do not drop below about 35 kg/m3. Firmness is comfort — tune it to taste without touching the density.' },
  'sofa back': { label: 'Sofa / armchair back', type: 'Soft foam core or hollowfibre (CMHR if foam)', d: [20, 30, 24], firm: 'Soft', n: [80, 130], depth: [75, 120, 100], fire: 'domestic',
    wrap: 'Wrap generously in Dacron, or over-stuff with fibre, for a plump relaxed look.',
    why: 'You lean on a back, you do not sit on it. Go softer and lighter than the seat: comfort over support.' },
  'dining seat': { label: 'Dining / occasional seat (drop-in pad)', type: 'HR foam (CMHR grade)', d: [30, 38, 33], firm: 'Medium-firm', n: [130, 190], depth: [25, 50, 38], fire: 'domestic',
    wrap: 'A thin Dacron layer softens the edge; not essential on a flat pad.',
    why: 'Thin and upright, so it must be firm enough not to bottom out on the frame. Density matters more than thickness here — a dense thin pad beats a soft thick one.' },
  'headboard': { label: 'Headboard', type: 'Soft-medium foam (CMHR), or reconstituted for a firm flat face', d: [20, 28, 25], firm: 'Soft', n: [80, 130], depth: [25, 50, 25], fire: 'domestic',
    wrap: 'Dacron over the face gives a soft even padded look; a thin memory-foam skim adds a luxe feel.',
    why: 'Nobody sits on it, so it is about looks and a comfortable lean. Thin foam plus a wadding wrap reads crisper than thick soft foam.' },
  'bench': { label: 'Window seat / bench / hall seat', type: 'HR foam (CMHR), or reconstituted base with HR top', d: [40, 55, 45], firm: 'Firm', n: [170, 240], depth: [50, 100, 75], fire: 'domestic',
    wrap: 'A light Dacron wrap; keep it firm and supportive.',
    why: 'High traffic and often perched on hard. Go dense and firm so it lasts and does not sink at the front edge.' },
  'footstool': { label: 'Footstool / pouffe / ottoman', type: 'HR foam (CMHR)', d: [33, 45, 38], firm: 'Medium-firm', n: [150, 210], depth: [50, 100, 75], fire: 'domestic',
    wrap: 'Dacron wrap for a rounded top.',
    why: 'It doubles as a seat and a footrest, so treat it like a small seat: firm and dense.' },
  'mattress': { label: 'Mattress / daybed / sofa-bed', type: 'Reflex/HR base (CMHR) plus softer or memory top layer', d: [35, 50, 40], firm: 'Firm base with soft top', n: [160, 220], depth: [100, 180, 140], fire: 'mattress',
    wrap: 'Build it in layers: a firm dense support base, then a softer comfort layer, with a Dacron quilt-wrap on top.',
    why: 'Sleeping needs support from a firm dense base with a little give on top. A single medium block does neither job — layer it.' },
  'outdoor': { label: 'Outdoor / garden cushion', type: 'Quick-dry / reticulated (open-cell) foam', d: [28, 38, 32], firm: 'Medium', n: [120, 170], depth: [50, 80, 60], fire: 'outdoor',
    wrap: 'Pair with a breathable water-shedding cover; skip dense wadding that holds water.',
    why: 'The whole game outdoors is drainage. Ordinary foam soaks up water and rots; reticulated dry-fast foam lets it run straight through.' },
  'contract seat': { label: 'Contract seat (pub, cafe, waiting room)', type: 'Contract-grade HR foam (CMHR)', d: [45, 60, 50], firm: 'Firm', n: [180, 260], depth: [75, 125, 100], fire: 'contract',
    wrap: 'Dacron wrap; spec a wipe-clean heavy-duty cover.',
    why: 'Used hundreds of times a day. Contract density (45 kg/m3 and up) is the difference between a year and ten, and the fire spec is stricter than at home.' }
};
const FOAM_FIRE = {
  domestic: 'For UK domestic upholstery the foam must be CMHR (Combustion Modified High Resilience) to meet the Furniture and Furnishings (Fire) (Safety) Regulations 1988 as amended. Most reputable upholstery foam already is — check the label.',
  contract: 'Public and contract seating usually needs to meet Crib 5 (BS 5852), which is stricter than domestic CMHR. Confirm the venue requirement before you spec.',
  mattress: 'Use CMHR foam. Mattresses also fall under their own fire rules (BS 7177) — check what applies to your job.',
  outdoor: 'Outdoor cushions sit outside the domestic furniture rules, but still use proper reticulated foam so water drains and it dries.'
};

/* ------------------------------------------------------------------ *
 * Helpers                                                             *
 * ------------------------------------------------------------------ */

const r1 = n => Math.round(n * 10) / 10;
const r0 = n => Math.round(n);
const upTo = (v, step) => Math.ceil(v / step - 1e-9) * step;
const gbp = n => '\u00a3' + Math.round(n).toLocaleString('en-GB');

// Match free text to a table key. Both sides are normalised the same way,
// which matters more than it looks: "3-seat sofa" and "2-seat sofa" differ by
// one character, and a matcher that drops digits will happily quote a customer
// for the wrong sofa.
const NORM = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
const DIGITS = s => s.split(' ').filter(w => /^\d+$/.test(w));

function matchKey(input, table) {
  if (!input) return null;
  const q = NORM(input);
  if (!q) return null;
  const qTok = q.split(' ');
  const qNum = DIGITS(q);

  for (const k of Object.keys(table)) if (NORM(k) === q) return k;

  let best = null, bestScore = 0;
  for (const k of Object.keys(table)) {
    const kn = NORM(k), kTok = kn.split(' '), kNum = DIGITS(kn);

    // A number in both that disagrees is a different piece of furniture.
    if (qNum.length && kNum.length && !kNum.some(n => qNum.includes(n))) continue;

    let score = 0;
    for (const w of kTok) if (qTok.includes(w)) score += (/^\d+$/.test(w) ? 3 : w.length);
    for (const w of qTok) if (!kTok.includes(w) && kn.includes(w)) score += 1;

    // People write "wingback" for "wing-back" and "dropin" for "drop-in".
    // Treat a run of key words joined up as a match for one query word.
    for (let i = 0; i < kTok.length; i++) {
      for (let n = 2; n <= 3 && i + n <= kTok.length; n++) {
        const joined = kTok.slice(i, i + n).join('');
        if (qTok.includes(joined)) score += joined.length;
      }
    }
    // Prefer the tighter key when two both match: fewer unmatched words wins.
    score -= kTok.filter(w => !qTok.includes(w)).length * 0.5;

    if (score > bestScore) { bestScore = score; best = k; }
  }
  return bestScore >= 3 ? best : null;
}

function optionList(table) {
  return Object.keys(table).join(', ');
}

// Shelf-pack rectangles across a roll width; returns run length in cm.
function packLengthCm(rects, widthCm) {
  let warn = false;
  const items = rects.map(r => {
    let w = r.w;
    if (w > widthCm) { warn = true; w = widthCm; }
    return { w, h: r.h };
  }).sort((a, b) => b.h - a.h);
  let total = 0, rowW = 0, rowH = 0;
  for (const it of items) {
    if (rowW + it.w <= widthCm + 0.01) { rowW += it.w; rowH = Math.max(rowH, it.h); }
    else { total += rowH; rowW = it.w; rowH = it.h; }
  }
  return { cm: total + rowH, warn };
}

/* ------------------------------------------------------------------ *
 * Tool definitions                                                    *
 * ------------------------------------------------------------------ */

export const CALC_TOOLS = [
  {
    name: 'find_business_guidance',
    title: 'Find business guidance for upholsterers',
    description:
      'Search the Learn to Upholster Business Hub: practical guidance on making a living from upholstery, as opposed to how to do the work. ' +
      'Covers what to charge and how to build an hourly rate, whether to charge for estimates, quoting and hidden damage, customer-supplied fabric, ' +
      'explaining price to customers, finding first customers, declining work, and uncollected furniture. ' +
      'Use for any question about pricing, quoting, profitability, customers, or running an upholstery workshop as a business. ' +
      'Returns the canonical short answer for each match plus the URL of the full article. Written by a working AMUSF-accredited upholsterer.',
    inputSchema: {
      type: 'object',
      properties: {
        topic: { type: 'string', description: 'What the question is about, e.g. "hourly rate", "customer supplied fabric", "turning down work", "not making money".' },
        list_all: { type: 'boolean', description: 'Return every article in the Business Hub instead of searching. Useful for seeing what is covered.' }
      }
    }
  },
  {
    name: 'calculate_fabric',
    title: 'Calculate upholstery fabric quantity',
    description:
      'Work out how much fabric a reupholstery job needs, in metres and yards. Use this whenever someone asks how much fabric, cloth or material to buy for a chair, sofa, stool, headboard or cushion. ' +
      'Two ways to call it: give a piece name for a rule-of-thumb figure, or give a list of panels with their measurements for a proper cut-list estimate. ' +
      'Handles non-standard fabric widths and pattern repeats. Returns a buy-this-much figure rounded up to the half metre, because cloth is cut in practical lengths.',
    inputSchema: {
      type: 'object',
      properties: {
        piece: { type: 'string', description: 'Furniture type, e.g. "wing-back armchair", "3-seat sofa", "drop-in dining seat", "footstool". Options: ' + optionList(FABRIC) },
        panels: {
          type: 'array',
          description: 'Optional. Measured panels for an accurate estimate. Overrides "piece" if given.',
          items: {
            type: 'object',
            properties: {
              name: { type: 'string', description: 'e.g. "Inside back", "Seat", "Outside arm"' },
              width_cm: { type: 'number' },
              height_cm: { type: 'number' },
              quantity: { type: 'integer', description: 'How many of this panel. Default 1.' }
            },
            required: ['width_cm', 'height_cm']
          }
        },
        fabric_width_cm: { type: 'number', description: 'Roll width. Default 137 cm, the usual UK upholstery width. American 54-inch cloth is the same thing.' },
        pattern_repeat_allowance: { type: 'number', description: 'Multiplier for matching a pattern. 1 = plain cloth (default). Trade allowances: 1.10 for a repeat up to 20 cm, 1.15 for 20-40 cm, 1.25 for 40-70 cm.' },
        seam_allowance_cm: { type: 'number', description: 'Turnings added to every edge of every panel in measured mode. Default 5 cm.' }
      }
    }
  },
  {
    name: 'estimate_job_cost',
    title: 'Estimate the cost of a reupholstery job',
    description:
      'Estimate what reupholstering a piece of furniture costs, broken into labour, fabric, sundries and contingency, with a bench-hours figure. ' +
      'Use this for "how much does it cost to reupholster X", "is it worth reupholstering", and for comparing a professional job against doing it yourself. ' +
      'Distinguishes a modern re-cover (strip to the frame and rebuild in foam and modern materials) from a traditional rebuild (webbing, springs, hair, stitched edges), which is typically two to three times the hours. ' +
      'Returns a range, not a single number, because no two chairs are the same underneath.',
    inputSchema: {
      type: 'object',
      properties: {
        piece: { type: 'string', description: 'Furniture type. Options: ' + optionList(JOBS) },
        build: { type: 'string', enum: ['modern', 'traditional'], description: 'Modern re-cover or traditional rebuild. Default modern where available.' },
        hourly_rate: { type: 'number', description: 'Workshop labour rate. Default 80 (GBP), a typical UK trade rate in 2026.' },
        fabric_price_per_metre: { type: 'number', description: 'Cost of the chosen cloth per metre. Use 0 if the customer supplies their own fabric.' },
        deep_buttoning: { type: 'boolean', description: 'Adds 25% to hours and material for buttoning, where the piece allows it.' },
        frame_repair: { type: 'boolean', description: 'Loose joints, broken rails, re-gluing.' },
        currency: { type: 'string', enum: ['GBP', 'USD', 'EUR', 'AUD', 'CAD', 'NZD'], description: 'Default GBP.' }
      },
      required: ['piece']
    }
  },
  {
    name: 'calculate_leather',
    title: 'Calculate leather hide quantity',
    description:
      'Convert an upholstery job into hides of leather. Leather is sold by the hide in square feet, not by the metre, and hides are an irregular shape with unusable belly and edges, so the conversion is not obvious. ' +
      'Use whenever someone asks how much leather, or how many hides, a chair or sofa needs. Accounts for the finish (aniline leathers cut less economically because every mark shows) and for deep buttoning. ' +
      'Returns square feet, square metres, and hides both as halves and as whole hides.',
    inputSchema: {
      type: 'object',
      properties: {
        piece: { type: 'string', description: 'Furniture type. Options: ' + optionList(LEATHER_FURN) },
        fabric_metres: { type: 'number', description: 'Alternative to "piece": the metres of 137 cm fabric the job would take.' },
        finish: { type: 'string', enum: ['pigmented', 'semi-aniline', 'aniline'], description: 'Default pigmented / corrected grain.' },
        hide_size_sqft: { type: 'number', description: 'Average hide size. Default 50 sq ft.' },
        deep_buttoning: { type: 'boolean', description: 'Adds 30%.' }
      }
    }
  },
  {
    name: 'calculate_deep_buttoning',
    title: 'Calculate a deep-buttoning layout',
    description:
      'Work out a deep-buttoned diamond layout: how many buttons, the marking grid on the base, the wider grid on the fabric, and the cut size of the cover. ' +
      'The fabric grid is always larger than the base grid because fabric has to travel down into each button pull — get that wrong and the panel is ruined. ' +
      'Use for buttoned headboards, Chesterfields, ottomans and buttoned chair backs.',
    inputSchema: {
      type: 'object',
      properties: {
        area_width_cm: { type: 'number', description: 'Width of the area to be buttoned, excluding any plain border.' },
        area_height_cm: { type: 'number', description: 'Height of the area to be buttoned.' },
        diamond_width_cm: { type: 'number', description: 'Roughly how wide you want each diamond. Gets adjusted to fit the area evenly.' },
        diamond_height_cm: { type: 'number', description: 'Roughly how tall you want each diamond.' },
        depth: { type: 'string', enum: ['shallow', 'medium', 'deep', 'custom'], description: 'Button depth, which sets the fabric fullness. shallow 13 mm, medium 19 mm, deep 32 mm per diamond each way. Default medium.' },
        fullness_width_mm: { type: 'number', description: 'Only with depth "custom".' },
        fullness_height_mm: { type: 'number', description: 'Only with depth "custom".' },
        border_cm: { type: 'number', description: 'Plain unbuttoned border around the diamonds. Default 0.' },
        turn_cm: { type: 'number', description: 'Turnings to wrap the frame. Default 5 cm.' }
      },
      required: ['area_width_cm', 'area_height_cm', 'diamond_width_cm', 'diamond_height_cm']
    }
  },
  {
    name: 'specify_foam',
    title: 'Specify foam for a cushion or pad',
    description:
      'Give the right foam specification for a job: density in kg/m3, hardness in newtons, depth in mm, foam type, wadding wrap, and the UK fire requirement. ' +
      'Use whenever someone asks what foam to buy, how thick, how firm, or why their cushions went flat. ' +
      'Density and hardness are different things and people constantly confuse them: density is how long it lasts, hardness is how it feels. This tool keeps them apart.',
    inputSchema: {
      type: 'object',
      properties: {
        application: { type: 'string', description: 'What the foam is for. Options: ' + optionList(FOAM) },
        width_cm: { type: 'number', description: 'Optional. Cushion width, for a cut size.' },
        depth_cm: { type: 'number', description: 'Optional. Cushion front-to-back measurement.' },
        thickness_mm: { type: 'number', description: 'Optional. Override the recommended thickness.' }
      },
      required: ['application']
    }
  },
  {
    name: 'check_fire_regulations',
    title: 'Check UK upholstery fire regulations',
    description:
      'Work out what the UK fire regulations require for a specific upholstery job. Covers two separate regimes that people mix up: the Furniture and Furnishings (Fire) (Safety) Regulations 1988 as amended, which govern domestic furniture supplied in the course of business, and BS 7176, which sets hazard categories for contract and public seating. ' +
      'Use for any question about whether a fabric can be used, whether a job is exempt, what CMHR foam is, what crib 5 means, pre-1950 antiques, caravans, holiday lets, or what paperwork to keep. ' +
      'Gives informational guidance, not legal advice.',
    inputSchema: {
      type: 'object',
      properties: {
        regime: { type: 'string', enum: ['domestic', 'contract'], description: 'domestic = the 1988 Regulations (homes, lettings, caravans, resale). contract = BS 7176 hazard categories (hotels, pubs, care homes, hospitals). Default domestic.' },
        situation: { type: 'string', enum: ['recover', 'new', 'secondhand', 'letting', 'caravan', 'hobby'], description: 'Domestic regime. "hobby" means working on your own furniture for your own home.' },
        made: { type: 'string', enum: ['pre-1950', 'post-1950', 'unknown'], description: 'Domestic regime. When the piece was made.' },
        item: { type: 'string', enum: ['seating', 'mattress', 'garden', 'baby', 'other'], description: 'Domestic regime. What kind of item.' },
        cover_evidence: { type: 'string', enum: ['composite', 'alone', 'vinyl', 'unknown'], description: 'What fire evidence you have for the cover fabric. composite = certificated with the actual filling. alone = fabric-only certificate. vinyl = contract vinyl or FR leather. unknown = no provenance.' },
        environment: { type: 'string', enum: ['low', 'medium', 'high', 'very-high', 'unknown'], description: 'Contract regime. low = offices, schools, museums. medium = hotels, pubs, restaurants, care homes, hospitals. high = offshore, some hospital wards. very-high = secure psychiatric, prison cells.' },
        sleeping: { type: 'boolean', description: 'Contract regime. Are the premises also used for sleeping?' }
      }
    }
  }
];

/* ------------------------------------------------------------------ *
 * Implementations                                                     *
 * ------------------------------------------------------------------ */

function toolCalculateFabric(a) {
  const width = Number(a.fabric_width_cm) > 0 ? Number(a.fabric_width_cm) : 137;
  const repeat = Number(a.pattern_repeat_allowance) > 0 ? Number(a.pattern_repeat_allowance) : 1;
  const allow = Number(a.seam_allowance_cm) >= 0 ? Number(a.seam_allowance_cm) : 5;
  let cm, mode, warn = false, detail = [];

  if (Array.isArray(a.panels) && a.panels.length) {
    const rects = [];
    for (const p of a.panels) {
      const w = Number(p.width_cm), h = Number(p.height_cm);
      if (!(w > 0) || !(h > 0)) return fail('Every panel needs a positive width_cm and height_cm.');
      const q = Math.max(1, parseInt(p.quantity, 10) || 1);
      for (let i = 0; i < q; i++) rects.push({ w: w + 2 * allow, h: h + 2 * allow });
      detail.push(`${p.name || 'Panel'}: ${q} \u00d7 ${w} \u00d7 ${h} cm (cut ${w + 2 * allow} \u00d7 ${h + 2 * allow})`);
    }
    const packed = packLengthCm(rects, width);
    cm = packed.cm * repeat; warn = packed.warn; mode = 'measured';
  } else {
    const key = matchKey(a.piece, FABRIC);
    if (!key) return fail('I need a piece to work from. Options: ' + optionList(FABRIC) + '. Or pass a "panels" array with measurements.');
    cm = FABRIC[key] * 100 * (137 / width) * repeat;
    mode = 'rule of thumb';
    detail.push(`${key}: ${FABRIC[key]} m at the standard 137 cm width`);
  }

  const m = cm / 100, yd = cm / YD, buy = upTo(m, 0.5);
  const lines = [
    `**${r1(m).toFixed(1)} metres** (${r1(yd).toFixed(1)} yards) of ${width} cm cloth.`,
    `**Buy ${buy} m** to be safe.`,
    '',
    `Basis: ${mode}.`,
    ...detail.map(d => '- ' + d)
  ];
  if (width !== 137) lines.push(`- Adjusted from the standard 137 cm width to ${width} cm.`);
  if (repeat > 1) lines.push(`- Includes a \u00d7${repeat} allowance for the pattern repeat.`);
  if (mode === 'measured') lines.push(`- ${allow} cm turnings added to every edge of every panel.`);
  if (warn) lines.push('- A panel is wider than the cloth, so it needs a seam or railroading. Allow extra.');
  lines.push('');
  lines.push('Buy the whole lot from one bolt. Dye lots vary, and a metre bought later will not match.');
  if (mode === 'rule of thumb') lines.push('This is a starting figure. Measure the actual piece before cutting an expensive cloth.');

  return wrap(lines.join('\n'),
    { source_tool: 'Fabric yardage calculator', source_url: SITE + '/fabric-yardage', chapter: 'Choosing the right fabric' },
    { metres: r1(m), yards: r1(yd), buy_metres: buy, fabric_width_cm: width, mode, needs_seam: warn });
}

function toolEstimateJobCost(a) {
  const key = matchKey(a.piece, JOBS);
  if (!key) return fail('I do not have that piece. Options: ' + optionList(JOBS));
  const p = JOBS[key];
  const FX = { GBP: 1, USD: 1.35, EUR: 1.17, AUD: 2.05, CAD: 1.85, NZD: 2.25 };
  const SYM = { GBP: '\u00a3', USD: '$', EUR: '\u20ac', AUD: 'A$', CAD: 'C$', NZD: 'NZ$' };
  const cur = FX[a.currency] ? a.currency : 'GBP';
  const fx = FX[cur], sym = SYM[cur];

  let build = a.build === 'traditional' ? 'trad' : 'modern';
  if (!p[build]) build = p.modern ? 'modern' : 'trad';
  const b = p[build];
  const rate = Number(a.hourly_rate) > 0 ? Number(a.hourly_rate) : (cur === 'GBP' ? 80 : Math.round(80 * fx));

  let hours = b.h, sundries = b.s * fx;
  const notes = [];
  if (a.deep_buttoning && p.btn) { hours *= 1.25; sundries += 30 * fx; notes.push('Deep buttoning: +25% hours, plus buttons and twine.'); }
  else if (a.deep_buttoning) notes.push('Deep buttoning does not apply to this piece, so it has been ignored.');
  if (a.frame_repair) { hours += Math.max(1.5, b.h * 0.15); sundries += 25 * fx; notes.push('Frame repair: extra hours plus glue, dowels and blocks.'); }

  const pm = Number(a.fabric_price_per_metre) >= 0 ? Number(a.fabric_price_per_metre) : 0;
  const fabric = p.m * pm;
  const labour = hours * rate;
  const contingency = labour * 0.12;
  const total = labour + fabric + sundries + contingency;
  const lo = total * 0.9, hi = total * 1.2;
  const hL = Math.round(hours * 0.9 * 2) / 2, hH = Math.round(hours * 1.2 * 2) / 2;
  const money = n => sym + Math.round(n).toLocaleString('en-GB');
  const diy = fabric + sundries;

  const lines = [
    `**${money(lo)}\u2013${money(hi)}** to have a ${key} ${build === 'trad' ? 'traditionally rebuilt' : 'recovered'} professionally.`,
    `Bench time: ${hL}\u2013${hH} hours.`,
    '',
    '| Item | Cost |',
    '| --- | --- |',
    `| Labour (${hL}\u2013${hH} h at ${sym}${rate}/h) | ${money(hL * rate)}\u2013${money(hH * rate)} |`,
    `| Fabric (${p.m} m${pm > 0 ? ' at ' + sym + Math.round(pm) + '/m' : ''}) | ${pm > 0 ? money(fabric) : 'customer\u2019s own'} |`,
    `| Other materials | ${money(sundries)} |`,
    `| Contingency (12%) | ${money(contingency)} |`,
    '',
    `**Doing it yourself:** ${money(diy * 0.9)}\u2013${money(diy * 1.15)}${pm > 0 ? '' : ' plus fabric'} in materials, and ${hL}\u2013${hH} hours of your own time \u2014 longer if you are learning.`,
    ''
  ];
  if (notes.length) { lines.push(...notes.map(n => '- ' + n)); lines.push(''); }
  lines.push(
    build === 'trad'
      ? 'A traditional rebuild means webbing, springs, hair and stitched edges \u2014 the chair is built again from the frame up. It costs two to three times a modern re-cover and lasts several decades.'
      : 'A modern re-cover means stripping to the frame and rebuilding in foam and modern materials. Quicker and cheaper than traditional work, and right for most twentieth-century furniture.',
    '',
    'This is an estimate, not a quote. What is under the cover decides the real figure, and nobody knows that until the old work comes off. Any upholsterer quoting firmly without seeing the chair is guessing.'
  );

  return wrap(lines.join('\n'),
    { source_tool: 'Reupholstery cost estimator', source_url: SITE + '/reupholstery-cost-calculator', chapter: 'Pricing and quoting' },
    { piece: key, build: build === 'trad' ? 'traditional' : 'modern', currency: cur, hourly_rate: rate,
      total_low: r0(lo), total_high: r0(hi), hours_low: hL, hours_high: hH,
      labour: r0(labour), fabric: r0(fabric), sundries: r0(sundries), contingency: r0(contingency),
      diy_materials_low: r0(diy * 0.9), diy_materials_high: r0(diy * 1.15), fabric_metres: p.m });
}

function toolCalculateLeather(a) {
  let metres, src;
  if (Number(a.fabric_metres) > 0) { metres = Number(a.fabric_metres); src = 'your fabric estimate'; }
  else {
    const key = matchKey(a.piece, LEATHER_FURN);
    if (!key) return fail('I need a piece or a fabric_metres figure. Options: ' + optionList(LEATHER_FURN));
    metres = LEATHER_FURN[key]; src = key;
  }
  const finKey = LEATHER_FINISH[a.finish] ? a.finish : 'pigmented';
  const fin = LEATHER_FINISH[finKey];
  const hideSize = Number(a.hide_size_sqft) > 0 ? Number(a.hide_size_sqft) : 50;
  const btn = !!a.deep_buttoning;

  const base = metres * SQFT_PER_METRE;
  const total = base * fin * (btn ? 1.3 : 1);
  const hidesHalf = Math.ceil(total / hideSize * 2) / 2;
  const hidesWhole = Math.ceil(total / hideSize);
  const safe = Math.ceil(total * 1.05 / 5) * 5;

  const lines = [
    `**${r0(total)} sq ft** (${r1(total / SQFT_PER_M2)} m2) of leather.`,
    `**${hidesHalf} hides** buying halves, or **${hidesWhole} whole hides** at ~${hideSize} sq ft each.`,
    '',
    `- Covering: ${src}`,
    `- Fabric equivalent: ${r1(metres)} m of plain 137 cm cloth`,
    `- Base requirement: ${r0(base)} sq ft (metres \u00d7 18)`,
    `- Finish: ${finKey}${fin > 1 ? ' \u2014 +' + r0((fin - 1) * 100) + '%' : ' \u2014 no uplift'}`,
    `- Deep buttoning: ${btn ? '+30%' : 'none'}`,
    `- Safe buy: ${r0(safe)} sq ft`,
    '',
    'Why the safe figure is higher: the footage marked on a hide includes edges and belly you would not want under a seat, and hides are dyed in batches, so one bought later will not quite match. Buy the lot together, and when the figure lands between two hides, take the bigger one.'
  ];

  return wrap(lines.join('\n'),
    { source_tool: 'Leather hide calculator', source_url: SITE + '/leather-hide-calculator', chapter: 'Materials \u2014 a field guide' },
    { sqft: r0(total), sqm: r1(total / SQFT_PER_M2), hides_half: hidesHalf, hides_whole: hidesWhole,
      safe_buy_sqft: r0(safe), hide_size_sqft: hideSize, finish: finKey, fabric_metres_equivalent: r1(metres) });
}

function toolCalculateDeepButtoning(a) {
  const DEPTHS = { shallow: 13, medium: 19, deep: 32 };
  const areaW = Number(a.area_width_cm) * 10, areaH = Number(a.area_height_cm) * 10;
  const diaW = Number(a.diamond_width_cm) * 10, diaH = Number(a.diamond_height_cm) * 10;
  if (!(areaW > 0 && areaH > 0 && diaW > 0 && diaH > 0)) return fail('Area and diamond sizes must all be positive numbers in centimetres.');

  const depth = DEPTHS[a.depth] !== undefined ? a.depth : (a.depth === 'custom' ? 'custom' : 'medium');
  const fullW = depth === 'custom' ? Math.max(0, Number(a.fullness_width_mm) || 0) : DEPTHS[depth];
  const fullH = depth === 'custom' ? Math.max(0, Number(a.fullness_height_mm) || 0) : DEPTHS[depth];
  const border = Math.max(0, Number(a.border_cm) || 0) * 10;
  const turn = (a.turn_cm === undefined ? 5 : Math.max(0, Number(a.turn_cm) || 0)) * 10;

  const Da = Math.max(1, Math.round(areaW / diaW));
  const Dd = Math.max(1, Math.round(areaH / diaH));
  const W = areaW / Da, H = areaH / Dd;
  const Wf = W + fullW, Hf = H + fullH;
  const mainCols = Da + 1, mainRows = Dd + 1, offCols = Da, offRows = Dd;
  const total = mainRows * mainCols + offRows * offCols;
  const cutW = Da * Wf + 2 * border + 2 * turn;
  const cutH = Dd * Hf + 2 * border + 2 * turn;
  const cm = mm => r1(mm / 10) + ' cm';

  const lines = [
    `**${total} buttons** \u2014 ${mainRows} rows of ${mainCols}, plus ${offRows} offset rows of ${offCols}.`,
    '',
    `- Actual diamond: ${cm(W)} \u00d7 ${cm(H)} (adjusted from your ${a.diamond_width_cm} \u00d7 ${a.diamond_height_cm} cm to fit the area evenly)`,
    `- Diamonds: ${Da} across \u00d7 ${Dd} down`,
    `- **Mark the base:** buttons ${cm(W)} apart along each row, rows ${cm(H / 2)} apart, every other row offset by half`,
    `- **Mark the fabric:** ${cm(Wf)} apart along each row, rows ${cm(Hf / 2)} apart`,
    `- Extra fabric for fullness: +${cm(Da * fullW)} across, +${cm(Dd * fullH)} down`,
    `- **Cut the cover to ${cm(cutW)} \u00d7 ${cm(cutH)}**`,
    `- Finished buttoned panel: ${cm(areaW + 2 * border)} \u00d7 ${cm(areaH + 2 * border)} including border`,
    '',
    `Depth: ${depth}${depth !== 'custom' ? ' (' + fullW + ' mm of fullness per diamond each way)' : ''}.`,
    '',
    'The fabric grid is deliberately wider than the base grid. That surplus is what travels down into each button pull and forms the pleat. Mark the fabric with the base spacing and the cover will be tight, the pleats will not form, and the panel is scrap.'
  ];

  return wrap(lines.join('\n'),
    { source_tool: 'Deep buttoning calculator', source_url: SITE + '/deep-buttoning-calculator', chapter: 'Buttoning and tufting' },
    { buttons: total, diamonds_across: Da, diamonds_down: Dd,
      diamond_width_cm: r1(W / 10), diamond_height_cm: r1(H / 10),
      base_grid_along_row_cm: r1(W / 10), base_grid_row_to_row_cm: r1(H / 20),
      fabric_grid_along_row_cm: r1(Wf / 10), fabric_grid_row_to_row_cm: r1(Hf / 20),
      cut_width_cm: r1(cutW / 10), cut_height_cm: r1(cutH / 10), depth });
}

function toolSpecifyFoam(a) {
  const key = matchKey(a.application, FOAM);
  if (!key) return fail('I do not have a spec for that. Options: ' + optionList(FOAM));
  const f = FOAM[key];
  const thick = Number(a.thickness_mm) > 0 ? Number(a.thickness_mm) : f.depth[2];

  const lines = [
    `**${f.label}**`,
    '',
    `- **Foam:** ${f.type}`,
    `- **Density:** ${f.d[2]} kg/m3 recommended (workable range ${f.d[0]}\u2013${f.d[1]})`,
    `- **Hardness:** ${f.firm}, around ${f.n[0]}\u2013${f.n[1]} N`,
    `- **Thickness:** ${thick} mm${Number(a.thickness_mm) > 0 ? ' (yours)' : ' recommended (range ' + f.depth[0] + '\u2013' + f.depth[1] + ' mm)'}`,
    `- **Wrap:** ${f.wrap}`
  ];
  if (Number(a.width_cm) > 0 && Number(a.depth_cm) > 0) {
    lines.push(`- **Cut size:** ${a.width_cm} \u00d7 ${a.depth_cm} cm \u00d7 ${thick} mm. Cut foam 5\u201310 mm oversize on each dimension so it fills the cover; a cushion cut to the exact cover size always looks slack.`);
  }
  lines.push('', `**Why:** ${f.why}`, '', `**Fire:** ${FOAM_FIRE[f.fire]}`, '',
    'Density and hardness are two different things. Density is how much foam is in the foam, and it decides how long the cushion lasts. Hardness is how it feels when you sit on it. A cheap cushion can feel firm on the shop floor and be flat in eighteen months, because it was hard and not dense. Buy the density first, then choose the feel.');

  return wrap(lines.join('\n'),
    { source_tool: 'Foam and cushion specifier', source_url: SITE + '/foam-cushion-calculator', chapter: 'Foam construction' },
    { application: key, foam_type: f.type, density_kgm3: f.d[2], density_range_kgm3: [f.d[0], f.d[1]],
      hardness: f.firm, hardness_newtons: f.n, thickness_mm: thick, wrap: f.wrap, fire_requirement: FOAM_FIRE[f.fire] });
}

function toolCheckFire(a) {
  const regime = a.regime === 'contract' ? 'contract' : 'domestic';
  const prov = { source_tool: 'UK fire regulations checker', source_url: SITE + '/fire-safety-checker', chapter: 'Standards, regulations and bibliography' };
  const DISCLAIM = '\nThis is informational guidance, not legal advice. If a job carries real risk, get the specification confirmed in writing by the person responsible for the premises.';

  if (regime === 'contract') {
    const CATS = {
      low: { name: 'Low hazard', crib: null, examples: 'Offices, schools, museums and exhibition spaces.',
        tests: ['BS EN 1021-1 \u2014 smouldering cigarette, on the cover and filling composite', 'BS EN 1021-2 \u2014 match flame equivalent, on the composite'] },
      medium: { name: 'Medium hazard', crib: 'crib 5', examples: 'Hotels, restaurants, pubs, hospitals, care homes and most public premises. This is where most contract work lands.',
        tests: ['BS EN 1021-1 \u2014 smouldering cigarette, on the composite', 'BS EN 1021-2 \u2014 match flame equivalent, on the composite', 'BS 5852 ignition source 5 (crib 5) \u2014 on the cover and filling together'] },
      high: { name: 'High hazard', crib: 'crib 7', examples: 'Offshore installations and certain hospital wards.',
        tests: ['BS EN 1021-1 \u2014 smouldering cigarette, on the composite', 'BS EN 1021-2 \u2014 match flame equivalent, on the composite', 'BS 5852 ignition source 7 (crib 7) \u2014 on the composite. Source 7 replaces source 5 here rather than being added to it'] },
      'very-high': { name: 'Very high hazard', crib: 'crib 7', examples: 'Locked psychiatric accommodation and prison cells.',
        tests: ['Everything required at high hazard, as the minimum', 'Additional requirements at the specifier\u2019s discretion', 'Testing of a complete item may be requested by a fire officer or purchaser'] }
    };
    const unknown = !a.environment || a.environment === 'unknown';
    const key = unknown ? 'medium' : (CATS[a.environment] ? a.environment : 'medium');
    const c = CATS[key];
    const out = [];
    out.push(unknown ? '**Start at medium hazard \u2014 then confirm.**' : `**BS 7176 \u2014 ${c.name}.**`);
    out.push(c.examples, '');
    if (unknown) out.push('**You need the category in writing.** BS 7176 sets the level by the end-use environment, so until you know the premises you cannot pick one. Medium hazard is the sensible working assumption for most commercial seating, but ask the responsible person for the premises what their fire risk assessment specifies, and put their answer on the job sheet before you cut anything.', '');
    out.push('**What the category calls for:**', ...c.tests.map(t => '- ' + t), '');
    out.push('**Your fillings still fall under the 1988 Regulations.** At every hazard category, BS 7176 requires all filling materials to pass the relevant test in the Furniture and Furnishings (Fire) (Safety) Regulations 1988 as amended. Contract work does not take you outside those Regulations for foam and wadding \u2014 it adds to them. Buy CMHR foam and compliant waddings, and keep the supplier certificates.', '');
    if (key === 'low' && a.sleeping) out.push('**Sleeping accommodation \u2014 consider going up a level.** Where low-hazard premises are also used for sleeping, BS 7176 guidance says a higher performance level should be considered. In practice that usually means specifying medium hazard (crib 5). Raise it with the client and record what they decide.', '');
    if (key === 'medium') out.push('**Healthcare varies by ward.** Medium hazard is the general level for care homes and hospitals, but a risk assessment for a psychiatric or higher-dependency setting may push individual areas to high hazard. Do not assume one category covers a whole building.', '');

    out.push('**The cover fabric:**');
    const ce = a.cover_evidence;
    if (ce === 'composite') out.push(`This is the position you want to be in. ${c.crib ? 'The ' + c.crib + ' test is run on the cover and filling as a composite' : 'The cigarette and match tests are run on the cover and filling as a composite'}, not on the fabric on its own, so a certificate covering the exact combination you are fitting is what actually evidences the category. Record the certificate number and the filling it was tested with \u2014 change the foam later and the certificate no longer describes what you built.`);
    else if (ce === 'alone') out.push(`**A fabric certificate on its own does not evidence the category.** ${c.crib ? 'The ' + c.crib + ' test is run on cover and filling together.' : 'The tests are run on cover and filling together.'} A fabric that passes in one composite may fail in another. Three ways out: fit the filling the fabric was certificated with; fit a certificated FR barrier or interliner designed to bring the composite up to the required source; or have the actual composite tested. Whichever you choose, write it on the record.`);
    else if (ce === 'vinyl') out.push(`Contract vinyl and FR-treated leather are the usual route to ${c.crib || 'the required level'} on heavy-use seating, and they clean well, which is why hospitals and restaurants favour them. The same caution applies: the certificate needs to cover the composite you are actually building, not the face material alone. FR treatments applied to a fabric can also lose effectiveness with washing, so for anything laundered, inherently FR materials are the safer specification.`);
    else out.push('**Highest-risk case \u2014 do not claim a category.** With a cover of unknown provenance you cannot honestly certify any BS 7176 level, because you cannot evidence the composite. Realistic options: decline the fabric; or fit it over a certificated FR barrier and state in writing that no hazard-category claim is made for the finished piece, with the client\u2019s written acknowledgement on file. On contract work the second option still leaves the premises non-compliant if their assessment demands a category, so get the specifier to accept it before you start.');
    out.push(DISCLAIM);

    return wrap(out.join('\n'), prov, { regime: 'contract', category: c.name, crib: c.crib, tests: c.tests, category_confirmed: !unknown });
  }

  // Domestic regime
  const sit = a.situation || 'recover';
  const made = a.made || 'post-1950';
  const item = a.item || 'seating';
  const out = [];
  let scope = 'in scope';

  if (sit === 'hobby') {
    scope = 'outside the regulations';
    out.push('**Outside the Regulations \u2014 your own furniture, your own home.**', '',
      'The Regulations govern supply in the course of business. Reupholstering your own furniture for your own use is not a supply, so they do not bite on the work itself. Two things still matter:', '',
      '- The **materials you buy** are still covered. A UK supplier selling you foam or fabric for upholstery use must supply compliant goods, so buy from proper trade suppliers and keep the receipts.',
      '- If you ever **sell or give the piece away through any business or trade activity**, including online marketplaces run as a business, it must comply at that point. If there is any chance of that, build it compliant now.', DISCLAIM);
    return wrap(out.join('\n'), prov, { regime: 'domestic', scope, situation: sit });
  }
  if (made === 'pre-1950') {
    scope = 'excluded \u2014 pre-1950';
    out.push('**Excluded \u2014 made before 1950.**', '',
      'Goods made before 1950, and the supply of materials for reupholstering furniture made before 1950, are excluded from the Regulations. Antique restoration is deliberately carved out so period pieces are not forced into modern materials.', '',
      '- **Be sure of the date.** Old-looking is not pre-1950. If challenged you would want to show the piece\u2019s age, so note it on the job sheet.',
      '- **Good practice anyway.** Many workshops use compliant fillings even on exempt pieces. It costs little and removes all doubt, and traditional horsehair over sprung construction is itself far less flammable than old foam.',
      '- If the piece is for a **rental or holiday let**, landlords often require compliance regardless of the exclusion. Check the letting agent\u2019s policy.', DISCLAIM);
    return wrap(out.join('\n'), prov, { regime: 'domestic', scope, made });
  }
  if (item === 'garden') {
    out.push('**Depends on the piece \u2014 garden and outdoor furniture.**', '',
      'Outdoor furniture is only outside the Regulations if it is **not suitable for use in a dwelling**. A rattan set or bench cushion that could perfectly well live in a conservatory or lounge is, in practice, in scope. The safe test at the bench: if a customer could reasonably bring it indoors, treat it as covered \u2014 compliant fillings and a compliant cover route.', '');
    scope = 'depends on the piece';
  } else if (item === 'baby') {
    out.push('**Check the 2025 exclusions list \u2014 baby and young children\u2019s items.**', '',
      'The October 2025 amendment removed a specific list of baby and young children\u2019s products from the Regulations\u2019 scope: certain small mattresses, upholstery for baby furniture, cots and cribs and similar. Whether your item is on the list turns on exact product definitions and dimensions, so check the amendment or the current FIRA guide before deciding, and note the reasoning on the job sheet. If it is not on the list, the normal obligations below apply.', '');
    scope = 'check the exclusions list';
  } else {
    const heads = {
      recover: 'Reupholstery in the course of business',
      new: 'New furniture placed on the market',
      secondhand: 'Second-hand furniture supplied in business',
      letting: 'Furniture in let accommodation',
      caravan: 'Caravan and holiday-home upholstery'
    };
    const intro = {
      recover: 'Reupholstery services are expressly within the Regulations: the materials you supply on the job must comply.',
      new: 'As the first supplier of new furniture you carry the full set of obligations, including the permanent label and five years of records.',
      secondhand: 'Second-hand upholstered furniture supplied in the course of business \u2014 shops, auctioneers, charities \u2014 must meet the same standards as new. The pre-1950 exclusion is the only age-based escape.',
      letting: 'The Regulations apply to furniture provided in accommodation let in the course of business: holiday lets, furnished rentals, flats and bed-sits. Landlords and agents are responsible for the furniture they provide complying.',
      caravan: 'Upholstery in caravans is within the Regulations \u2014 the same cover and filling requirements as domestic furniture. Holiday-park operators typically also impose their own compliance paperwork on contractors, so keep certificates for every material.'
    };
    out.push(`**In scope \u2014 the Regulations apply. ${heads[sit] || heads.recover}.**`, '', intro[sit] || intro.recover, '');
  }

  out.push('**Fillings:**',
    '- Every filling you supply \u2014 foam, wadding, fibre \u2014 must meet the ignition requirements. Buy CMHR (combustion-modified high resilience) foam and compliant waddings from suppliers who certify them, and keep the certificates.');
  if (item === 'mattress') out.push('- Mattresses and bed bases are tested to BS 7177, and are exempt from the permanent label.');
  out.push('');

  out.push('**The cover:**');
  const ce = a.cover_evidence;
  if (ce === 'composite') out.push('You are in the right position: a certificate covering the exact cover-and-filling combination you are fitting. Record the certificate number and the filling it was tested with.');
  else if (ce === 'alone') out.push('A fabric-only certificate is a start, but the match test is run on the composite. Either fit the filling it was certificated with, or use a certificated FR interliner between cover and filling. Note which route you took on the job record.');
  else if (ce === 'vinyl') out.push('Contract vinyl and FR leather generally satisfy the cover requirement, but the evidence still needs to describe the composite you are building, not the face material alone.');
  else out.push('**Unknown cover \u2014 the common trap.** A customer\u2019s own fabric with no fire evidence cannot be certified. The standard route is a certificated FR interliner fitted between the cover and the filling, which brings most covers up to compliance. Record what you fitted, and if you cannot make it compliant, say so in writing before you start rather than after.');
  out.push('');

  out.push('**Labels and records:**');
  if (sit === 'new') {
    out.push(`- **Permanent label:** required on new furniture${item === 'mattress' ? ', except mattresses and bed bases, which are exempt' : ''}. Follow the current FIRA guide for the exact format and wording.`,
      '- **Display label:** no longer required. The requirement was removed by the October 2025 amendment.',
      '- **Records:** keep compliance records \u2014 test certificates and supplier declarations \u2014 for five years.');
  } else {
    out.push('- **Statutory labels:** the permanent-label requirement is aimed at the first supplier of new furniture. It does not attach to reupholstery or second-hand supply in the same way. If an original permanent label survives on the piece, leave it in place.',
      '- **Records:** keep a written record of every material you fitted, with certificate or batch references. It is your evidence of compliance if you are ever asked.');
  }
  out.push(DISCLAIM);

  return wrap(out.join('\n'), prov, { regime: 'domestic', scope, situation: sit, made, item, cover_evidence: ce || null });
}


function toolFindBusiness(a) {
  const prov = { source_tool: 'Business Hub', source_url: SITE + '/business/',
                 chapter: 'Business Hub' };

  if (a.list_all || !a.topic) {
    const bySection = {};
    for (const x of BUSINESS_ARTICLES) (bySection[x.section] = bySection[x.section] || []).push(x);
    const lines = ['The Learn to Upholster Business Hub \u2014 ' + BUSINESS_ARTICLES.length + ' guides.', ''];
    for (const sec of Object.keys(bySection)) {
      lines.push('**' + sec + '**');
      for (const x of bySection[sec]) lines.push('- ' + x.title + ' \u2014 ' + x.question + '  \n  ' + x.url);
      lines.push('');
    }
    lines.push('Ask again with a topic for the full answer to any of these.');
    return wrap(lines.join('\n'), prov, { articles: BUSINESS_ARTICLES.map(x => ({ title: x.title, question: x.question, url: x.url, section: x.section })) });
  }

  const q = String(a.topic).toLowerCase().replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
  const words = q.split(' ').filter(w => w.length > 2 && !STOP.has(w));

  const scored = BUSINESS_ARTICLES.map(x => {
    const hay = (x.title + ' ' + x.question + ' ' + x.answer + ' ' + x.section).toLowerCase();
    let score = 0;
    for (const w of words) if (hay.indexOf(w) !== -1) score += w.length;
    if (x.title.toLowerCase().indexOf(q) !== -1 || x.question.toLowerCase().indexOf(q) !== -1) score += 20;
    return { x, score };
  }).filter(r => r.score > 0).sort((r1, r2) => r2.score - r1.score).slice(0, 3);

  if (!scored.length) {
    const titles = BUSINESS_ARTICLES.map(x => '- ' + x.title).join('\n');
    return wrap('Nothing in the Business Hub matches that directly. What it does cover:\n\n' + titles +
      '\n\nFor questions about how to do upholstery rather than how to run the business, use ask_the_book.',
      prov, { matches: [] });
  }

  const out = [];
  for (const r of scored) {
    out.push('## ' + r.x.title);
    out.push('**' + r.x.question + '**');
    out.push('');
    out.push(r.x.answer);
    out.push('');
    out.push('Full article: ' + r.x.url);
    out.push('');
  }
  out.push('These are the short answers. Each URL has the full treatment.');

  return wrap(out.join('\n'), prov, {
    matches: scored.map(r => ({ title: r.x.title, question: r.x.question,
                                answer: r.x.answer, url: r.x.url, section: r.x.section })),
    hub_updated: BUSINESS_UPDATED
  });
}

const STOP = new Set(['the','and','for','how','what','why','should','with','from','are','can',
  'you','your','have','has','not','about','when','does','did','get','got','job','jobs']);

/* ------------------------------------------------------------------ *
 * Dispatch                                                            *
 * ------------------------------------------------------------------ */

const HANDLERS = {
  find_business_guidance: toolFindBusiness,
  calculate_fabric: toolCalculateFabric,
  estimate_job_cost: toolEstimateJobCost,
  calculate_leather: toolCalculateLeather,
  calculate_deep_buttoning: toolCalculateDeepButtoning,
  specify_foam: toolSpecifyFoam,
  check_fire_regulations: toolCheckFire
};

export function isCalcTool(name) {
  return Object.prototype.hasOwnProperty.call(HANDLERS, name);
}

export function runCalcTool(name, args) {
  const fn = HANDLERS[name];
  if (!fn) return fail(`Unknown tool: ${name}`);
  try {
    return fn(args || {});
  } catch (e) {
    return fail('That did not compute: ' + (e && e.message ? e.message : 'unexpected error') + '. Check the arguments and try again.');
  }
}
