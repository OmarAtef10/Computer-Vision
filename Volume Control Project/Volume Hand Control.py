import HandTrackingModule as htm
import cv2
import time
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


############################
# parameters
camWidth, camHeight = 640, 480
pTime = 0
############################


cap = cv2.VideoCapture(0)
cap.set(3, camWidth)
cap.set(4, camHeight)

detector = htm.handDetection(detectionCon=0.7)



devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange=volume.GetVolumeRange()
minvol=volRange[0]
maxVol=volRange[1]


while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPos(img, draw=False)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]

        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

        length = math.hypot(x2 - x1, y2 - y1)
        # print (length)

        ##HandRange 40 -> 280
        ##volume -65 -> 0

        vol = np.interp(length,[10,180],[minvol,maxVol])
        print(int(length),vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length<40:
            cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

    ################## Frames
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f"FPS: {int(fps)}", (40, 40), cv2.FONT_HERSHEY_COMPLEX, 1,
                (0, 255, 0), 2)

    cv2.imshow("Volume Controller", img)
    cv2.waitKey(1)
