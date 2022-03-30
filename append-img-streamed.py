'''
A simple Program for grabing video from basler camera and converting it to opencv img.
Tested on Basler acA1300-200uc (USB3, linux 64bit , python 3.5)
'''
from pypylon import pylon
import numpy as np
import cv2
import time

# conecting to the first available camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Grabing Continusely (video) with minimal delay
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()

# converting to opencv bgr format
#converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputPixelFormat = pylon.PixelType_Mono8
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

### - Variables
i = 0
pano = np.zeros((2048, 1), dtype=int)
speed = 40



while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Access the image data
        image = converter.Convert(grabResult)
        img = image.GetArray()

        #cv2.namedWindow('title', cv2.WINDOW_NORMAL)
        #cv2.imshow('title', img)

        print(img.shape)

        pano = np.append(pano, img, axis=1)

        cv2.imwrite('img/pano_' + str(i) + '.png', pano)

        i += 1
        time.sleep(3) #statt time sleep bewegungsende der stage abwarten

        k = cv2.waitKey(1)
        if k == 27:
            break
    grabResult.Release()

# Releasing the resource
camera.StopGrabbing()

cv2.destroyAllWindows()