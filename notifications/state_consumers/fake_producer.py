import json
import random
import time

import pika
from state_consumers.client import get_channel, QUEUE_NAME


def get_message():
    return {
        "sensor_id": str(random.randint(0, 1000)),
        "data": random.randint(0, 10),
    }


if __name__ == "__main__":
    with get_channel() as channel:
        while True:
            channel.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=json.dumps(get_message()),
                properties = pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
            print(" [x] Sent")
            time.sleep(1)
