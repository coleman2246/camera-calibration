import threading
import multiprocessing
from multiprocessing import Process, Queue

import numpy as np
import cv2
import glob



class CameraCalibrator:
    def __init__(self, filename, save_format = "pickle"):
        self.format = save_format
        acceptable_formats = ["pickle","yaml","json"]

        if self.format not in acceptable_formats:
            raise ValueError("Invalid Save Format")
            
        self.filename = filename
        self.objpoints = []
        
        # termination criteria
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)

        self.objp = np.zeros((9*6,3), np.float32)
        self.objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

        # Arrays to store object points and image points from all the images.
        
        self.video = "test.avi"
        self.cap = cv2.VideoCapture(self.video)
        
        self.lock = threading.Lock()
        
        # Check if camera opened successfully
        if (self.cap.isOpened()== False): 
            print("Error opening video stream or file")
            exit()
        self.inqueue = Queue()
        self.images = []
        
    def load_images(self):
        while(self.cap.isOpened()):
            self.lock.acquire()
            ret, frame = self.cap.read()
            self.lock.release()
            if ret == True:
                self.inqueue.put(frame)
                self.images.append(frame)
            else: 
                break

    def save_calibration(self,ret, mtx, dist, rvecs, tvecs):
        if self.format == "pickle":
            camaera_data = {
                "ret": ret,
                "mtx": mtx,
                "dist": dist,
                "rvecs": rvecs,
                "tvecs": tvecs
            }
            # writes to a pickle file using protocl 2
            with open(self.filename,"rb") as f:
                pickle.dump(camera_data, f, 2)
        elif self.format == "yaml":
            pass
        elif self.format == "json":
            pass

    def find_chessboards(self,inqueue,outqueue):
        objpoints = []
        imgpoints = []
            
        while True:
            img = inqueue.get()
            if img is None:
                outqueue.put((objpoints,imgpoints))
                break

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (9,6), None)
            # If found, add object points, image points (after refining them)
            if ret == True:
                objpoints.append(self.objp)
                corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), self.criteria)
                imgpoints.append(corners)
                # Draw and display the corners
            
    def generate_calibration(self):
        number_of_threads = multiprocessing.cpu_count()
        threads = []
        print("Loading Images")
        for i in range(number_of_threads):
            threads.append(threading.Thread(target=self.load_images))
            threads[i].start()
        
        for index, thread in enumerate(threads):
            thread.join()
        self.cap.release()
        print("Images Loaded")

            
        outqueue = multiprocessing.Queue()
        processes = []

        for i in range(number_of_threads):
            self.inqueue.put(None)
        print("Finding Chessboards")
        for i in range(number_of_threads):
            p = Process(target=self.find_chessboards, args=(self.inqueue,outqueue,))
            processes.append(p)
            processes[i].start()
        
        for i in range(number_of_threads):
            processes[i].join()

        print("Done Finding Chessboards")
        self.gray = cv2.cvtColor(self.images[-1], cv2.COLOR_BGR2GRAY)        

        objpoints = [] # 3d point in real world space
        imgpoints = [] # 2d points in image plane.
        for i in range(number_of_threads):
            results = outqueue.get()
            objpoints += results[0]
            imgpoints += results[1]

        h,  w =  self.images[-1].shape[:2]
        print(h,w)
        print("Calculting Camera Parameters (This May Take A While)")
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, self.gray.shape[::-1], None, None)
        print("Done Calculting Camera Parameters")

        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
        print("Saving Calibration")
        self.save_calibration(ret, newcameramtx, dist, rvecs, tvecs)
        print("Done Saving Calibration")
d = CameraCalibrator()
d.generate_calibration()
