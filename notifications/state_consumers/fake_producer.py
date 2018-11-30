import json
import random

from state_consumers.client import get_channel, QUEUE_NAME


test_message = {
    "sensor_id": str(random.randint(0, 1000)),
    "data": random.randint(0, 10),
}


if __name__ == "__main__":
    with get_channel() as channel:
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(test_message)
        )
        print(" [x] Sent")
