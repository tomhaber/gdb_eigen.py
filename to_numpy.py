import gdb
import numpy as np
from .helpers import *

def info_to_numpy(info):
    rows, cols, rowMajor, innerType, data = info

    dtype = innerType.name
    order = rowMajor and 'C' or 'F'

    array = np.empty([rows, cols], dtype=dtype, order=order)
    if rowMajor:
        dataPtr = data
        for r in range(rows):
            for c in range(cols):
                array[r,c] = dataPtr.dereference()
                dataPtr = dataPtr + 1
    else:
        dataPtr = data
        for c in range(cols):
            for r in range(rows):
                array[r,c] = dataPtr.dereference()
                dataPtr = dataPtr + 1

    return array

def expr_to_info(expr):
    val = gdb.parse_and_eval(expr)

    converter = find_converter(val)
    if not converter:
        raise gdb.GdbError("cannot convert value to numpy")

    return converter(val)

def to_numpy(expr):
    info = expr_to_info(expr)
    return info_to_numpy(info)

def from_numpy(expr, array):
    info = expr_to_info(expr)

    rows, cols, rowMajor, innerType, data = info
    eigen_sizeof = rows * cols* innerType.sizeof

    if array.shape[0] != rows and array.shape[1] != cols:
        raise gdb.GdbError("array dimensions {}x{} mismatch with eigen object {}x{}"
                % (array.shape[0], array.shape[1], rows, cols))

    if rowMajor:
        v = array.astype(innerType.name, order='C', copy=False)
    else:
        v = array.T.astype(innerType.name, order='C', copy=False)

    if eigen_sizeof != v.nbytes:
        raise gdb.GdbError("size mismatch, cannot correct")

    z = gdb.selected_inferior().write_memory(data, v, v.nbytes)
    return array
