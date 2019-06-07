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

/*******************************************************************
  Variables for the experimenter to tweak alarm periods and haptic amplitude.
********************************************************************/
unsigned long  minPeriod = 60000; // input in milliseconds here minimum time period between alarms
unsigned long  maxPeriod = 70000; // input in milliseconds here maximum time period between alarms
unsigned long alarmPeriod = 10000; //var in milliseconds that decides time alarm sounds before it fails and stops. Max 16 bits (65535 because of wire.transmit constraints)

int scen1Alarms = 2; //value deciding number of alarms in scenario 1
int scen2Alarms = 3; //value deciding number of alarms in scenario 2
int scen3Alarms = 5; //value deciding number of alarms in scenario 3
//*******************************************************************

/*******************************************************************
  PIN DEFINITIONS
 ********************************************************************/
int bPin = 3; //pin number for button
int activePin = 7; //digital pin triggering device on/off.
int alarmTypePin = 8; //digital pin triggering which alarm system is active
//******************************************************************

/*******************************************************************
  RANDOM VARIABLES
 ********************************************************************/
byte rVal = 0; //variable that is randomized to decide which alarm is triggered
bool bVal = LOW; //value read from button 2
int knobValue = 0; //variable that holds which scenario (1-3) is active
int scenarioValue = 0;
bool active = 0; //0 or 1, decides if it will trigger alarms or not

int alarms = 1; //value to hold number of alarms that will be triggered in total before device becomes inactive again
int currentAlarm = 0; //counter counting how many alarms have happened
unsigned long currentTime = 0; //var to store current time using millis(), to be updated throughout
unsigned long startTime = 0; //time when alarm starts
unsigned long responseTime = 0; //response time to react to alarm
unsigned long randomPeriod = 0; //Variable to hold ranomized waiting time untill alarm is triggered
unsigned long limitTime = 0; //Variable to hold time limit where alarm task is failed due to no action

int alarmType = 0; //Var to hold which alarm system is active (0 for system A (light, sound, 1 for system B (light, sound, haptic)
int alarmSystemMod = 0; //Variable adjusting rVal in line with what system is active
int disarmedMessageState = LOW;

//*******************************************************************
void alarmTypeCheck() {
  alarmType = digitalRead(alarmTypePin); //Real value of alarmTypePin, deciding which system should be used.
  
  if (alarmType == 0) {
    alarmSystemMod = 0;
    write_int(12, 0); //Sends alarm type A
  }
  if (alarmType == 1) {
    alarmSystemMod = 3;
    write_int(12, 1); //Sends alarm type B
  }
}
void scenarioCheck() {
  int sensorValue = analogRead(A3);
  if (sensorValue >= 0 && sensorValue < 100) {
    alarms = scen1Alarms;
    write_int(13, 1); //Sends packet informing that scenario 1 is active
  }
  if (sensorValue >= 100 && sensorValue < 923) {
    alarms = scen2Alarms;
    write_int(13, 2); //Sends packet informing that scenario 2 is active
  }
  if (sensorValue >= 924) {
    alarms = scen3Alarms;
    write_int(13, 3); //Sends packet informing that scenario 3 is active
  }
}

void writeToSlave(byte alarmNumber) {
  Wire.beginTransmission(1); ///transmit   to device #1
  Wire.write(alarmNumber);
  Wire.endTransmission();

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

void setup() {
  // put your setup code here, to run once:

  pinMode(activePin, INPUT);
  pinMode(bPin, INPUT);
  Serial.begin(115200);

  Wire.begin(); //join i2c bus
  randomSeed(analogRead(0));

}

void loop() {
  //  Writing float:
  //  write_float(0xAA, 123.4141);
  //  Writing integer:
  //  write_int(0xAA, 5234);

  active = digitalRead(activePin); //Read value of on-switch

  if (active == HIGH && currentAlarm < alarms) {
    write_int(11, 1); //Sends alarm=armed
    disarmedMessageState = LOW; //Resets state variable allowing device to report when disarmed
    alarmTypeCheck(); //Checks which alarm system is selected, sets alarmSystemMod-variable and sends packet informing of system A or B
    scenarioCheck(); //Checks position of scenario switch, sets correct nuber of alarms and sends packet informing of scenario 1, 2 or 3
  }
  while (active == HIGH && currentAlarm < alarms) {      //Condition to execute when device is on/armed.
    ++currentAlarm; //Increments alarm counter by 1
    currentTime = millis(); //reading of current time
    randomPeriod = random(minPeriod, maxPeriod); //randomized waiting time untill first alarm is triggered
    limitTime = currentTime + randomPeriod + alarmPeriod; //time where alarm task is failed due to no action
    delay(randomPeriod);
    active = digitalRead(activePin);
    if (active == HIGH) {
      rVal = random(1, 4);
      write_int(15, rVal); //Sends ID of the triggeder alarm
      //write_int(14, currentAlarm); //Sends alarm number
      startTime = millis();
      writeToSlave(rVal + alarmSystemMod);
    }
    while (currentTime < limitTime && active == HIGH) {
      bVal = buttonCheck(bVal, bPin);
      currentTime = millis();
      active = digitalRead(activePin);
      if (bVal == HIGH) {
        write_int(16, 1); //Send packet reporting button was pushed.
        writeToSlave(0); //Send signal to slave stopping alarms.
        break;
      }
      else if (currentTime >= limitTime && bVal == LOW) {
        write_int(15, 2); //Sends result of alarm test being failed due to inactivity
        writeToSlave(0);
      }
      if (active == LOW) {
        writeToSlave(0);
      }
    }
    active = digitalRead(activePin); //Checks if device is still active and should continue looping
  }
  if (disarmedMessageState == LOW) {
    write_int(11, 0); //Sends packet informing that alarm device is disarmed.
    disarmedMessageState = HIGH;
  }
  delay(300);
  if (active == LOW) {
    currentAlarm = 0;
  }

}
