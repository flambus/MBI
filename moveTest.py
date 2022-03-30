from ctypes import *
import time
import os
import sys
import platform
import tempfile
import re

#from move import open_name
from ximc.crossplatform.wrappers.python.pyximc import lib

cur_dir = os.path.abspath(os.path.dirname(__file__))  # Specifies the current directory.
ximc_dir = os.path.join(cur_dir, "ximc")
ximc_package_dir = os.path.join(ximc_dir, "crossplatform", "wrappers", "python")
sys.path.append(ximc_package_dir)  # add pyximc.py wrapper to python path

if platform.system() == "Windows":
    # Determining the directory with dependencies for windows depending on the bit depth.
    arch_dir = "win64" if "64" in platform.architecture()[0] else "win32"  #
    libdir = os.path.join(ximc_dir, arch_dir)
    if sys.version_info >= (3, 8):
        os.add_dll_directory(libdir)
    else:
        os.environ["Path"] = libdir + ";" + os.environ["Path"]  # add dll path into an environment variable

try:
    from pyximc import *
except ImportError as err:
    print(
        "Can't import pyximc module. The most probable reason is that you changed the relative location of the test_Python.py and pyximc.py files. See developers' documentation for details.")
    exit()
except OSError as err:
    # print(err.errno, err.filename, err.strerror, err.winerror) # Allows you to display detailed information by mistake.
    if platform.system() == "Windows":
        if err.winerror == 193:  # The bit depth of one of the libraries bindy.dll, libximc.dll, xiwrapper.dll does not correspond to the operating system bit.
            print(
                "Err: The bit depth of one of the libraries bindy.dll, libximc.dll, xiwrapper.dll does not correspond to the operating system bit.")
            # print(err)
        elif err.winerror == 126:  # One of the library bindy.dll, libximc.dll, xiwrapper.dll files is missing.
            print("Err: One of the library bindy.dll, libximc.dll, xiwrapper.dll is missing.")
            print(
                "It is also possible that one of the system libraries is missing. This problem is solved by installing the vcredist package from the ximc\\winXX folder.")
            # print(err)
        else:  # Other errors the value of which can be viewed in the code.
            print(err)
        print(
            "Warning: If you are using the example as the basis for your module, make sure that the dependencies installed in the dependencies section of the example match your directory structure.")
        print("For correct work with the library you need: pyximc.py, bindy.dll, libximc.dll, xiwrapper.dll")
    else:
        print(err)
        print(
            "Can't load libximc library. Please add all shared libraries to the appropriate places. It is decribed in detail in developers' documentation. On Linux make sure you installed libximc-dev package.\nmake sure that the architecture of the system and the interpreter is the same")
    exit()

device_id = lib.open_device(open_name)
print("Device id: " + repr(device_id))

def test_left(lib, device_id):
    print("\nMoving left")
    result = lib.command_left(device_id)
    print("Result: " + repr(result))

test_left(lib, device_id)

print("\nClosing")

# The device_t device parameter in this function is a C pointer, unlike most library functions that use this parameter
lib.close_device(byref(cast(device_id, POINTER(c_int))))
print("Done")