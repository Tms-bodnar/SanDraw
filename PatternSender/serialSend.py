
import time
import math
import os
import glob
import serial

fileList = []
path = '/home/pi/API/patternDir'
for r, d, f in os.walk(path):
    for file in f:
        if '.thr' in file:
            fileList.append(file)
ser = serial.Serial('/dev/ttyACM0', '9600')
ser.flushInput()
for file in fileList:
    print(len(fileList))
    with open(path + "/" + file) as f:
        while True: 
            resp = ser.readline();
            
            if "OK" in resp.decode('utf-8'):
                print(resp);
                line = f.readline()
                if not line:
                    break
                if not '#' in line:
                    ser.write(line.encode('utf-8'))
