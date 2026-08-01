// functions/api/survey.js
//
// POST — record a response.
// GET  — public aggregates, gated behind a minimum sample size.
//
// The gate matters. Publishing "the average UK shop rate is £62" off four
// responses would be worse than publishing nothing: it is the sort of number
// that gets quoted back for years. Nothing is shown until MIN_N is reached, and
// per-country figures need MIN_N_COUNTRY of their own.

// The D1 binding name depends on how it was configured. `wrangler d1 create`
// suggests a name munged from the database ("ltu_survey"); the setup notes ask
// for SURVEY_DB. Accept either rather than have the whole thing 500 over a
// naming convention, and say which names were tried if neither is present.
function getDB(env) {
  return env.SURVEY_DB || env.ltu_survey || env.DB || null;
}

// If this ever fires again, the binding has gone missing from the Pages config.
// It lives in wrangler.toml under [[env.production.d1_databases]] — and it has
// to be in that environment block, not at the top level, because
// env.production already overrides kv_namespaces and therefore stops
// inheriting top-level bindings entirely.
function noDb() {
  return {
    error: 'Survey database not bound.',
    looked_for: ['SURVEY_DB', 'ltu_survey', 'DB'],
    fix: 'Check [[env.production.d1_databases]] in wrangler.toml, then redeploy.',
  };
}

const MIN_N = 30;
const MIN_N_COUNTRY = 8;
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

// GET results are cacheable; writes and errors never are. The aggregate changes
// at most a few times an hour, so serving repeat views from Cloudflare's edge
// costs nothing and keeps a thousand page views from becoming a thousand D1
// reads. s-maxage is what the edge honours; max-age keeps browsers honest too.
const CACHE_SECONDS = 300;

const json = (o, s, cacheable) => new Response(JSON.stringify(o), {
  status: s || 200,
  headers: Object.assign(
    { 'Content-Type': 'application/json' },
    CORS,
    cacheable
      ? { 'Cache-Control': `public, max-age=60, s-maxage=${CACHE_SECONDS}` }
      : { 'Cache-Control': 'no-store' }
  ),
});

// Allowed values. Anything not on these lists is rejected rather than coerced,
// so the dataset cannot fill up with junk that has to be cleaned out later.
const FIELDS = {
  country: null, // any 2-letter code, checked separately
  currency: ['GBP', 'USD', 'EUR', 'AUD', 'CAD', 'NZD', 'ZAR', 'SEK', 'DKK', 'NOK', 'CHF', 'JPY', 'OTHER'],
  years_trade: ['<2', '2-5', '6-10', '11-20', '21-30', '30+'],
  business_type: ['sole-trader', 'partnership', 'limited', 'employed', 'part-time', 'hobby'],
  premises: ['home', 'rented-unit', 'shared', 'shop-frontage', 'mobile'],
  pricing_method: ['hourly', 'per-job', 'per-piece-type', 'mixed'],
  fabric_markup: ['none', 'under-25', '25-50', '50-100', 'over-100', 'customer-supplies'],
  lead_time: ['under-2', '2-4', '5-8', '9-16', 'over-16'],
  best_work: ['domestic-recover', 'traditional-restoration', 'contract', 'caravan-marine',
              'teaching', 'soft-furnishings', 'antiques-trade'],
  turning_away: ['often', 'sometimes', 'never'],
};

async function sha256(s) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
}

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: CORS });
}

