-- survey-schema.sql — State of the Upholstery Trade
--
-- Deliberately holds no personal data. No names, no emails, no free text.
-- Every column is a bounded value from a fixed list or a number, which means
-- there is nothing here that identifies a respondent and nothing that needs a
-- deletion process. The IP is stored only as a salted hash, only to stop one
-- person filling it in fifty times, and it is not reversible.
--
-- Create the database first:
--   npx wrangler d1 create ltu-survey
-- then put the returned database_id in wrangler.toml, then:
--   npx wrangler d1 execute ltu-survey --remote --file=survey-schema.sql

CREATE TABLE IF NOT EXISTS responses (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at      TEXT    NOT NULL,

  country         TEXT    NOT NULL,
  currency        TEXT    NOT NULL,
  years_trade     TEXT    NOT NULL,   -- band
  business_type   TEXT    NOT NULL,
  premises        TEXT    NOT NULL,

  hourly_rate     REAL,               -- in the stated currency
  pricing_method  TEXT,
  fabric_markup   TEXT,               -- band

  hours_wingback  REAL,               -- traditional wing-back rebuild
  hours_wingback_modern REAL,         -- same chair, modern re-cover

  lead_time       TEXT,               -- band, weeks
  best_work       TEXT,
  turning_away    TEXT,

  ip_hash         TEXT    NOT NULL,
  ua_hash         TEXT
);

CREATE INDEX IF NOT EXISTS idx_responses_created ON responses (created_at);
CREATE INDEX IF NOT EXISTS idx_responses_country ON responses (country);
CREATE INDEX IF NOT EXISTS idx_responses_iphash  ON responses (ip_hash, created_at);
