// POST /api/visualise — "See your chair in your fabric"
// Secrets: GEMINI_API_KEY, TURNSTILE_SECRET, RESEND_API_KEY (Turnstile no longer used)
// KV binding required: VISUALISER_KV  (rate limits + daily cap)
// Vars (optional): DAILY_CAP (default 100), HOURLY_TRIES (default 3),
//                  DAILY_SEED (default 61) — each day's counter starts at this many
//                  'already used', so the tool opens showing cap−seed available (39 of 100).

// Nano Banana 2 — best editing model in the flash tier. Falls back automatically
// to the previous model if Google retires the ID.
const MODEL = 'gemini-3.1-flash-image-preview';
const MODEL_LEGACY = 'gemini-2.5-flash-image';

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};
export async function onRequestGet(context) {
  const { env } = context;
  const cap = parseInt(env.DAILY_CAP || '100', 10);
  const seed = parseInt(env.DAILY_SEED || '61', 10);
  const raw = await env.VISUALISER_KV.get('day:' + new Date().toISOString().slice(0, 10));
  const used = raw === null ? seed : parseInt(raw, 10);
  return new Response(JSON.stringify({ remainingToday: Math.max(0, cap - used), cap }),
    { headers: { 'Content-Type': 'application/json', ...CORS } });
}

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: CORS });
}

async function sha(s) {
  const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(b)].slice(0, 12).map(x => x.toString(16).padStart(2, '0')).join('');
}

export async function onRequestPost(context) {
  const { env, request } = context;
  const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { 'Content-Type': 'application/json', ...CORS } });

  let body;
  try { body = await request.json(); } catch { return json({ error: 'Bad request' }, 400); }
  const { chair, fabric, email, hp, t0, token } = body || {};
  if (!chair || !fabric || !email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email))
    return json({ error: 'Please add both photos and a valid email.' }, 400);
  if (chair.length > 2_800_000 || fabric.length > 2_800_000)
    return json({ error: 'Images too large — please retry.' }, 400);

  // 1. Bot heuristics: honeypot must be empty, form must have taken >4s
  if (hp) return json({ error: 'Something went wrong - please retry.' }, 403);
  if (!t0 || Date.now() - t0 < 4000)
    return json({ error: 'That was quick! Give the photos a second, then try again.' }, 429);

  // 1b. Turnstile
  const tv = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ secret: env.TURNSTILE_SECRET, response: token,
      remoteip: request.headers.get('CF-Connecting-IP') }),
  }).then(r => r.json()).catch(() => ({ success: false }));
  if (!tv.success) return json({ error: 'Bot check failed - please refresh and retry.' }, 403);

  // 2. Global daily cap — the "cannot lose money" valve
  const cap = parseInt(env.DAILY_CAP || '100', 10);
  const seed = parseInt(env.DAILY_SEED || '61', 10);
  const dayKey = 'day:' + new Date().toISOString().slice(0, 10);
  const rawDay = await env.VISUALISER_KV.get(dayKey);
  const used = rawDay === null ? seed : parseInt(rawDay, 10);
  if (used >= cap)
    return json({ error: "Today's free visualisations are all used up — try again tomorrow!" }, 429);

  // 3. Per-user limit: 3/hour on email+IP
  const tries = parseInt(env.HOURLY_TRIES || '3', 10);
  const ip = request.headers.get('CF-Connecting-IP') || '';
  const uKey = 'u:' + await sha(email.toLowerCase().trim() + '|' + ip);
  const uUsed = parseInt((await env.VISUALISER_KV.get(uKey)) || '0', 10);
  if (uUsed >= tries)
    return json({ error: `That's ${tries} tries this hour — the next one unlocks shortly.` }, 429);

  // 4. Gemini: fabric onto chair
  const b64 = (d) => d.split(',')[1];
  const mime = (d) => (d.match(/^data:([^;]+);/) || [,'image/jpeg'])[1];
  const prompt =
    'Re-upholster the piece of furniture shown in IMAGE 1 using the fabric shown in IMAGE 2.\n\n' +
    'THIS IS A PHOTO-EDITING TASK, NOT A NEW PHOTOGRAPH. The output is IMAGE 1 itself with different fabric on ' +
    'the furniture. Everything about the photograph stays as it is: the same composition, the same crop, the same ' +
    'camera position, the same orientation, the same lighting and shadows, the same background and floor, the ' +
    'same objects in shot. Whatever is on the left of IMAGE 1 remains on the left. The piece faces the same way, ' +
    'at the same angle, in the same position in the frame. It is not re-photographed from another angle, not ' +
    'mirrored, not flipped, not rotated, not moved and not re-framed. Someone comparing the two pictures should ' +
    'see one difference only: the fabric.\n\n' +
    'FIRST, AND ABOVE EVERYTHING ELSE: the finished result is the same piece of furniture as IMAGE 1, with exactly ' +
    'the parts it already has and no others. Study IMAGE 1 and count what is actually there \u2014 the separate ' +
    'pieces, the seams, the edges, the trim, the details \u2014 and reproduce exactly that, no more and no fewer. ' +
    'The piece gains nothing and loses nothing.\n\n' +
    'Cover every upholstered surface visible in IMAGE 1 completely in the new fabric. Work from the photograph: ' +
    'whatever padded or fabric-covered areas that particular piece happens to have, cover those and only those. ' +
    'No upholstered surface may keep its original fabric, colour or pattern.\n\n' +
    'The construction must match IMAGE 1 exactly: the same panels, the same seam lines, the same edges and the ' +
    'same details. The only difference between IMAGE 1 and the finished result is the fabric covering it.\n\n' +
    'Keep everything else exactly as it is: the wooden or metal frame, the legs, any show-wood, the room, the ' +
    'background, the floor, the lighting, the shadows and the camera angle. Do not change the room. Scale the fabric pattern realistically for the size of ' +
    'the piece and follow its panels and seams so the cloth sits and drapes as real upholstery would. ' +
    'The result must be a photorealistic photograph of the same piece in the same place, visibly re-covered ' +
    'in the new fabric.';

  const buildBody = (m) => '{"contents":[{"parts":[' +
      '{"text":"IMAGE 1 \u2014 the furniture to re-cover:"},' +
      '{"inline_data":{"mime_type":"' + mime(chair) + '","data":"' + b64(chair) + '"}},' +
      '{"text":"IMAGE 2 \u2014 the fabric to use:"},' +
      '{"inline_data":{"mime_type":"' + mime(fabric) + '","data":"' + b64(fabric) + '"}},' +
      '{"text":' + JSON.stringify(prompt) + '}' +
      ']}],"generationConfig":{"temperature":0.25,"responseModalities":["TEXT","IMAGE"]}}';

  const call = (m) => fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${m}:generateContent?key=${env.GEMINI_API_KEY}`,
    { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: buildBody(m) });

  let gr = await call(MODEL);
  if (!gr.ok && (gr.status === 404 || gr.status === 400)) gr = await call(MODEL_LEGACY);
  if (!gr.ok) {
    const msg = (await gr.text()).slice(0, 200);
    return json({ error: 'The visualiser is having a moment — please try again in a minute. (' + gr.status + ')', detail: msg }, 502);
  }
  const gd = await gr.json();
  const parts = gd.candidates?.[0]?.content?.parts || [];
  const img = parts.find(p => p.inline_data || p.inlineData);
  if (!img) return json({ error: 'No image came back — try clearer photos (whole chair, flat swatch).' }, 502);
  const outData = (img.inline_data || img.inlineData).data;
  const outMime = (img.inline_data || img.inlineData).mime_type || (img.inline_data || img.inlineData).mimeType || 'image/png';

  // 5. Count usage only after success
  await env.VISUALISER_KV.put(dayKey, String(used + 1), { expirationTtl: 90000 });
  await env.VISUALISER_KV.put(uKey, String(uUsed + 1), { expirationTtl: 3600 });

  // 6. Email the result. Sender must be a Resend-verified domain: greenwoodupholstery.com
  // is verified and works; set MAIL_FROM (plaintext var) to switch to a learntoupholster.com
  // address once that domain is verified in Resend.
  let emailed = false;
  try {
    const er = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: env.MAIL_FROM || 'Learn to Upholster <quotes@greenwoodupholstery.com>',
      to: [email],
      subject: 'Your chair, in your fabric \u2014 from Learn to Upholster',
      html: `<p>Here it is \u2014 your fabric on your furniture (attached).</p>
