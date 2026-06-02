up-dev:
	docker compose up -d --build --force-recreate --remove-orphans

up-prod:
	docker build --target prod -t fastapi_img:prod . && \
	docker run -d --name fastapi_ctn -p 8000:8000 fastapi_img:prod

start-dev:
	docker compose start

stop:
	docker compose stop

down-dev:
	docker compose down --volumes --remove-orphans && docker image rm fastapi_img || true

down-prod:
	docker stop fastapi_ctn || true && \
	docker rm fastapi_ctn || true && \
	docker image rm fastapi_img:prod || true

logs:
	docker compose logs

shell:
	docker compose exec fastapi sh

audit:
	docker compose exec fastapi poetry run pip-audit
