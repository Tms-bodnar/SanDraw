
import math
import os
import serial

fileList = []
start = "S"
end = "E"
last = False
MICROSTEP_CORR = 0.1125
maxRadius = 0
stepDivRemainderArm2 = 0
stepDivRemainderArm1 = 0
prevArm2Deg = 0
prevArm1Deg = 0
firstLine = False
path = '/home/pi/SanDraw/PatternSender/patternDir'
resfile = open(path + '/res.txt','a') 
for r, d, f in os.walk(path):
    for file in f:
        if '.thr' in file:
            fileList.append(file)
ser = serial.Serial('/dev/ttyACM0', '9600')
ser.flushInput()

def parseDegrees(line):
    global firstLine
    global prevArm1Deg
    global prevArm2Deg
    global stepDivRemainderArm2
    global stepDivRemainderArm1
    global maxRadius
    global deg2Modifier
    global deg1Modifier
    raws = line.split(" ")
    Z = 0
    tht = 0
    armLength = 0.5
    
    tht = float(raws[0])
    Z = float(raws[1])
    
    arm1Step = 0
    arm1Deg = 0
    thtdeg = round(math.degrees(tht), 6)
    if tht < 0:
        thtdeg = round(thtdeg + (360 * round(abs(thtdeg) // 360, 0)+1)  + 180, 6)
    arm1Deg = round(math.degrees(math.acos(Z)), 6)
    arm1Step = (( prevArm1Deg - arm1Deg ) / MICROSTEP_CORR)  * 1.333333
    stepDivRemainderArm1 = arm1Step % 1 + stepDivRemainderArm1
    if stepDivRemainderArm1 > 1:
        arm1Step = arm1Step + stepDivRemainderArm1 // 1 if arm1Step > 0 else arm1Step - stepDivRemainderArm1 // 1
        stepDivRemainderArm1 = stepDivRemainderArm1 % 1    
    
    arm2Deg = round(math.degrees(math.asin(Z)), 6) * 2
    arm2Step = abs(( prevArm2Deg - arm2Deg ) / MICROSTEP_CORR)
    stepDivRemainderArm2 = arm2Step % 1 + stepDivRemainderArm2
    if stepDivRemainderArm2 > 1:
        arm2Step = arm2Step + stepDivRemainderArm2 // 1 if arm2Step > 0 else arm2Step - stepDivRemainderArm2 // 1
        stepDivRemainderArm2 = stepDivRemainderArm2 % 1
            
    coordinates = "<" + str(arm1Step).split(".")[0].zfill(5) + "T" + str(0).split(".")[0].zfill(5) + "R>";
    if not firstLine:
        resfile.write(str(tht) + ' ' +  str(Z) + ' ' + str(int(arm1Step)) + ' ' + str(int(arm2Step)) + '\n')
        ser.write(coordinates.encode('utf-8'))
        print(coordinates)
        checkResponse()
    
    if not firstLine:
        temp1 = arm1Deg
        arm1Deg =  arm1Deg - prevArm1Deg 
        prevArm1Deg = temp1
        
        temp2 = arm2Deg
        arm2Deg = arm2Deg - prevArm2Deg
        prevArm2Deg = temp2
      
        if prevArm2Deg == 0:
            deg2Modifier = deg2Modifier * -1
            deg1Modifier = deg1Modifier * -1
       
    if firstLine:
        prevArm1Deg = arm1Deg     
        prevArm2Deg = arm2Deg
    firstLine = False

def checkResponse():
    wait = True
    while wait:
        checkedResp = ser.readline()
    #    print(checkedResp.decode('utf-8'))
        if "Done" in checkedResp.decode('utf-8'):
            wait = False
        

def sendCoords():
    global maxRadius
    global deg2Modifier
    global deg1Modifier
    for oneFile in fileList:
        deg2Modifier = 1
        deg1Modifier = 1
        with open(path + "/" + oneFile) as openedFile:
            global firstLine
            global last
            firstLine = True
            lines = openedFile.readlines()
            last = lines[-1]
            for line in lines:
                print(lines.index(line) - 17)
                if not line:
                    last = True
                    break
                if line.find('Max Radius: ') > 0:
                    maxRadius = float(line[18:])
                if not line.startswith('#') and not line.startswith('\n'):
                    parseDegrees(line)
                    
                if line is last:
                    resfile.close()
                    ser.write(end.encode('utf-8'))
                    break
            
x = 0
while x < 1:
    ser.write(start.encode('utf-8'))
    resp = ser.readline()
    if "Waiting" in resp.decode('utf-8'):
        sendCoords()
        x += 1

