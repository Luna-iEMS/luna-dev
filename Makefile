dev:
	docker compose -f docker-compose.dev.yml up --build

down:
	docker compose -f docker-compose.dev.yml down -v

smoke:
	curl -f http://localhost:8000/api/v1/system/info || (echo "Smoke test failed!" && exit 1)
