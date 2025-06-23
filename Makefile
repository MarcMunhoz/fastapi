up:
	docker compose up -d

stop:
	docker compose stop

down:
	docker compose down --volumes --remove-orphans && docker image rm fastapi_img

logs:
	docker compose logs -f

shell:
	docker compose exec fastapi sh