"""
Created at 04.11.2019

@author: Piotr Bartman
@author: Sylwester Arabas
"""

import numpy as np
import numba
from numba import void, float64, int64, boolean, prange
from PySDM.conf import NUMBA_PARALLEL


class StorageMethods:
    storage = np.ndarray

    @staticmethod
    def array(shape, dtype):
        if dtype is float:
            data = np.full(shape, -1., dtype=np.float64)
        elif dtype is int:
            data = np.full(shape, -1, dtype=np.int64)
        else:
            raise NotImplementedError()
        return data

    @staticmethod
    def download(backend_data, np_target):
        np.copyto(np_target, backend_data, casting='safe')

    @staticmethod
    def dtype(data):
        return data.dtype

    @staticmethod
    def from_ndarray(array):
        if str(array.dtype).startswith('int'):
            dtype = np.int64
        elif str(array.dtype).startswith('float'):
            dtype = np.float64
        else:
            raise NotImplementedError()

        result = array.astype(dtype).copy()
        return result

    @staticmethod
    def read_row(array, i):
        return array[i, :]

    @staticmethod
    def shape(data):
        return data.shape

    @staticmethod
    @numba.njit(void(int64[:], int64, int64), parallel=NUMBA_PARALLEL)
    def shuffle(idx, length, axis):
        permutation = np.random.permutation(length)

        if axis == 0:
            idx[:length] = idx[permutation[:length]]
        else:
            raise NotImplementedError()

    @staticmethod
    def stable_argsort(idx, keys, length):
        idx[:length] = idx[np.argsort(keys[idx[:length]], kind='stable')]

    @staticmethod
    def to_ndarray(data):
        return data.copy()

    @staticmethod
    def upload(np_data, backend_target):
        np.copyto(backend_target, np_data, casting='safe')

    @staticmethod
    def write_row(array, i, row):
        array[i, :] = row
