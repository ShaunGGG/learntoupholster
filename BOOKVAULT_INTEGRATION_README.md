# Book shop integration — learntoupholster.com

Sells the wiro edition at £44.99 via Stripe Checkout; each paid order is emailed to
you and (once the API key is in) placed with BookVault automatically. Same
architecture as Bodella: no database, Stripe is the order record, email is the
safety net — an order can never be lost even if the BookVault call fails.

## Files
- buy-the-book.html                → page at /buy-the-book
- functions/api/book-checkout.js   → creates the Stripe Checkout session
- functions/api/book-webhook.js    → handles payment success, emails + fulfils

## Deploy (usual workflow)
unzip into ~/learntoupholster, then:
  npx wrangler pages deploy . --project-name=learntoupholster --branch=production
and git push. Add a cover image at /images/book-cover-green.jpg (the front-cover
PNG from the covers work, resized to ~800px wide, is ideal).

## One-time setup
1. STRIPE. Dashboard → Developers → Webhooks → Add endpoint:
   https://learntoupholster.com/api/book-webhook
   Event: checkout.session.completed. Copy the signing secret.
2. SECRETS. Cloudflare Pages → learntoupholster → Settings → Variables & Secrets:
   STRIPE_SECRET_KEY      (live key — can reuse the Bodella Stripe account or a new one)
   STRIPE_WEBHOOK_SECRET  (from step 1 — this endpoint's own secret, not Bodella's)
   RESEND_API_KEY         (existing Resend account; verify learntoupholster.com as a
                           sending domain in Resend, or change the from: address in
                           book-webhook.js to the greenwoodupholstery.com one)
   BOOKVAULT_API_KEY      (portal → Apps → BookVault API → Generate Credentials)
   BOOKVAULT_SKU          (portal → Titles → cart icon on the book → Product ID/SKU)
3. BOOKVAULT API CALL. The order endpoint URL and payload field names in
   placeBookvaultOrder() are marked CONFIRM — check them against the API docs
   linked from the portal Apps page and adjust if their names differ. Until then
   orders arrive by email and can be placed manually in the portal (Place An Order).
4. BALANCE. BookVault auto-processes API/store orders from your account balance —
   keep it topped up or orders sit as drafts awaiting manual payment.
5. TEST. Use Stripe test keys first: buy the book with card 4242 4242 4242 4242,
   confirm the email arrives and the BookVault draft appears, then swap live keys.

## Numbers
£44.99 − ~£6.05 print − ~£3.50 UK ship (absorbed) − ~£1.05 Stripe ≈ £34 per copy.
