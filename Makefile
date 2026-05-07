up-dev:
	docker compose up -d

up-prod:
	docker build --target prod -t fastapi_img:prod . && \
	docker run -d --name fastapi_ctn -p 8000:8000 fastapi_img:prod

stop:
	docker compose stop

down-dev:
	docker compose down --volumes --remove-orphans && docker image rm fastapi_img || true

down-prod:
	docker stop fastapi_ctn || true && \
	docker rm fastapi_ctn || true && \
	docker image rm fastapi_img:prod || true

logs:
	docker compose logs -f

shell:
	docker compose exec fastapi sh
