// ClearCore - Z-Axis Motor Controller
// Receives move commands from Arduino Uno over COM-0 (Serial0)
// Drives ClearPath MCPV in Pulse Burst Positioning mode on M-0
//
// Serial Protocol:
//   Arduino sends: "Z <pulses>\n"  (positive = down, negative = up)
//   ClearCore replies: "DONE\n" when move is complete
//   ClearCore replies: "HOMED\n" when homing is complete
//   ClearCore replies: "ERROR\n" if something goes wrong
//
// Wiring:
//   ClearPath motor -> ClearCore M-0 (8-pin Molex cable)
//   Cat6 cable: COM-0 RJ45 to Arduino (Pin 8->Uno pin 10, Pin 5->Uno pin 11, Pin 4->Uno GND)
//   ClearCore 24V logic power + separate 24V motor power

#include "ClearCore.h"

#define motor ConnectorM0

// Adjust these to match your MSP settings
// At 1000 RPM: 1000/60 * 6400 = 106,667 pulses/sec consumed
// PULSE_RATE must be higher than that. Set to 120,000.
#define PULSE_RATE 120000  // pulses per second

bool motorReady = false;

void setup() {
  Serial.begin(9600);    // USB Serial Monitor (for debugging)
  Serial0.begin(9600);   // COM-0 UART to Arduino Uno
  delay(1000);

  Serial.println("ClearCore Z-Axis Controller Starting...");

  // Set motor mode to Step and Direction (used for Pulse Burst on ClearCore)
  MotorMgr.MotorModeSet(MotorManager::MOTOR_ALL,
                         Connector::CPM_MODE_STEP_AND_DIR);

  // In Pulse Burst mode, ClearPath handles the move profile internally.
  // Set VelMax and AccelMax to max so ClearCore sends pulses as fast as possible.
  motor.VelMax(INT32_MAX);
  motor.AccelMax(INT32_MAX);

  // Set HLFB mode to bipolar PWM (for ASG-Position w/Measured Torque)
  motor.HlfbMode(MotorDriver::HLFB_MODE_HAS_BIPOLAR_PWM);
  motor.HlfbCarrier(MotorDriver::HLFB_CARRIER_482_HZ);

  Serial.println("Enabling motor (homing will begin)...");

  // Enable the motor - this triggers the homing sequence
  motor.EnableRequest(true);

  // Wait for homing to complete (HLFB asserts when done)
  Serial.println("Waiting for homing to complete...");
  uint32_t homingTimeout = millis();
  while (motor.HlfbState() != MotorDriver::HLFB_ASSERTED &&
         motor.HlfbState() != MotorDriver::HLFB_HAS_MEASUREMENT) {
    if (millis() - homingTimeout > 30000) {  // 30 second timeout
      Serial.println("ERROR: Homing timed out!");
      Serial0.println("ERROR");
      motorReady = false;
      return;
    }
    delay(10);
  }

  motorReady = true;
  Serial.println("Homing complete. Motor ready.");
  Serial0.println("HOMED");
}

void loop() {
  if (!motorReady) return;

  // Check for commands from Arduino
  if (Serial0.available()) {
    String received = Serial0.readStringUntil('\n');
    received.trim();

    if (received.length() > 0) {
      Serial.print("Received command: ");
      Serial.println(received);

      // Parse "Z <pulses>" command
      if (received.startsWith("Z ")) {
        long pulses = received.substring(2).toInt();

        if (pulses == 0 && received.substring(2) != "0") {
          Serial.println("ERROR: Invalid pulse count");
          Serial0.println("ERROR");
          return;
        }

        Serial.print("Moving ");
        Serial.print(pulses);
        Serial.println(" pulses...");

        // Command the move
        motor.Move(pulses);

        // Wait for move to complete
        uint32_t moveTimeout = millis();
        while (!motor.StepsComplete()) {
          if (millis() - moveTimeout > 30000) {  // 30 second timeout
            Serial.println("ERROR: Move timed out!");
            Serial0.println("ERROR");
            return;
          }
          delay(5);
        }

        // Wait for HLFB to confirm motor has settled
        uint32_t settleTimeout = millis();
        while (motor.HlfbState() != MotorDriver::HLFB_ASSERTED &&
               motor.HlfbState() != MotorDriver::HLFB_HAS_MEASUREMENT) {
          if (millis() - settleTimeout > 5000) {
            Serial.println("WARNING: HLFB settle timeout, but steps complete.");
            break;
          }
          delay(5);
        }

        Serial.println("Move complete.");
        Serial0.println("DONE");
      }
      else {
        Serial.print("Unknown command: ");
        Serial.println(received);
        Serial0.println("ERROR");
      }
    }
  }
}
