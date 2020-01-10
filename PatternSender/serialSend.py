
import time
import math
import os
import glob
import serial

fileList = []
start = "S"
end = "End"
last = False
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
        print(resp.decode('utf-8'))
        if "Done" in resp.decode('utf-8'):
            wait = False
        

def sendCoords():
    for file in fileList:
        with open(path + "/" + file) as f:
                lines = f.readlines()
                last = lines[-1]
                for line in lines:
                    if not line:
                        break
                    if not '#' in line:
                        ser.write(line.encode('utf-8'))
                        checkResponse()
                    if line is last:
                        last = True
                        break
                

while not last:
    ser.write(start.encode('utf-8'))
    resp = ser.readline()
    if "Waiting" in resp.decode('utf-8'):
        sendCoords()

