import gdb
import h5py
import numpy as np

from .to_numpy import to_numpy, from_numpy

class WriteEigenH5(gdb.Command):
  """Write eigen matrix/array to hdf5."""

  def __init__ (self):
    super(WriteEigenH5, self).__init__ ("write-h5", gdb.COMMAND_USER)

  def invoke (self, arg, from_tty):
    argv = gdb.string_to_argv(arg)
    if len(argv) < 3:
        raise gdb.GdbError("expecting filename, name and expression")

    fname = argv[0]
    name = argv[1]
    expr = " ".join(argv[2:])
    array = to_numpy(expr)

    hf = h5py.File(fname, 'a')
    if not name in hf:
        hf.create_dataset(name, data=array)
    else:
        data = hf.get(name)
        data[...] = array
    hf.close()

    self.dont_repeat()

class ReadEigenH5(gdb.Command):
  """read eigen matrix/array from hdf5."""

  def __init__ (self):
    super(ReadEigenH5, self).__init__ ("read-h5", gdb.COMMAND_USER)

  def invoke(self, arg, from_tty):
    argv = gdb.string_to_argv(arg)
    if len(argv) < 3:
        raise gdb.GdbError("expecting filename, name and expression")

    fname = argv[0]
    name = argv[1]
    expr = " ".join(argv[2:])

    hf = h5py.File(fname, 'r')
    array = hf.get(name).value
    hf.close()

    from_numpy(expr, array)
    self.dont_repeat()

WriteEigenH5()
ReadEigenH5()
