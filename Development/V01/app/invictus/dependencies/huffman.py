"""
Dependency provider for Huffman coding

It provides the low level functionality not exposed in the API code
"""
import dahuffman
import base64
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
        #self.result.update({"_codec": codec})
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
