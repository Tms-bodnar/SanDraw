
import time
import math
import os
import glob
import serial

fileList = []
start = "Start"
path = '/home/pi/SanDraw/PatternSender/patternDir'
for r, d, f in os.walk(path):
    for file in f:
        if '.thr' in file:
            fileList.append(file)
ser = serial.Serial('/dev/ttyACM0', '9600')
ser.flushInput()

def checkResponse():
    wait = True
    while wait:
        resp = ser.readline()
        if "Done" in resp.decode('utf-8'):
            wait = False
        

def sendCoords():
    print("function called")
    for file in fileList:
        with open(path + "/" + file) as f:
            while True: 
                line = f.readline()
                if not line:
                    break
                if not '#' in line:
                    print("coord sent")
                    ser.write(line.encode('utf-8'))
                    checkResponse()
                

while True:
    ser.write(start.encode('utf-8'))
    resp = ser.readline()
    print(resp.decode('utf-8'))
    if "Waiting" in resp.decode('utf-8'):
        print("Waiting came")
        sendCoords()
        break

