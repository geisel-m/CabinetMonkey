// Full X-Y-Z Gantry Controller
// X and Y: Stepper motors via DM542T/DM542 drivers
// Z: ClearPath MCPV via ClearCore over SoftwareSerial
// Arduino Uno
//
// Wiring:
//   X motor: PUL+ = pin 8, DIR+ = pin 9
//   Y motor: PUL+ = pin 3, DIR+ = pin 4
//   X limit switch: NC = pin 5, COM = GND
//   Y limit switch: NC = pin 2, COM = GND
//   ClearCore COM-0: Cat6 Pin 8 -> Arduino pin 10, Pin 5 -> Arduino pin 11, Pin 4 -> GND

#include <SoftwareSerial.h>

// ============ PIN DEFINITIONS ============
#define X_PUL 8
#define X_DIR 9
#define X_LIMIT 5
#define Y_PUL 3
#define Y_DIR 4
//#define Y_LIMIT 2

// SoftwareSerial to ClearCore
// Pin 10 = RX (from ClearCore), Pin 11 = TX (to ClearCore)
SoftwareSerial clearCoreSerial(10, 11);

// ============ MOTOR SETTINGS ============
const int STEPS_PER_REV = 800;
const float X_STEPS_PER_MM = 160.0;   // 800 steps/rev / 5mm lead
const float Y_STEPS_PER_MM = 200.0;   // 800 steps/rev / 4mm lead
// Z-axis: 6400 counts/rev, 20:1 gearbox, 44.75mm winch diameter
// Winch circumference = pi * 44.75 = 140.6 mm per winch rev
// 1 motor rev = 1/20 winch rev = 7.03 mm linear travel
// 6400 pulses / 7.03 mm = ~910 pulses per mm
const float Z_PULSES_PER_MM = 910.0;

// Speed control
int pulseDelay = 200;  // microseconds between step pulses
const int PULSE_DELAY_FLOOR = 50;

// ============ POSITION TRACKING ============
long currentX = 0;
long currentY = 0;
long currentZ_pulses = 0;  // Z position in pulses

// ============ Z-AXIS STATE ============
bool zAxisReady = false;

void setup() {
    Serial.begin(9600);
    clearCoreSerial.begin(9600);

    pinMode(X_PUL, OUTPUT);
    pinMode(X_DIR, OUTPUT);
    pinMode(X_LIMIT, INPUT_PULLUP);
    pinMode(Y_PUL, OUTPUT);
    pinMode(Y_DIR, OUTPUT);
    //pinMode(Y_LIMIT, INPUT_PULLUP);

    digitalWrite(X_PUL, LOW);
    digitalWrite(X_DIR, LOW);
    digitalWrite(Y_PUL, LOW);
    digitalWrite(Y_DIR, LOW);

    Serial.println("X-Y-Z Gantry Controller Starting...");
    Serial.println("Waiting for Z-axis to home...");

    // Wait for ClearCore to finish homing (up to 10 seconds)
    // If missed, use ZR command to manually set Z ready
    if (waitForClearCore("HOMED", 10000)) {
        Serial.println("Z-axis homed successfully.");
    } else {
        Serial.println("WARNING: Z-axis did not respond. Type ZR to enable Z manually.");
    }

    Serial.println("Commands:");
    Serial.println("  G X100 Y50   - Move to X=100mm Y=50mm");
    Serial.println("  G Z10        - Move Z to 10mm absolute");
    Serial.println("  H            - Move to current (0,0)");
    Serial.println("  HX           - Home X to limit switch");
    Serial.println("  HY           - Home Y to limit switch");
    Serial.println("  HA           - Home both X and Y");
    Serial.println("  P            - Print current position");
    Serial.println("  S200         - Set pulse delay (speed)");
    Serial.println("  Z            - Zero both X and Y");
    Serial.println("  ZX           - Zero X only");
    Serial.println("  ZY           - Zero Y only");
    Serial.println("  ZZ           - Zero Z only");
    Serial.println("  ZR           - Manually set Z as ready");
}

void loop() {
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        if (cmd.length() > 0) {
            parseCommand(cmd);
        }
    }
}

