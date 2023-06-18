import cv2
import mediapipe
import time
import numpy as np
import HandTrackinngModule as htm
import math

def control():

    ############### ---------------pycaw github -------------##############

    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    ############### ---------------pycaw github -------------##############

    cap = cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480)

    pTime = 0
    cTime = 0

    detector = htm.handDetector(detectionConfidence=0.7)

    ####################  pycaw functions  ################################

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # volume.GetMute()
    # volume.GetMasterVolumeLevel()

    volumeRange = volume.GetVolumeRange()

    ####################  pycaw functions  ################################

    minVolume = volumeRange[0]
    maxVolume = volumeRange[1]

    volBar = 400
    volPer = 0

    while True:
        sucess, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img,draw=False)
        if len(lmList)!=0:
            # print(lmList[4],lmList[8])
            x1,y1 = lmList[4][1],lmList[4][2]
            x2,y2 = lmList[8][1],lmList[8][2]
            cx ,cy = (x1+x2)//2,(y1+y2)//2
            cv2.circle(img,(x1,y1),10,(0,255,0),-1)
            cv2.circle(img,(x2,y2),10,(0,255,0),-1)
            cv2.line(img,(x1,y1),(x2,y2),(0,255,0),3)

            # distance between 2 points
            length = math.hypot(x2-x1,y2-y1)
            # print(length) # min = 20 max = 150

            # change range of 20 - 150 in -65 - 0
            # Here -65 - 0 is rage in function GetVolumeRange range
            vol = np.interp(length,[20,150],[minVolume,maxVolume])
            # print(vol)

            volBar = np.interp(length, [20,150],[400,150])
            volPer = np.interp(length, [20, 150], [0, 100])

            # function of pycaw to change volume
            volume.SetMasterVolumeLevel(vol, None)


            if length<50:
                cv2.circle(img, (cx, cy), 10, (255, 0, 0), -1)

        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), -1)
        cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, f'FPS {int(fps)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("video", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyWindow("video")