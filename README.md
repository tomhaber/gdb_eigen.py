# gdb_eigen.py
pretty printing and read/write to hdf5 of eigen matrices in gdb

## Installation
Place the files in some directory, for example ~/.gdb/eigen, and put the following code snippet in your ~/.gdbinit file:
```
python
import sys
sys.path.insert(0, '<folder containing 'eigen'>')
import eigen
end
```
