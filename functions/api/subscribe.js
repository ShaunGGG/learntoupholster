// POST /api/subscribe  { email, source?, consent? }
// GET  /api/subscribe?unsub=<email>&t=<token>   one-click unsubscribe
//
// Writes the signup to D1 (SURVEY_DB.subscribers), adds the contact to a
// Resend audience if RESEND_AUDIENCE_ID is set, and still emails Pat so the
// existing habit of watching the inbox keeps working.
//
// Bindings / secrets used:
//   SURVEY_DB           D1  (already bound)
//   RESEND_API_KEY      secret (already set)
//   RESEND_AUDIENCE_ID  optional — if absent, the D1 write still happens and
//                       resend_synced stays 0 so you can back-fill later
//   UNSUB_SECRET        optional — signs unsubscribe links; falls back to
//                       RESEND_API_KEY so the link works without extra setup
//
// Deliberately single opt-in: the list is your own audience, the wording on
// the form is explicit, and every send carries an unsubscribe link. Storing
// consent_text means that if the form copy changes you still know what each
// person actually agreed to.

const FROM = 'Learn to Upholster <quotes@greenwoodupholstery.com>';
const NOTIFY = ['pat@greenwoodupholstery.com', 'shaun@greenwoodupholstery.com'];
const SITE = 'https://www.learntoupholster.com';

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { 'content-type': 'application/json' },
  });

const esc = (s) =>
  String(s ?? '').replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const page = (title, body) =>
  new Response(
    `<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex">
<meta name="viewport" content="width=device-width,initial-scale=1">
<body style="font-family:Georgia,serif;background:#FBF6ED;color:#2A2622;display:grid;place-items:center;min-height:90vh;margin:0">
<div style="max-width:34rem;text-align:center;padding:2rem">
<h1 style="color:#2F4A3A;font-weight:500">${title}</h1>
<p style="font-size:1.1rem;line-height:1.6">${body}</p>
<p><a href="${SITE}" style="color:#2F4A3A">Back to Learn to Upholster</a></p></div>`,
    { headers: { 'content-type': 'text/html; charset=utf-8' } }
  );

async function hmac(secret, payload) {
  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(String(secret || '')),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(payload));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

const unsubSecret = (env) => env.UNSUB_SECRET || env.RESEND_API_KEY || '';

// ------------------------------------------------------------------ POST

