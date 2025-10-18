-- Users
CREATE TABLE IF NOT EXISTS users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  external_id TEXT UNIQUE,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Items
CREATE TABLE IF NOT EXISTS items (
  item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  kind TEXT NOT NULL,
  source TEXT,
  title TEXT,
  tags TEXT[],
  url TEXT,
  sha256 TEXT UNIQUE,
  version INT DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_items_tags ON items USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_items_sha ON items(sha256);

-- Chunks
CREATE TABLE IF NOT EXISTS item_chunks (
  chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id UUID REFERENCES items(item_id) ON DELETE CASCADE,
  chunk_idx INT NOT NULL,
  text TEXT NOT NULL,
  qdrant_id TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_chunks_item ON item_chunks(item_id);

-- Events (Timescale)
CREATE TABLE IF NOT EXISTS events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(user_id),
  ts TIMESTAMPTZ NOT NULL,
  type TEXT NOT NULL,
  item_id UUID REFERENCES items(item_id),
  chunk_id UUID REFERENCES item_chunks(chunk_id),
  meta JSONB DEFAULT '{}'::jsonb
);
SELECT create_hypertable('events','ts', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_events_user_ts ON events(user_id, ts DESC);

-- Smart Meter
CREATE TABLE IF NOT EXISTS smart_meter_readings (
  meter_id TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  consumption_kw DOUBLE PRECISION,
  production_kw DOUBLE PRECISION,
  voltage DOUBLE PRECISION,
  quality TEXT,
  PRIMARY KEY (meter_id, ts)
);
SELECT create_hypertable('smart_meter_readings','ts', if_not_exists => TRUE);

-- Market Prices
CREATE TABLE IF NOT EXISTS market_prices (
  market TEXT NOT NULL,
  product TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  price_eur_mwh DOUBLE PRECISION,
  volume DOUBLE PRECISION,
  PRIMARY KEY (market, product, ts)
);
SELECT create_hypertable('market_prices','ts', if_not_exists => TRUE);

-- Labels (Feedback)
CREATE TABLE IF NOT EXISTS labels (
  user_id UUID REFERENCES users(user_id),
  item_id UUID REFERENCES items(item_id),
  ts TIMESTAMPTZ DEFAULT now(),
  reward DOUBLE PRECISION NOT NULL,
  reason TEXT,
  PRIMARY KEY(user_id, item_id, ts)
);
