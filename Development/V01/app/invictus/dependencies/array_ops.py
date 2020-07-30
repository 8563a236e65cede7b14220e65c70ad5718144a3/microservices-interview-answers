"""
Dependency Provider for Array Operations

Low level code for array operations
"""
from nameko.extensions import DependencyProvider


class ArrayOps:

    def __init__(self):
        self.int_arr = list()

    def square_odds(self, int_arr):
        self.int_arr = int_arr
        for i in range(len(self.int_arr)):
            if i % 2 == 1:
                self.int_arr[i] *= self.int_arr[i]


class ArrayOpsProvider(DependencyProvider):

    def setup(self):
        self.arr_op = ArrayOps()

    def stop(self):
        del self.arr_op

    def get_dependency(self, worker_ctx):
        return self.arr_op