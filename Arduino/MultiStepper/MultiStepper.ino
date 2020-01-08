// MultiStepper.pde
// -*- mode: C++ -*-
// Use MultiStepper class to manage multiple steppers and make them all move to
// the same position at the same time for linear 2d (or 3d) motion.

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
// EG X-Y position bed driven by 2 steppers
// Alas its not possible to build an array of these with different pins for each :-(
AccelStepper stepper1(1, MOTOR_A_STEP_PIN, MOTOR_A_DIR_PIN);
AccelStepper stepper2(1, MOTOR_B_STEP_PIN, MOTOR_B_DIR_PIN);

// Up to 10 steppers can be handled as a group by MultiStepper
MultiStepper steppers;
String readStep1;
String readStep2;
bool startup = true;
bool isOk = false;

void readSerial()
{
  while (Serial.available()) {
    String resp = "";
    resp = Serial.readString();    
    Serial.println(resp);
    if (resp.indexOf('S') > -1) {
      Serial.print("Waiting");
    }
    if (resp.indexOf("T") > 0) {
      readStep1 = resp.substring(0, resp.indexOf('T'));
      readStep2 = resp.substring(0,resp.indexOf('R'));
      isOk = true;
    }
  }
}

void setup() {
  Serial.begin(9600);
  stepper1.setEnablePin(MOTOR_A_ENABLE_PIN);
  stepper1.setPinsInverted(false, false, true);
  stepper2.setEnablePin(MOTOR_B_ENABLE_PIN);
  stepper2.setPinsInverted(false, false, true);
  pinMode(MOTOR_A_ENABLE_PIN, OUTPUT);
  pinMode(MOTOR_B_ENABLE_PIN, OUTPUT);
  stepper1.setMaxSpeed(75);
  stepper2.setMaxSpeed(75);
  stepper1.enableOutputs();
  stepper2.enableOutputs();
  steppers.addStepper(stepper1);
  steppers.addStepper(stepper2);
}

void loop() {
  long positions[2]; // Array of desired stepper positions
    if (Serial.available()) {
      readSerial();
      if (isOk) {
        stepper1.enableOutputs();
        stepper2.enableOutputs();
        if (!steppers.run()) {
          positions[0] = readStep1.toInt();
          positions[1] = readStep2.toInt();
          Serial.print(positions[0]);
          Serial.print(" ");
          Serial.println(positions[1]);
          steppers.moveTo(positions);
          steppers.runSpeedToPosition();
          Serial.println(DONE);
          isOk = false;
        } else {
          
        }
      }
    } else {
      stepper1.disableOutputs();
      stepper2.disableOutputs();
    }
}
