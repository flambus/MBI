import numpy as np
import pandas as pd
import os
import cv2
import matplotlib.pyplot as plt
import skimage.feature
#%matplotlib inline

image = cv2.imread('img/testlight_white_thin.png')

image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

blobs = skimage.feature.blob_log(image, min_sigma=3, max_sigma=4, num_sigma=1, threshold=0.02)

image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

#cv2.imshow('image', image)
print(blobs)
print(type(blobs))
print(len(blobs))

cv2.waitKey(0)
cv2.destroyAllWindows()

