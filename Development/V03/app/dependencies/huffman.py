"""
Dependency provider for Huffman coding

It provides the low level functionality not exposed in the API code
"""
import dahuffman
import base64
import pickle


class HuffmanCoding:
    """
    The HuffmanCoding class forms the base of the dependency provider
    for the Huffman Coding algorithm. It uses dahuffman.HuffmanCodec
    to perform the majority of the work. Data is base64 encoded for
    transfer over the network
    """

    @staticmethod
    def encode(str_list):
        """
        The main function to produce a dictionary of original and
        encoded strings. A code table is added to the result for
        calibrating a new Huffman codec for decode. The code table
        is pickled first, and then base64 encoded to deal with custom
        _EOF marker included in dahuffman
        :param str_list: The list of strings to train the codec
        :return: a dictionary of strings whose keys are the original
                 strings and whose values are the base64 encoded
                 versions of the Huffman encoded string plus a
                 code table
        """
        # Initialize the result dictionary
        result = dict()

        # Create and train the codec
        codec = dahuffman.HuffmanCodec.from_data("".join(str_list))

        # Build dictionary with keys as original strings and values as
        # base64 encoded versions of the Huffman codec bytes objects
        for i in str_list:
            result.update({i: base64.b64encode(codec.encode(i)).decode("utf-8")})

        # Retrieve the code table for packaging and package
        code_table = codec.get_code_table()
        data = {
            "code_table": code_table
        }

        # Data is pickled, base64 encoded and then decoded to a
        # string object for transmission over the network
        data = base64.b64encode(pickle.dumps(data)).decode("utf-8")
        result.update({"_codec": data})

        return result

    @staticmethod
    def decode(args):
        """
        The main function to decode a string, given a previously trained
        codec's code table. All inputs are base64 encoded for network
        transfer.
        :param saved_codec: a base64 encoded version of the codec that was
                            trained on the original data
        :param string: a base64 encoded version of the huffman encoded bytes object
                       to decode.
        :return: the decoded string
        """
        saved_codec = base64.b64decode(args["saved_codec"])
        saved_codec = pickle.loads(saved_codec)
        code_table = saved_codec["code_table"]

        codec = dahuffman.HuffmanCodec(code_table=code_table)

        return "".join(codec.decode(base64.b64decode(args["string"])))
