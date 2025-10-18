"""init core tables"""

from alembic import op

# Revision identifiers, used by Alembic.
revision = "20251017_080759"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create smart_meter_readings (idempotent)
    op.execute("""        CREATE TABLE IF NOT EXISTS smart_meter_readings (
            meter_id TEXT NOT NULL,
            ts TIMESTAMPTZ NOT NULL,
            consumption_kw DOUBLE PRECISION,
            production_kw DOUBLE PRECISION,
            voltage DOUBLE PRECISION,
            quality TEXT,
            PRIMARY KEY (meter_id, ts)
        );
    """)

    # Create market_prices (idempotent)
    op.execute("""        CREATE TABLE IF NOT EXISTS market_prices (
            ts TIMESTAMPTZ NOT NULL,
            price_eur_mwh DOUBLE PRECISION,
            region TEXT NOT NULL,
            PRIMARY KEY (ts, region)
        );
    """)

    # If TimescaleDB is present, convert to hypertable (idempotent)
    op.execute("""        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
                PERFORM create_hypertable('smart_meter_readings', 'ts', if_not_exists => TRUE);
                PERFORM create_hypertable('market_prices', 'ts', if_not_exists => TRUE);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS market_prices CASCADE;")
    op.execute("DROP TABLE IF EXISTS smart_meter_readings CASCADE;")
