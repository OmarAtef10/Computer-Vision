import math
import time
from ctypes import cast, POINTER

import autopy
import cv2
import numpy as np
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import HandTrackingModule as htm

##########################
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 3  # Smoothing factor for mouse motion
#########################

pTime = 0
prevlocX, prevlocY = 0, 0
currlocX, currlocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()  # Getting screen size (1920 x 1080 for me)
# print(wScr, hScr)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minvol = volRange[0]
maxVol = volRange[1]

while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    # 2. Get the tip of the index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print(x1, y1, x2, y2)

    # 3. Check which fingers are up
    fingers = detector.fingersUp()
    # print(fingers)
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                  (255, 0, 255), 2)
    # 4. Only Index Finger : Moving Mode
    if fingers[1] == 1 and fingers[2] == 0:
        # 5. Convert Coordinates
        x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
        # 6. Smoothen Values
        currlocX = prevlocX + (x3 - prevlocX) / smoothening
        currlocY = prevlocY + (y3 - prevlocY) / smoothening

        # 7. Move Mouse
        autopy.mouse.move(wScr - currlocX, currlocY)
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        prevlocX, prevlocY = currlocX, currlocY

    # 8. Both Index and middle fingers are up : Clicking Mode
    elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
        # 9. Find distance between fingers
        length, img, lineInfo = detector.findDistance(8, 12, img)
        print(length)
        # 10. Click mouse if distance short
        if length < 40:
            cv2.circle(img, (lineInfo[4], lineInfo[5]),
                       15, (0, 255, 0), cv2.FILLED)
            autopy.mouse.click()

    elif fingers[4] == 1:
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

            # HandRange 10 -> 180
            # volume -65 -> 0

            vol = np.interp(length, [10, 180], [minvol, maxVol])
            print(int(length), vol)
            volume.SetMasterVolumeLevel(vol, None)

            if length < 40:
                cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)
    # 12. Display
    cv2.imshow("Result", img)
    cv2.waitKey(1)
