// GET /go/amazon?q=<search terms>&u=<encoded original amazon.co.uk URL>
// UK & Ireland visitors: 302 to the original tagged amazon.co.uk link (zero change).
// Everyone else: 302 to a search on their home Amazon marketplace, with the
// local Associates tag once one exists in TAGS below.
//
// TO ADD A MARKETPLACE TAG LATER: register the Associates account for that
// country, then put the tag in TAGS and redeploy. One line per country.

const TAGS = {
  'co.uk': '842699-21',  // UK - live
  'com':   '',           // US  - add tag after registering US Associates
  'ca':    '',           // Canada
  'com.au':'',           // Australia
  'de':    '',           // Germany
  'fr':    '',           // France
  'it':    '',           // Italy
  'es':    '',           // Spain
  'nl':    '',           // Netherlands
};

const MARKET = {
  US:'com', CA:'ca', AU:'com.au', NZ:'com.au',
  DE:'de', AT:'de', CH:'de',
  FR:'fr', BE:'fr', LU:'fr',
  IT:'it', ES:'es', PT:'es', NL:'nl',
  GB:'co.uk', IE:'co.uk', JE:'co.uk', GG:'co.uk', IM:'co.uk',
};

export async function onRequestGet(context) {
  const { request } = context;
  const url = new URL(request.url);
  const q = url.searchParams.get('q') || 'upholstery tools';
  const u = url.searchParams.get('u') || '';
  const country = (request.cf && request.cf.country) || 'GB';
  const domain = MARKET[country] || 'com';

  let dest;
  if (domain === 'co.uk' && u) {
    dest = u;  // original tagged UK link, untouched
  } else {
    const tag = TAGS[domain];
    dest = `https://www.amazon.${domain}/s?k=${encodeURIComponent(q)}` +
           (tag ? `&tag=${encodeURIComponent(tag)}` : '');
  }
  return new Response(null, {
    status: 302,
    headers: { 'Location': dest, 'Cache-Control': 'no-store', 'Vary': 'CF-IPCountry',
               'X-Robots-Tag': 'noindex, nofollow' },
  });
}
