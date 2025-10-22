-- Create minimal tables (extend as needed)
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
