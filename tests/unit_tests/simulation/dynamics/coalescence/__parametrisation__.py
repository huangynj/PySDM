"""
Created at 04.11.2019

@author: Piotr Bartman
@author: Sylwester Arabas
"""

import pytest
import numpy as np


class StubKernel:
    def __init__(self, returned_value=-1):
        self.returned_value = returned_value

    def __call__(self, backend, output, is_first_in_pair, state):
        backend_fill(backend, output, self.returned_value)


def backend_fill(backend, array, value, odd_zeros=False):
    if odd_zeros:
        if isinstance(value, np.ndarray):
            full_ndarray = insert_zeros(value).astype(np.float64)
        else:
            full_ndarray = np.full(backend.shape(array)[0] // 2, value).astype(np.float64)
            full_ndarray = insert_zeros(full_ndarray)
            if backend.shape(array)[0] % 2 != 0:
                full_ndarray = np.concatenate((full_ndarray, np.zeros(1)))
    else:
        full_ndarray = np.full(backend.shape(array), value).astype(np.float64)

    full_backend = backend.from_ndarray(full_ndarray)
    backend.multiply(array, 0.)
    backend.add(array, full_backend)


def insert_zeros(array):
    result = np.concatenate((array, np.zeros_like(array))).reshape(2, -1).flatten(order='F')
    return result


'''
x parametrisation: x_2
'''

__x__ = {'ones_2': pytest.param(np.array([1., 1.])),
         'random_2': pytest.param(np.array([4., 2.]))
         }


@pytest.fixture(params=[
    __x__['ones_2'],
    __x__['random_2']
])
def x_2(request):
    return request.param


'''
n parametrisation: 
'''

__n__ = {'1_1': pytest.param(np.array([1, 1])),
         '5_1': pytest.param(np.array([5, 1])),
         '5_3': pytest.param(np.array([5, 3]))
         }


@pytest.fixture(params=[
    __n__['1_1'],
    __n__['5_1'],
    __n__['5_3']
])
def n_2(request):
    return request.param