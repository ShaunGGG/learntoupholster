// POST /api/book-checkout — RETIRED 20260917-220824
//
// The wiro-bound workshop edition is no longer sold. The book is on Amazon in
// hardback, paperback and Kindle; /buy-the-book links straight there.
//
// This endpoint stays in place, returning 410, so a cached page or a bookmarked
// POST cannot start a Stripe session for a book that is not being printed.
// The original is in the .bak-wiro-20260917-220824 file beside this one.

export async function onRequestPost() {
  return new Response(
    JSON.stringify({ error: 'The workshop edition is no longer sold. The book is available on Amazon.' }),
    { status: 410, headers: { 'content-type': 'application/json' } }
  );
}

export async function onRequestGet() {
  return new Response('Gone', { status: 410 });
}
