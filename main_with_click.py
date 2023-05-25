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
import pyfirmata
from datetime import datetime
import pathlib
import matplotlib.pyplot as plt
import re
import skimage.feature

port = 'COM6'
board = pyfirmata.Arduino(port)
pin = 13

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

sys.path.append(r'C:/lab/MBI/libximc_2.13.2/ximc-2.13.3/ximc/crossplatform/wrappers/python')

if platform.system() == "Windows":
    # Determining the directory with dependencies for windows depending on the bit depth.
    arch_dir = "win64" if "64" in platform.architecture()[0] else "win32"  #
    libdir = r"C:/lab/MBI/libximc_2.13.2/ximc-2.13.3/ximc/win64"
    sys.path.append(r"C:/lab/MBI/libximc_2.13.2/ximc-2.13.3/ximc/win64")
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
    # print("Result: " + repr(result))


def get_position(lib, device_id):
    print("\nRead position")
    x_pos = get_position_t()
    result = lib.get_position(device_id, byref(x_pos))
    # print("Result: " + repr(result))
    if result == Result.Ok:
        print("Position: {0} steps, {1} microsteps".format(x_pos.Position, x_pos.uPosition))
    return x_pos.Position, x_pos.uPosition


def centroiding(M, th, mn, mx, r):
    # M = self.cam_im_proc
    # th = int(self.gui_centroiding_threshold_spinner.value())
    # r = int(self.gui_centroiding_radius_spinner.value())
    cm = M.copy()

    # copy image into matrix with borders
    cm_bigger = np.zeros((cm.shape[0] + 100, cm.shape[1] + 100))
    for k in range(0, cm.shape[0]):
        for j in range(0, cm.shape[0]):
            cm_bigger[k + 50][j + 50] = cm[k][j]

    (Nx, Ny) = np.shape(cm_bigger)

    # XX,YY=np.meshgrid(range(0,Nx),range(0,Ny))
    XX, YY = np.meshgrid(range(0, Ny), range(0, Nx))

    # cm[0:r, :] = 0
    # cm[:, 0:r] = 0
    # cm[Nx - r:Nx, :] = 0
    # cm[:, Ny - r:Ny] = 0

    rM = np.zeros((Nx, Ny))
    ind = np.flatnonzero(M > th)
    print(ind)
    (x, y) = np.unravel_index(ind, np.shape(cm_bigger))
    # print (np.shape(ind))
    Xarr = []
    Yarr = []
    for i in range(0, len(ind)):
        if cm_bigger[x[i], y[i]] > 0:
            A = cm_bigger[x[i] - r:x[i] + r, y[i] - r:y[i] + r]
            sA = np.sum(A)
            if mn < sA < mx:
                cx = int(np.sum(XX[x[i] - r:x[i] + r,
                                y[i] - r:y[i] + r] * A) / sA + 0.5)
                cy = int(np.sum(YY[x[i] - r:x[i] + r,
                                y[i] - r:y[i] + r] * A) / sA + 0.5)
                # rM[cy,cx] = 1 # maybe good to set to sA?
                # if self.gui_centroiding_sum_cb.isChecked():
                Xarr.append(cx)
                Yarr.append(cy)
                rM[cy, cx] = sA  # maybe good to set to sA?
            # else:
            # rM[cy, cx] = 1
            cm_bigger[x[i] - r:x[i] + r, y[i] - r:y[i] + r] = 0
    return np.array(Xarr), np.array(Yarr)
    # self.cam_im_centr = rM


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
    uri = urllib.parse.urlunparse(
        urllib.parse.ParseResult(scheme="file", netloc=None, path=tempdir, params=None, query=None,
                                 fragment=None))
    # open_nameX = re.sub(r'^file', 'xi-emu', uri).encode()
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

laserX_raw, laserY_raw = -1, -1
# while 1:
#     # get current live image
#     grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

#     def click(event, x, y, flags, param):
#         global laserX_raw, laserY_raw
#         if event == cv.EVENT_LBUTTONDOWN:
#             laserX_raw, laserY_raw = x, y
#             print(x, y)

#     if grabResult.GrabSucceeded():
#         image = converter.Convert(grabResult)
#         img = image.GetArray()
#         cv.line(img, pt1=(1024, 2048), pt2=(1024, 0), color=(0, 0, 255), thickness=1)
#         cv.line(img, pt1=(0, 1024), pt2=(2048, 1024), color=(0, 0, 255), thickness=1)
#         cv.namedWindow('image', cv.WINDOW_NORMAL)
#         cv.imshow('image', img)
#         cv.setMouseCallback('image', click)
#     grabResult.Release()

#     k = cv.waitKey(20) & 0xFF
#     if k == ord('a'):
#         break

# cv.destroyAllWindows()

stepSize = 0.323

# laserX = laserX_raw - 1024
# laserY = laserY_raw - 1024
# laserX = int(round((laserX * stepSize), 3))
# laserY = int(round((laserY * stepSize), 3))
laserX = 0
laserY = 0
print(laserX, laserY)

