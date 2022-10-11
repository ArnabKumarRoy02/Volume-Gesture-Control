import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Setting up the resolution of the camera
wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
cap.set(cv2.CAP_PROP_FPS, 60)
pTime = 0

detector = htm.handDetector(detectionCon=0.9)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]
volBAR = 400
vol = 400
volPER = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 10, (0, 100, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (0, 100, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (0, 100, 0), 3)
        cv2.circle(img, (cx, cy), 10, (0, 100, 0), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        # print(length)

        # Hand range 50 - 300
        # Volume range -65 - 0

        vol = np.interp(length, [30, 200], [minVol, maxVol])
        volBAR = np.interp(length, [30, 200], [400, 150])
        volPER = np.interp(length, [30, 200], [0, 100])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length < 30:
            cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

    cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 255), 3)
    cv2.rectangle(img, (50, int(volBAR)), (85, 400), (0, 0, 255), cv2.FILLED)
    cv2.putText(img, f'{int(volPER)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN,
                3, (0, 0, 255), 3)

    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_PLAIN,
                3, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
