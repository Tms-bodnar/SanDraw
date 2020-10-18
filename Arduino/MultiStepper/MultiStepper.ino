#include <AccelStepper.h>
#include <MultiStepper.h>

#define MOTOR_A_ENABLE_PIN 8
#define MOTOR_A_STEP_PIN 2
#define MOTOR_A_DIR_PIN 5

#define MOTOR_B_ENABLE_PIN 8
#define MOTOR_B_STEP_PIN 3
#define MOTOR_B_DIR_PIN 6

#define WAITING "Waiting"
#define DONE "Done"

#define MOTORS 2

AccelStepper stepper1(1, MOTOR_A_STEP_PIN, MOTOR_A_DIR_PIN);
AccelStepper stepper2(1, MOTOR_B_STEP_PIN, MOTOR_B_DIR_PIN);
MultiStepper steppers;

const byte incomingSize = 32;
char incoming[incomingSize];
boolean newData = false;

long positions[MOTORS];

void initPosArray() {
  positions[0] = 0;
  positions[1] = 0;
}

bool readIncoming() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char startOperation = 'S';
  char endOperation = 'E';
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();
    if (recvInProgress == true) {
      if (rc != endMarker) {
        incoming[ndx] = rc;
        ndx++;
        if (ndx >= incomingSize) {
          ndx = incomingSize - 1;
        }
      }
      else {
        incoming[ndx] = '\0';
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
      return true;
    }
    else if (rc == startMarker) {
      recvInProgress = true;
      return true;
    }
    else if (rc == startOperation) {
      Serial.println(WAITING);
      return true;
    }
    else if ( rc == endOperation ) {
      return false;
    }
  }
}

void moveSteppers() {
  if (newData == true) {
    stepper1.enableOutputs();
    stepper2.enableOutputs();
    stepper1.setCurrentPosition(0);
    stepper2.setCurrentPosition(0);
    stepper1.setMaxSpeed(35);
    stepper2.setMaxSpeed(35);
    int i = 0;
    long positions[MOTORS];
    char temp[5];
    temp[0] = incoming[0];
    temp[1] = incoming[1];
    temp[2] = incoming[2];
    temp[3] = incoming[3];
  temp[4] = incoming[4];
    i = atol(temp);
    positions[0] = i;
    temp[0] = incoming[6];
    temp[1] = incoming[7];
    temp[2] = incoming[8];
    temp[3] = incoming[9];
    temp[4] = incoming[10];
    i = atol(temp);
    positions[1] = i;
    Serial.print(positions[0]);
    Serial.print(" ");
    Serial.print(positions[1]);
    Serial.print(" Step ");
//    if ( positions[0] == 0 ) {
//      stepper1.disableOutputs();
//    }
//    if ( positions[1] == 0 ) {
//      stepper2.disableOutputs();
//    }
    steppers.moveTo(positions);
    steppers.runSpeedToPosition();
    Serial.println(DONE);
    newData = false;
  }
}

void disableSteppers(){
  stepper1.disableOutputs();
  stepper2.disableOutputs();
}

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(100);
  Serial.println(WAITING);
  initPosArray();
  stepper1.setEnablePin(MOTOR_A_ENABLE_PIN);
  stepper1.setPinsInverted(false, false, true);
  stepper2.setEnablePin(MOTOR_B_ENABLE_PIN);
  stepper2.setPinsInverted(false, false, true);
  pinMode(MOTOR_A_ENABLE_PIN, OUTPUT);
  pinMode(MOTOR_B_ENABLE_PIN, OUTPUT);
  steppers.addStepper(stepper1);
  steppers.addStepper(stepper2);
}

void loop() {
  if ( readIncoming() ){
  moveSteppers();
  }
  else {
    disableSteppers();
  }
}
