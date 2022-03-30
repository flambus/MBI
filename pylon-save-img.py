"""This sample shows how grabbed images can be saved using pypylon only (no
need to use openCV).
Available image formats are     (depending on platform):
 - pylon.ImageFileFormat_Bmp    (Windows)
 - pylon.ImageFileFormat_Tiff   (Linux, Windows)
 - pylon.ImageFileFormat_Jpeg   (Windows)
 - pylon.ImageFileFormat_Png    (Linux, Windows)
 - pylon.ImageFileFormat_Raw    (Windows)
"""
from pypylon import pylon
# import platform # braucht man nur, wenn man mit pypylon Bilder abspeichern will
import cv2
import time

num_img_to_save = 5
img = pylon.PylonImage()
tlf = pylon.TlFactory.GetInstance()

cam = pylon.InstantCamera(tlf.CreateFirstDevice())

converter = pylon.ImageFormatConverter()

### converting to opencv readable arrays ###
# converter.OutputPixelFormat = pylon.PixelType_BGR8packed # converted to RGB, no use with IR cam
converter.OutputPixelFormat = pylon.PixelType_Mono8 # converting to 8bit grayscale
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned # I don't know what this is good for

cam.Open()
cam.StartGrabbing()

for i in range(num_img_to_save):
    with cam.RetrieveResult(2000) as result:


        # Calling AttachGrabResultBuffer creates another reference to the
        # grab result buffer. This prevents the buffer's reuse for grabbing.

        image = converter.Convert(result)

        img = image.GetArray()

        print(img.shape)

        #cv2.imshow('title', img)

        cv2.imwrite('img/test_'+str(i)+'.png', img)

        time.sleep(5)

cam.StopGrabbing()
cam.Close()