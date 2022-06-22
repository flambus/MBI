from ctypes import *
import time
import os
import sys
import platform
import tempfile
import re
from pypylon import pylon
import cv2

# conecting to the first available camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Grabing Continusely (video) with minimal delay
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()

# converting to opencv bgr format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

if sys.version_info >= (3, 0):
    import urllib.parse

# Dependences

# For correct usage of the library libximc,
# you need to add the file pyximc.py wrapper with the structures of the library to python path.
# cur_dir = os.path.abspath(os.path.dirname(__file__)) # Specifies the current directory.
# print(cur_dir)
# ximc_dir = os.path.join(cur_dir, "..", "..", "..", "ximc") # Formation of the directory name with all dependencies. The dependencies for the examples are located in the ximc directory.
# ximc_package_dir = os.path.join(ximc_dir, "crossplatform", "wrappers", "python") # Formation of the directory name with python dependencies.
# sys.path.append(ximc_package_dir)  # add pyximc.py wrapper to python path

sys.path.append(r'C:\Users\lab\Desktop\LIA\Stage\integration\libximc_2.13.2\ximc-2.13.3\ximc\crossplatform\wrappers'
                r'\python')

# Depending on your version of Windows, add the path to the required DLLs to the environment variable
# bindy.dll
# libximc.dll
# xiwrapper.dll
if platform.system() == "Windows":
    # Determining the directory with dependencies for windows depending on the bit depth.
    arch_dir = "win64" if "64" in platform.architecture()[0] else "win32"  #
    # libdir = os.path.join(ximc_dir, arch_dir)
    libdir = r"C:\Users\lab\Desktop\LIA\Stage\integration\libximc_2.13.2\ximc-2.13.3\ximc\win64"
    sys.path.append(r"C:\Users\lab\Desktop\LIA\Stage\integration\libximc_2.13.2\ximc-2.13.3\ximc\win64")
    print(libdir)
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

def test_info(lib, device_id):
    print("\nGet device info")
    x_device_information = device_information_t()
    result = lib.get_device_information(device_id, byref(x_device_information))
    print("Result: " + repr(result))
    if result == Result.Ok:
        print("Device information:")
        print(" Manufacturer: " +
              repr(string_at(x_device_information.Manufacturer).decode()))
        print(" ManufacturerId: " +
              repr(string_at(x_device_information.ManufacturerId).decode()))
        print(" ProductDescription: " +
              repr(string_at(x_device_information.ProductDescription).decode()))
        print(" Major: " + repr(x_device_information.Major))
        print(" Minor: " + repr(x_device_information.Minor))
        print(" Release: " + repr(x_device_information.Release))


def test_status(lib, device_id):
    print("\nGet status")
    x_status = status_t()
    result = lib.get_status(device_id, byref(x_status))
    print("Result: " + repr(result))
    if result == Result.Ok:
        print("Status.Ipwr: " + repr(x_status.Ipwr))
        print("Status.Upwr: " + repr(x_status.Upwr))
        print("Status.Iusb: " + repr(x_status.Iusb))
        print("Status.Flags: " + repr(hex(x_status.Flags)))


def test_get_position(lib, device_id):
    print("\nRead position")
    x_pos = get_position_t()
    result = lib.get_position(device_id, byref(x_pos))
    print("Result: " + repr(result))
    if result == Result.Ok:
        print("Position: {0} steps, {1} microsteps".format(x_pos.Position, x_pos.uPosition))
    return x_pos.Position, x_pos.uPosition


def test_left(lib, device_id):
    print("\nMoving left")
    result = lib.command_left(device_id)
    print("Result: " + repr(result))

def right(lib, device_id):
    print("\nMoving right")
    result = lib.command_right(device_id)
    print("Result: " + repr(result))

def test_move(lib, device_id, distance, udistance):
    print("\nGoing to {0} steps, {1} microsteps".format(distance, udistance))
    result = lib.command_move(device_id, distance, udistance)
    print("Result: " + repr(result))


def test_wait_for_stop(lib, device_id, interval):
    print("\nWaiting for stop")
    result = lib.command_wait_for_stop(device_id, interval)
    print("Result: " + repr(result))


def test_serial(lib, device_id):
    print("\nReading serial")
    x_serial = c_uint()
    result = lib.get_serial_number(device_id, byref(x_serial))
    if result == Result.Ok:
        print("Serial: " + repr(x_serial.value))


