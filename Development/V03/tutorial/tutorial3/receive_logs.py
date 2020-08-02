"""
Fanout client example
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

    # Declare an exchange
    channel.exchange_declare(exchange="logs", exchange_type="fanout")

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    # Bind the queue to the exchange
    channel.queue_bind(exchange="logs", queue=queue_name)

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
