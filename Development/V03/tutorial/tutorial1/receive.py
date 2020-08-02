"""
Receive a single message
"""
import pika


def callback(ch, method, properties, body):
    print(f" [x] Received {body!r}")


def main():
    # Create blocking connection to RabbitMQ server
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("172.18.0.2")
    )

    # Open a channel
    channel = connection.channel()

    # Declare a queue to ensure existence
    channel.queue_declare(queue="hello")

    channel.basic_consume(
        queue="hello",
        auto_ack=True,
        on_message_callback=callback
    )

    print(" [*} Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    main()
