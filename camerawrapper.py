"""
If you are able to import picam, then PiCamera is used.
If not, then opencv's VideoCapture is used.
"""
import time
import cv2
import numpy as np

useArducam = False
usePiCam = False
try:
    import picamera
    from picamera.array import PiRGBArray
    usePiCam = True
except ImportError:
    pass


class CameraWrapper:
    cam = ""
    source = 0
    widht = 640
    height = 480
    def __init__(self,width=640,height=480, source=0):
        self.source = source
        self.width = width
        self.height = height
        self.createCam()

    def createCam(self):
        if usePiCam:
            self.cam = piCameraWrapper(self.width, self.height)
        elif useArducam:
            from arducam import ArduCamAR0135
            ArduCamAR0135.startMainCamera('./arducam/AR0135/AR0135_qr.cfg')
            self.cam = ArduCamAR0135
        else:
            self.cam = Logitech_C525(self.source, self.width, self.height)
        return self.cam

    def getCamera(self):
        return self.cam

    def setZoom(self, zoom):
        if usePiCam:
            self.cam.setZoom(zoom)
        else:
            pass

    def getZoom(self):
        if usePiCam:
            self.cam.getZoom()
        else:
            return np.array([0.0, 0.0, 1.0, 1.0])

class Logitech_C525:

    def __init__(self, source, width, height):
            self.cam = cv2.VideoCapture(source)
            self.cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
            #self.cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
            #self.cam.set(cv2.CAP_PROP_EXPOSURE,1)
            # Logitech C525 
            cam = self.cam
            cam.set(3 , 640  ) # width        
            cam.set(4 , 480  ) # height       
            #cam.set(10, 100  ) # brightness     min: 0   , max: 255 , increment:1  
            #cam.set(11, 100   ) # contrast       min: 0   , max: 255 , increment:1     
            #cam.set(12, 70   ) # saturation     min: 0   , max: 255 , increment:1
            #cam.set(13, 13   ) # hue         
            #cam.set(14, 120   ) # gain           min: 0   , max: 127 , increment:1
            #cam.set(15, -2   ) # exposure       min: -7  , max: -1  , increment:1
            #cam.set(17, 5000 ) # white_balance  min: 4000, max: 7000, increment:1
            #cam.set(28, 5    ) # focus          min: 0   , max: 255 , increment:5
    
    def read(self):
        return self.cam.read()

class piCameraWrapper:
    width = 640
    height = 480
    rawCapture = ""
    zoom = np.array([0.0, 0.0, 1.0, 1.0])

    def __init__(self,width=640,height=480):
        self.width = width
        self.height = height
        self.cam = picamera.PiCamera()
        self.cam.resolution = (width, height)
        #camera.framerate = 32
        self.cam.framerate = 30
        #self.cam.zoom = (0.2,0.2,0.8,0.8)
        self.cam.exposure_mode = "sports"
        self.cam.shutter_speed = 1500
        #self.cam.exposure_mode = "snow"
        self.rawCapture = PiRGBArray(self.cam,size=(width,height))
        # allow the camera to warmup
        time.sleep(0.1)
        self.it = self.cam.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
    
    def getZoom(self):
        return self.zoom

    def setZoom(self,newZoom):
        print(newZoom)
        zoom = np.array(newZoom)
        print(zoom)
        zoom[zoom > 1.0] = 1.0
        zoom[zoom < 0.0] = 0.0
        self.zoom = zoom
        #self.cam.zoom = (0.2,0.2,0.8,0.8)
        self.cam.zoom = tuple(self.zoom)

    def read(self):
        ret = 1
        frame = next(self.it).array
        self.rawCapture.truncate()
        self.rawCapture.seek(0)
        return ret,frame
        
