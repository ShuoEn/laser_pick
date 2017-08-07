from time import sleep, time
import sys
import os
import datetime

import numpy as np
import cv2
from collections import Counter
import serial

class CameraBase():
    """CameraBase class
        Do some camera related computing
    """
    cameraport=1
    path='./images/'
    thres=35
    ser=None
    def __init__(self):
        pass
    def mse(self,imageA, imageB):
        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images;
        # NOTE: the two images must have the same dimension
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])
        
        # return the MSE, the lower the error, the more "similar"
        # the two images are
        return err
    def compare_images(self,imageA, imageB):
        # compute the mean squared error and structural similarity
        # index for the images
        m = self.mse(imageA, imageB)
        print("MSE: %.2f" %m)

    def show_red(self,img_d):
        cnt = Counter()
        thres=0
        for i in img_d[:]:  # only consider lower part,
            for j in i:
                cnt[j] += 1
        for i in cnt.most_common():
            if i[1] >= thres:  # compute weighted arithmetic mean
                print("[x]:{} [count]:{}".format(i[0],i[1]))
    def print_outcome(self,res):
        """
        using package figlet to color print the outcome
        """
        if type(res) == bool:
            if res:
                print('\033[32m')  # green
                print("PASS")
                # os.system('figlet -c "P A S S"')
            else:
                print('\033[31m')  # red
                print("FAIL")
                #os.system('figlet -c "F A I L"')
        else:  # print the string if it's bot bool
            print('\033[31m')  # red
            print(res)
            #os.system('figlet -c "%s"' % res)
        print('\033[0m')

    def get_image(self,file_suffix='',count=5):
        timestamp = datetime.datetime.fromtimestamp(time()).strftime('%Y-%m-%d-%H-%M-%S')

        retry = 0
        camera = cv2.VideoCapture(self.cameraport)

        # 0. CV_CAP_PROP_POS_MSEC Current position of the video file in milliseconds.
        # CV_CAP_PROP_POS_FRAMES 0-based index of the frame to be decoded/captured next.
        # CV_CAP_PROP_POS_AVI_RATIO Relative position of the video file
        # CV_CAP_PROP_FRAME_WIDTH Width of the frames in the video stream.
        # CV_CAP_PROP_FRAME_HEIGHT Height of the frames in the video stream.
        # CV_CAP_PROP_FPS Frame rate.
        # CV_CAP_PROP_FOURCC 4-character code of codec.
        # CV_CAP_PROP_FRAME_COUNT Number of frames in the video file.
        # CV_CAP_PROP_FORMAT Format of the Mat objects returned by retrieve() .
        # CV_CAP_PROP_MODE Backend-specific value indicating the current capture mode.
        # CV_CAP_PROP_BRIGHTNESS Brightness of the image (only for cameras).
        # CV_CAP_PROP_CONTRAST Contrast of the image (only for cameras).
        # CV_CAP_PROP_SATURATION Saturation of the image (only for cameras).
        # CV_CAP_PROP_HUE Hue of the image (only for cameras).
        # CV_CAP_PROP_GAIN Gain of the image (only for cameras).
        # CV_CAP_PROP_EXPOSURE Exposure (only for cameras).
        # CV_CAP_PROP_CONVERT_RGB Boolean flags indicating whether images should be converted to RGB.
        # CV_CAP_PROP_WHITE_BALANCE Currently unsupported
        # CV_CAP_PROP_RECTIFICATION Rectification flag for stereo cameras (note: only supported by DC1394 v 2.x backend currently)
        # Change the camera setting using the set() function
        # camera.set(3,1024)
        # camera.set(4,768)
        camera.set(3,640)
        camera.set(4,480)
        camera.set(5,30)

        camera.set(15, -8)
        # test = camera.get(0)
        # ratio = camera.get(1)
        # frame_rate = camera.get(5)
        # width = camera.get(3)
        # height = camera.get(4)
        # brightness = camera.get(10)
        # contrast = camera.get(11)
        # saturation = camera.get(12)
        # hue = camera.get(13)
        # gain = camera.get(14)
        # exposure = camera.get(15)
        # print("Test: ", test)
        # print("Ratio: ", ratio)
        # print("Frame Rate: ", frame_rate)
        # print("Height: ", height)
        # print("Width: ", width)
        # print("Brightness: ", brightness)
        # print("Contrast: ", contrast)
        # print("Saturation: ", saturation)
        # print("Hue: ", hue)
        # print("Gain: ", gain)
        # print("Exposure: ", exposure)

        # image = self.get_image(camera)
        camera.read()
        # image= np.zeros((720,1280,3), np.uint8)
        image= np.zeros((480,640,3), np.uint8)
        for i in range(count):
            retval, image_temp = camera.read()
            image=cv2.addWeighted(image,1.0,image_temp,1.0/count,0)
        if image is None:
            flag = 'no image'
            print(flag)

        else:
            file_name = self.path + timestamp + file_suffix+'.jpg'
            if file_suffix !='':
                cv2.imwrite(file_name, image)
            flag='get image'
            # print(flag)
        camera.release()
        return image

    def highlight(self,img_diff,thres):
        # print("thres={}".format(thres))

        img_diff = img_diff.astype(np.uint8)
        # ret,thresh5 = cv2.threshold(img_diff,60,255,cv2.THRESH_TOZERO_INV)


        ret,thresh2 = cv2.threshold(img_diff,thres,255,cv2.THRESH_BINARY)
        # ret,thresh4 = cv2.threshold(thresh5,thres,255,cv2.THRESH_TOZERO)
        # noise_sum=np.sum(thresh2)
        # print(noise_sum)
        return thresh2
    def go(self):
        # self.connect_serial()
        red_ratio=0.8
        lumin_ratio=1-red_ratio
        self.get_image()
        self.laser_switch(1,0)
        self.laser_switch(2,0)
        # print('p1')
        p1=self.get_image('_p1')
        # print('p2')
        self.laser_switch(1,1)
        self.laser_switch(2,1)
        sleep(0.1)
        p2=self.get_image('_p2')
        d = cv2.absdiff(p1, p2)
        timestamp = datetime.datetime.fromtimestamp(time()).strftime('%Y-%m-%d-%H-%M-%S')
        file_name = self.path + timestamp + '_diff.jpg'
        cv2.imwrite(file_name, d)
        # print(d)        
        # self.compare_images(p1,p2)
        # self.show_red(d[:,:,2])

        file_name = self.path + timestamp + '_diff_x.jpg'

        d=d[:,:,0]*(0.7152*lumin_ratio)+d[:,:,1]*(0.0722*lumin_ratio)+d[:,:,2]*(0.2126*lumin_ratio)+d[:,:,2]*red_ratio
        # d=d[:,:,2]
        cv2.imwrite(file_name, d)
        d=self.highlight(d,self.thres)

        max_line_width = 0

        # for y in range(0, 720): 
        #     line_width = 0
        #     for x in range(0, 1280):
        #         if d[y][x] > 128:
        #             line_width = line_width + 1
        #         else:
        #             if line_width > 0:
        #                 max_line_width = max(line_width, max_line_width)
        #             line_width = 0

        # print("Max line width: %d" % max_line_width)
        # font = cv2.FONT_HERSHEY_SIMPLEX
        # if max_line_width>40:
        #     print('FAIL')
        #     cv2.putText(d,str(max_line_width)+' FAIL',(10,50), font, 1,(255,255,255),2)
        # else:
        #     print('PASS')
        #     cv2.putText(d,str(max_line_width)+' PASS',(10,50), font, 1,(255,255,255),2)

        cv2.imshow('image',d)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        file_name = self.path + timestamp + '_diff_x_hl.jpg'
        cv2.imwrite(file_name, d)

        # cv2.imshow('image',d)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # self.ser.close()
    def connect_serial(self,port=''):
        if port != '':
            print('port={}'.format(port))
            self.ser = serial.Serial(port, 115200, timeout=10)
        else:
            ports=self.serial_ports()
            for _port in ports:
                print('"{}"'.format(_port))
                ser = serial.Serial(_port, 115200, timeout=10)
                ser.write(b'tool ping \n')
                s = ser.readline()
                if s == b'pong\n':
                    ser.close()
                    self.ser = serial.Serial(_port, 115200, timeout=10)
                    return
                ser.close()
        
    def laser_switch(self,laser_channel,sw):
        return
        switch=''
        if sw==1:
            if laser_channel==1:
                self.ser.write(b'tool laser_on \n')
                # self.ser.write(b'X1O1\n')
            else:
                self.ser.write(b'tool laser_on \n')
                # self.ser.write(b'X1O2\n')
        else:
            self.ser.write(b'tool laser_off \n')
            # self.ser.write(b'X1F\n')
    def serial_ports(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

if __name__ == '__main__':
    _CameraBase = CameraBase()
    s=''
    num=35
    
    while(s!='END'):
        try:
            num=int(s,10)
            _CameraBase.thres=num
        except:
            num=35
        _CameraBase.go()
        s=input('END to exit or ENTER to continue.\n')