def test_get_speed(lib, device_id):
    print("\nGet speed")
    # Create move settings structure
    mvst = move_settings_t()
    # Get current move settings from controller
    result = lib.get_move_settings(device_id, byref(mvst))
    # Print command return status. It will be 0 if all is OK
    print("Read command result: " + repr(result))

    return mvst.Speed


def test_set_speed(lib, device_id, speed):
    print("\nSet speed")
    # Create move settings structure
    mvst = move_settings_t()
    # Get current move settings from controller
    result = lib.get_move_settings(device_id, byref(mvst))
    # Print command return status. It will be 0 if all is OK
    print("Read command result: " + repr(result))
    print("The speed was equal to {0}. We will change it to {1}".format(mvst.Speed, speed))
    # Change current speed
    mvst.Speed = int(speed)
    # Write new move settings to controller
    result = lib.set_move_settings(device_id, byref(mvst))
    # Print command return status. It will be 0 if all is OK
    print("Write command result: " + repr(result))


def test_set_microstep_mode_256(lib, device_id):
    print("\nSet microstep mode to 256")
    # Create engine settings structure
    eng = engine_settings_t()
    # Get current engine settings from controller
    result = lib.get_engine_settings(device_id, byref(eng))
    # Print command return status. It will be 0 if all is OK
    print("Read command result: " + repr(result))
    # Change MicrostepMode parameter to MICROSTEP_MODE_FRAC_256
    # (use MICROSTEP_MODE_FRAC_128, MICROSTEP_MODE_FRAC_64 ... for other microstep modes)
    eng.MicrostepMode = MicrostepMode.MICROSTEP_MODE_FRAC_256
    # Write new engine settings to controller
    result = lib.set_engine_settings(device_id, byref(eng))
    # Print command return status. It will be 0 if all is OK
    print("Write command result: " + repr(result))

# variable 'lib' points to a loaded library
# note that ximc uses stdcall on win
print("Library loaded")

sbuf = create_string_buffer(64)
lib.ximc_version(sbuf)
print("Library version: " + sbuf.raw.decode().rstrip("\0"))

# Set bindy (network) keyfile. Must be called before any call to "enumerate_devices" or "open_device" if you
# wish to use network-attached controllers. Accepts both absolute and relative paths, relative paths are resolved
# relative to the process working directory. If you do not need network devices then "set_bindy_key" is optional.
# In Python make sure to pass byte-array object to this function (b"string literal").
result = lib.set_bindy_key(
    os.path.join(r"C:\Users\lab\Desktop\LIA\Stage\integration\libximc_2.13.2\ximc-2.13.3\ximc", "win32",
                 "keyfile.sqlite").encode("utf-8"))
if result != Result.Ok:
    lib.set_bindy_key("keyfile.sqlite".encode("utf-8"))  # Search for the key file in the current directory.

# This is device search and enumeration with probing. It gives more information about devices.
probe_flags = EnumerateFlags.ENUMERATE_PROBE + EnumerateFlags.ENUMERATE_NETWORK
enum_hints = b"addr="
# enum_hints = b"addr=" # Use this hint string for broadcast enumerate
devenum = lib.enumerate_devices(probe_flags, enum_hints)
print("Device enum handle: " + repr(devenum))
print("Device enum handle type: " + repr(type(devenum)))

dev_count = lib.get_device_count(devenum)
print("Device count: " + repr(dev_count))

controller_name = controller_name_t()
for dev_ind in range(0, dev_count):
    enum_name = lib.get_device_name(devenum, dev_ind)
    result = lib.get_enumerate_device_controller_name(devenum, dev_ind, byref(controller_name))
    if result == Result.Ok:
        print("Enumerated device #{} name (port name): ".format(dev_ind) + repr(enum_name) + ". Friendly name: " + repr(
            controller_name.ControllerName) + ".")

flag_virtual = 0

open_nameX = None
open_nameY = None
if len(sys.argv) > 1:
    open_nameX = sys.argv[1]
elif dev_count > 0:
    open_nameX = lib.get_device_name(devenum, 0)
    open_nameY = lib.get_device_name(devenum, 1)
