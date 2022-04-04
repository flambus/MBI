import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import skimage.feature
import os

img = cv.imread('img/testlight_white_2.png')
img = cv.resize(img, (400, 400))
gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(gray,0,255,cv.THRESH_BINARY_INV+cv.THRESH_OTSU)

# noise removal
kernel = np.ones((3,3),np.uint8)
opening = cv.morphologyEx(thresh,cv.MORPH_OPEN,kernel, iterations = 2)
# sure background area
sure_bg = cv.dilate(opening,kernel,iterations=3)
# Finding sure foreground area
dist_transform = cv.distanceTransform(opening,cv.DIST_L2,5)
ret, sure_fg = cv.threshold(dist_transform,0.5*dist_transform.max(),255,0)
# Finding unknown region
sure_fg = np.uint8(sure_fg)
unknown = cv.subtract(sure_bg,sure_fg)

# Marker labelling
ret, markers = cv.connectedComponents(sure_fg)
# Add one to all labels so that sure background is not 0, but 1
markers = markers+1
# Now, mark the region of unknown with zero
markers[unknown==255] = 0

# Marker labelling
ret, markers = cv.connectedComponents(sure_fg)
# Add one to all labels so that sure background is not 0, but 1
markers = markers+1
# Now, mark the region of unknown with zero
markers[unknown==255] = 0

mask_1 = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
mask_1[mask_1 < 20] = 0
mask_1[mask_1 > 0] = 255

image_4 = cv.bitwise_or(img, img, mask=mask_1)

image_6 = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

blobs = skimage.feature.blob_log(image_6, min_sigma=3, max_sigma=4, num_sigma=1, threshold=0.02)

cv.imshow('thresh', thresh)
cv.imshow('opening', opening)
cv.imshow('sure_bg', sure_bg)
cv.imshow('dist_transform', dist_transform)
cv.imshow('sure_fg', sure_fg)

directory = r'C:/IljaGavrylov/Projects/MBI/LIA/python/img/lighttest'
os.chdir(directory)

cv.imwrite('sure_fg.png', sure_fg)
cv.imshow('unknown', unknown)
#cv.imshow('markers', markers)
cv.waitKey(0)
cv.destroyAllWindows()