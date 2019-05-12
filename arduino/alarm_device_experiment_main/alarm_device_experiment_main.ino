const int packet_size = 6;

typedef union {
  float floatingPoint;
  byte binary[4];
} binaryFloat;

void write_float(char id, float value) {
  binaryFloat reading;
  reading.floatingPoint = value;

  byte res[packet_size];
  res[0] = id;
  res[1] = reading.binary[3];
  res[2] = reading.binary[2];
  res[3] = reading.binary[1];
  res[4] = reading.binary[0];
  res[5] = '\n';

  Serial.write(res, packet_size);
}

void write_long(char id, long value32) {
  byte res[packet_size];
  res[0] = id;
  res[1] = (value32 >> 24) & 0xFF;
  res[2] = (value32 >> 16) & 0xFF;
  res[3] = (value32 >> 8)  & 0xFF;
  res[4] = value32 & 0xFF;
  res[5] = '\n';

  Serial.write(res, packet_size);
}

void write_int(char id, int value16) {
  long value32 = (long) value16;
  write_long(id, value32);
}

#include <Wire.h>


int bPin1 = 2; //pin number 1st button
int bPin2 = 3; //pin number 2nd button
int bPin3 = 4; //pin number 3rd button
bool bVal1 = LOW; //value read from button 1
bool bVal2 = LOW; //value read from button 2
bool bVal3 = LOW; //value read from button 3
int activePin = 8; //digital pin triggering device on/off.
int alarmTypePin = 9; //digital pin triggering which alarm system is active
int knobValue = 0;
int scenarioValue = 0;

bool active = 0; //0 or 1, decides if it will trigger alarms or not

int alarms = 1; //value to hold number of alarms that will be triggered in total before device becomes inactive again
int currentAlarm = 0; //counter counting how many alarms have happened
int minPeriod = 50000; // input in seconds here minimum time period between alarms
int maxPeriod = 70000; // input in seconds here maximum time period between

byte rVal = 0;

int scen1Alarms = 2; //value deciding number of alarms in scenario 1
int scen2Alarms = 3; //value deciding number of alarms in scenario 2
int scen3Alarms = 5; //value deciding number of alarms in scenario 3

unsigned long currentTime = 0; //var to store current time using millis(), to be updated throughout
unsigned long startTime = 0; //time when alarm starts
unsigned long responseTime = 0; //response time to react to alarm
unsigned long alarmPeriod = 10000; //var in milliseconds that decides how long the alarm should sound before alarm task is failed due to no action.
unsigned long randomPeriod = 0; //Variable to hold ranomized waiting time untill alarm is triggered
unsigned long limitTime = 0; //Variable to hold time limit where alarm task is failed due to no action

int alarmType = 0; // Set to 0 for system A (light, sound) and 1 for system B (light, sound, haptic)
int alarmSystemMod = 0; //Variable adjusting rVal in line with what system is active

int scenarioKnob() {
  int sensorValue = analogRead(A3);
  if (sensorValue >= 0 && sensorValue < 100) {
    knobValue = 1;
  }
  if (sensorValue >= 100 && sensorValue < 923) {
    knobValue = 2;
  }
  if (sensorValue >= 924) {
    knobValue = 3;
  }
  //Serial.println(knobValue);
  return knobValue;
}

void setup() {
  // put your setup code here, to run once:

  pinMode(activePin, INPUT);
  pinMode(bPin1, INPUT);
  pinMode(bPin2, INPUT);
  pinMode(bPin3, INPUT);
  Serial.begin(115200);

  Wire.begin(); //join i2c bus
  randomSeed(analogRead(0));

}

