import time
import cv2
import mediapipe as mp
import numpy as np
import RPi.GPIO as GPIO

class gesturelock:

    
  def __init__(self, cap, locked, pw, circuit=False):
    self.cap = cap
    self.locked = locked
    self.pw = pw
    self.circuit = circuit

    if self.circuit:
      # for led setup
      self.ledPIN = 4
      GPIO.setmode(GPIO.BCM)
      GPIO.setup(self.ledPIN, GPIO.OUT)
      GPIO.output(self.ledPIN, GPIO.LOW)

      #   for servo setup
      servoPIN = 17
      GPIO.setmode(GPIO.BCM)
      GPIO.setup(servoPIN, GPIO.OUT)
      self.servo = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
      self.servo.start(7.5) # Initialization
    
    

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
      self.flashLED()
      time.sleep(1)
      count = 0
      intsDetected = []
      with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
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
                # store landmarks in a list
                temp.append(hand_no)
                temp.append(i)
                temp.append(int(hand_landmarks.landmark[mp_hands.HandLandmark(i).value].x * self.cap.get(3)))
                temp.append(int(hand_landmarks.landmark[mp_hands.HandLandmark(i).value].y * self.cap.get(4)))
                temp.append(int(hand_landmarks.landmark[mp_hands.HandLandmark(i).value].z * -100))
                list.append(temp)

              # find the middle of the palm (4 points)
              averagePalmX = (list[0][2] + list[5][2] + list[13][2] + list[17][2]) / 4
              averagePalmY = (list[0][3] + list[5][3] + list[13][3] + list[17][3]) / 4

              #todo: create average of palm points to accurately depict thumb distance
              #identify gesture
              dec_number = 0
              #start: 4, end: 24, step: 4
              for i, b in zip(range(4, 24, 4), range(5)):
                # if tip of the finger is farther from center of palm than base of the finger, then its a 1. else 0
                dist1 = np.hypot(list[i][2] - averagePalmX, list[i][3] - averagePalmY)
                dist2 = np.hypot(list[i - 2][2] - averagePalmX, list[i - 2][3] - averagePalmY)
                dist3 = np.hypot(list[i - 1][2] - averagePalmX, list[i - 1][3] - averagePalmY)
                dist4 = np.hypot(list[i - 3][2] - averagePalmX, list[i - 3][3] - averagePalmY)
                if dist1 > dist2 and dist1 > dist3 and dist1 > dist4:
                  dec_number += 2**b
              # store the detected number in a list (should be one for every frame of video)
              intsDetected.append(dec_number)
          else :
            # if no hand is detected then store a -1 for that frame
            intsDetected.append(-1)
          # Flip the image horizontally for a selfie-view display.
          cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
          if count >= 30: # use 30 frames of gesture
            # get mode of the list
            mode = max(set(intsDetected), key = intsDetected.count)
            # mode = getMode(intsDetected)
            # add this gesture to the input
            inputPw.append(mode)
            # tell the user which number gesture was detected
            print(mode)
            break
          count += 1 
          if cv2.waitKey(5) == ord('q'): # command to end the program
            quit()
    if len(inputPw) > 1: print(inputPw) # tell the user the entire input combination
    return inputPw

  def unlock(self) :
    print('unlock()')
    print("pw is ", self.pw)
    if self.locked :
      if self.pw == self.getInput(len(self.pw)) :
        self.locked = False
        if self.circuit:
          # print ("led off")
          # GPIO.output(self.ledPIN, GPIO.LOW)
          self.servo.ChangeDutyCycle(2.5) # servo pointed right
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
      print("length of pw is", n)
      if not n == 0 :
        self.pw = self.getInput(n)
      else :
        self.pw = []
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
      if self.circuit:
        self.locked = True
        # print ("led on")
        # GPIO.output(self.ledPIN, GPIO.HIGH)
        self.servo.ChangeDutyCycle(7.5) # servo pointed upwards
      print("locked")

  def flashLED(self):
    print("flashing led")
    GPIO.output(self.ledPIN, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(self.ledPIN, GPIO.LOW)
    