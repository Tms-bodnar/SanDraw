import math
import os
import serial

waiting_for_arduino = True

# variables file ops
fileList = []
start_code = "S"
end_code = "E"
line_is_first = False
path = '/home/pi/SanDraw/PatternSender/patternDir'
steps_result_file = open(path + '/res.csv', 'a')

# variables step calculation
MICRO_STEP_CORR = 0.1125
ARM_LENGTH = 0.5
GEAR_RATIO = 1.333333
POSITIVE = 1
NEGATIVE = -1
theta_previous: float
rho_previous: float
rho_previous_for_arm1: float
arm2_step_remainder = 0
arm1_step_remainder = 0

# read *.tht files to array
for r, d, f in os.walk(path):
    for file in f:
        if '.thr' in file:
            fileList.append(file)

# start serial
ser = serial.Serial('/dev/ttyACM0', '9600')
ser.flushInput()


# calculate steps from theta-rho pairs
def parse_degrees(line):
    global ARM_LENGTH
    global line_is_first
    global theta_previous
    global rho_previous
    global rho_previous_for_arm1
    global arm1_step_remainder
    global arm2_step_remainder

    arm2_direction_modifier = POSITIVE  # variable for arm2 direction
    raws = line.split(" ")
    theta = float(raws[0])
    rho = float(raws[1])

    if line_is_first:
        theta_previous = theta
        rho_previous = rho
        rho_previous_for_arm1 = rho

    rho_for_arm1_calc = rho
    if theta < 0:
        theta += (theta % math.pi) * math.pi
        rho_for_arm1_calc *= NEGATIVE
        arm2_direction_modifier = NEGATIVE

    theta_degrees = round(math.degrees(theta), 6)
    theta_degrees_previous = round(math.degrees(theta_previous), 6)

    arm1_degrees = round(theta_degrees + math.degrees(math.acos(rho_for_arm1_calc)), 6)
    arm1_degrees_previous = round(theta_degrees_previous + math.degrees(math.acos(rho_previous_for_arm1)), 6)
    arm1_step = ((arm1_degrees_previous - arm1_degrees) / MICRO_STEP_CORR) * GEAR_RATIO

    arm1_step_remainder += arm1_step % 1
    if abs(arm1_step_remainder) > 1:
        arm1_step += arm1_step_remainder
        arm1_step_remainder = arm1_step % 1

    arm2_degrees = round(math.degrees(math.acos((ARM_LENGTH - rho * rho) / ARM_LENGTH)), 6)
    arm2_degrees_previous = round(math.degrees(math.acos((ARM_LENGTH - rho_previous * rho_previous) / ARM_LENGTH)), 6)
    arm2_step = (arm2_degrees_previous - arm2_degrees) / MICRO_STEP_CORR * arm2_direction_modifier

    arm2_step_remainder += arm2_step % 1
    if abs(arm2_step_remainder) > 1:
        arm2_step += arm2_step_remainder
        arm2_step_remainder = arm2_step % 1
     
    coordinates = "<" + str(arm1_step).split(".")[0].zfill(5) + "T" + str(arm2_step).split(".")[0].zfill(5) + "R>"

    if line_is_first:
        steps_result_file.write('x,y' + '\n')
        line_is_first = False
    else:
        steps_result_file.write(str(arm1_step).split(".")[0] + ',' + str(arm2_step).split(".")[0] + '\n')
        ser.write(coordinates.encode('utf-8'))
        print(coordinates)
        check_response()

    theta_previous = theta
    rho_previous = rho
    rho_previous_for_arm1 = rho_for_arm1_calc


def check_response():
    wait = True
    while wait:
        response = ser.readline()
        if "Done" in response.decode('utf-8'):
            wait = False
        

def send_coordinates():
    for oneFile in fileList:
        with open(path + "/" + oneFile) as opened_file:
            global line_is_first
            line_is_first = True
            lines = opened_file.readlines()
            last_line = lines[-1]
            for line in lines:
                if not line.startswith('#') and not line.startswith('\n'):
                    parse_degrees(line)
                if line is last_line:
                    steps_result_file.close()
                    ser.write(end_code.encode('utf-8'))
                    break


while waiting_for_arduino:
    ser.write(start_code.encode('utf-8'))
    resp = ser.readline()
    if "Waiting" in resp.decode('utf-8'):
        send_coordinates()
        waiting_for_arduino = False
