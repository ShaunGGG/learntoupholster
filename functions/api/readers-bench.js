// Reader's Bench — reader-submitted first projects, moderated by email.
// Reuses existing infrastructure only:
//   KV binding: VISUALISER_KV   (records under rb:*)
//   Secrets:    RESEND_API_KEY  (moderation + featured emails)
//               TURNSTILE_SECRET (optional — verified only if set)
// No new namespaces, buckets or secrets required.

const MOD_EMAIL = 'shaun@greenwoodupholstery.com';
// Sender must be Resend-verified; greenwoodupholstery.com is. Override with MAIL_FROM once
// learntoupholster.com is verified in Resend.
const FROM_DEFAULT = 'Learn to Upholster <quotes@greenwoodupholstery.com>';
const SITE = 'https://www.learntoupholster.com';
const MAX_IMG = 6 * 1024 * 1024;          // 6 MB after client-side resize
const TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const PENDING_TTL = 60 * 60 * 24 * 90;    // pending auto-expires after 90 days

const esc = (s) => String(s || '').replace(/[&<>"']/g, (c) =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });

const page = (title, body) =>
  new Response(`<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex">
<body style="font-family:Georgia,serif;background:#FBF6ED;color:#2A2622;display:grid;place-items:center;min-height:90vh">
<div style="max-width:34rem;text-align:center;padding:2rem"><h1 style="color:#2F4A3A">${title}</h1><p style="font-size:1.15rem">${body}</p>
<p><a href="${SITE}/readers-bench" style="color:#2F4A3A">Back to the Reader&#8217;s Bench</a></p></div>`,
    { headers: { 'content-type': 'text/html; charset=utf-8' } });

// ---------------------------------------------------------------- GET
export async function onRequestGet({ request, env }) {
  const u = new URL(request.url);
  const action = u.searchParams.get('action') || 'list';

  if (action === 'list') {
    const ids = JSON.parse((await env.VISUALISER_KV.get('rb:approved')) || '[]');
    const items = [];
    for (const id of ids.slice(0, 60)) {
      const rec = await env.VISUALISER_KV.get('rb:sub:' + id, 'json');
      if (rec && rec.status === 'approved')
        items.push({ id: rec.id, name: rec.name, town: rec.town, note: rec.note, ts: rec.ts });
    }
    return new Response(JSON.stringify({ items }), {
      headers: { 'content-type': 'application/json', 'cache-control': 'public, max-age=300' } });
  }

  if (action === 'image') {
    const id = (u.searchParams.get('id') || '').replace(/[^a-z0-9-]/gi, '');
    const rec = await env.VISUALISER_KV.get('rb:sub:' + id, 'json');
    if (!rec) return new Response('Not found', { status: 404 });
    const ok = rec.status === 'approved' || u.searchParams.get('token') === rec.token;
    if (!ok) return new Response('Not found', { status: 404 });
    const { value, metadata } = await env.VISUALISER_KV.getWithMetadata('rb:img:' + id, 'arrayBuffer');
    if (!value) return new Response('Not found', { status: 404 });
    return new Response(value, { headers: {
      'content-type': (metadata && metadata.ct) || 'image/jpeg',
      'cache-control': rec.status === 'approved' ? 'public, max-age=86400' : 'no-store' } });
  }

  if (action === 'moderate') {
    const id = (u.searchParams.get('id') || '').replace(/[^a-z0-9-]/gi, '');
    const token = u.searchParams.get('token') || '';
    const decision = u.searchParams.get('decision');
    const rec = await env.VISUALISER_KV.get('rb:sub:' + id, 'json');
    if (!rec || token !== rec.token) return page('Link not valid', 'This moderation link has expired or already been used.');

    if (decision === 'approve') {
      if (rec.status !== 'approved') {
        rec.status = 'approved';
        const img = await env.VISUALISER_KV.get('rb:img:' + id, 'arrayBuffer');
        await env.VISUALISER_KV.put('rb:img:' + id, img, { metadata: { ct: rec.ct } }); // drop TTL
        await env.VISUALISER_KV.put('rb:sub:' + id, JSON.stringify(rec));
        const ids = JSON.parse((await env.VISUALISER_KV.get('rb:approved')) || '[]');
        if (!ids.includes(id)) ids.unshift(id);
        await env.VISUALISER_KV.put('rb:approved', JSON.stringify(ids));
        if (rec.email) await sendEmail(env, rec.email, 'Your seat is on the Reader\u2019s Bench',
          `<p>Hello ${esc(rec.name)},</p>
           <p>Your first seat has been checked over and it&#8217;s now up on the Reader&#8217;s Bench for everyone to see:</p>
           <p><a href="${SITE}/readers-bench">${SITE}/readers-bench</a></p>
           <p>Well made. Now do four more &#8212; one seat teaches you the sequence; five teach you tension.</p>
           <p>&#8212; Shaun Greenwood, Learn to Upholster</p>`);
      }
      return page('Approved', `${esc(rec.name)}&#8217;s seat is now live on the bench, and they&#8217;ve been emailed.`);
    }
    if (decision === 'reject') {
      await env.VISUALISER_KV.delete('rb:sub:' + id);
      await env.VISUALISER_KV.delete('rb:img:' + id);
      const ids = JSON.parse((await env.VISUALISER_KV.get('rb:approved')) || '[]');
      await env.VISUALISER_KV.put('rb:approved', JSON.stringify(ids.filter((x) => x !== id)));
      return page('Removed', 'The submission and its photo have been deleted.');
    }
    return page('No decision', 'The link was missing an approve/reject decision.');
  }

  return new Response('Not found', { status: 404 });
}

// ---------------------------------------------------------------- POST
export async function onRequestPost({ request, env }) {
  let form;
  try { form = await request.formData(); }
  catch { return json({ ok: false, error: 'Could not read the form.' }, 400); }

  // honeypot
  if (form.get('website')) return json({ ok: true });

  // rate limit: 3 submissions / day / IP
  const ip = request.headers.get('cf-connecting-ip') || 'unknown';
  const day = new Date().toISOString().slice(0, 10);
  const rk = `rb:rate:${ip}:${day}`;
  const used = parseInt((await env.VISUALISER_KV.get(rk)) || '0', 10);
  if (used >= 3) return json({ ok: false, error: 'That\u2019s three today \u2014 the bench will still be here tomorrow.' }, 429);

  // optional Turnstile (verified only when the secret is configured)
  if (env.TURNSTILE_SECRET) {
    const token = form.get('cf-turnstile-response');
    if (token) {
      const v = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ secret: env.TURNSTILE_SECRET, response: token, remoteip: ip }) })
        .then((r) => r.json()).catch(() => ({ success: true }));
      if (v.success === false) return json({ ok: false, error: 'The anti-spam check failed \u2014 please try again.' }, 400);
    }
  }

  const name = String(form.get('name') || '').trim().slice(0, 40);
  const town = String(form.get('town') || '').trim().slice(0, 40);
  const email = String(form.get('email') || '').trim().slice(0, 100);
  const note = String(form.get('note') || '').trim().slice(0, 300);
  const consent = form.get('consent');
  const photo = form.get('photo');

  if (!name || !town) return json({ ok: false, error: 'A first name and a town, please \u2014 that\u2019s how the card reads.' }, 400);
  if (!consent) return json({ ok: false, error: 'Please tick the box confirming it\u2019s your own photo.' }, 400);
  if (!photo || typeof photo === 'string') return json({ ok: false, error: 'The photo didn\u2019t arrive \u2014 please attach one.' }, 400);
  if (!TYPES.includes(photo.type)) return json({ ok: false, error: 'JPEG, PNG or WebP photos only.' }, 400);
  if (photo.size > MAX_IMG) return json({ ok: false, error: 'That photo is over 6 MB \u2014 a smaller export will do fine.' }, 400);

  const id = crypto.randomUUID();
  const token = crypto.randomUUID().replace(/-/g, '');
  const bytes = await photo.arrayBuffer();
  const rec = { id, token, name, town, email, note, ct: photo.type,
                ts: Date.now(), status: 'pending' };

  await env.VISUALISER_KV.put('rb:img:' + id, bytes,
    { expirationTtl: PENDING_TTL, metadata: { ct: photo.type } });
  await env.VISUALISER_KV.put('rb:sub:' + id, JSON.stringify(rec), { expirationTtl: PENDING_TTL });
  await env.VISUALISER_KV.put(rk, String(used + 1), { expirationTtl: 90000 });

  const mod = `${SITE}/api/readers-bench?action=moderate&id=${id}&token=${token}`;
  await sendEmail(env, MOD_EMAIL, `Reader\u2019s Bench submission \u2014 ${name}, ${town}`,
    `<p><strong>${esc(name)}</strong>, ${esc(town)}${email ? ` &middot; <a href="mailto:${esc(email)}">${esc(email)}</a>` : ''}</p>
     ${note ? `<p style="font-style:italic">&#8220;${esc(note)}&#8221;</p>` : ''}
     <p><img src="${SITE}/api/readers-bench?action=image&id=${id}&token=${token}" style="max-width:480px;border:1px solid #ccc" alt="submission"></p>
     <p style="font-size:1.1rem">
       <a href="${mod}&decision=approve" style="background:#2F4A3A;color:#FBF6ED;padding:.6rem 1.2rem;text-decoration:none;border-radius:4px">Approve &#10003;</a>
       &nbsp;&nbsp;
       <a href="${mod}&decision=reject" style="background:#B5552D;color:#FBF6ED;padding:.6rem 1.2rem;text-decoration:none;border-radius:4px">Reject &#10007;</a>
     </p>
     <p style="color:#777">Nothing appears on the site until you approve it. Unmoderated submissions delete themselves after 90 days.</p>`);

  return json({ ok: true });
}

async function sendEmail(env, to, subject, html) {
  if (!env.RESEND_API_KEY) return;
  try {
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { 'content-type': 'application/json', authorization: `Bearer ${env.RESEND_API_KEY}` },
      body: JSON.stringify({ from: env.MAIL_FROM || FROM_DEFAULT, to: [to], subject, html }),
    });
  } catch { /* email failure must never lose a submission */ }
}