elif sys.version_info >= (3, 0):
    # use URI for virtual device when there is new urllib python3 API
    tempdir = tempfile.gettempdir() + "/testdevice.bin"
    if os.altsep:
        tempdir = tempdir.replace(os.sep, os.altsep)
    # urlparse build wrong path if scheme is not file
    uri = urllib.parse.urlunparse(urllib.parse.ParseResult(scheme="file", \
                                                           netloc=None, path=tempdir, params=None, query=None,
                                                           fragment=None))
    open_nameX = re.sub(r'^file', 'xi-emu', uri).encode()
    flag_virtual = 1
    print("The real controller is not found or busy with another app.")
    print("The virtual controller is opened to check the operation of the library.")
    print("If you want to open a real controller, connect it or close the application that uses it.")

if not open_nameX:
    exit(1)

if type(open_nameX) is str:
    open_nameX = open_nameX.encode()

print("\nOpen device " + repr(open_nameX))
device_id = lib.open_device(open_nameX)
print("Device id: " + repr(device_id))

print("\nOpen device " + repr(open_nameY))
device_id2 = lib.open_device(open_nameY)
print("Device id: " + repr(device_id2))

steps = 5
stepValue = 80
for i in range(steps):
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    image = converter.Convert(grabResult)
    img = image.GetArray()
    cv2.namedWindow('title', cv2.WINDOW_NORMAL)
    cv2.imshow('title', img)
    cv2.imwrite('img/calibration/22-06_moved100steps{0}.png'.format(i), img)

    startposX, ustartposX = test_get_position(lib, device_id)
    test_move(lib, device_id, startposX + stepValue, ustartposX)
    time.sleep(2)
    grabResult.Release()

startposX, ustartposX = test_get_position(lib, device_id)
test_move(lib, device_id, startposX - (stepValue * steps), ustartposX)
startposX, ustartposX = test_get_position(lib, device_id2)

## test step one direction and back

# startposX, ustartposX = test_get_position(lib, device_id)
# grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
# image = converter.Convert(grabResult)
# img = image.GetArray()
# cv2.line(img, pt1=(0, 1024), pt2=(2048, 1024), color=(0, 0, 255), thickness=1)
# cv2.line(img, pt1=(1024, 2048), pt2=(1024, 0), color=(0, 0, 255), thickness=1)
# cv2.imwrite('img/13-06_startingPosition.png', img)
# grabResult.Release()
#
# test_move(lib, device_id, startposX - 100, ustartposX)
# time.sleep(2)
# grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
# image = converter.Convert(grabResult)
# img = image.GetArray()
# cv2.line(img, pt1=(0, 1024), pt2=(2048, 1024), color=(0, 0, 255), thickness=1)
# cv2.line(img, pt1=(1024, 2048), pt2=(1024, 0), color=(0, 0, 255), thickness=1)
# cv2.imwrite('img/13-06_moved100steps.png', img)
# grabResult.Release()
#
# startposX, ustartposX = test_get_position(lib, device_id)
# test_move(lib, device_id, startposX + 100, ustartposX)
# time.sleep(2)
# grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
# image = converter.Convert(grabResult)
# img = image.GetArray()
# cv2.line(img, pt1=(0, 1024), pt2=(2048, 1024), color=(0, 0, 255), thickness=1)
# cv2.line(img, pt1=(1024, 2048), pt2=(1024, 0), color=(0, 0, 255), thickness=1)
# cv2.imwrite('img/13-06_moved100stepsBack.png', img)
# grabResult.Release()


# Releasing the resource
camera.StopGrabbing()

cv2.destroyAllWindows()

#test_wait_for_stop(lib, device_id, 100)

#test_get_position(lib, device_id)


    # second move

#current_speed = test_get_speed(lib, device_id)
#test_set_speed(lib, device_id, current_speed / 2)
# test_move(lib, device_id, startpos, ustartpos)
#test_move(lib, device_id, 1200, 160)
# test_wait_for_stop(lib, device_id, 100)
#test_status(lib, device_id)
#test_serial(lib, device_id)

print("\nClosing")

# The device_t device parameter in this function is a C pointer, unlike most library functions that use this parameter
lib.close_device(byref(cast(device_id, POINTER(c_int))))
print("Done")

if flag_virtual == 1:
    print(" ")
    print("The real controller is not found or busy with another app.")
    print("The virtual controller is opened to check the operation of the library.")
    print("If you want to open a real controller, connect it or close the application that uses it.")
