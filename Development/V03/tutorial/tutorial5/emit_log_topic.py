"""
Log emitter for topic exchange
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
    channel.exchange_declare(exchange="topic_logs",
                             exchange_type="topic")

    # Get severity arguments
    routing_key = sys.argv[1] if len(sys.argv) > 2 else "anonymous.info"

    # Create message
    message = " ".join(sys.argv[2:]) or "Hello World!"

    # Publish the message
    # Routing-key is created routing key
    channel.basic_publish(
        exchange="topic_logs",
        routing_key=routing_key,
        body=message
    )
    print(f" [x] Sent '{routing_key!r}':'{message!r}'")

    # Close connection to flush buffers
    connection.close()


if __name__ == "__main__":
    main()
