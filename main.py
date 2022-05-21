from util import gesturelock
import cv2

cap = cv2.VideoCapture(0)
locked = False
pw = []

lock = gesturelock(cap, locked, pw)

print('Press q to end program')
lock.setPw()
while True :
  command = lock.getInput(1, True)[0] # get command
  options = {
    0 : lock.lock, # closed hand
    31 : lock.unlock, # open hand
    1 : lock.setPw, # thumb out
  }
  if command in options: options[command]()

  # if x == 0 :
  #   print("Helper.lock()")
  #   lock.lock()
  # elif x == 31 :
  #   print("Helper.unlock()")
  #   lock.unlock()
  # elif x == 1 :
  #   print("Helper.setPw()")
  #   lock.setPw()
  
