docker-up-infra:
	docker-compose up rabbit postgres

docker-up:
	docker-compose up

docker-clean:
	docker-compose down

tests:
	LOCK_SENSORS_TESTING=1 python -m lock_sensors.common.testing
