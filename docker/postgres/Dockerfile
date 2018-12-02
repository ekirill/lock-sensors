FROM postgres

RUN mkdir -p /docker-entrypoint-initdb.d
COPY lock_sensors/common/db/schema/*.sql /docker-entrypoint-initdb.d/
