"""
Direct client example
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
    channel.exchange_declare(exchange="direct_logs",
                             exchange_type="direct")

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    # Get severities
    severities = sys.argv[1:]

    if not severities:
        sys.stderr.write(f"Usage: {sys.argv[0]} "
                         f"[info] [warning] [error]\n" )
        sys.exit(1)

    for severity in severities:
        channel.queue_bind(
            exchange="direct_logs",
            queue=queue_name,
            routing_key=severity
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