export async function onRequestPost(context) {
  const { request, env } = context;

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'Bad request' }, 400);
  }

  const email = String(body.email || '').trim().slice(0, 200);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
    return json({ error: 'Please enter a valid email address' }, 400);
  }

  const source = String(body.source || '').trim().slice(0, 200) || null;
  const consent = String(body.consent || '').trim().slice(0, 500) || null;

  // Coarse abuse signal only — hashed, never stored raw.
  let ipHash = null;
  try {
    const ip = request.headers.get('CF-Connecting-IP') || '';
    if (ip) ipHash = (await hmac(unsubSecret(env), ip)).slice(0, 32);
  } catch { /* not worth failing a signup over */ }

  // --- D1 -----------------------------------------------------------------
  // A repeat signup is almost always someone who forgot, or someone coming
  // back after unsubscribing. Neither should error: update in place and
  // clear any previous unsubscribe.
  let stored = false;
  let alreadyOn = false;
  if (env.SURVEY_DB) {
    try {
      const existing = await env.SURVEY_DB
        .prepare('SELECT id, unsubscribed_at FROM subscribers WHERE lower(email) = lower(?)')
        .bind(email)
        .first();

      if (existing) {
        alreadyOn = !existing.unsubscribed_at;
        await env.SURVEY_DB
          .prepare(
            `UPDATE subscribers
                SET unsubscribed_at = NULL,
                    source = COALESCE(?, source),
                    consent_text = COALESCE(?, consent_text)
              WHERE id = ?`
          )
          .bind(source, consent, existing.id)
          .run();
      } else {
        await env.SURVEY_DB
          .prepare(
            `INSERT INTO subscribers (email, source, consent_text, ip_hash)
             VALUES (?, ?, ?, ?)`
          )
          .bind(email, source, consent, ipHash)
          .run();
      }
      stored = true;
    } catch (e) {
      console.error('subscriber store failed:', e && e.message);
    }
  }

  // --- Resend audience ----------------------------------------------------
  // Optional. If the audience id is not set the D1 row still exists with
  // resend_synced = 0, so nothing is lost and it can be back-filled.
  if (env.RESEND_API_KEY && env.RESEND_AUDIENCE_ID) {
    try {
      const r = await fetch(
        `https://api.resend.com/audiences/${env.RESEND_AUDIENCE_ID}/contacts`,
        {
          method: 'POST',
          headers: {
            'content-type': 'application/json',
            authorization: `Bearer ${env.RESEND_API_KEY}`,
          },
          body: JSON.stringify({ email, unsubscribed: false }),
        }
      );
      if (r.ok && env.SURVEY_DB) {
        await env.SURVEY_DB
          .prepare('UPDATE subscribers SET resend_synced = 1 WHERE lower(email) = lower(?)')
          .bind(email)
          .run();
      }
    } catch (e) {
      console.error('resend audience sync failed:', e && e.message);
    }
  }

  // --- Notify -------------------------------------------------------------
  // Kept from the original route. Now includes the running total, so the
  // email answers "how many are we on?" without opening anything.
  if (env.RESEND_API_KEY) {
    let total = null;
    if (env.SURVEY_DB) {
      try {
        const row = await env.SURVEY_DB
          .prepare('SELECT COUNT(*) n FROM subscribers WHERE unsubscribed_at IS NULL')
          .first();
        total = row && row.n;
      } catch { /* count is a nicety, not a reason to fail */ }
    }
    try {
      await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
          authorization: `Bearer ${env.RESEND_API_KEY}`,
        },
        body: JSON.stringify({
          from: FROM,
          to: NOTIFY,
          subject: 'New Learn to Upholster mailing list signup',
          text:
            `${email}\n` +
            (source ? `Signed up from: ${source}\n` : '') +
            (total != null ? `\nList now stands at ${total}.\n` : '') +
            (stored ? '' : '\nWARNING: this was NOT saved to the database.\n'),
        }),
      });
    } catch (e) {
      console.error('signup notify failed:', e && e.message);
    }
  }

  return json({ ok: true, already: alreadyOn });
}

// ------------------------------------------------------------------- GET
// One-click unsubscribe. The link is signed, so nobody can unsubscribe
// somebody else by guessing the URL.

export async function onRequestGet(context) {
  const { request, env } = context;
  const u = new URL(request.url);
  const email = String(u.searchParams.get('unsub') || '').trim().slice(0, 200);
  const token = String(u.searchParams.get('t') || '');

  if (!email) return page('Nothing to do', 'No address was given.');

  const expected = await hmac(unsubSecret(env), email.toLowerCase());
  if (token !== expected) {
    return page(
      'That link did not work',
      'It may have been truncated by an email client. Reply to any of our emails and we will take you off by hand.'
    );
  }

  if (env.SURVEY_DB) {
    try {
      await env.SURVEY_DB
        .prepare(
          `UPDATE subscribers SET unsubscribed_at = datetime('now')
            WHERE lower(email) = lower(?)`
        )
        .bind(email)
        .run();
    } catch (e) {
      console.error('unsubscribe failed:', e && e.message);
    }
  }

  if (env.RESEND_API_KEY && env.RESEND_AUDIENCE_ID) {
    try {
      await fetch(
        `https://api.resend.com/audiences/${env.RESEND_AUDIENCE_ID}/contacts/${encodeURIComponent(email)}`,
        {
          method: 'PATCH',
          headers: {
            'content-type': 'application/json',
            authorization: `Bearer ${env.RESEND_API_KEY}`,
          },
          body: JSON.stringify({ unsubscribed: true }),
        }
      );
    } catch (e) {
      console.error('resend unsubscribe failed:', e && e.message);
    }
  }

  return page(
    'You are unsubscribed',
    `We will not email <strong>${esc(email)}</strong> again. The site stays free to read, and you are welcome back any time.`
  );
}
