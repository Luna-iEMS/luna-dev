-- Basistabellen für RAG (Luna IEMS)
CREATE TABLE IF NOT EXISTS items (
    item_id     SERIAL PRIMARY KEY,
    kind        TEXT,
    source      TEXT,
    title       TEXT,
    tags        TEXT[],
    sha256      TEXT UNIQUE,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS item_chunks (
    chunk_id    SERIAL PRIMARY KEY,
    item_id     INT REFERENCES items(item_id) ON DELETE CASCADE,
    chunk_idx   INT,
    text        TEXT,
    metadata    JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_item_chunks_item_id ON item_chunks(item_id);
