import cv2
import sys
sys.path.append('home/pi/repos/qrcodescanner/arducam')
import config_template as config
import numpy as np

import camerawrapper
from datetime import datetime
from timeit import default_timer as timer
import traceback
import queue
import threading
import os
import pickle
import socket
import time # for sleep

HOSTNAME = socket.gethostname()


camwrapper = False  # Keeps the camera object.
currentShutterspeed = 25000
frameQ = queue.Queue()
exitLoop = False


def addTextToScreen(im):
  # Add room for text
  # Video is 640x480 
  # Screen is 800x480 480/800 = 1.67
  screenWidth = 800
  videoWidth =  640
  videoHeight = 480
  screenHeight = 480
  topBorder = 500
  imageHeight = videoHeight+topBorder
  imageWidth = screenWidth* int(imageHeight/screenHeight)

  sideBorder = imageWidth - videoWidth
  grayIntensity = 50
  im = cv2.copyMakeBorder(
        im,
        top=topBorder,
        bottom=0,
        left=0,
        right=sideBorder,
        borderType=cv2.BORDER_CONSTANT,
        value=[grayIntensity, grayIntensity, grayIntensity])
  
  totalPerHour = 999

  font = cv2.FONT_HERSHEY_SIMPLEX
  cv2.putText(im, 'Average %4d per hour' % totalPerHour, (10,120), font, 1.3, (0, 255, 0), 1, cv2.LINE_AA)

  cv2.putText(im, 'Monochrome green on pale black is not cool, but its how it was', (10,180+35*0), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
   
  cv2.putText(im, 'Some more green retro text', (1050,200+35*0), font, 1.0, (0, 255, 0), 1, cv2.LINE_AA)
  
  return (im)



def onMouseCallback(event, x, y, flags, param):
	# grab references to the global variables
  global currentShutterspeed
	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that cropping is being
	# performed
  if event == cv2.EVENT_LBUTTONDOWN:
	  # We have 800x480 px
    if (x > 500 and x <= 650 ) and (y > 400 and y < 450):
      settingsWindow = "Settings"
      cv2.moveWindow(settingsWindow, 200,100)
      currentShutterspeed -= 100
      setShutterSpeed(currentShutterspeed)
      print(currentShutterspeed)
      
    if (x > 650 and x <= 800 ) and (y > 400 and y < 450):
      currentShutterspeed += 100
      setShutterSpeed(currentShutterspeed)
      print(currentShutterspeed)
  
  # check to see if the left mouse button was released
  elif event == cv2.EVENT_LBUTTONUP:
    pass

def setShutterSpeed(newShutterSpeed):
  """ Works only on picam """
  global camwrapper
  try:
    cam = camwrapper.getCamera()
    cam.cam.shutter_speed = newShutterSpeed
  except:
    print("Unexpected error:", sys.exc_info()[0])
    traceback.print_exc()

def on_trackbar_exposure(val):
  setShutterSpeed(val)  

def on_trackbar_x1(val,configuration):
  """ Works only on picam """
  global camwrapper
  try:
    
    zoom = configuration['zoom']
    zoom[0] = val/100.0
    camwrapper.setZoom(zoom)
    configuration['zoom'] = zoom
    saveConfiguration(configuration, configuration['CONFIG_FILE'] )
  except:
    print("Unexpected error:", sys.exc_info()[0])
    traceback.print_exc()

def on_trackbar_y1(val,configuration):
  """ Works only on picam """
  global camwrapper
  try:
    zoom = configuration['zoom']
    zoom[1] = val/100.0
    camwrapper.setZoom(zoom)
    configuration['zoom'] = zoom
    saveConfiguration(configuration, configuration['CONFIG_FILE'] )
  except:
    print("Unexpected error:", sys.exc_info()[0])
    traceback.print_exc()

def on_trackbar_x2(val,configuration):
  """ Works only on picam """
  global camwrapper
  try:
    zoom = configuration['zoom']
    zoom[2] = val/100.0
    camwrapper.setZoom(zoom)
    configuration['zoom'] = zoom
    saveConfiguration(configuration, configuration['CONFIG_FILE'] )
  except:
    print("Unexpected error:", sys.exc_info()[0])
    traceback.print_exc()

def on_trackbar_y2(val,configuration):
  """ Works only on picam """
  global camwrapper
  try:
    zoom = configuration['zoom']
    zoom[3] = val/100.0
    print(val)
    print("ZOOM")
    print(zoom)

    camwrapper.setZoom(zoom)
    configuration['zoom'] = zoom
    print("ZOOM")
    print(zoom)
    saveConfiguration(configuration, configuration['CONFIG_FILE'] )
  except:
    print("Unexpected error:", sys.exc_info()[0])
    traceback.print_exc()

def getZoom():
  global camwrapper
  try:
    zoom = camwrapper.getZoom()
  except:
    print("Not able to get zoom from camera")
    return np.array([0.0,0.0,1.0,1.0])
  return zoom

def saveConfiguration(config, configfile ):
  try:
    with open(configfile, 'wb') as f:
      pickle.dump(config, f, pickle.HIGHEST_PROTOCOL)
  except:
    print("NOT ABLE TO SAVE CONFIGURATION")
    print("Unexpected error:", sys.exc_info()[0])
    traceback.print_exc()

def loadConfiguration(configfile):
  try:
    with open(configfile, 'rb') as f:
      return pickle.load(f)
  except:
    print("Not able to load configuration. Using default values.")
    print("Unexpected error:", sys.exc_info()[0])
    traceback.print_exc()
    return False



def displayFrames(arg1 ,stop_event):
  CONFIG_FILE = "config.pkl"
  global exitLoop
  global camwrapper
  import cv2

  global currentShutterspeed
  configuration = {}
  configuration['CONFIG_FILE'] = CONFIG_FILE
  configuration['currentShutterspeed'] = currentShutterspeed
  configuration['zoom'] = np.array([0.0,0.0,1.0,1.0], dtype="float") 
  loadedConfig = loadConfiguration(CONFIG_FILE)
  if loadedConfig:
    configuration = loadedConfig
    currentShutterspeed = configuration['currentShutterspeed']
    camwrapper.setZoom(configuration['zoom'])

  settingsWindow = "Settings"
  cv2.namedWindow(settingsWindow)
  cv2.moveWindow(settingsWindow, 200,100)
  #cv2.setMouseCallback(outputWindow, onMouseCallback)

  trackbarNameExposure = "Exposure"
  exposureMax = 50000
  cv2.createTrackbar(trackbarNameExposure, settingsWindow , 100, exposureMax, on_trackbar_exposure)

  print(configuration)
  
  cv2.createTrackbar("zoom x1", settingsWindow , int(configuration['zoom'][0]*100), 100, lambda x: on_trackbar_x1(x, configuration))
  cv2.createTrackbar("zoom y1", settingsWindow , int(configuration['zoom'][1]*100), 100, lambda x: on_trackbar_y1(x, configuration))
  cv2.createTrackbar("zoom x2", settingsWindow , int(configuration['zoom'][2]*100), 100, lambda x: on_trackbar_x2(x, configuration))
  cv2.createTrackbar("zoom y2", settingsWindow , int(configuration['zoom'][3]*100), 100, lambda x: on_trackbar_y2(x, configuration))
  
  setShutterSpeed(currentShutterspeed)
  outputWindow = "Results"
  cv2.namedWindow(outputWindow)
  cv2.moveWindow(outputWindow, 1,0)
  cv2.setMouseCallback(outputWindow, onMouseCallback)
  
  lastAggrSend = timer()
  start = timer()
  savedImageNumber = 0 # Number series for the saved images
  while ((not stop_event.is_set()) and not exitLoop):
    if frameQ.qsize() >= 3:      #
      while frameQ.qsize() > 1:
        # empty Q
        frameQ.get()
        frameQ.task_done()
    if frameQ.qsize() >= 1:
      end = timer()
      displayFps = 1 / (end - start) 
      start = timer()
      (originalFrame, fps) = frameQ.get()
      (frame) = addTextToScreen(originalFrame.copy())

      font = cv2.FONT_HERSHEY_SIMPLEX
      cv2.putText(frame, 'cam fps:%.1f' % fps, (10,frame.shape[0]-10), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
      cv2.putText(frame, 'screen fps:%.1f' % displayFps, (10,frame.shape[0]-50), font, 1, (0, 255, 0), 2, cv2.LINE_AA)      
      frame = cv2.resize(frame, (800,450))
      cv2.putText(frame, 'Exposure %s' % (currentShutterspeed), (520,395), font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
      frame = cv2.rectangle(frame, (500,400), (650,450), (0,100,200), -1)
      frame = cv2.rectangle(frame, (650,400), (800,450), (200,100,0), -1)
      cv2.putText(frame, '-', (550,445), font, 2, (0, 255, 0), 4, cv2.LINE_AA)
      cv2.putText(frame, '+', (530+150+20,445), font, 2, (0, 255, 0), 4, cv2.LINE_AA)
      try:
        if cv2.getWindowProperty(outputWindow, 0) < 0:
          exitLoop = True
      except:
          print("Not able to get property from window. Exiting...")
          exitLoop = True
      cv2.imshow(outputWindow, frame)
      cv2.waitKey(1)
      #sendData(order)
      if timer() - lastAggrSend > 60:
        print("Sending aggrdata......")
        lastAggrSend = timer()
        
      #vid_writer.write(frame)
      k = cv2.waitKey(10)
      if k == 27 :
          break
      if k == ord('s'):
        savedImageNumber += 1
        filename = f'savedImage_{savedImageNumber}.jpg'
        cv2.imwrite(filename, originalFrame) 
        print(f"Saved {filename}")



def sendData(order):
  pass


if __name__ == "__main__":
  source = 0
  if len(sys.argv) > 1:
      source = sys.argv[1]
  #source = "pakking60cm.mov"
  
  #vid_writer = cv2.VideoWriter('output.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 15, (frame.shape[1],frame.shape[0]))
  
  start = timer()

  stop_event = threading.Event()
  displayThrd = threading.Thread(target=displayFrames, args=('',stop_event))
  displayThrd.setDaemon(True)
  displayThrd.start()


  camwrapper = camerawrapper.CameraWrapper(source=source)
  cap = camwrapper.getCamera() 
  ret, frame = cap.read()
  frameCopy = frame.copy()

  while(not exitLoop):
      # Time FPS
      end = timer()
      fps = 1 / (end - start) 
      start = timer()
      
      try:
        ret, frame = cap.read()
      except:
        print("Unexpected camera read error:", sys.exc_info()[0])
        traceback.print_exc()
        # Recreating the object.
        cap = camwrapper.createCam()
      
      # Remove frames if they are queing up.
      if frameQ.qsize() >= 5:     
        while frameQ.qsize() > 3:
          # empty Q 
          frameQ.get()
          frameQ.task_done()
      frameCopy = frame.copy()
      frameQ.put((frameCopy, fps))  
  
  cv2.destroyAllWindows()
  #vid_writer.release()