// ============ COMMAND PARSER ============
void parseCommand(String cmd) {
    if (cmd.charAt(0) == 'G' || cmd.charAt(0) == 'g') {
        // Check if this is a Z move
        int zIdx = cmd.indexOf('Z');
        if (zIdx < 0) zIdx = cmd.indexOf('z');
        if (zIdx >= 0) {
            float zDist = cmd.substring(zIdx + 1).toFloat();
            moveZ(zDist);
        }

        // Parse X and Y targets
        float targetX_mm = 0;
        float targetY_mm = 0;
        bool hasX = false;
        bool hasY = false;

        int xIdx = cmd.indexOf('X');
        if (xIdx < 0) xIdx = cmd.indexOf('x');
        if (xIdx >= 0) {
            targetX_mm = cmd.substring(xIdx + 1).toFloat();
            hasX = true;
        }

        int yIdx = cmd.indexOf('Y');
        if (yIdx < 0) yIdx = cmd.indexOf('y');
        if (yIdx >= 0) {
            targetY_mm = cmd.substring(yIdx + 1).toFloat();
            hasY = true;
        }

        if (hasX || hasY) {
            long targetX_steps = hasX ? (long)(targetX_mm * X_STEPS_PER_MM) : currentX;
            long targetY_steps = hasY ? (long)(targetY_mm * Y_STEPS_PER_MM) : currentY;

            Serial.print("Moving to X=");
            Serial.print(targetX_mm);
            Serial.print("mm Y=");
            Serial.print(targetY_mm);
            Serial.println("mm");

            moveToPosition(targetX_steps, targetY_steps);

            Serial.println("Move complete.");
            printPosition();
        }
    }
    else if (cmd.charAt(0) == 'H' || cmd.charAt(0) == 'h') {
        if (cmd.length() > 1 && (cmd.charAt(1) == 'Y' || cmd.charAt(1) == 'y')) {
            homeY();
        }
        else if (cmd.length() > 1 && (cmd.charAt(1) == 'X' || cmd.charAt(1) == 'x')) {
            homeX();
        }
        else if (cmd.length() > 1 && (cmd.charAt(1) == 'A' || cmd.charAt(1) == 'a')) {
            homeX();
            homeY();
            Serial.println("Both axes homed.");
            printPosition();
        }
        else {
            Serial.println("Moving to (0, 0)...");
            moveToPosition(0, 0);
            Serial.println("Move complete.");
            printPosition();
        }
    }
    else if (cmd.charAt(0) == 'P' || cmd.charAt(0) == 'p') {
        printPosition();
    }
    else if (cmd.charAt(0) == 'S' || cmd.charAt(0) == 's') {
        pulseDelay = cmd.substring(1).toInt();
        if (pulseDelay < PULSE_DELAY_FLOOR) pulseDelay = PULSE_DELAY_FLOOR;
        Serial.print("Pulse delay set to: ");
        Serial.print(pulseDelay);
        Serial.println(" us");
    }
    else if (cmd.charAt(0) == 'Z' || cmd.charAt(0) == 'z') {
        if (cmd.length() > 1 && (cmd.charAt(1) == 'X' || cmd.charAt(1) == 'x')) {
            currentX = 0;
            Serial.println("X position zeroed.");
        }
        else if (cmd.length() > 1 && (cmd.charAt(1) == 'Y' || cmd.charAt(1) == 'y')) {
            currentY = 0;
            Serial.println("Y position zeroed.");
        }
        else if (cmd.length() > 1 && (cmd.charAt(1) == 'Z' || cmd.charAt(1) == 'z')) {
            currentZ_pulses = 0;
            Serial.println("Z position zeroed.");
        }
        else if (cmd.length() > 1 && (cmd.charAt(1) == 'R' || cmd.charAt(1) == 'r')) {
            zAxisReady = true;
            currentZ_pulses = 0;
            Serial.println("Z-axis manually set to ready. Z position zeroed.");
        }
        else {
            currentX = 0;
            currentY = 0;
            Serial.println("X and Y position zeroed.");
        }
        printPosition();
    }
    else {
        Serial.println("Unknown command.");
    }
}

