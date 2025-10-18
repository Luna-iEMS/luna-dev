# Luna IEMS – Dev Stack (Clean)

This package contains a cleaned & fixed dev stack:

- Robust `docker-compose.dev.yml` with correct healthchecks
- Separate `api/` and `worker/` images
- Alembic with raw SQL migrations creating required tables
- Minimal `.env.dev` you can copy to `.env`

## Quick start

```bash
cp .env.dev .env
docker compose -f docker-compose.dev.yml up --build
```

### First run
Alembic runs automatically inside the API container:
- Creates `smart_meter_readings` and `market_prices` tables
- Converts them to TimescaleDB hypertables

### Smoke checks
```bash
curl http://localhost:8000/api/v1/system/info
docker logs -f luna-worker
```

### Rebuild from scratch
```bash
docker compose -f docker-compose.dev.yml down -v --remove-orphans
docker system prune -af
docker compose -f docker-compose.dev.yml up --build
```
# Luna IEMS – Development Setup

## Start
```bash
docker compose -f docker-compose.dev.yml up -d
