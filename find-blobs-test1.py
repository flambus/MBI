import cv2 as cv
import numpy as np

img = cv.imread('img/testlight_white_thin.png')

imgG = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
imgG = cv.resize(imgG, (400, 400))

#ret, thresh = cv.threshold(imgG, 127, 255, cv.THRESH_BINARY)
#kernel = np.ones((6, 6), np.uint8)

blur = cv.GaussianBlur(imgG, (3, 3), 0)
ret3, th3 = cv.threshold(blur, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)

kernel2 = np.ones((3, 3), np.uint8)
opening = cv.morphologyEx(th3, cv.MORPH_OPEN, kernel2, iterations=2)
# sure background area
sure_bg = cv.dilate(opening, kernel2, iterations=3)
# Finding sure foreground area
dist_transform = cv.distanceTransform(opening, cv.DIST_L2, 5)
ret, sure_fg = cv.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
# Finding unknown region
sure_fg = np.uint8(sure_fg)
unknown = cv.subtract(sure_bg, sure_fg)

# th, im_th = cv.threshold(blur, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
# im_floodfill = im_th.copy()
# h, w = im_th.shape[:2]
# mask = np.zeros((h + 2, w + 2), np.uint8)
# cv.floodFill(im_floodfill, mask, (255, 255), 255)
# im_floodfill_inv = cv.bitwise_not(im_floodfill)
# im_out = im_th | im_floodfill_inv

dilation = cv.dilate(th3, kernel2, iterations=3)

edges = cv.Canny(dilation, 400, 400)

#contours, hierarchy = cv.findContours(dilation, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
#objects = str(len(contours))

#text = "Obj:"+str(objects)
#cv.putText(dilation, text, (0, 80),  cv.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 2)
#cv.putText(img, text, (0, 80),  cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)

#cv.imshow('Original', imgG)
cv.imshow('Thresh', th3)
cv.imshow('Dilatation', dilation)
cv.imshow('Edges', edges)
#cv.imshow('im_out', im_out)
cv.imshow('other', opening)


cv.waitKey(0)
cv.destroyAllWindows()