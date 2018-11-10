docker-up-infra:
	docker-compose up rabbit postgres

docker-up:
	docker-compose up

docker-clean:
	docker-compose down
