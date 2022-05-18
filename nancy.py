#necesary packages 
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model


handobj = mp.solutions.hands #hand obj w hand rec algorithim 
hands = handobj.Hands(max_num_hands=2, min_detection_confidence=0.7) #initalize model
mpDraw = mp.solutions.drawing_utils #draw detected points
