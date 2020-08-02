"""
Topic client example
"""
import pika
import sys


def callback(ch, method, properties, body):
    print(f" [x] {method.routing_key!r}:{body!r}")


def main():
    # Create blocking connection to RabbitMQ server
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("172.18.0.2")
    )

    # Open a channel
    channel = connection.channel()

    # Declare an exchange
    channel.exchange_declare(exchange="topic_logs",
                             exchange_type="topic")

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    # Get severities
    binding_keys = sys.argv[1:]

    if not binding_keys:
        sys.stderr.write(f"Usage: {sys.argv[0]} "
                         f"[binding_key] ...\n")
        sys.exit(1)

    for binding_key in binding_keys:
        channel.queue_bind(
            exchange="topic_logs",
            queue=queue_name,
            routing_key=binding_key
        )

    print(" [*] Waiting for logs. To exit press CTRL+C")

    #Consume the logs
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=True
    )

    channel.start_consuming()


if __name__ == "__main__":
    main()
