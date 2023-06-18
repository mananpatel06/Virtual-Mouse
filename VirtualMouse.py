import cv2
import numpy as np
import HandTrackinngModule as htm
import time
import autopy
import Volumecontrol as vc
import math
import pyautogui

############### ---------------pycaw-------------##############

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

############### ---------------pycaw-------------##############

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


wCam, hCam = 640, 480
wScr,hScr =autopy.screen.size()
frameR = 100 # Frame Reduction
smoothening= 7

plocX, plocY = 0, 0 #previous location 
clocX, clocY = 0, 0 #current location

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

pTime = 0
cTime = 0

detector = htm.handDetector()
lmList = []
bbox=[]

# move courser
# click
# screenshot
# volume control



################## Gui code ########################

# import everything from tkinter module
from tkinter import *
import time
from PIL import ImageTk, Image
from tkinter import filedialog

# create a tkinter window
root = Tk()

# Open window having dimension 100x100
root.geometry('640x480')
root.title(string='VM')

path = 'gui.png'

img = Image.open(path)
img = ImageTk.PhotoImage(img)
panel = Label(root, image=img)
panel.pack()
#btn = Button(root, text = 'Start Now', bd = '3',command = root.destroy  ,width= '640',compound = LEFT ).pack(side = 'bottom')
#delay
root.after(5000,lambda :root.destroy())
root.mainloop()

############################################

while True:
     sucess,img = cap.read()


     img = detector.findHands(img)
     lmlist = detector.findPosition(img)
     # lmList = detector.findPosition(img, draw=False)

     if(len(lmlist)!=0):
          x1,y1 = lmlist[8][1:]
          x2, y2 = lmlist[12][1:]
          cv2.circle(img,(x1,y1),15,(0,0,0),-1)
          cv2.circle(img, (x2, y2), 15, (0, 0, 0), -1)

          #  Check which fingers are up
          fingers = detector.fingersUp()
          # print(fingers)
          
          cv2.rectangle(img,(frameR,frameR),(wCam-frameR,hCam-frameR),(255,0,255),2)
          
          # Only Index Finger : Moving Mode
          if fingers[1]==1 and fingers[2]==0:
               
               # Convert Coordinates
               x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
               y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

               # Smoothen Values
               clocX = plocX + (x3 - plocX) / smoothening
               clocY = plocY + (y3 - plocY) / smoothening

               # Move Mouse
               autopy.mouse.move(wScr - clocX, clocY)
               cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
               plocX, plocY = clocX, clocY
          
          # Both Index and middle fingers are up : Clicking Mode
          if fingers[1]==1 and fingers[2]==1:
               length,img,lineInfo =detector.findDistance(8,12,img)
               # print(length)
               # Click mouse if distance short
               if length < 40:
                    cv2.circle(img,(lineInfo[4],lineInfo[5]),15,(0,255,0),cv2.FILLED)
                    autopy.mouse.click()

          # All Fingers are up : Volume Mode          
          if fingers.count(fingers[1])==len(fingers):
               # print(lmList)
               cx1, cy1 = lmlist[4][1], lmlist[4][2]
               cx2, cy2 = lmlist[8][1], lmlist[8][2]
               cx, cy = (cx1 + cx2) // 2, (cy1 + cy2) // 2
               cv2.circle(img, (cx1, cy1), 10, (0, 255, 0), -1)
               cv2.circle(img, (cx2, cy2), 10, (0, 255, 0), -1)
               cv2.line(img, (cx1, cy1), (cx2, cy2), (0, 255, 0), 3)

               # distance between 2 points
               length = math.hypot(cx2 - cx1, cy2 - cy1)
               # print(length) # min = 20 max = 150

               # change range of 20 - 150 in -65 - 0
               # Here -65 - 0 is rage in function GetVolumeRange range
               vol = np.interp(length, [20, 150], [minVolume, maxVolume])
               # print(vol)

               volBar = np.interp(length, [20, 150], [400, 150])
               volPer = np.interp(length, [20, 150], [0, 100])

               # function of pycaw to change volume
               volume.SetMasterVolumeLevel(vol, None)

          # First 3 fingers are up : Screenshot Mode
          if fingers[1]==1 and fingers[2]==1 and fingers[3]==1 and fingers[4]==0:
               
               image = pyautogui.screenshot()
   
               # since the pyautogui takes as a PIL(pillow) and in RGB we need to
               # convert it to numpy array and BGR, so we can write it to the disk
               image = cv2.cvtColor(np.array(image),
                                    cv2.COLOR_RGB2BGR)
               cv2.rectangle(img, (0, 200), (img.shape[1], 300), (0, 255, 0), cv2.FILLED)
               cv2.putText(img, "Screen Shot", (400, 270), cv2.FONT_HERSHEY_SIMPLEX,
                           1, (0, 0, 255), 2)
               # writing it to the disk using opencv
               cv2.imwrite("screenshot.png", image);


     cTime = time.time()
     fps = 1 / (cTime - pTime)
     pTime = cTime
     cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 3)

     cv2.imshow("VM", img)

     if cv2.waitKey(1) & 0xFF ==ord('q'):
         break