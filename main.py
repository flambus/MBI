'''
A simple Program for grabing video from basler camera and converting it to opencv img.
Tested on Basler acA1300-200uc (USB3, linux 64bit , python 3.5)
'''
from pypylon import pylon
import cv2 as cv
import numpy as np
from ctypes import *
import time
import os
import sys
import platform
import tempfile
import re
import skimage.feature

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

sys.path.append(r'C:\Users\lab\Desktop\LIA\Stage\integration\libximc_2.13.2\ximc-2.13.3\ximc\crossplatform\wrappers'
                r'\python')

if platform.system() == "Windows":
    # Determining the directory with dependencies for windows depending on the bit depth.
    arch_dir = "win64" if "64" in platform.architecture()[0] else "win32"  #
    libdir = r"C:\Users\lab\Desktop\LIA\Stage\integration\libximc_2.13.2\ximc-2.13.3\ximc\win64"
    sys.path.append(r"C:\Users\lab\Desktop\LIA\Stage\integration\libximc_2.13.2\ximc-2.13.3\ximc\win64")
    if sys.version_info >= (3, 8):
        os.add_dll_directory(libdir)
    else:
        os.environ["Path"] = libdir + ";" + os.environ["Path"]  # add dll path into an environment variable

try:
    from pyximc import *
except ImportError as err:
    print(
        "Can't import pyximc module. The most probable reason is that you changed the relative location of the "
        "test_Python.py and pyximc.py files. See developers' documentation for details.")
    exit()
except OSError as err:
    # print(err.errno, err.filename, err.strerror, err.winerror) # Allows you to display detailed information by
    # mistake.
    if platform.system() == "Windows":
        if err.winerror == 193:  # The bit depth of one of the libraries bindy.dll, libximc.dll, xiwrapper.dll does
            # not correspond to the operating system bit.
            print(
                "Err: The bit depth of one of the libraries bindy.dll, libximc.dll, xiwrapper.dll does not correspond "
                "to the operating system bit.")
            # print(err)
        elif err.winerror == 126:  # One of the library bindy.dll, libximc.dll, xiwrapper.dll files is missing.
            print("Err: One of the library bindy.dll, libximc.dll, xiwrapper.dll is missing.")
            print(
                "It is also possible that one of the system libraries is missing. This problem is solved by "
                "installing the vcredist package from the ximc\\winXX folder.")
            # print(err)
        else:  # Other errors the value of which can be viewed in the code.
            print(err)
        print(
            "Warning: If you are using the example as the basis for your module, make sure that the dependencies "
            "installed in the dependencies section of the example match your directory structure.")
        print("For correct work with the library you need: pyximc.py, bindy.dll, libximc.dll, xiwrapper.dll")
    else:
        print(err)
        print(
            "Can't load libximc library. Please add all shared libraries to the appropriate places. It is decribed in "
            "detail in developers' documentation. On Linux make sure you installed libximc-dev package.\nmake sure "
            "that the architecture of the system and the interpreter is the same")
    exit()

def move(lib, device_id, distance, udistance):
    print("\nGoing to {0} steps, {1} microsteps".format(distance, udistance))
    result = lib.command_move(device_id, distance, udistance)
    print("Result: " + repr(result))

def get_position(lib, device_id):
    print("\nRead position")
    x_pos = get_position_t()
    result = lib.get_position(device_id, byref(x_pos))
    print("Result: " + repr(result))
    if result == Result.Ok:
        print("Position: {0} steps, {1} microsteps".format(x_pos.Position, x_pos.uPosition))
    return x_pos.Position, x_pos.uPosition

print("Library loaded")

sbuf = create_string_buffer(64)
lib.ximc_version(sbuf)
print("Library version: " + sbuf.raw.decode().rstrip("\0"))

# Set bindy (network) keyfile. Must be called before any call to "enumerate_devices" or "open_device" if you
# wish to use network-attached controllers. Accepts both absolute and relative paths, relative paths are resolved
# relative to the process working directory. If you do not need network devices then "set_bindy_key" is optional.
# In Python make sure to pass byte-array object to this function (b"string literal").
result = lib.set_bindy_key(os.path.join(r"C:\Users\lab\Desktop\LIA\Stage\integration\libximc_2.13.2\ximc-2.13.3\ximc", "win32", "keyfile.sqlite").encode("utf-8"))
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
    #open_nameX = re.sub(r'^file', 'xi-emu', uri).encode()
    flag_virtual = 1
    print("The real controller is not found or busy with another app.")
    print("The virtual controller is opened to check the operation of the library.")
    print("If you want to open a real controller, connect it or close the application that uses it.")

