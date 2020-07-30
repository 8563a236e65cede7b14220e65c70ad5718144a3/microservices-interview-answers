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
        self.saved_codec = 0

    def encode(self, str_list):
        self.result = dict()
        self.str_list = str_list
        codec = dahuffman.HuffmanCodec.from_data("".join(self.str_list))
        for i in self.str_list:
            print(i, codec.encode(i), codec.decode(codec.encode(i)))
            self.result.update({i: base64.b64encode(codec.encode(i)).decode("utf-8")})
        code_table = codec.get_code_table()
        print(code_table)
        data = {
            "code_table": code_table
        }
        data = base64.b64encode(pickle.dumps(data)).decode("utf-8")
        self.result.update({"_codec": data})
        #print(self.result)
        return self.result

    def decode(self, saved_codec, string):
        self.saved_codec = saved_codec
        self.saved_codec = base64.b64decode(self.saved_codec)
        self.saved_codec = pickle.loads(self.saved_codec)
        code_table = self.saved_codec["code_table"]
        #print(frequencies)
        codec = dahuffman.HuffmanCodec(code_table=code_table)
        #print(base64.b64decode(string))
        return "".join(codec.decode(base64.b64decode(string)))


class HuffmanProvider(DependencyProvider):

    def setup(self):
        self.codec = HuffmanCoding()

    def stop(self):
        del self.codec

    def get_dependency(self, worker_ctx):
        return self.codec
