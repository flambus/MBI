from skimage.feature import blob_dog, blob_log, blob_doh
from skimage.io import imread, imshow
from skimage.color import rgb2gray
from math import sqrt
import matplotlib.pyplot as plt
import numpy as np
from skimage.morphology import erosion, dilation, opening, closing
from skimage.measure import label, regionprops
from skimage.color import label2rgb

im = rgb2gray(imread("python/img/lighttest/testlight_white_2.png"))
imshow(im)
im_bw = im<0.8
imshow(im_bw)

blobs = blob_log(im_bw, max_sigma=30, min_sigma = 23, num_sigma=2, threshold=0.3, overlap = 0.1)
fig, ax = plt.subplots()
ax.imshow(im_bw, cmap='gray')
for blob in blobs:
    y, x, area = blob
    ax.add_patch(plt.Circle((x, y), area*np.sqrt(2), color='r', 
                            fill=False))

print(blobs)
print(len(blobs))