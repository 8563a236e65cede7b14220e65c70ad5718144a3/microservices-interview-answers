"""
Log emitter for direct exchange
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
    channel.exchange_declare(exchange="direct_logs",
                             exchange_type="direct")


    # Get severity arguments
    severity = sys.argv[1] if len(sys.argv) > 1 else "info"

    # Create message
    message = " ".join(sys.argv[2:]) or "Hello World!"

    # Publish the message
    # Routing-key is severity
    channel.basic_publish(
        exchange="direct_logs",
        routing_key=severity,
        body=message
    )
    print(f" [x] Sent '{severity!r}':'{message!r}'")

    # Close connection to flush buffers
    connection.close()


if __name__ == "__main__":
    main()
