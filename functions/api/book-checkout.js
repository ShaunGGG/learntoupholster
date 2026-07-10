// POST /api/book-checkout  — creates a Stripe Checkout Session for the wiro edition
// Secrets required (Cloudflare Pages > Settings > Variables & Secrets):
//   STRIPE_SECRET_KEY
export async function onRequestPost(context) {
  const { env, request } = context;
  const origin = new URL(request.url).origin;

  const params = new URLSearchParams();
  params.append('mode', 'payment');
  params.append('success_url', `${origin}/buy-the-book?status=success`);
  params.append('cancel_url', `${origin}/buy-the-book?status=cancelled`);
  params.append('line_items[0][quantity]', '1');
  params.append('line_items[0][price_data][currency]', 'gbp');
  params.append('line_items[0][price_data][unit_amount]', '4499');
  params.append('line_items[0][price_data][product_data][name]',
    "The Working Upholsterer's Bible — Wiro-Bound Workshop Edition");
  params.append('line_items[0][price_data][product_data][description]',
    'A4 wire-bound, 188 pages, full colour. Printed to order in the UK.');
  params.append('line_items[0][price_data][product_data][images][0]',
    `${origin}/images/book-cover-green.jpg`);

  // Collect a shipping address everywhere BookVault ships
  params.append('shipping_address_collection[allowed_countries][0]', 'GB');
  params.append('shipping_address_collection[allowed_countries][1]', 'IE');
  params.append('shipping_address_collection[allowed_countries][2]', 'US');
  params.append('shipping_address_collection[allowed_countries][3]', 'AU');
  params.append('shipping_address_collection[allowed_countries][4]', 'NZ');
  params.append('shipping_address_collection[allowed_countries][5]', 'CA');
  params.append('shipping_address_collection[allowed_countries][6]', 'FR');
  params.append('shipping_address_collection[allowed_countries][7]', 'DE');
  params.append('shipping_address_collection[allowed_countries][8]', 'NL');
  params.append('shipping_address_collection[allowed_countries][9]', 'ES');
  params.append('shipping_address_collection[allowed_countries][10]', 'IT');

  // Shipping options: free UK, flat rates abroad (tune once real BV rates are known)
  params.append('shipping_options[0][shipping_rate_data][display_name]', 'UK delivery (free)');
  params.append('shipping_options[0][shipping_rate_data][type]', 'fixed_amount');
  params.append('shipping_options[0][shipping_rate_data][fixed_amount][amount]', '0');
  params.append('shipping_options[0][shipping_rate_data][fixed_amount][currency]', 'gbp');
  params.append('shipping_options[1][shipping_rate_data][display_name]', 'Europe');
  params.append('shipping_options[1][shipping_rate_data][type]', 'fixed_amount');
  params.append('shipping_options[1][shipping_rate_data][fixed_amount][amount]', '999');
  params.append('shipping_options[1][shipping_rate_data][fixed_amount][currency]', 'gbp');
  params.append('shipping_options[2][shipping_rate_data][display_name]', 'Rest of world');
  params.append('shipping_options[2][shipping_rate_data][type]', 'fixed_amount');
  params.append('shipping_options[2][shipping_rate_data][fixed_amount][amount]', '1499');
  params.append('shipping_options[2][shipping_rate_data][fixed_amount][currency]', 'gbp');

  params.append('metadata[product]', 'twub-wiro-2ed');
  params.append('payment_intent_data[statement_descriptor_suffix]', 'LTU BOOK');
  params.append('payment_intent_data[description]', 'TWUB wiro edition — learntoupholster.com');

  const resp = await fetch('https://api.stripe.com/v1/checkout/sessions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.STRIPE_SECRET_KEY}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: params,
  });
  const session = await resp.json();
  if (!resp.ok) {
    return new Response(JSON.stringify({ error: session.error?.message || 'Stripe error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } });
  }
  return new Response(JSON.stringify({ url: session.url }),
    { headers: { 'Content-Type': 'application/json' } });
}
