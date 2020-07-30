"""
Service API

Contains the classes that the RPC call goes to
"""
from nameko.rpc import rpc, RpcProxy
from .dependencies.array_ops import ArrayOpsProvider
from .dependencies.huffman import HuffmanProvider


class ArrayOpsService:
    """
    The main API entrypoint into the array_ops services
    """
    name = "arr_ops_service"
    arr_ops_provider = ArrayOpsProvider()

    @rpc
    def square_odds(self, int_arr):
        """
        Function to return a list of integers with entries
        which are odd squared
        :param int_arr: a list of integers
        :return: the list with odd valued entries squared
        """
        return self.arr_ops_provider.square_odds(int_arr)


class HuffmanService:
    """
    The main API entrypoint into the huffman services
    """
    name = "huffman_service"
    huffman_provider = HuffmanProvider()

    @rpc
    def encode(self, str_list):
        """
        Given a list of strings, returns a dictionary whose
        keys are the strings in the list, and values are the
        base64 encoded version of the huffman encoded bytes
        object
        :param str_list: A list of strings to train the codec
        :return: dictionary with original:b64(huffman(original))
                 key value pairs
        """
        return self.huffman_provider.encode(str_list)

    @rpc
    def decode(self, saved_codec, string):
        """
        Given a saved codec, and a base64 huffman encoded string,
        returns the decoded string
        :param saved_codec: base64 encoded code table
        :param string: base64 encoded huffman encoded string
        :return: the decoded string
        """
        return self.huffman_provider.decode(saved_codec, string)
