#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <Arduino.h>
#include <string.h>

#define SERVO_MIN 150
#define SERVO_MAX 600
#define SERVO_FREQ 50

#define NUM_SERVOS 5

const uint8_t servoPins[NUM_SERVOS] = {0, 1, 2, 3, 4};

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

static constexpr unsigned long BAUD_RATE = 115200;
static constexpr size_t MAX_LINE_LENGTH = 128;

char lineBuffer[MAX_LINE_LENGTH];
size_t lineLength = 0;

// Current + target angles
float currentAngles[NUM_SERVOS] = {90, 90, 90, 90, 90};
float targetAngles[NUM_SERVOS]  = {90, 90, 90, 90, 90};

bool moving = false;
float stepSize = 1.5; // degrees per update

void resetLineBuffer() {
    lineLength = 0;
    lineBuffer[0] = '\0';
}

uint16_t convertAngleToPosition(float angle) {
    angle = constrain(angle, 0.0, 180.0);
    return SERVO_MIN + ((SERVO_MAX - SERVO_MIN) * angle) / 180.0;
}

void setServoPosition(uint8_t i, float angle) {
    pwm.setPWM(servoPins[i], 0, convertAngleToPosition(angle));
}

bool waitForServoAngles(char *buffer) {
    while (Serial.available() > 0) {
        char incoming = (char)Serial.read();

        if (incoming == '\n' || incoming == '\r') {
            if (lineLength == 0) continue;

            lineBuffer[lineLength] = '\0';
            strcpy(buffer, lineBuffer);
            resetLineBuffer();
            return true;
        }

        if (lineLength < MAX_LINE_LENGTH - 1) {
            lineBuffer[lineLength++] = incoming;
        } else {
            resetLineBuffer();
        }
    }
    return false;
}

bool digestCommand(const char *command, float angles[NUM_SERVOS]) {
    int parsed = sscanf(command,
        "%f,%f,%f,%f,%f",
        &angles[0],
        &angles[1],
        &angles[2],
        &angles[3],
        &angles[4]);

    return parsed == NUM_SERVOS;
}

// Smooth motion update
void updateMotion() {
    bool allReached = true;

    for (int i = 0; i < NUM_SERVOS; i++) {
        float diff = targetAngles[i] - currentAngles[i];

        if (abs(diff) > stepSize) {
            allReached = false;
            currentAngles[i] += (diff > 0 ? stepSize : -stepSize);
        } else {
            currentAngles[i] = targetAngles[i];
        }

        setServoPosition(i, currentAngles[i]);
    }

    if (allReached) {
        moving = false;
        Serial.println("SUCCESS");
    }
}

void setup() {
    Serial.begin(BAUD_RATE);

    pwm.begin();
    pwm.setPWMFreq(SERVO_FREQ);

    resetLineBuffer();

    for (int i = 0; i < NUM_SERVOS; i++) {
        currentAngles[i] = 90;
        targetAngles[i] = 90;
        setServoPosition(i, 90);
    }

    Serial.println("Ready");
}

void loop() {
    char command[MAX_LINE_LENGTH];

    // Read command
    if (waitForServoAngles(command)) {

        if (strcmp(command, "CANCEL") == 0) {
            moving = false;
            Serial.println("CANCELLED");
            return;
        }

        float angles[NUM_SERVOS];

        if (!digestCommand(command, angles)) {
            Serial.println("ERROR");
            return;
        }

        for (int i = 0; i < NUM_SERVOS; i++) {
            if (angles[i] < 0 || angles[i] > 180) {
                Serial.println("ERROR");
                return;
            }
            targetAngles[i] = angles[i];
        }

        moving = true;
    }

    // Keep moving even without new commands
    if (moving) {
        updateMotion();
        delay(10); // controls smoothness
    }
}