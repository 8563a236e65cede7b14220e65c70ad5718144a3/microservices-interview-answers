"""
Service API

Contains the classes that the RPC call goes to
"""
from nameko.rpc import rpc, RpcProxy
from .dependencies.array_ops import ArrayOpsProvider
from .dependencies.huffman import HuffmanProvider


class ArrayOpsService:

    name = "arr_ops_service"
    arr_ops_provider = ArrayOpsProvider()

    @rpc
    def square_odds(self, int_arr):
        self.arr_ops_provider.square_odds(int_arr)


class HuffmanService:
    name = "huffman_service"
    huffman_provider = HuffmanProvider()

    @rpc
    def encode(self, str_list):
        return self.huffman_provider.encode(str_list)

    @rpc
    def decode(self, encoded_dict, string):
        return self.huffman_provider.decode(encoded_dict, string)
