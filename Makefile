collect : # freeze recently installed dependencies
	uv pip freeze | uv pip compile - -o requirements.txt

up : # docker compose local
	docker compose -f ./docker-compose.local.yml --env-file ./env/local/ports.env up

prod : # docker compose production
	docker compose -f ./docker-compose.production.yml --env-file ./env/production/ports.env up -d

refresh : # run container again
	make --ignore-errors _refresh

_refresh :
	docker stop test-exchanges-bot-1
	docker rm test-exchanges-bot-1
	docker rmi test-exchanges-bot
	docker volume rm test-exchanges_app
	make up

rebuild : # run container again with clearing caches
	make --ignore-errors _rebuild

_rebuild :
	docker stop test-exchanges-bot-1
	docker rm test-exchanges-bot-1
	docker rmi test-exchanges-bot
	docker volume rm test-exchanges_app
	docker builder prune -f
	make up
