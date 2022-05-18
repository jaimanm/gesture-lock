import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    
    success, image = cap.read()
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
    temp2 = []
    
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
          temp.append(int(hand_landmarks.landmark[mp_hands.HandLandmark(i).value].x * cap.get(3)))
          temp.append(int(hand_landmarks.landmark[mp_hands.HandLandmark(i).value].y * cap.get(4)))
          temp.append(int(hand_landmarks.landmark[mp_hands.HandLandmark(i).value].z * -100))
          list.append(temp)
        temp2 = list



        #identify gesture
        str = ""
        for i in range(5) :
          dist1 = np.hypot(list[(i + 1) * 4][2] - list[0][2], list[((i + 1) * 4)][3] - list[0][3])
          dist2 = np.hypot(list[(i + 1) * 4 - 1][2] - list[0][2], list[((i + 1) * 4 - 1)][3] - list[0][3])
          if dist1 > dist2 :
            str = str + "1"
          else :
            str = str + "0"
    # Flip the image horizontally for a selfie-view display.
    cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
    if cv2.waitKey(5) == ord('q'):
      break
    #count += 1 
cap.release()