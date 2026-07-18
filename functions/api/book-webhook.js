// POST /api/book-webhook — Stripe webhook for completed book purchases.
// Secrets required:
//   STRIPE_WEBHOOK_SECRET   (from the webhook endpoint you create in Stripe)
//   RESEND_API_KEY          (order notifications)
//   BOOKVAULT_API_KEY       (optional until confirmed — orders email regardless)
// Optional vars:
//   BOOKVAULT_SKU           (the Product ID/SKU BookVault shows for the title)

async function verifyStripeSignature(payload, sigHeader, secret) {
  const parts = Object.fromEntries(sigHeader.split(',').map(p => p.split('=')));
  const signedPayload = `${parts.t}.${payload}`;
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const mac = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(signedPayload));
  const expected = [...new Uint8Array(mac)].map(b => b.toString(16).padStart(2, '0')).join('');
  return expected === parts.v1;
}

async function sendOrderEmail(env, s, bvResult) {
  const a = s.shipping_details?.address || s.customer_details?.address || {};
  const name = s.shipping_details?.name || s.customer_details?.name || 'Unknown';
  const lines = [
    `New book order — £${(s.amount_total / 100).toFixed(2)} paid`,
    ``,
    `Customer: ${name}`,
    `Email: ${s.customer_details?.email || 'n/a'}`,
    `Ship to: ${[a.line1, a.line2, a.city, a.postal_code, a.country].filter(Boolean).join(', ')}`,
    ``,
    `Stripe session: ${s.id}`,
    `BookVault: ${bvResult}`,
  ].join('\n');
  await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: env.MAIL_FROM || 'Learn to Upholster <quotes@greenwoodupholstery.com>',
      to: ['shaun@greenwoodupholstery.com'],
      subject: `Book order: ${name} — £${(s.amount_total / 100).toFixed(2)}`,
      text: lines,
    }),
  });
}

// ── BookVault fulfilment ─────────────────────────────────────────────
// Auth header format confirmed from BookVault help docs:
//   Authorization: basic bv_YOUR_API_KEY
// ENDPOINT AND PAYLOAD FIELD NAMES TO CONFIRM against the API docs linked
// from the portal Apps page before going live. The shape below follows
// their documented order model (title SKU + shipping address) and is
// isolated here so only this function needs touching.
async function placeBookvaultOrder(env, s) {
  if (!env.BOOKVAULT_API_KEY) return 'not attempted (no API key set)';
  const a = s.shipping_details?.address || {};
  const payload = {
    orderReference: s.id,
    items: [{ sku: env.BOOKVAULT_SKU || 'SET_BOOKVAULT_SKU', quantity: 1 }],
    shippingAddress: {
      name: s.shipping_details?.name || s.customer_details?.name,
      line1: a.line1, line2: a.line2 || '',
      city: a.city, postcode: a.postal_code, country: a.country,
    },
    email: s.customer_details?.email,
  };
  try {
    const r = await fetch('https://api.bookvault.app/api/v1/orders', {  // CONFIRM base URL in docs
      method: 'POST',
      headers: {
        'Authorization': `basic ${env.BOOKVAULT_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    const body = await r.text();
    return r.ok ? `order placed (${r.status})` : `FAILED ${r.status}: ${body.slice(0, 300)} — place manually in portal`;
  } catch (e) {
    return `FAILED (${e.message}) — place manually in portal`;
  }
}

export async function onRequestPost(context) {
  const { env, request } = context;
  const payload = await request.text();
  const sig = request.headers.get('stripe-signature') || '';
  const ok = await verifyStripeSignature(payload, sig, env.STRIPE_WEBHOOK_SECRET);
  if (!ok) return new Response('Bad signature', { status: 400 });

  const event = JSON.parse(payload);
  if (event.type === 'checkout.session.completed') {
    const s = event.data.object;
    if (s.metadata?.product === 'twub-wiro-2ed' && s.payment_status === 'paid') {
      const bvResult = await placeBookvaultOrder(env, s);
      await sendOrderEmail(env, s, bvResult);
    }
  }
  return new Response('ok');
}
