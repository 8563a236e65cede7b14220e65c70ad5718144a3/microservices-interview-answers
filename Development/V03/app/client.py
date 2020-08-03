import pika
import uuid
import json


def pika_init(self):
    self.response = None
    self.corr_id = None

    self.connection = pika.BlockingConnection(
        pika.ConnectionParameters("172.18.0.2")
    )

    self.channel = self.connection.channel()

    result = self.channel.queue_declare(
        queue="",
        exclusive=True
    )
    self.callback_queue = result.method.queue

    self.channel.basic_consume(
        queue=self.callback_queue,
        on_message_callback=self.on_response,
        auto_ack=True
    )


def pika_on_response(self, ch, method, props, body):
    if self.corr_id == props.correlation_id:
        self.response = body


def rpc_basic_publish_props(
        self,
        exchange,
        routing_key,
        body
):
    return dict(
        exchange=exchange,
        routing_key=routing_key,
        properties=pika.BasicProperties(
            reply_to=self.callback_queue,
            correlation_id=self.corr_id,
            content_type="text/json"
        ),
        body=json.dumps(body)
    )


def rpc_call(self, call, data):
    self.response = None
    self.corr_id = str(uuid.uuid4())
    body = {
        "call": call,
        "data": data
    }
    x = rpc_basic_publish_props(
            self,
            exchange="",
            routing_key="rpc_queue",
            body=body
        )

    self.channel.basic_publish(
        **x
    )
    while self.response is None:
        self.connection.process_data_events()
    return json.loads(self.response)["response"]


class ArrayOps(object):

    def __init__(self):
        pika_init(self)

    def on_response(self, ch, method, props, body):
        pika_on_response(self, ch, method, props, body)

    def square_odds(self, int_arr):
        return rpc_call(self, "ArrayOps.square_odds", int_arr)


class HuffmanCoding(object):

    def __init__(self):
        pika_init(self)

    def on_response(self, ch, method, props, body):
        pika_on_response(self, ch, method, props, body)

    def encode(self, str_list):
        return rpc_call(self, "HuffmanCoding.encode", str_list)

    def decode(self, saved_codec, string):
        return rpc_call(self,
                        "HuffmanCoding.decode",
                        {
                            "saved_codec": saved_codec,
                            "string": string
                        }
                        )


def main():
    arr_ops = ArrayOps()
    huff_coding = HuffmanCoding()

    print(" [x] Requesting ArrayOps.square_odds([1,2,3,4,5,6])")
    response = arr_ops.square_odds([1, 2, 3, 4, 5, 6])
    print(response, "\n")
    print(" [x] Requesting HuffmanEncode.encode(['abc','def','ghi'])")
    response = huff_coding.encode(["abc", "def", "ghi"])
    print(response, "\n")
    print(" [x] Requesting HuffmanEncode.decode()")
    decoded = huff_coding.decode(response["_codec"], response["abc"])
    print(decoded, "\n")


if __name__ == "__main__":
    main()
