import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv

def centroiding(M, th, mn, mx, r):
    #M = self.cam_im_proc
    #th = int(self.gui_centroiding_threshold_spinner.value())
    #r = int(self.gui_centroiding_radius_spinner.value())
    cm = M.copy()

    bordersize = r
    border = cv.copyMakeBorder(
        cm,
        top=bordersize,
        bottom=bordersize,
        left=bordersize,
        right=bordersize,
        borderType=cv.BORDER_CONSTANT,
        value=[255, 255, 255]
    )
    (Nx, Ny) = np.shape(cm)
    print(Ny, Nx)
    #border = cv.resize(border, (400, 400))
    #cv.imshow("border", border)
    #cv.waitKey(0)

    # XX,YY=np.meshgrid(range(0,Nx),range(0,Ny))
    XX, YY = np.meshgrid(range(0, Ny), range(0, Nx))
    # cm[0:r, :] = 0
    # cm[:, 0:r] = 0
    # cm[Nx - r:Nx, :] = 0
    # cm[:, Ny - r:Ny] = 0
    rM = np.zeros((Nx, Ny))
    ind = np.flatnonzero(M > th)
    print(ind)
    (x, y) = np.unravel_index(ind, np.shape(cm))
    # print (np.shape(ind))
    Xarr=[]
    Yarr=[]
    for i in range(0, len(ind)):
        if (cm[x[i], y[i]] > 0):
            A = cm[x[i] - r:x[i] + r, y[i] - r:y[i] + r]
            sA = np.sum(A)
            if (sA>mn and sA<mx):
                cx = int(np.sum(XX[x[i] - r:x[i] + r,
                                y[i] - r:y[i] + r] * A) / sA + 0.5)
                cy = int(np.sum(YY[x[i] - r:x[i] + r,
                                y[i] - r:y[i] + r] * A) / sA + 0.5)
                # rM[cy,cx] = 1 # maybe good to set to sA?
                #if self.gui_centroiding_sum_cb.isChecked():
                Xarr.append(cx)
                Yarr.append(cy)
                rM[cy, cx] = sA  # maybe good to set to sA?
            #else:
                #rM[cy, cx] = 1
            cm[x[i] - r:x[i] + r, y[i] - r:y[i] + r] = 0
    return rM, np.array(Xarr), np.array(Yarr)
    #self.cam_im_centr = rM

M = cv.imread('img/Image__2022-04-29__14-09-37.jpg')
gray = cv.cvtColor(M, cv.COLOR_BGR2GRAY)
M = 255-gray

print(np.max(M), np.min(M))
rM, Xarr, Yarr = centroiding(M, 80, 500000, 10000000, 80)

blobs = []
for i in range(len(Xarr)):
    blob=[Xarr[i], Yarr[i]]
    blobs.append(blob)
blobs = np.array(blobs)
print(blobs)
print(type(blobs))
print(blobs.shape)

#cv.imshow("gray", rM)
#cv.waitKey(0)

# closing all open windows
#cv.destroyAllWindows()

plt.figure()
plt.imshow(gray, cmap='gray')
plt.scatter(Xarr, Yarr, s=10)#, markers="x")
plt.show()
