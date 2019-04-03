

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

#include <Servo.h>
#define in1 11 //first pin for fan control
#define in2 12 // second pin for fan controol
Servo myservo;  // create servo object to control a servo

int bPin1 = 2; //pin number 1st button
int bPin2 = 3; //pin number 2nd button
int bPin3 = 4; //pin number 3rd button
bool bVal1 = LOW; //value read from button 1
bool bVal2 = LOW; //value read from button 2
bool bVal3 = LOW; //value read from button 3
int ledPin1 = 13;  //pin number 1st led (disabled, set to pin 5 to activate)
int ledPin2 = 13;  //pin number 2nd led (disabled, set to pin 6 to activate)
int ledPin3 = 13;  //pin number 3rd led (disabled, set to pin 7 to activate) 
//int speakerPin = 9; //pin number speaker
int activePin = 8; //digital pin triggering device on/off.
int smellPin = 10; //pin for servo controlling smell device

bool active = 0; //0 or 1, decides if it will trigger alarms or not

int alarms = 5; //number of alarms that will be triggered in total before device becomes inactive again
int currentAlarm = 0; //counter counting how many alarms have happened
int minPeriod = 30000; // input in seconds here minimum time period between alarms
int maxPeriod = 90000; // input in seconds here maximum time period between
int rVal = 0;

unsigned long currentTime = 0; //var to store current time using millis(), to be updated throughout
unsigned long startTime = 0; //time when alarm starts
unsigned long responseTime = 0; //response time to react to alarm
unsigned long alarmPeriod = 5000; //var in milliseconds that decides how long the alarm should sound before alarm task is failed due to no action.
unsigned long randomPeriod = 0; //Variable to hold ranomized waiting time untill alarm is triggered
unsigned long limitTime = 0; //Variable to hold time limit where alarm task is failed due to no action


void setup() {
  // put your setup code here, to run once:

  pinMode(activePin, INPUT);
  pinMode(bPin1, INPUT);
  pinMode(bPin2, INPUT);
  pinMode(bPin3, INPUT);
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
  pinMode(ledPin3, OUTPUT);
  myservo.attach(10);  // attaches the servo on pin 10 to the servo object
  Serial.begin(115200);
  randomSeed(analogRead(0));

}

void loop() {
  // put your main code here, to run repeatedly:
  //  Writing float:
  //  write_float(0xAA, 123.4141);

  //  Writing integer:
  //  write_int(0xAA, 5234);


  active = digitalRead(activePin); //Read value of on-switch
  if (active == HIGH && currentAlarm < alarms) {
    write_int(11, 1); //informs of alarm type being smell
    write_int(12, 1); //Sends alarm=armed

  }

  while (active == HIGH && currentAlarm < alarms) {      //Condition to execute when device is on/armed.
    ++currentAlarm; //Increments alarm counter by 1
    write_int(13, currentAlarm); //Sends alarm number

    currentTime = millis(); //reading of current time
    randomPeriod = random(minPeriod, maxPeriod); //randomized waiting time untill first alarm is triggered
    limitTime = currentTime + randomPeriod + alarmPeriod; //time where alarm task is failed due to no action
    delay(randomPeriod);
    rVal = random(1, 4);
    switch (rVal) {
      case 1: //Alarm scenario 1
        write_int(14, rVal); //Sends ID of the triggeder alarm
        startTime = millis();
        digitalWrite(ledPin1, HIGH); //light led1
        smellAlarm(1); //trigger smell alarm 1
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
        digitalWrite(ledPin1, LOW); //darken led1
        break;
      case 2: //Alarm scenario 1
        write_int(14, rVal); //Sends ID of the triggeder alarm
        //Serial.println("Alarm 2 triggered");
        startTime = millis();
        digitalWrite(ledPin2, HIGH); //light led2
        smellAlarm(2); //trigger smell alarm 2
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
        digitalWrite(ledPin2, LOW); //darken led2
        break;
      case 3: //Alarm scenario 3
        write_int(14, rVal); //Sends ID of the triggeder alarm
        //Serial.println("Alarm 3 triggered");
        startTime = millis();
        digitalWrite(ledPin3, HIGH); //light led3
        smellAlarm(3); //trigger smell alarm 3
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
        digitalWrite(ledPin3, LOW); //darken led2
        break;
      default:
        write_int(15, rVal); //Sends that alarm number was invalid
        //Serial.println("error in alarm cases");
        break;
    }
    active = digitalRead(activePin); //Checks if device is still active and should continue looping
    smellAlarm(0); //Put smell cartridge in neutral position
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

void smellAlarm(int smellAlarmNumber) {
  switch (smellAlarmNumber) {
    case 1: //Alarm scenario 1
      //Serial.println("smellAlarm 1 triggered");
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      myservo.write(1);
      break;
    case 2: //Alarm secnario 2
      //Serial.println("smellAlarm 2 triggered");
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      myservo.write(120);
      break;
    case 3: //ALarm scenario 3
      //Serial.println("smellAlarm 3 triggered");
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      myservo.write(180);
      break;
    default:
      //Serial.println("Returned to 0");
      digitalWrite(in1, LOW);
      digitalWrite(in2, HIGH);
      myservo.write(60);
      break;
  }
}
