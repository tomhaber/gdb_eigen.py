import gdb
import re

def value_type(val):
    type_ = val.type

    if type_.code == gdb.TYPE_CODE_REF:
        type_ = type_.target()

    type_ = type_.unqualified().strip_typedefs()

    typename = type_.tag
    return type_, typename

def extract_template_params(typename):
    regex = re.compile('\<.*\>')
    m = regex.findall(typename)[0][1:-1]
    template_params = m.split(',')
    template_params = [x.replace(" ", "") for x in template_params]
    return template_params

def eigen_matrix_info(val):
    type_, tag = value_type(val)
    template_params = extract_template_params(tag)

    innerType, rows, cols, options = (type_.template_argument(i) for i in range(4))
    if rows == -1:
        rows = int(val['m_storage']['m_rows'])
    else:
        rows = int(rows)

    if cols == -1:
        cols = int(val['m_storage']['m_cols'])
    else:
        cols = int(cols)

    rowMajor = (int(options) & 0x1) != 0
    data = val['m_storage']['m_data']

    # Fixed size matrices have a struct as their storage
    if data.type.code == gdb.TYPE_CODE_STRUCT:
        data = data['array']
        data = data.cast(self.innerType.pointer())

    return rows, cols, rowMajor, innerType, data

def eigen_ref_info(val):
    type_, tag = value_type(val)
    derived = type_.template_argument(0)

    innerType, rows, cols, options = (derived.template_argument(i) for i in range(4))
    if rows == -1:
        rows = int(val['m_rows']['m_value'])
    else:
        rows = int(rows)

    if cols == -1:
        cols = int(val['m_cols']['m_value'])
    else:
        cols = int(cols)

    rowMajor = (int(options) & 0x1) != 0

    data = val['m_data']
    return rows, cols, rowMajor, innerType, data

def eigen_block_info(val):
    type_, tag = value_type(val)
    derived = type_.template_argument(0)

    innerType, rows, cols, options = (derived.template_argument(i) for i in range(4))
    rows, cols = (type_.template_argument(i) for i in range(1,3))
    if rows == -1:
        rows = int(val['m_rows']['m_value'])
    else:
        rows = int(rows)

    if cols == -1:
        cols = int(val['m_cols']['m_value'])
    else:
        cols = int(cols)

    rowMajor = (int(options) & 0x1) != 0

    data = val['m_data']
    return rows, cols, rowMajor, innerType, data

def find_converter(val):
    type_, typename = value_type(val)
    for matcher, converter in type_dict.items():
        if matcher.search(typename):
            return converter

type_dict = {}
type_dict[re.compile('^Eigen::Matrix<.*>$')] = lambda val: eigen_matrix_info(val)
type_dict[re.compile('^Eigen::Array<.*>$')]  = lambda val: eigen_matrix_info(val)
type_dict[re.compile('^Eigen::Ref<.*>$')]  = lambda val: eigen_ref_info(val)
type_dict[re.compile('^Eigen::Map<.*>$')]  = lambda val: eigen_ref_info(val)
type_dict[re.compile('^Eigen::Block<.*>$')]  = lambda val: eigen_block_info(val)
