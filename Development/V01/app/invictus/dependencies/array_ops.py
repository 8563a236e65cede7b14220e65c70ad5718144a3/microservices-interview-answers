"""
Dependency Provider for Array Operations

Low level code for array operations
"""
from nameko.extensions import DependencyProvider


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


class ArrayOpsProvider(DependencyProvider):
    """
    Dependency Provider class for the array_ops service
    """
    def setup(self):
        self.arr_op = ArrayOps()

    def stop(self):
        del self.arr_op

    def get_dependency(self, worker_ctx):
        return self.arr_op