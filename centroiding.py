import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv
from pypylon import pylon

# conecting to the first available camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Grabing Continusely (video) with minimal delay
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()

# converting to opencv bgr format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned


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
    XX, YY = np.meshgrid(range(0, Ny), range(0, Nx))

    rM = np.zeros((Nx, Ny))
    ind = np.flatnonzero(M > th)
    print(ind)
    (x, y) = np.unravel_index(ind, np.shape(cm_bigger))
    print((x, y))
    Xarr = []
    Yarr = []
    for i in range(0, len(ind)):
        if cm_bigger[x[i], y[i]] > 0:
            A = cm_bigger[x[i] - r:x[i] + r, y[i] - r:y[i] + r]
            sA = np.sum(A)
            if mn < sA < mx:
                cx = int(np.sum(XX[x[i] - r:x[i] + r, y[i] - r:y[i] + r] * A) / sA + 0.5)
                cy = int(np.sum(YY[x[i] - r:x[i] + r, y[i] - r:y[i] + r] * A) / sA + 0.5)
                # rM[cy,cx] = 1 # maybe good to set to sA?
                Xarr.append(cx)
                Yarr.append(cy)
                rM[cy, cx] = sA  # maybe good to set to sA?
            cm_bigger[x[i] - r:x[i] + r, y[i] - r:y[i] + r] = 0
    return np.array(Xarr), np.array(Yarr)


grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
if grabResult.GrabSucceeded():
    image = converter.Convert(grabResult)
    img = image.GetArray()
grabResult.Release()
camera.StopGrabbing()

# convert image to gray and run the centroiding algorithm
threshold = 40
mn = 300000
mx = 1000000
r = 100
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
gray = 255 - gray
Xarr, Yarr = centroiding(gray, threshold, mn, mx, r)
print("Xarr:\n")
print(Xarr)
print("\nYarr:\n")
print(Yarr)

# create blob x/y-datapairs from Xarr and Yarr
blobs = []
for i in range(len(Xarr)):
    if 2048 > Xarr[i] > 0 and 2048 > Yarr[i] > 0:
        blob = [Xarr[i], Yarr[i]]
        blobs.append(blob)
blobs = np.array(blobs)

# create an image with all blobs marked (for each frame)
for blob in blobs:
    blob[0] = blob[0] - 50
    blob[1] = blob[1] - 50
    cv.circle(img, (blob[0], blob[1]), radius=10, color=(0, 0, 255), thickness=-1)

img = cv.circle(img, (1024, 1024), radius=10, color=(50, 205, 50), thickness=-1)  # draw circle in image center (to test precision)
cv.line(img, pt1=(0, 683), pt2=(2048, 683), color=(0, 0, 255), thickness=1)
cv.line(img, pt1=(0, 1365), pt2=(2048, 1365), color=(0, 0, 255), thickness=1)
cv.line(img, pt1=(1024, 2048), pt2=(1024, 0), color=(0, 0, 255), thickness=1)
# img = cv.resize(img, (800, 800))
# cv.imshow("img", img)
# cv.waitKey(0)
cv.imwrite("img/centroidingTest/img{4}_centroidingTest_th{0}_mn{1}_mx{2}_r{3}.jpeg".format(threshold, mn, mx, r, 10), img)

# blobs = []
# for i in range(len(Xarr)):
#     blob=[Xarr[i], Yarr[i]]
#     blobs.append(blob)
# blobs = np.array(blobs)
# print(blobs)
# print(type(blobs))
# print(blobs.shape)

# closing all open windows
# cv.destroyAllWindows()

# plt.figure()
# plt.imshow(gray, cmap='gray')
# plt.scatter(Xarr, Yarr, s=10)  # , markers="x")
# plt.show()