// ============ SIMULTANEOUS X-Y MOVE (Bresenham) ============
void moveToPosition(long targetX, long targetY) {
    long dx = targetX - currentX;
    long dy = targetY - currentY;

    digitalWrite(X_DIR, dx >= 0 ? HIGH : LOW);
    digitalWrite(Y_DIR, dy >= 0 ? HIGH : LOW);

    long absX = abs(dx);
    long absY = abs(dy);
    long totalSteps = max(absX, absY);

    if (totalSteps == 0) return;

    long errX = 0;
    long errY = 0;

    for (long i = 0; i < totalSteps; i++) {
        // Check limit switches
        // if (digitalRead(X_LIMIT) == HIGH && dx != 0) {
        //     Serial.println("X limit switch hit! Stopping.");
        //     break;
        // }
        //if (digitalRead(Y_LIMIT) == HIGH && dy > 0) {
        //    Serial.println("Y limit switch hit! Stopping.");
        
        

        errX += absX;
        errY += absY;

        bool stepX = false;
        bool stepY = false;

        if (errX >= totalSteps) {
            errX -= totalSteps;
            stepX = true;
        }
        if (errY >= totalSteps) {
            errY -= totalSteps;
            stepY = true;
        }

        if (stepX) digitalWrite(X_PUL, HIGH);
        if (stepY) digitalWrite(Y_PUL, HIGH);

        delayMicroseconds(pulseDelay);

        if (stepX) digitalWrite(X_PUL, LOW);
        if (stepY) digitalWrite(Y_PUL, LOW);

        delayMicroseconds(pulseDelay);

        if (stepX) currentX += (dx >= 0) ? 1 : -1;
        if (stepY) currentY += (dy >= 0) ? 1 : -1;
    }
}

// ============ Z-AXIS MOVE VIA CLEARCORE (ABSOLUTE) ============
void moveZ(float targetZ_mm) {
    if (!zAxisReady) {
        Serial.println("ERROR: Z-axis not ready.");
        return;
    }

    long targetZ_pulses = (long)(targetZ_mm * Z_PULSES_PER_MM);
    long deltaPulses = targetZ_pulses - currentZ_pulses;

    if (deltaPulses == 0) {
        Serial.println("Z already at target position.");
        return;
    }

    Serial.print("Moving Z to ");
    Serial.print(targetZ_mm);
    Serial.print(" mm (delta: ");
    Serial.print(deltaPulses);
    Serial.println(" pulses)");

    clearCoreSerial.print("Z ");
    clearCoreSerial.println(deltaPulses);

    if (waitForClearCore("DONE", 30000)) {
        currentZ_pulses = targetZ_pulses;
        Serial.println("Z move complete.");
        printPosition();
    } else {
        Serial.println("ERROR: Z move failed or timed out.");
    }
}

// ============ CLEARCORE COMMUNICATION ============
bool waitForClearCore(const char* expected, unsigned long timeout) {
    unsigned long startTime = millis();

    while (millis() - startTime < timeout) {
        if (clearCoreSerial.available()) {
            String response = clearCoreSerial.readStringUntil('\n');
            response.trim();

            if (response.length() > 0) {
                Serial.print("ClearCore: ");
                Serial.println(response);

                if (response == expected) {
                    if (String(expected) == "HOMED") zAxisReady = true;
                    return true;
                }
                if (response == "ERROR") {
                    return false;
                }
            }
        }
    }

    return false;
}

// ============ HOME Y TO LIMIT SWITCH ============
void homeY() {
    // Serial.println("Homing Y-axis to limit switch...");
    // digitalWrite(Y_DIR, LOW);

    // int homeSpeed = 400;

    // while (digitalRead(Y_LIMIT) == LOW) {
    //     digitalWrite(Y_PUL, HIGH);
    //     delayMicroseconds(homeSpeed);
    //     digitalWrite(Y_PUL, LOW);
    // //    delayMicroseconds(homeSpeed);
    // }

    Serial.println("Limit switch hit. Zeroing Y position.");
    currentY = 0;
    printPosition();
}

// ============ HOME X TO LIMIT SWITCH ============
void homeX() {
    Serial.println("Homing X-axis to limit switch...");
    digitalWrite(X_DIR, LOW);

    int homeSpeed = 400;

    while (digitalRead(X_LIMIT) == LOW) {
        digitalWrite(X_PUL, HIGH);
        delayMicroseconds(homeSpeed);
        digitalWrite(X_PUL, LOW);
        delayMicroseconds(homeSpeed);
    }

    Serial.println("Limit switch hit. Zeroing X position.");
    currentX = 0;
    printPosition();
}

// ============ PRINT POSITION ============
void printPosition() {
    Serial.print("Position: X=");
    Serial.print(currentX / X_STEPS_PER_MM);
    Serial.print("mm (");
    Serial.print(currentX);
    Serial.print(" steps) | Y=");
    Serial.print(currentY / Y_STEPS_PER_MM);
    Serial.print("mm (");
    Serial.print(currentY);
    Serial.print(" steps) | Z=");
    Serial.print(currentZ_pulses / Z_PULSES_PER_MM);
    Serial.print("mm (");
    Serial.print(currentZ_pulses);
    Serial.println(" pulses)");
}