export async function onRequestPost({ request, env }) {
  const DB = getDB(env);
  if (!DB) return json(noDb(), 500);

  let body;
  try { body = await request.json(); } catch { return json({ error: 'Bad JSON.' }, 400); }

  // Honeypot: a real browser leaves this empty because it is visually hidden.
  if (body.website) return json({ ok: true, recorded: false });

  for (const [k, allowed] of Object.entries(FIELDS)) {
    const v = body[k];
    if (k === 'country') {
      if (typeof v !== 'string' || !/^[A-Z]{2}$/.test(v)) return json({ error: 'Invalid country.' }, 400);
      continue;
    }
    if (allowed && v !== undefined && v !== null && v !== '' && !allowed.includes(v)) {
      return json({ error: `Invalid value for ${k}.` }, 400);
    }
  }
  for (const k of ['country', 'currency', 'years_trade', 'business_type', 'premises']) {
    if (!body[k]) return json({ error: `${k} is required.` }, 400);
  }

  // Numbers: reject the impossible rather than storing it and filtering later.
  const num = (v, lo, hi) => {
    if (v === undefined || v === null || v === '') return null;
    const n = Number(v);
    return Number.isFinite(n) && n >= lo && n <= hi ? n : undefined;
  };
  const rate = num(body.hourly_rate, 1, 1000);
  const hw = num(body.hours_wingback, 1, 300);
  const hwm = num(body.hours_wingback_modern, 1, 300);
  if (rate === undefined || hw === undefined || hwm === undefined) {
    return json({ error: 'A number is outside the plausible range.' }, 400);
  }

  const salt = env.SURVEY_SALT || 'ltu-survey';
  const ip = request.headers.get('cf-connecting-ip') || '0.0.0.0';
  const ipHash = await sha256(salt + ip);
  const uaHash = await sha256(salt + (request.headers.get('user-agent') || ''));

  // One response per person per 24h. Not airtight, and not meant to be.
  const dupe = await DB
    .prepare("SELECT 1 FROM responses WHERE ip_hash = ? AND created_at > datetime('now','-1 day') LIMIT 1")
    .bind(ipHash).first();
  if (dupe) return json({ ok: true, recorded: false, reason: 'already-submitted' });

  await DB.prepare(
    `INSERT INTO responses (created_at, country, currency, years_trade, business_type, premises,
       hourly_rate, pricing_method, fabric_markup, hours_wingback,
       hours_wingback_modern, lead_time, best_work, turning_away, ip_hash, ua_hash)
     VALUES (datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  ).bind(
    body.country, body.currency, body.years_trade, body.business_type, body.premises,
    rate, body.pricing_method || null, body.fabric_markup || null, hw, hwm,
    body.lead_time || null, body.best_work || null, body.turning_away || null,
    ipHash, uaHash
  ).run();

  const { total } = await DB.prepare('SELECT COUNT(*) AS total FROM responses').first();
  return json({ ok: true, recorded: true, total, min_to_publish: MIN_N });
}

// Median rather than mean throughout: one person typing 900 for their hourly
// rate should not move the published figure.
function median(xs) {
  const a = xs.filter(n => typeof n === 'number' && Number.isFinite(n)).sort((x, y) => x - y);
  if (!a.length) return null;
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : Math.round(((a[m - 1] + a[m]) / 2) * 10) / 10;
}

function tally(rows, key) {
  const c = {};
  for (const r of rows) if (r[key]) c[r[key]] = (c[r[key]] || 0) + 1;
  return Object.entries(c).sort((a, b) => b[1] - a[1])
    .map(([value, count]) => ({ value, count, pct: Math.round(count / rows.length * 100) }));
}

export async function onRequestGet({ env }) {
  const DB = getDB(env);
  if (!DB) return json(noDb(), 500);

  const { results } = await DB.prepare(
    `SELECT country, currency, years_trade, business_type, premises, hourly_rate,
            pricing_method, fabric_markup, hours_wingback,
            hours_wingback_modern, lead_time, best_work, turning_away
     FROM responses`).all();

  const n = results.length;
  const base = {
    responses: n,
    min_to_publish: MIN_N,
    published: n >= MIN_N,
    updated: new Date().toISOString().slice(0, 10),
    source: 'https://www.learntoupholster.com/state-of-the-trade',
    licence: 'Free to cite with attribution to Learn to Upholster.',
  };
  if (n < MIN_N) {
    return json(Object.assign(base, {
      note: `Results publish once ${MIN_N} upholsterers have responded. ${MIN_N - n} to go.`,
      cache_seconds: CACHE_SECONDS,
    }), 200, true);
  }

  const byCountry = {};
  for (const r of results) (byCountry[r.country] = byCountry[r.country] || []).push(r);

  const countries = Object.entries(byCountry)
    .filter(([, rows]) => rows.length >= MIN_N_COUNTRY)
    .map(([code, rows]) => {
      const cur = tally(rows, 'currency')[0];
      return {
        country: code,
        responses: rows.length,
        currency: cur ? cur.value : null,
        median_hourly_rate: median(rows.map(r => r.hourly_rate)),
        median_hours_wingback: median(rows.map(r => r.hours_wingback)),
        median_hours_wingback_modern: median(rows.map(r => r.hours_wingback_modern)),
      };
    }).sort((a, b) => b.responses - a.responses);

  return json(Object.assign(base, {
    overall: {
      median_hours_wingback: median(results.map(r => r.hours_wingback)),
      median_hours_wingback_modern: median(results.map(r => r.hours_wingback_modern)),
      // The reason for asking both: how much longer a traditional rebuild takes
      // than a modern re-cover, evidenced rather than asserted.
      traditional_vs_modern_multiplier: (function () {
        const t = median(results.map(r => r.hours_wingback));
        const m = median(results.map(r => r.hours_wingback_modern));
        return (t && m) ? Math.round((t / m) * 10) / 10 : null;
      })(),
      years_in_trade: tally(results, 'years_trade'),
      business_type: tally(results, 'business_type'),
      premises: tally(results, 'premises'),
      pricing_method: tally(results, 'pricing_method'),
      fabric_markup: tally(results, 'fabric_markup'),
      lead_time: tally(results, 'lead_time'),
      most_profitable_work: tally(results, 'best_work'),
      turning_work_away: tally(results, 'turning_away'),
    },
    by_country: countries,
    countries_below_threshold: Object.entries(byCountry)
      .filter(([, rows]) => rows.length < MIN_N_COUNTRY).length,
    note: `Rates are medians in each country's own currency, shown only where at least ${MIN_N_COUNTRY} upholsterers responded.`,
    cache_seconds: CACHE_SECONDS,
  }), 200, true);
}