<p><strong>Love it?</strong> <a href="https://www.learntoupholster.com/find-an-upholsterer">Find a professional upholsterer near you</a> \u2014 UK, US and worldwide \u2014 and they'll show you the real thing.</p>
<p>Work out the fabric you'd need with the <a href="https://www.learntoupholster.com/fabric-yardage">fabric calculator</a>, and if you'd like to learn the craft itself, it's all in <a href="https://www.learntoupholster.com/buy-the-book"><em>The Working Upholsterer's Bible</em></a>.</p>
<p style="background:#fff9ec;border-left:4px solid #C19A4B;padding:12px 14px"><strong>Ready for a quote?</strong> Copy this and send it with your photos to any upholsterer from the directory:</p>
<p style="background:#f7f2e7;padding:12px 14px;font-style:italic">\u201CHi \u2014 I\u2019m looking to have a piece reupholstered. I\u2019ve attached a photo of the piece and my fabric choice, plus an AI mock-up from learntoupholster.com. Could you give me a rough estimate for the work? I can work out the fabric quantity with their calculator if helpful.\u201D</p>
<p style="color:#7C8C5D;font-size:.9em">This is an AI impression to help you imagine the finish \u2014 pattern scale and seams are approximate. Your upholsterer will show you the real thing.</p>`,
      attachments: [{ filename: 'your-chair-in-your-fabric.png', content: outData }],
    }),
    });
    emailed = er.ok;
  } catch { /* image still returns even if email fails */ }

  return json({ image: `data:${outMime};base64,${outData}`, emailed, remaining: tries - uUsed - 1, remainingToday: Math.max(0, cap - used - 1) });
}
