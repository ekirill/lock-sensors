import json
import multiprocessing
import signal
import time

from lock_sensors.state_consumers.client import get_channel, QUEUE_NAME


POOL_SIZE = 2


WORKERS = []
_WORKER_ID = None


def callback(ch, method, properties, body):
    print(f"[x] {_WORKER_ID} Received {body}")
    try:
        task = json.loads(body)
        time.sleep(task['data'])
        print(f"[x] {_WORKER_ID} Done {task['sensor_id']}")
    except (ValueError, TypeError) as e:
        print(f"[!] {_WORKER_ID} ERROR {e}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def run_worker(worker_id):
    channel = None
    global _WORKER_ID
    _WORKER_ID = worker_id

    def _stop(signum, frame):
        print(f'[*] {_WORKER_ID} Got {signum} signal, stopping')
        if channel:
            channel.stop_consuming()
            print(f'[*] {_WORKER_ID} Consumer stopped, waiting current task to complete')

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    with get_channel() as channel:
        channel.basic_consume(
            callback,
            queue=QUEUE_NAME,
        )
        print(f'[*] {_WORKER_ID} Started.')
        channel.start_consuming()


def exit_gracefully(signum, frame):
    for w in WORKERS:
        w.terminate()


signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)


if __name__ == "__main__":
    print(f'[*] Starting {POOL_SIZE} workers.')
    WORKERS = []
    for i in range(POOL_SIZE):
        w = multiprocessing.Process(target=run_worker, args=(i, ))
        w.start()

    print(f'[*] Waiting for messages. To exit press CTRL+C')

    for w in WORKERS:
        w.join()
