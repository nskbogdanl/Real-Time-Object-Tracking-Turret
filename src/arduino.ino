#include <Servo.h>
#include "Arduino_LED_Matrix.h"

ArduinoLEDMatrix matrix;

Servo servoX;
Servo servoY;

// Image of the cross on the LED matrix
uint8_t crossIcon[8][12] = {
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0},
  {0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0},
  {0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0},
  {0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0},
  {0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0}
};

// Image of the checkmark on the LED matrix
uint8_t checkIcon[8][12] = {
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0},
  {0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0},
  {0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
};

// Image of the dots on the LED matrix
uint8_t dotsIcon[8][12] = {
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0},
  {0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
};

const int servoX_pin = 9;
const int servoY_pin = 10;
long lastCommand=0;

void setup() {
  Serial.begin(9600);
  servoX.attach(servoX_pin);
  servoY.attach(servoY_pin);
  
  servoX.write(90); // Center
  servoY.write(90); // Center
  delay(500);
  Serial.println("Arduino ready");

  matrix.begin();
  matrix.renderBitmap(crossIcon, 8, 12);
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    if (data.length() == 0) return;

    if (data == "PING") {
      Serial.println("PONG");
      return;
    }

    int commaIndex = data.indexOf(',');
    if (commaIndex > 0) {
      int x_axis_speed = data.substring(0, commaIndex).toInt();
      int y_axis_speed = data.substring(commaIndex + 1).toInt();

      x_axis_speed = constrain(x_axis_speed, 0, 180);
      y_axis_speed = constrain(y_axis_speed, 0, 180);

      servoX.write(x_axis_speed);
      servoY.write(y_axis_speed);
      matrix.renderBitmap(checkIcon, 8, 12);
    }
    lastCommand=millis();
  }
  if (millis() - lastCommand > 500) {
        servoX.write(90);
        servoY.write(90);
        matrix.renderBitmap(crossIcon, 8, 12);
      }
}