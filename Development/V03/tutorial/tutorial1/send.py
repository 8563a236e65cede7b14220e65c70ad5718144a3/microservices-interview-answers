"""
Send a single message to RabbitMQ queue
"""
import pika


def main():
    # Create blocking connection to RabbitMQ server
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("172.18.0.2")
    )

    # Open a channel
    channel = connection.channel()

    # Declare a queue to ensure existence
    channel.queue_declare(queue="hello")

    # Publish the message
    # Routing-key is queue name
    channel.basic_publish(
        exchange="",  # amq.direct
        routing_key="hello",
        body="Hello World!"
    )
    print(" [x] Sent 'Hello World!'")

    # Close connection to flush buffers
    connection.close()


if __name__ == "__main__":
    main()
