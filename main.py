import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Hand detector
detector = HandDetector(detectionCon=0.8)

# Keyboard layout (numbers, letters, space, backspace, clear)
keys = [
    ["1","2","3","4","5","6","7","8","9","0"],
    ["Q","W","E","R","T","Y","U","I","O","P"],
    ["A","S","D","F","G","H","J","K","L"],
    ["Z","X","C","V","B","N","M","BS","SPACE"],
    ["CLEAR"]
]

finalText = ""

# Track hold
holdStart = None
currentKey = None
holdTime = 1 # seconds to confirm a key

# Draw keyboard
def drawAll(img, buttonList):
    for button in buttonList:
        x,y = button.pos
        w,h = button.size
        cv2.rectangle(img, (x,y), (x+w,y+h), (175,0,175), cv2.FILLED)
        cv2.putText(img, button.text, (x+20,y+65),
                    cv2.FONT_HERSHEY_PLAIN, 4, (255,255,255), 4)
    return img

# Button class
class Button():
    def __init__(self,pos,text,size=[85,85]):
        self.pos = pos
        self.size = size
        self.text = text

# Create button list
buttonList = []
for i in range(len(keys)):
    for j,key in enumerate(keys[i]):
        buttonList.append(Button([100*j+50,100*i+50], key))

# Main loop
while True:
    success, img = cap.read()
    img = cv2.flip(img,1)
    hands, img = detector.findHands(img)

    img = drawAll(img, buttonList)

    if hands:
        lmList = hands[0]['lmList']
        if lmList:
            x,y = lmList[8][0:2]  # index fingertip
            cv2.circle(img,(x,y),15,(0,255,255),cv2.FILLED)

            keyFound = None
            for button in buttonList:
                bx,by = button.pos
                bw,bh = button.size

                if bx < x < bx+bw and by < y < by+bh:
                    keyFound = button
                    cv2.rectangle(img, (bx,by), (bx+bw,by+bh), (0,255,0), cv2.FILLED)
                    cv2.putText(img, button.text, (bx+20,by+65),
                                cv2.FONT_HERSHEY_PLAIN, 4, (255,255,255), 4)

                    if currentKey != keyFound:
                        # New key touched
                        holdStart = time.time()
                        currentKey = keyFound
                    else:
                        # Still holding same key
                        elapsed = time.time() - holdStart
                        cv2.putText(img, f"{elapsed:.1f}s", (bx+10, by-10),
                                    cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)

                        if elapsed >= holdTime:
                            if currentKey.text == "SPACE":
                                finalText += " "
                            elif currentKey.text == "BS":
                                finalText = finalText[:-1]
                            elif currentKey.text == "CLEAR":
                                finalText = ""
                            else:
                                finalText += currentKey.text
                            currentKey = None
                            holdStart = None
                    break

            if keyFound is None:
                # Finger not on any key
                currentKey = None
                holdStart = None

    # Draw text box
    cv2.rectangle(img, (50,600), (1200,700), (175,0,175), cv2.FILLED)
    cv2.putText(img, finalText, (60,680),
                cv2.FONT_HERSHEY_PLAIN, 5, (255,255,255), 5)

    cv2.imshow("Virtual Keyboard", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
