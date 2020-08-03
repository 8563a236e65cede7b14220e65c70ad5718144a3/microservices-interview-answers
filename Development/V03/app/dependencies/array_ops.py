"""
Dependency Provider for Array Operations

Low level code for array operations
"""


class ArrayOps:
    """
    The ArrayOps class forms the base of the dependency
    provider for array operations.
    """
    @staticmethod
    def square_odds(int_arr):
        """
        Squares all entries within the given list of
        integers that are odd numbers. Loop through the list
        and check if each entry is odd with modulus operator.
        If true, square entry, otherwise leave entry alone.
        :param int_arr: a list of integers
        :return: the list of integers with odd numbers squared
        """
        int_arr = int_arr
        for i in range(len(int_arr)):
            if int_arr[i] % 2 == 1:
                int_arr[i] *= int_arr[i]
        return int_arr