void loop() {
  // put your main code here, to run repeatedly:
  //  Writing float:
  //  write_float(0xAA, 123.4141);

  //  Writing integer:
  //  write_int(0xAA, 5234);


  active = digitalRead(activePin); //Read value of on-switch
  alarmType = digitalRead(alarmTypePin); //Real value of alarmTypePin, deciding which system should be used.

  if (active == HIGH && currentAlarm < alarms) {
    write_int(12, 1); //Sends alarm=armed
  }
  if (alarmType == 0) {
    alarmSystemMod = 0;
    //Serial.println("System A (light, sound) is active.");
  }
  if (alarmType == 1) {
    alarmSystemMod = 3;
    //Serial.println("System B (light, sound, haptic) is active.");
  }
  scenarioValue = scenarioKnob();
  write_int(17, scenarioValue); //Sends if scenario 1, 2 or 3 is active
  
  if (scenarioValue == 1) {
    alarms = scen1Alarms;
    //Serial.println("Scenario 1 active");
  }
  if (scenarioValue == 2) {
    alarms = scen2Alarms;
    //Serial.println("Scenario 2 active");
  }
  if (scenarioValue == 3) {
    alarms = scen3Alarms;
    //Serial.println("Scenario 3 active");
  }
  
  while (active == HIGH && currentAlarm < alarms) {      //Condition to execute when device is on/armed.
    ++currentAlarm; //Increments alarm counter by 1
    write_int(13, currentAlarm); //Sends alarm number

    currentTime = millis(); //reading of current time
    randomPeriod = random(minPeriod, maxPeriod); //randomized waiting time untill first alarm is triggered
    limitTime = currentTime + randomPeriod + alarmPeriod; //time where alarm task is failed due to no action
    delay(randomPeriod);
    rVal = random(1, 4);
    //Serial.println(rVal);
    switch (rVal) {
      case 1: //Alarm scenario 1
        write_int(14, rVal); //Sends ID of the triggeder alarm
        startTime = millis();

        writeToSlave(rVal + alarmSystemMod);

        while (currentTime < limitTime) {
          bVal1 = buttonCheck(bVal1, bPin1);
          bVal2 = buttonCheck(bVal2, bPin2);
          bVal3 = buttonCheck(bVal3, bPin3);
          if (bVal1 == HIGH) {
            write_int(15, 1); //Sends result of alarm test being passed
            break;
          }
          if (bVal2 == HIGH || bVal3 == HIGH) {
            write_int(15, 0); //Sends result of alarm test being failed
            break;
          }
          currentTime = millis();
          if (currentTime >= limitTime) {
            write_int(15, 2); //Sends result of alarm test being failed due to inactivity
          }
        }
        break;
      case 2: //Alarm scenario 2
        write_int(14, rVal); //Sends ID of the triggeder alarm
        //Serial.println("Alarm 2 triggered");
        startTime = millis();

        writeToSlave(rVal + alarmSystemMod);

        while (currentTime < limitTime) {
          bVal1 = buttonCheck(bVal1, bPin1);
          bVal2 = buttonCheck(bVal2, bPin2);
          bVal3 = buttonCheck(bVal3, bPin3);
          if (bVal2 == HIGH) {
            write_int(15, 1); //Sends result of alarm test being passed
            break;
          }
          if (bVal1 == HIGH || bVal3 == HIGH) {
            write_int(15, 0); //Sends result of alarm test being failed
            break;
          }
          currentTime = millis();
          if (currentTime >= limitTime) {
            write_int(15, 2); //Sends result of alarm test being failed due to inactivity
          }
        }
        break;
      case 3: //Alarm scenario 3
        write_int(14, rVal); //Sends ID of the triggeder alarm
        //Serial.println("Alarm 3 triggered");
        startTime = millis();

        writeToSlave(rVal + alarmSystemMod);

        while (currentTime < limitTime) {
          bVal1 = buttonCheck(bVal1, bPin1);
          bVal2 = buttonCheck(bVal2, bPin2);
          bVal3 = buttonCheck(bVal3, bPin3);
          if (bVal3 == HIGH) {
            write_int(15, 1); //Sends result of alarm test being passed
            break;
          }
          if (bVal1 == HIGH || bVal2 == HIGH) {
            write_int(15, 0); //Sends result of alarm test being failed
            break;
          }
          currentTime = millis();
          if (currentTime >= limitTime) {
            write_int(15, 2); //Sends result of alarm test being failed due to inactivity
          }
        }
        break;
      default:
        write_int(15, rVal); //Sends that alarm number was invalid
        //Serial.println("error in alarm cases");
        break;
    }
    active = digitalRead(activePin); //Checks if device is still active and should continue looping
    writeToSlave(0);
  }

  //Serial.println("Device disarmed");
  write_int(12, 0); //Sends alarm=disarmed
  delay(3000);
  if (active == LOW) {
    currentAlarm = 0;
  }
}

bool buttonCheck(bool bValX, int buttonPinX) {
  bool newBValX = LOW;
  newBValX = digitalRead(buttonPinX);
  if (newBValX != bValX) {
    bValX = HIGH;
  }
  if (newBValX == bValX) {
    bValX = LOW;
  }
  return newBValX;
}


void writeToSlave(byte alarmNumber) {
  Wire.beginTransmission(1); ///transmit   to device #1
  Wire.write(alarmNumber);
  Wire.endTransmission();
}
