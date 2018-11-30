from contextlib import contextmanager
from typing import NamedTuple

import pika
from pika.adapters.blocking_connection import BlockingChannel


QUEUE_NAME = 'sensors'


class RabbitConfig(NamedTuple):
    host: str
    port: int
    vhost: str
    username: str
    password: str


CONF = RabbitConfig(
    host="localhost",
    port=5672,
    vhost="vh_sensors",
    username="testuser",
    password="testuserpass",
)


@contextmanager
def get_channel() -> BlockingChannel:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=CONF.host, port=CONF.port, virtual_host=CONF.vhost,
            credentials=pika.PlainCredentials(
                username=CONF.username, password=CONF.password,
            )
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    yield channel

    connection.close()
