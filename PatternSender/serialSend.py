import math
import os
import serial

fileList = []
start = "S"
end = "E"
last = False
MICRO_STEP_CORR = 0.1125
max_radius = 0
step_div_remainder_arm2 = 0
step_div_remainder_arm1 = 0
prev_arm2_deg = 0
prev_arm1_deg = 0
deg2_modifier = 0
deg1_modifier = 0
first_line = False
# path = '/home/pi/SanDraw/PatternSender/patternDir'
path = './PatternDir'
# res_file = open(path + '/res.txt', 'a')
res_file = open(path + '/res.txt', 'a')
for r, d, f in os.walk(path):
    for file in f:
        if '.thr' in file:
            fileList.append(file)
# ser = serial.Serial('/dev/ttyACM0', '9600')
ser = serial.Serial('COM8')
ser.flushInput()


def parse_degrees(line):
    global first_line
    global prev_arm1_deg
    global prev_arm2_deg
    global step_div_remainder_arm2
    global step_div_remainder_arm1
    global max_radius
    global deg2_modifier
    global deg1_modifier
    raws = line.split(" ")
    z: float
    tht: float
    # arm_length = 0.5
    tht = float(raws[0])
    z = float(raws[1])
    
    arm1_step: float
    arm1_deg: float
    # tht_deg = round(math.degrees(tht), 6)
    # if tht < 0:
    # tht_deg = round(tht_deg + (360 * round(abs(tht_deg) // 360, 0)+1) + 180, 6)
    arm1_deg = round(math.degrees(math.acos(z)), 6)
    arm1_step = ((prev_arm1_deg - arm1_deg) / MICRO_STEP_CORR) * 1.333333
    step_div_remainder_arm1 = arm1_step % 1 + step_div_remainder_arm1
    if step_div_remainder_arm1 > 1:
        arm1_step = arm1_step + step_div_remainder_arm1 // 1 if arm1_step > 0 \
            else arm1_step - step_div_remainder_arm1 // 1
        step_div_remainder_arm1 = step_div_remainder_arm1 % 1
    
    arm2_deg = round(math.degrees(math.asin(z)), 6) * 2
    arm2_step = abs((prev_arm2_deg - arm2_deg) / MICRO_STEP_CORR)
    step_div_remainder_arm2 = arm2_step % 1 + step_div_remainder_arm2
    if step_div_remainder_arm2 > 1:
        arm2_step = arm2_step + step_div_remainder_arm2 // 1 if arm2_step > 0 \
            else arm2_step - step_div_remainder_arm2 // 1
        step_div_remainder_arm2 = step_div_remainder_arm2 % 1
            
    coordinates = "<" + str(arm1_step).split(".")[0].zfill(5) + "T" + str(0).split(".")[0].zfill(5) + "R>"
    if not first_line:
        res_file.write(str(tht) + ' ' + str(z) + ' ' + str(arm1_step) + ' ' + str(arm2_step) + '\n')
        ser.write(coordinates.encode('utf-8'))
        print(coordinates)
        check_response()
    
    if not first_line:
        temp1 = arm1_deg
        arm1_deg = arm1_deg - prev_arm1_deg
        prev_arm1_deg = temp1
        
        temp2 = arm2_deg
        arm2_deg = arm2_deg - prev_arm2_deg
        prev_arm2_deg = temp2
      
        if prev_arm2_deg == 0:
            deg2_modifier = deg2_modifier * -1
            deg1_modifier = deg1_modifier * -1
       
    if first_line:
        prev_arm1_deg = arm1_deg
        prev_arm2_deg = arm2_deg
    first_line = False


def check_response():
    wait = True
    while wait:
        check_resp = ser.readline()
    #    print(check_resp.decode('utf-8'))
        if "Done" in check_resp.decode('utf-8'):
            wait = False
        

def send_coordinates():
    global max_radius
    global deg2_modifier
    global deg1_modifier
    for oneFile in fileList:
        deg2_modifier = 1
        deg1_modifier = 1
        with open(path + "/" + oneFile) as openedFile:
            global first_line
            global last
            first_line = True
            lines = openedFile.readlines()
            last = lines[-1]
            for line in lines:
                print(lines.index(line) - 17)
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
