import time
import cv2
import mediapipe as mp
import numpy as np

class gesturelock:
  def __init__(self, cap, locked, pw):
    self.cap = cap
    self.locked = locked
    self.pw = pw

  def getInput(self, numGestures, getCommand=False):
    # numGestures = int(numGestures)
    inputPw = []
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_hands = mp.solutions.hands
    # For webcam input:
    for i in range(numGestures) :
      if not getCommand: print('Prepare Gesture', (i+1))
      else: print('Prepare Command')
      time.sleep(0.5)
      count = 0
      anotherList = []
      with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while self.cap.isOpened():
          success, image = self.cap.read()
          if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

          # To improve performance, optionally mark the image as not writeable to
          # pass by reference.
          image.flags.writeable = False
          image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
          results = hands.process(image)

          # Draw the hand annotations on the image.
          image.flags.writeable = True
          image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
          
          if results.multi_hand_landmarks:
            for hand_no, hand_landmarks in enumerate(results.multi_hand_landmarks):
              mp_drawing.draw_landmarks(
                  image,
                  hand_landmarks,
                  mp_hands.HAND_CONNECTIONS,
                  mp_drawing_styles.get_default_hand_landmarks_style(),
                  mp_drawing_styles.get_default_hand_connections_style())
              list = []
              for i in range(21):
                temp = []
                temp.append(hand_no)
                temp.append(i)
                temp.append(int(hand_landmarks.landmark[mp_hands.HandLandmark(i).value].x * self.cap.get(3)))
                temp.append(int(hand_landmarks.landmark[mp_hands.HandLandmark(i).value].y * self.cap.get(4)))
                temp.append(int(hand_landmarks.landmark[mp_hands.HandLandmark(i).value].z * -100))
                list.append(temp)

              #todo: create average of palm points to accurately depict thumb distance
              #identify gesture
              s = ""
              for i in range(5) :
                averagePalmX = (list[0][2] + list[5][2] + list[13][2] + list[17][2]) / 4
                averagePalmY = (list[0][3] + list[5][3] + list[13][3] + list[17][3]) / 4
                dist1 = np.hypot(list[(i + 1) * 4][2] - averagePalmX, list[((i + 1) * 4)][3] - averagePalmY)
                dist2 = np.hypot(list[(i + 1) * 4 - 2][2] - averagePalmX, list[((i + 1) * 4 - 2)][3] - averagePalmY)
                dist3 = np.hypot(list[(i + 1) * 4 - 1][2] - averagePalmX, list[((i + 1) * 4 - 1)][3] - averagePalmY)
                dist4 = np.hypot(list[(i + 1) * 4 - 3][2] - averagePalmX, list[((i + 1) * 4 - 3)][3] - averagePalmY)
                if dist1 < dist2 or dist1 < dist3 or dist1 < dist4:
                  s = s + "0"
                else :
                  s = s + "1"
              dec_number = int(s[::-1], 2)
              anotherList.append(dec_number)
          else :
            anotherList.append(-1)
          # Flip the image horizontally for a selfie-view display.
          cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
          if count >= 50:
            mode = max(set(anotherList), key = anotherList.count)
            inputPw.append(mode)
            print(mode)
            break
          count += 1 
          if cv2.waitKey(5) == ord('q'):
            quit()
    if len(inputPw) > 1: print(inputPw)
    return inputPw

  def unlock(self) :
    print('unlock()')
    print("pw is ", self.pw)
    if self.locked :
      if self.pw == self.getInput(len(self.pw)) :
        self.locked = False
        print("unlocked")
      else :
        print("wrong pw")
    else :
      print("already unlocked")
  
  def setPw(self) :
    print('setPw()')
    if self.locked == False :
      print("input length of new password")
      n = self.getInput(1)[0]
      if not n == 0 :
        self.pw = self.getInput(n)
        print("Password is now", self.pw)
        self.lock()
        print("set and locked")
    else :
      print("cannot set pw")
  
  def lock(self) :
    print('lock()')
    if self.locked :
      print("already locked")
    else :
      self.locked = True
      print("locked")
    