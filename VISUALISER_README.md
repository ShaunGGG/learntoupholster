# Fabric Visualiser — setup (one-time, ~15 minutes)

Free tool: user uploads chair photo + fabric swatch (email required), Gemini
renders the chair in the fabric (~3-4p/image), result shown on page AND emailed
with the find-an-upholsterer handoff + copy-paste quote template. Hard-capped
so it cannot lose money.

## Files
- fabric-visualiser.html          → the page at /fabric-visualiser
- functions/api/visualise.js      → the engine
- patch-visualiser.py             → nav, tools card, sitemap

## 1. Gemini API key
aistudio.google.com → Get API key → create. IMPORTANT: in Google AI Studio /
Cloud billing, set a monthly budget alert (e.g. £20) as the second backstop.
  npx wrangler pages secret put GEMINI_API_KEY --project-name=learntoupholster

## 2. Turnstile (free bot check)
Cloudflare dashboard → Turnstile → Add site → learntoupholster.com, Managed.
Copy BOTH keys:
  - Site key → into the page:
      sed -i 's/TURNSTILE_SITE_KEY_HERE/YOUR_SITE_KEY/' fabric-visualiser.html
  - Secret key:
      npx wrangler pages secret put TURNSTILE_SECRET --project-name=learntoupholster

## 3. KV namespace (rate limits + daily cap)
  npx wrangler kv namespace create VISUALISER_KV
Then bind it: Cloudflare dashboard → Workers & Pages → learntoupholster →
Settings → Bindings → Add → KV namespace → variable name VISUALISER_KV →
select the namespace just created. (Bindings, like secrets, apply on next deploy.)

## 4. Optional tuning (plain-text variables, same Settings page)
  DAILY_CAP      default 300   (worst-case day ≈ £9-12)
  HOURLY_TRIES   default 3

## 5. Deploy
  cd ~ && unzip -o fabric_visualiser.zip -d learntoupholster && cd learntoupholster
  python3 patch-visualiser.py
  npx wrangler pages deploy . --project-name=learntoupholster --branch=production
  git add -A && git commit -m "Fabric visualiser: AI see-your-chair tool" && git push

## 6. Test
Open /fabric-visualiser, upload a chair photo + any fabric photo, use your own
email. Expect ~20s, image on page + email with the quote template. Then try a
4th go inside the hour to see the limiter refuse politely.

## Economics reminder
Email required BEFORE generation → 100% capture. Costs: ~3-4p/success, counted
only on success, capped at DAILY_CAP/day, plus your Google budget alert.
Resend attachment ≈ free tier. Result page + email both route to
/find-an-upholsterer (worldwide directory handoff), the fabric calculator and
the book.
