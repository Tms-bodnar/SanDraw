import math
import os
import serial

fileList = []
start = "S"
end = "E"
last = False
MICRO_STEP_CORR = 0.1125
max_radius = 0
prev_tht: float
prev_z: float
prev_z_for_arm1: float
step_div_remainder_arm2 = 0
step_div_remainder_arm1 = 0

first_line = False
path = '/home/pi/SanDraw/PatternSender/patternDir'
res_file = open(path + '/res.csv', 'a')
for r, d, f in os.walk(path):
    for file in f:
        if '.thr' in file:
            fileList.append(file)
ser = serial.Serial('/dev/ttyACM0', '9600')
ser.flushInput()


def parse_degrees(line):
    global first_line
    global prev_tht
    global prev_z
    global prev_z_for_arm1
    global step_div_remainder_arm2
    global step_div_remainder_arm1
    arm2_multiplier = 1;
    raws = line.split(" ")
    z: float
    z_for_arm1: float
    tht: float
    prev_tht_deg: float
    arm_length = 0.5
    tht = float(raws[0])
    z = float(raws[1])
    if first_line:
        prev_z = z
        prev_tht = tht
        prev_z_for_arm1 = z
    arm1_step: float
    arm1_deg: float
    z_for_arm1 = z
    if tht < 0:
        tht += math.pi
        z_for_arm1 *= -1
        arm2_multiplier *= -1
    tht_deg = round(math.degrees(tht), 6)
    prev_tht_deg = round(math.degrees(prev_tht), 6)
    arm1_deg = round(tht_deg + math.degrees(math.acos(z_for_arm1)), 6)
    prev_arm1_deg = round(prev_tht_deg + math.degrees(math.acos(prev_z_for_arm1)), 6)
    arm1_step = ((prev_arm1_deg - arm1_deg) / MICRO_STEP_CORR) * 1.333333
    step_div_remainder_arm1 += arm1_step % 1
    if abs(step_div_remainder_arm1) > 1:
        arm1_step += step_div_remainder_arm1
        step_div_remainder_arm1 = arm1_step % 1
        
    prev_arm2_deg = round(math.degrees(math.acos((arm_length - prev_z * prev_z) / arm_length)), 6)       
    arm2_deg = round(math.degrees(math.acos((arm_length - z * z) / arm_length)), 6) 
    arm2_step = (prev_arm2_deg - arm2_deg) / MICRO_STEP_CORR * arm2_multiplier
    step_div_remainder_arm2 += arm2_step % 1
    if abs(step_div_remainder_arm2) > 1:
        arm2_step += step_div_remainder_arm2
        step_div_remainder_arm2 = arm2_step % 1
     
    coordinates = "<" + str(arm1_step).split(".")[0].zfill(5) + "T" + str(arm2_step).split(".")[0].zfill(5) + "R>"
    if not first_line:
        res_file.write(str(arm1_step).split(".")[0] + ',' + str(arm2_step).split(".")[0]  + '\n')
        ser.write(coordinates.encode('utf-8'))
        print(coordinates)
        check_response()
    else:
        res_file.write('x,y' + '\n')
    prev_tht = tht
    prev_z = z
    prev_z_for_arm1 = z_for_arm1
    first_line = False


def check_response():
    wait = True
    while wait:
        check_resp = ser.readline()
        if "Done" in check_resp.decode('utf-8'):
            wait = False
        

def send_coordinates():
    global max_radius
    for oneFile in fileList:
        with open(path + "/" + oneFile) as openedFile:
            global first_line
            global last
            first_line = True
            lines = openedFile.readlines()
            last = lines[-1]
            for line in lines:
                if not line:
                    last = True
                    break
                if line.find('Max Radius: ') > 0:
                    max_radius = float(line[18:])
                if not line.startswith('#') and not line.startswith('\n'):
                    parse_degrees(line)
                    
                if line is last:
                    res_file.close()
                    ser.write(end.encode('utf-8'))
                    break


x = 0
while x < 1:
    ser.write(start.encode('utf-8'))
    resp = ser.readline()
    if "Waiting" in resp.decode('utf-8'):
        send_coordinates()
        x += 1