# create a directory to save live images
now = datetime.now()
year = now.strftime("%Y")
month = now.strftime("%m")
day = now.strftime("%d")
directoryName = "{0}-{1}-{2}".format(year, month, day)
path = "C:/lab/MBI/img/" + directoryName
directory = pathlib.Path(path)
if directory.exists():
    # for file_name in os.listdir(path):
    #     file = path + "/" + file_name
    #     os.remove(file)
    pass
else:
    os.mkdir(path)

imageCount = 0
gateOpened = False
startTime = -1

ix, iy = -1, -1
prevX, prevY = -1, -1
while camera.IsGrabbing():
    # get current live image
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult)
        img = image.GetArray()
        img_clean = np.copy(img)
        # cv.line(img, pt1=(0, laserY_raw), pt2=(2048, laserY_raw), color=(0, 0, 255), thickness=1)
        # cv.line(img, pt1=(laserX_raw, 2048), pt2=(laserX_raw, 0), color=(0, 0, 255), thickness=1)
        cv.line(img, pt1=(0, 1024), pt2=(2048, 1024), color=(0, 0, 255), thickness=1)
        cv.line(img, pt1=(1024, 2048), pt2=(1024, 0), color=(0, 0, 255), thickness=1)
        img = cv.resize(img, (2048, 2048))
        cv.namedWindow('image', cv.WINDOW_NORMAL)
        if gateOpened == True:
            diff = (datetime.now() - startTime).seconds
            hours = diff // 3600
            minutes = diff // 60
            seconds = diff % 60
            cv.putText(img, '{0}:{1}:{2}'.format(hours, minutes, seconds), (70,70), cv.FONT_HERSHEY_SIMPLEX , 1, (255, 0, 0), 2, cv.LINE_AA) # adding timer text
        cv.imshow('image', img)
    grabResult.Release()
    k = cv.waitKey(20) & 0xFF
    if k == ord('n'):
        print('n pressed')
        # move one frame from center
        currentPosX, currentUPosX = get_position(lib, device_id1)
        currentPosY, currentUPosY = get_position(lib, device_id2)
        print(currentPosX, currentPosY)
        moveToNextFrame = int(round(2048 * stepSize))
        print(moveToNextFrame)
        move(lib, device_id1, currentPosX + moveToNextFrame, currentUPosX)
        print("\n-------\nframe changed\n-------\n")
        #time.sleep(2)
    elif k == ord('a'):
        break
    elif k == ord('o'):
        print('o pressed')
        # open and close gate
        board.digital[pin].write(1)
        gateOpened = True
        startTime = datetime.now()
        # time.sleep(120)
        # board.digital[pin].write(0)
    elif k == ord('c'):
        print('c pressed')
        # open and close gate
        board.digital[pin].write(0)
        gateOpened = False
        startTime = -1
    elif k == ord('s'):
        print('s pressed')
        # save current live image
        filename = "{0}/frame{1}.jpeg".format(path, imageCount)
        cv.imwrite(filename, img_clean)
        imageCount += 1

    # mouse callback function
    def click(event, x, y, flags, param):
        global ix, iy
        global prevX, prevY
        if event == cv.EVENT_LBUTTONDOWN:
            # if ix == -1:
            ix, iy = x, y
            print("x, y:")
            print('y')
            print(x, y)
            blob = [ix - 1024, iy - 1024]
            print("object:")
            print(blob)
            # compute needed steps to reach egg (pixels -> stage steps)
            xPxToSteps = int(round((blob[0] * stepSize) - laserX, 3))
            yPxToSteps = int(round((blob[1] * stepSize) - laserY, 3))
            currentPosX, currentUPosX = get_position(lib, device_id1)
            currentPosY, currentUPosY = get_position(lib, device_id2)
            print(prevX)
            # if ix > 0 and prevX < -1:
            #     move(lib, device_id1, currentPosX + xPxToSteps + 3, currentUPosX)
            #     move(lib, device_id2, currentPosY + yPxToSteps, currentUPosY)
            #     print("\ngoing to {0}x, {1}y\n".format(blob[0], blob[1]))
            #     time.sleep(2)
            # elif ix < 0 and prevX > 0:
            #     move(lib, device_id1, currentPosX + xPxToSteps - 3, currentUPosX)
            #     move(lib, device_id2, currentPosY + yPxToSteps, currentUPosY)
            #     print("\ngoing to {0}x, {1}y\n".format(blob[0], blob[1]))
            #     time.sleep(2)
            # else:
            move(lib, device_id1, currentPosX + xPxToSteps, currentUPosX)
            move(lib, device_id2, currentPosY + yPxToSteps, currentUPosY)
            print("\ngoing to {0}x, {1}y\n".format(blob[0], blob[1]))
            #time.sleep(2) ###was removed to have continuous cam image flow
            prevX = ix - 1024
            print("prevX: ", prevX)

    cv.setMouseCallback('image', click)

camera.StopGrabbing()
cv.destroyAllWindows()

print("\nClosing")

# The device_t device parameter in this function is a C pointer, unlike most library functions that use this parameter
lib.close_device(byref(cast(device_id1, POINTER(c_int))))
print("Done")
