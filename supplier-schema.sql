-- supplier_submissions — moderation queue for the supplier directory.
-- Nothing here appears on /suppliers until it has been checked and added to
-- supplier-data.py by hand. Run against the existing ltu-survey database:
--   npx wrangler d1 execute ltu-survey --remote --file=supplier-schema.sql

CREATE TABLE IF NOT EXISTS supplier_submissions (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at  TEXT NOT NULL,
  name        TEXT NOT NULL,
  url         TEXT NOT NULL,
  host        TEXT NOT NULL,
  country     TEXT NOT NULL,
  cats        TEXT,
  note        TEXT,
  ip_hash     TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'pending'   -- pending | added | rejected
);

CREATE INDEX IF NOT EXISTS idx_sub_status ON supplier_submissions (status, created_at);
CREATE INDEX IF NOT EXISTS idx_sub_host   ON supplier_submissions (host);
