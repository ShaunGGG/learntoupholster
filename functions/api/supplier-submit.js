// functions/api/supplier-submit.js
//
// Supplier submissions from /suppliers. Moderated: nothing reaches the public
// directory until it has been checked and added to supplier-data.py by hand.
// That is deliberate — the directory's whole value is that it is compiled
// rather than crowd-dumped.

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

const json = (o, s) => new Response(JSON.stringify(o), {
  status: s || 200,
  headers: Object.assign({ 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }, CORS),
});

function getDB(env) {
  return env.SURVEY_DB || env.ltu_survey || env.DB || null;
}

const COUNTRIES = ['GB','US','AU','NZ','CA','IE','ZA','OTHER'];
const CATS = ['traditional','foam','fabric','tools','sundries','auto'];

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

async function sha256(s) {
  const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join('');
}

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: CORS });
}

export async function onRequestPost({ request, env }) {
  const DB = getDB(env);
  if (!DB) return json({ error: 'Database not bound.' }, 500);

  let b;
  try { b = await request.json(); } catch { return json({ error: 'Bad JSON.' }, 400); }

  // Honeypot: hidden field, only a bot fills it.
  if (b.website_confirm) return json({ ok: true, recorded: false });

  const name = (b.name || '').trim().slice(0, 120);
  const url = (b.url || '').trim().slice(0, 300);
  const country = (b.country || '').trim().toUpperCase();
  const note = (b.note || '').trim().slice(0, 600);
  const cats = Array.isArray(b.cats) ? b.cats.filter(c => CATS.includes(c)).join(' ') : '';

  if (!name || !url || !country) return json({ error: 'Name, website and country are needed.' }, 400);
  if (!COUNTRIES.includes(country)) return json({ error: 'Unknown country.' }, 400);

  let host;
  try {
    const p = new URL(url);
    if (!/^https?:$/.test(p.protocol)) throw 0;
    host = p.hostname;
  } catch { return json({ error: 'That does not look like a web address.' }, 400); }

  const salt = env.SURVEY_SALT || 'ltu';
  const ipHash = await sha256(salt + (request.headers.get('cf-connecting-ip') || '0.0.0.0'));

  // Same supplier twice, or one person submitting a dozen, both get dropped quietly.
  const dupe = await DB.prepare(
    "SELECT 1 FROM supplier_submissions WHERE (host = ? OR ip_hash = ?) AND created_at > datetime('now','-1 day') LIMIT 1"
  ).bind(host, ipHash).first();
  if (dupe) return json({ ok: true, recorded: false, reason: 'already-submitted' });

  await DB.prepare(
    `INSERT INTO supplier_submissions
       (created_at, name, url, host, country, cats, note, ip_hash, status)
     VALUES (datetime('now'), ?, ?, ?, ?, ?, ?, ?, 'pending')`
  ).bind(name, url, host, country, cats, note, ipHash).run();

  const { n } = await DB.prepare(
    "SELECT COUNT(*) AS n FROM supplier_submissions WHERE status = 'pending'"
  ).first();

  // Tell Shaun. A moderation queue nobody is told about is a moderation queue
  // nobody empties. Fire and forget — a failed email must never lose the entry,
  // which is already safely in the database by this point.
  if (env.RESEND_API_KEY && env.NOTIFY_EMAIL) {
    const lines = [
      `<h2>New supplier submission</h2>`,
      `<p><strong>${escapeHtml(name)}</strong><br>`,
      `<a href="${escapeHtml(url)}">${escapeHtml(url)}</a><br>`,
      `Country: ${escapeHtml(country)}<br>`,
      `Supplies: ${escapeHtml(cats || 'not stated')}</p>`,
      note ? `<p><em>${escapeHtml(note)}</em></p>` : '',
      `<p>${n} submission${n === 1 ? '' : 's'} now waiting.</p>`,
      `<hr><p style="font-size:13px;color:#666">To approve: check the site is real, add it to `,
      `<code>supplier-data.py</code>, then:<br>`,
      `<code>npx wrangler d1 execute ltu-survey --remote --command `,
      `"UPDATE supplier_submissions SET status='added' WHERE id=(SELECT MAX(id) FROM supplier_submissions)"</code></p>`,
    ].join('');

    try {
      await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.RESEND_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          from: env.NOTIFY_FROM || 'Learn to Upholster <onboarding@resend.dev>',
          to: [env.NOTIFY_EMAIL],
          subject: `Supplier submission: ${name} (${country})`,
          html: lines,
        }),
      });
    } catch (e) {
      // Swallowed on purpose. The submission is saved either way.
    }
  }

  return json({ ok: true, recorded: true, pending: n });
}
