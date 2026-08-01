// functions/go/amazon.js
//
// Affiliate redirect. The previous version discarded the `u` parameter, rebuilt
// the URL from `q`, and sent everyone to amazon.com with no tag at all — so all
// 333 affiliate links on the site were unattributed and earned nothing.
//
// This keeps the useful behaviour (never redirects off Amazon, so it can't be
// abused as an open redirect) and fixes the attribution.
//
// TO EARN ON US TRAFFIC you need a separate Amazon Associates US account — a
// UK "-21" tag is not valid on amazon.com. Add the tag below and it switches on.
// Until a locale has a tag, visitors go to their own store untagged, which is
// what happens today: no revenue, but no worse an experience either.

// Tags are keyed by STORE, not by country. An Irish visitor shops on
// amazon.co.uk, where the UK tag is perfectly valid — keying by country meant
// Ireland arrived untagged for no reason.
const STORE_TAGS = {
  'www.amazon.co.uk': '842699-21',   // active — covers GB and IE
  'www.amazon.com': '',              // needs Associates US        (tag ends -20)
  'www.amazon.ca': '',               // needs Associates CA        (-20)
  'www.amazon.com.au': '',           // needs Associates AU        (-22)
  'www.amazon.de': '',               // needs Associates DE        — covers DE and AT
  'www.amazon.fr': '',
  'www.amazon.it': '',
  'www.amazon.es': '',
  'www.amazon.nl': '',
  'www.amazon.se': '',
  'www.amazon.pl': '',
  'www.amazon.com.be': '',
  'www.amazon.co.jp': '',
  'www.amazon.in': '',
};

// Which Amazon store serves each country.
const STORES = {
  GB: 'www.amazon.co.uk', IE: 'www.amazon.co.uk',
  US: 'www.amazon.com',
  CA: 'www.amazon.ca',
  AU: 'www.amazon.com.au',
  DE: 'www.amazon.de', AT: 'www.amazon.de',
  FR: 'www.amazon.fr', BE: 'www.amazon.com.be',
  IT: 'www.amazon.it',
  ES: 'www.amazon.es',
  NL: 'www.amazon.nl',
  SE: 'www.amazon.se',
  PL: 'www.amazon.pl',
  JP: 'www.amazon.co.jp',
  IN: 'www.amazon.in',
};

const DEFAULT_COUNTRY = 'GB';
const AMAZON_HOST = /(^|\.)amazon\.(co\.uk|com|ca|com\.au|de|fr|it|es|nl|se|pl|co\.jp|in|com\.be)$/i;

function targetFor(country) {
  const c = (country || '').toUpperCase();
  const store = STORES[c];
  if (store) {
    // Their own store, tagged if we hold a tag for it. Sending a US buyer to
    // amazon.co.uk to protect a tag they cannot use loses the click and the
    // goodwill, and earns nothing either way.
    return { host: store, tag: STORE_TAGS[store] || '', country: c };
  }
  // Nowhere we have a store mapping for: fall back to the home market, tagged.
  const home = STORES[DEFAULT_COUNTRY];
  return { host: home, tag: STORE_TAGS[home] || '', country: DEFAULT_COUNTRY };
}

export async function onRequestGet({ request }) {
  const url = new URL(request.url);
  const q = (url.searchParams.get('q') || '').trim();
  const u = url.searchParams.get('u');

  const country = request.headers.get('cf-ipcountry') || DEFAULT_COUNTRY;
  const { host, tag } = targetFor(country);

  // Work out the path and query to carry across to the visitor's store.
  let path = '/s';
  const params = new URLSearchParams();

  let handled = false;
  if (u) {
    try {
      const parsed = new URL(u);
      // Only ever follow Amazon. Anything else is discarded, which is what kept
      // the old version from being an open redirect.
      if (AMAZON_HOST.test(parsed.hostname)) {
        path = parsed.pathname || '/s';
        for (const [k, v] of parsed.searchParams) {
          if (k.toLowerCase() === 'tag') continue;   // re-applied per locale below
          params.set(k, v);
        }
        handled = true;
      }
    } catch (e) { /* malformed u: fall through to q */ }
  }

  if (!handled) {
    if (!q) {
      return Response.redirect('https://' + host + '/', 302);
    }
    path = '/s';
    params.set('k', q);
  }

  if (tag) params.set('tag', tag);

  const dest = 'https://' + host + path + (params.toString() ? '?' + params.toString() : '');

  return new Response(null, {
    status: 302,
    headers: {
      Location: dest,
      // Affiliate destinations vary by visitor country, so never let an edge or
      // browser cache pin one country's redirect for everybody.
      'Cache-Control': 'no-store',
      'Referrer-Policy': 'no-referrer-when-downgrade',
      'X-Robots-Tag': 'noindex, nofollow',
    },
  });
}
