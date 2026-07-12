// POST /api/visualise — "See your chair in your fabric"
// Secrets: GEMINI_API_KEY, TURNSTILE_SECRET, RESEND_API_KEY (Turnstile no longer used)
// KV binding required: VISUALISER_KV  (rate limits + daily cap)
// Vars (optional): DAILY_CAP (default 300), HOURLY_TRIES (default 3)

const MODEL = 'gemini-2.5-flash-image';

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};
export async function onRequestGet(context) {
  const { env } = context;
  const cap = parseInt(env.DAILY_CAP || '100', 10);
  const used = parseInt((await env.VISUALISER_KV.get('day:' + new Date().toISOString().slice(0, 10))) || '0', 10);
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
  const dayKey = 'day:' + new Date().toISOString().slice(0, 10);
  const used = parseInt((await env.VISUALISER_KV.get(dayKey)) || '0', 10);
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
  const prompt = 'Reupholster the piece of furniture in the first photo using the fabric shown in the ' +
    'second photo. Replace only the upholstered fabric surfaces; keep the wooden or metal frame, legs, ' +
    'the background, lighting and camera angle exactly as they are. Apply the fabric with a realistic ' +
    'pattern scale for the size of the furniture, following the panels and seams of the piece. ' +
    'Photorealistic result.';
  const gr = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${env.GEMINI_API_KEY}`,
    { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [
          { text: prompt },
          { inline_data: { mime_type: mime(chair), data: b64(chair) } },
          { inline_data: { mime_type: mime(fabric), data: b64(fabric) } },
        ]}],
        generationConfig: { responseModalities: ['TEXT', 'IMAGE'] },
      }) });
  if (!gr.ok) {
    const msg = (await gr.text()).slice(0, 200);
    return json({ error: 'The visualiser is having a moment — please try again. (' + gr.status + ')' , detail: msg }, 502);
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

  // 6. Email the result (fire and forget)
  context.waitUntil(fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: 'Learn to Upholster <tools@learntoupholster.com>',
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
  }).catch(() => {}));

  return json({ image: `data:${outMime};base64,${outData}`, remaining: tries - uUsed - 1, remainingToday: Math.max(0, cap - used - 1) });
}
