"""
Service API
"""
import pika
import json
import dependencies.array_ops as arr_op
import dependencies.huffman as huff


service_mapping = {
    "ArrayOps": {
        "square_odds": arr_op.ArrayOps().square_odds
    },
    "HuffmanCoding": {
        "encode": huff.HuffmanCoding().encode,
        "decode": huff.HuffmanCoding().decode
    }
}


def on_request(ch, method, props, body):
    query = json.loads(body)
    class_method = query["call"].split(".")
    print("call:", query["call"])
    print("data", query["data"])
    func = service_mapping[class_method[0]][class_method[1]]
    response = func(query["data"])
    print("response:", response, "\n\n")

    ch.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(
            correlation_id=props.correlation_id,
            content_type="text/json"
        ),
        body=json.dumps({"response": response})
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    # Create blocking connection to RabbitMQ server
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("172.18.0.2")
    )

    # Open a channel
    channel = connection.channel()

    # Declare RPC Queue
    channel.queue_declare(queue="rpc_queue")

    # Limit to distributing one message per worker
    channel.basic_qos(prefetch_count=1)

    # Set up basic consume
    channel.basic_consume(queue="rpc_queue",
                          on_message_callback=on_request)

    print(" [x] Awaiting RPC requests")
    channel.start_consuming()


if __name__ == "__main__":
    main()
