// POST /api/subscribe  { email: "..." }
// Forwards mailing-list signups by email via Resend.
// Requires secret: RESEND_API_KEY
//   npx wrangler pages secret put RESEND_API_KEY --project-name=learntoupholster

export async function onRequestPost(context) {
  const { request, env } = context;
  const json = (obj, status = 200) =>
    new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });

  let body;
  try { body = await request.json(); } catch { return json({ error: 'Bad request' }, 400); }
  const email = String(body.email || '').trim().slice(0, 200);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return json({ error: 'Please enter a valid email address' }, 400);

  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { 'content-type': 'application/json', authorization: `Bearer ${env.RESEND_API_KEY}` },
    body: JSON.stringify({
      from: 'Learn to Upholster <quotes@greenwoodupholstery.com>',
      to: ['pat@greenwoodupholstery.com'],
      subject: 'New Learn to Upholster mailing list signup',
      text: `New signup for the Learn to Upholster tips list:\n\n${email}\n\nSource: learntoupholster.com`
    })
  });
  if (!res.ok) return json({ error: 'Something went wrong \u2014 please try again later.' }, 502);
  return json({ ok: true });
}