if not open_nameX:
    exit(1)

if type(open_nameX) is str:
    open_nameX = open_nameX.encode()

if type(open_nameY) is str:
    open_nameY = open_nameY.encode()

print("\nOpen device " + repr(open_nameX))
device_id1 = lib.open_device(open_nameX)
print("Device id: " + repr(device_id1))

print("\nOpen device " + repr(open_nameY))
device_id2 = lib.open_device(open_nameY)
print("Device id: " + repr(device_id2))

if flag_virtual == 1:
    print(" ")
    print("The real controller is not found or busy with another app.")
    print("The virtual controller is opened to check the operation of the library.")
    print("If you want to open a real controller, connect it or close the application that uses it.")

startPosX = -1433
ustartPosX = -242
startPosY = 4490
ustartPosY = 73
finishPosX = 24835
ufinishPosX = 165
finishPosY = 4490
ufinishPosY = 73

currentPosX, currentUPosX = get_position(lib, device_id1)
currentPosY, currentUPosY = get_position(lib, device_id2)

xDif = (startPosX + ustartPosX) - (currentPosX + currentUPosX)
yDif = (startPosY + ustartPosY) - (currentPosY + currentUPosY)

move(lib, device_id1, currentPosX + xDif, currentUPosX)
move(lib, device_id2, currentPosY + yDif, currentUPosY)

while((currentPosX + currentUPosX) < (finishPosX + ufinishPosX)):
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult)
        img = image.GetArray()
    grabResult.Release()
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
    # noise removal
    kernel = np.ones((3, 3), np.uint8)
    opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=2)
    # sure background area
    sure_bg = cv.dilate(opening, kernel, iterations=3)
    # Finding sure foreground area
    dist_transform = cv.distanceTransform(opening, cv.DIST_L2, 5)
    ret, sure_fg = cv.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv.subtract(sure_bg, sure_fg)
    blobs = skimage.feature.blob_log(sure_fg, min_sigma=4, max_sigma=4, num_sigma=1, threshold=0.42)
    #sort by first column
    blobs = blobs[blobs[:, 0].argsort()]
    #blob coordinates to step instructions
    xMoveAggregator = 0
    yMoveAggregator = 0
    for blob in blobs:
        moveXinPX = blob[0] - 1024
        moveYinPX = blob[1] - 1024
        xPxToSteps = moveXinPX * 0.1925
        yPxToSteps = moveYinPX * 0.1925
        xMoveAggregator += xPxToSteps
        yMoveAggregator += yPxToSteps

# images = np.ndarray
#
# try:
#     while camera.IsGrabbing():
#         grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
#         if grabResult.GrabSucceeded():
#             # Access the image data
#             image = converter.Convert(grabResult)
#             startpos, ustartpos = get_position(lib, device_id1)
#             move(lib, device_id1, startpos + 1000, ustartpos + 1000)
#             time.sleep(5)
#             img = image.GetArray()
#             imgG = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#             np.append(images, imgG)
#             cv2.namedWindow('title', cv2.WINDOW_NORMAL)
#             cv2.imshow('title', imgG)
#             k = cv2.waitKey(1)
#             if k == 27:
#                 break
#         grabResult.Release()
# except KeyboardInterrupt:
#     raise Exception("stop")
#
#
# panorama = np.ndarray(images.shape[0] * 2048, images.shape[1])
# for image in images:
#     for i in range(2048):
#         np.append(panorama[i], image[i])
# cv2.namedWindow('panorama', cv2.WINDOW_NORMAL)
# cv2.imshow('panorama', panorama)
# # Releasing the resource
#
camera.StopGrabbing()
#
# cv2.destroyAllWindows()

print("\nClosing")

# The device_t device parameter in this function is a C pointer, unlike most library functions that use this parameter
lib.close_device(byref(cast(device_id1, POINTER(c_int))))
print("Done")