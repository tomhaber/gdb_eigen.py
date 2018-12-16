import gdb
import re
import itertools

from .helpers import *

class EigenMatrixPrinter:
    "Print Eigen Matrix or Array of some kind"

    def __init__(self, variety, info):
        self.variety = variety
        self.rows, self.cols, self.rowMajor, self.innerType, self.data = info

    class _iterator:
        def __init__ (self, rows, cols, dataPtr, rowMajor):
            self.rows = rows
            self.cols = cols
            self.dataPtr = dataPtr
            self.currentRow = 0
            self.currentCol = 0
            self.rowMajor = rowMajor

        def __iter__ (self):
            return self

        def next(self):
            return self.__next__()  # Python 2.x compatibility

        def __next__(self):
            row = self.currentRow
            col = self.currentCol
            if self.rowMajor == 0:
                if self.currentCol >= self.cols:
                    raise StopIteration

                self.currentRow = self.currentRow + 1
                if self.currentRow >= self.rows:
                    self.currentRow = 0
                    self.currentCol = self.currentCol + 1
            else:
                if self.currentRow >= self.rows:
                    raise StopIteration

                self.currentCol = self.currentCol + 1
                if self.currentCol >= self.cols:
                    self.currentCol = 0
                    self.currentRow = self.currentRow + 1

            item = self.dataPtr.dereference()
            self.dataPtr = self.dataPtr + 1
            if (self.cols == 1): #if it's a column vector
                    return ('[%d]' % (row,), item)
            elif (self.rows == 1): #if it's a row vector
                    return ('[%d]' % (col,), item)
            return ('[%d,%d]' % (row, col), item)

    def children(self):
        return self._iterator(self.rows, self.cols, self.data, self.rowMajor)

    def to_string(self):
        return "Eigen::%s<%s,%d,%d,%s> (data ptr: %s)" % (self.variety, self.innerType, self.rows, self.cols, "RowMajor" if self.rowMajor else  "ColMajor", self.data)

class EigenQuaternionPrinter:
    "Print an Eigen Quaternion"

    def __init__(self, val):
        "Extract all the necessary information"
        # The gdb extension does not support value template arguments - need to extract them by hand
        type = val.type
        if type.code == gdb.TYPE_CODE_REF:
                type = type.target()
        self.type = type.unqualified().strip_typedefs()
        self.innerType = self.type.template_argument(0)
        self.val = val

        # Quaternions have a struct as their storage, so we need to walk through this
        self.data = self.val['m_coeffs']['m_storage']['m_data']['array']
        self.data = self.data.cast(self.innerType.pointer())

    class _iterator:
        def __init__ (self, dataPtr):
            self.dataPtr = dataPtr
            self.currentElement = 0
            self.elementNames = ['x', 'y', 'z', 'w']

        def __iter__ (self):
            return self

        def next(self):
            return self.__next__()  # Python 2.x compatibility

        def __next__(self):
            element = self.currentElement

            if self.currentElement >= 4: #there are 4 elements in a quanternion
                    raise StopIteration

            self.currentElement = self.currentElement + 1

            item = self.dataPtr.dereference()
            self.dataPtr = self.dataPtr + 1
            return ('[%s]' % (self.elementNames[element],), item)

    def children(self):

            return self._iterator(self.data)

    def to_string(self):
            return "Eigen::Quaternion<%s> (data ptr: %s)" % (self.innerType, self.data)

def build_eigen_dictionary ():
    pretty_printers_dict[re.compile('^Eigen::Quaternion<.*>$')] = lambda val: EigenQuaternionPrinter(val)
    pretty_printers_dict[re.compile('^Eigen::Matrix<.*>$')] = lambda val: EigenMatrixPrinter("Matrix", eigen_matrix_info(val))
    pretty_printers_dict[re.compile('^Eigen::Array<.*>$')]  = lambda val: EigenMatrixPrinter("Array", eigen_matrix_info(val))
    pretty_printers_dict[re.compile('^Eigen::Ref<.*>$')]  = lambda val: EigenMatrixPrinter("Ref", eigen_ref_info(val))
    pretty_printers_dict[re.compile('^Eigen::Block<.*>$')]  = lambda val: EigenMatrixPrinter("Block", eigen_block_info(val))

def register_eigen_printers(obj):
    "Register eigen pretty-printers with objfile Obj"

    if obj == None:
        obj = gdb
    obj.pretty_printers.append(lookup_function)

def lookup_function(val):
    "Look-up and return a pretty-printer that can print va."

    type_, typename = value_type(val)
    if typename == None:
        return None

    for function in pretty_printers_dict:
        if function.search(typename):
            return pretty_printers_dict[function](val)

    return None

pretty_printers_dict = {}

build_eigen_dictionary()
