"""
Schedule tasks to queue
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

    # Declare a queue to ensure existence
    channel.queue_declare(queue="task_queue",
                          durable=True)

    # Create message
    message = " ".join(sys.argv[1:]) or "Hello World!"

    # Publish the message
    # Routing-key is queue name
    channel.basic_publish(
        exchange="",  # amq.direct
        routing_key="task_queue",
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(" [x] Sent 'Hello World!'")

    # Close connection to flush buffers
    connection.close()


if __name__ == "__main__":
    main()
