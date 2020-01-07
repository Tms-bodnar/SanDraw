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
// EG X-Y position bed driven by 2 steppers
// Alas its not possible to build an array of these with different pins for each :-(
AccelStepper stepper1(1, MOTOR_A_STEP_PIN, MOTOR_A_DIR_PIN);
AccelStepper stepper2(1, MOTOR_B_STEP_PIN, MOTOR_B_DIR_PIN);

// Up to 10 steppers can be handled as a group by MultiStepper
MultiStepper steppers;
String readStep1;
String readStep2;

bool readSerial(void)
{
  readStep1 = Serial.readStringUntil('A');
  readStep2 = Serial.readStringUntil('B');
  Serial.println("reading OK");
  return true;
}

void setup() {
  Serial.begin(9600);
  Serial.println("OK from setup");
  stepper1.setEnablePin(MOTOR_A_ENABLE_PIN);
  stepper1.setPinsInverted(false, false, true);
  stepper2.setEnablePin(MOTOR_B_ENABLE_PIN);
  stepper2.setPinsInverted(false, false, true);
  pinMode(MOTOR_A_ENABLE_PIN, OUTPUT);
  pinMode(MOTOR_B_ENABLE_PIN, OUTPUT);
  // Configure each stepper
  stepper1.setMaxSpeed(75);
  stepper2.setMaxSpeed(75);
  stepper1.enableOutputs();
  stepper2.enableOutputs();
  // Then give them to MultiStepper to manage
  steppers.addStepper(stepper1);
  steppers.addStepper(stepper2);
}

void loop() {
  long positions[2]; // Array of desired stepper positions
  if (Serial.available() > 0) {
    stepper1.enableOutputs();
    stepper2.enableOutputs();
    if (!steppers.run()) {
      readSerial();
      positions[0] = readStep1.toInt();
      positions[1] = readStep2.toInt();
      //positions[0] = 3000;
      //positions[1] = 2000;
      Serial.print(positions[0]);
      Serial.print(" ");
      Serial.println(positions[1]);
      steppers.moveTo(positions);
      steppers.runSpeedToPosition(); // Blocks until all are in position
    } else {
          Serial.println("loop not stepping OK");
    }
  } else {
    stepper1.disableOutputs();
    stepper2.disableOutputs();
  }
}
