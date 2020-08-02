"""
Worker script
"""
import pika
import time


def callback(ch, method, properties, body):
    print(f" [x] Received {body!r}")
    time.sleep(body.count(b"."))
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    # Create blocking connection to RabbitMQ server
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("172.18.0.2")
    )

    # Open a channel
    channel = connection.channel()

    # Declare a queue to ensure existence
    channel.queue_declare(queue="task_queue",
                          durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue="task_queue",
        on_message_callback=callback
    )

    print(" [*} Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    main()
