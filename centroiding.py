import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv

def centroiding(M, th, mn, mx, r):
    #M = self.cam_im_proc
    #th = int(self.gui_centroiding_threshold_spinner.value())
    #r = int(self.gui_centroiding_radius_spinner.value())
    cM = M.copy()
    (Nx, Ny) = np.shape(M)
    # XX,YY=np.meshgrid(range(0,Nx),range(0,Ny))
    XX, YY = np.meshgrid(range(0, Ny), range(0, Nx))
    cM[0:r, :] = 0
    cM[:, 0:r] = 0
    cM[Nx - r:Nx, :] = 0
    cM[:, Ny - r:Ny] = 0
    rM = np.zeros((Nx, Ny))
    ind = np.flatnonzero(M > th)
    (x, y) = np.unravel_index(ind, np.shape(M))
    # print (np.shape(ind))
    Xarr=[]
    Yarr=[]
    for i in range(0, len(ind)):
        if (cM[x[i], y[i]] > 0):
            A = cM[x[i] - r:x[i] + r, y[i] - r:y[i] + r]
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
            cM[x[i] - r:x[i] + r, y[i] - r:y[i] + r] = 0
    return rM, np.array(Xarr), np.array(Yarr)
    #self.cam_im_centr = rM

M = cv.imread('testlight_white_2.png')
gray = cv.cvtColor(M, cv.COLOR_BGR2GRAY)
M = 255-gray

print (np.max(M),np.min(M))
rM, Xarr, Yarr = centroiding(M, 50, 100000, 1000000, 80)


#cv.imshow("gray", rM)
#cv.waitKey(0)

# closing all open windows
#cv.destroyAllWindows()

plt.figure()
plt.imshow(gray,cmap='gray')
plt.scatter(Xarr, Yarr, s=10)#, markers="x")
plt.show()