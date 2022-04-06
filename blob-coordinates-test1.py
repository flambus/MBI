import numpy as np
import pandas as pd
import os
import cv2 as cv
import matplotlib.pyplot as plt
import skimage.feature
#%matplotlib inline

img = cv.imread('img/water_coins.jpg')
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
cv.imshow("sure_fg", sure_fg)
height, width = img.shape[:2]
print(height, width)
blobs = skimage.feature.blob_log(sure_fg, min_sigma=4, max_sigma=4, num_sigma=1, threshold=0.42)

blobs = blobs[blobs[:, 0].argsort()]
#cv2.imshow('image', image)
print(blobs)
print(type(blobs))
print(len(blobs))

cv.waitKey(0)
cv.destroyAllWindows()

