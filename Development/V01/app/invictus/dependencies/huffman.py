"""
Dependency provider for Huffman coding

It provides the low level functionality not exposed in the API code
"""
import dahuffman
import base64
import pickle
import json
import tempfile

from nameko.extensions import DependencyProvider


class HuffmanCoding:

    def __init__(self):
        self.str_list = list()
        self.result = dict()
        self.encoded_dict = dict()

    def encode(self, str_list):
        self.result = dict()
        self.str_list = str_list
        codec = dahuffman.HuffmanCodec.from_data("".join(self.str_list))
        for i in self.str_list:
            self.result.update({i: base64.b64encode(codec.encode(i)).decode("utf-8")})
        code_table = codec.get_code_table()
        data = {
            "code_table": code_table,
            "type": type(codec),
            "concat": codec._concat
        }
        data = base64.b64encode(pickle.dumps(data)).decode("utf-8")
        self.result.update({"_codec": data})
        return self.result

    def decode(self, encoded_dict, string):
        self.encoded_dict = encoded_dict
        return self.encoded_dict["_codec"].decode(string)


class HuffmanProvider(DependencyProvider):

    def setup(self):
        self.codec = HuffmanCoding()

    def stop(self):
        del self.codec

    def get_dependency(self, worker_ctx):
        return self.codec
