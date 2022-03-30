import cv2
import numpy as np
import matplotlib.pyplot as plt

img_1 = cv2.imread('img/img_1.png', cv2.IMREAD_GRAYSCALE)
img_2 = cv2.imread('img/img_2.png', cv2.IMREAD_GRAYSCALE)

print(img_1.shape)
print(img_2.shape)

img_1_2 = cv2.hconcat([img_1, img_2])

print(img_1_2.shape)

#cv2.imshow('image', img_1_2)

cv2.imwrite('img/img_1_2.png', img_1_2)



#cv2.imshow('image_1',img_1)
#cv2.imshow('image_2',img_2)


cv2.waitKey(0)
cv2.destroyAllWindows()