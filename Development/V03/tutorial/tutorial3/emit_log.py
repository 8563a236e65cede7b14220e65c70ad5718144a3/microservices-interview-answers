"""
Log emitter for fanout exchange
"""
import sys
import pika


def main():
    # Create blocking connection to RabbitMQ server
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("172.18.0.2")
    )

    # Open a channel
    channel = connection.channel()

    # Declare an exchange
    channel.exchange_declare(exchange="logs", exchange_type="fanout")

    # Create message
    message = " ".join(sys.argv[1:]) or "info: Hello World!"

    # Publish the message
    # Routing-key is queue name
    channel.basic_publish(
        exchange="logs",
        routing_key="",
        body=message
    )
    print(f" [x] Sent '{message!r}'")

    # Close connection to flush buffers
    connection.close()


if __name__ == "__main__":
    main()
