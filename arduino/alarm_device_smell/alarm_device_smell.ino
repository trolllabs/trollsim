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
int ledPin1 = 5;  //pin number 1st led
int ledPin2 = 6;  //pin number 2nd led
int ledPin3 = 7;  //pin number 3rd led
//int speakerPin = 8; //pin number speaker
int activePin = 9; //digital pin triggering device on/off.
int smellPin = 10; //pin for servo controlling smell device

bool active = 0; //0 or 1, decides if it will trigger alarms or not

int alarms = 10; //number of alarms that will be triggered in total before device becomes inactive again
int currentAlarm = 0; //counter counting how many alarms have happened
int minPeriod = 1000; // input in seconds here minimum time period between alarms
int maxPeriod = 4000; // input in seconds here maximum time period between
int rVal=0;

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
  Serial.begin(9600);
  randomSeed(analogRead(0));

}

void loop() {
  // put your main code here, to run repeatedly:
  active = digitalRead(activePin); //Read value of on-switch
  if (active == HIGH && currentAlarm < alarms) {
    Serial.println("Device armed");
  }

  while (active == HIGH && currentAlarm < alarms) {      //Condition to execute when device is on/armed.
    currentTime = millis(); //reading of current time
    randomPeriod = random(minPeriod, maxPeriod); //randomized waiting time untill first alarm is triggered
    limitTime = currentTime + randomPeriod + alarmPeriod; //time where alarm task is failed due to no action
    delay(randomPeriod);
    rVal=random(1,4);
    Serial.println(rVal);
    switch (rVal){
      case 1: //Alarm scenario 1
        Serial.println("Alarm 1 triggered");
        startTime = millis();
        digitalWrite(ledPin1, HIGH); //light led1
        smellAlarm(1); //trigger smell alarm 1
        while (currentTime < limitTime) {
          bVal1 = buttonCheck(bVal1, bPin1);
          bVal2 = buttonCheck(bVal2, bPin2);
          bVal3 = buttonCheck(bVal3, bPin3);
          if (bVal1 == HIGH) {
            Serial.println("Correct button - PASS");
            break;
          }
          if (bVal2 == HIGH || bVal3 == HIGH) {
            Serial.println("Wrong button - FAIL");
            break;
          }
          currentTime = millis();
          if (currentTime >= limitTime) {
            Serial.println("Time ran out, task failed.");
          }
        }
        digitalWrite(ledPin1, LOW); //darken led1
        break;
      case 2: //Alarm scenario 1
        Serial.println("Alarm 2 triggered");
        startTime = millis();
        digitalWrite(ledPin2, HIGH); //light led2
        smellAlarm(2); //trigger smell alarm 2
        while (currentTime < limitTime) {
          bVal1 = buttonCheck(bVal1, bPin1);
          bVal2 = buttonCheck(bVal2, bPin2);
          bVal3 = buttonCheck(bVal3, bPin3);
          if (bVal2 == HIGH) {
            Serial.println("Correct button - PASS");
            break;
          }
          if (bVal1 == HIGH || bVal3 == HIGH) {
            Serial.println("Wrong button - FAIL");
            break;
          }
          currentTime = millis();
          if (currentTime >= limitTime) {
            Serial.println("Time ran out, task failed.");
          }
        }
        digitalWrite(ledPin2, LOW); //darken led2
        break;
      case 3: //Alarm scenario 3
        Serial.println("Alarm 3 triggered");
        startTime = millis();
        digitalWrite(ledPin3, HIGH); //light led3
        smellAlarm(3); //trigger smell alarm 3
        while (currentTime < limitTime) {
          bVal1 = buttonCheck(bVal1, bPin1);
          bVal2 = buttonCheck(bVal2, bPin2);
          bVal3 = buttonCheck(bVal3, bPin3);
          if (bVal3 == HIGH) {
            Serial.println("Correct button - PASS");
            break;
          }
          if (bVal1 == HIGH || bVal2 == HIGH) {
            Serial.println("Wrong button - FAIL");
            break;
          }
          currentTime = millis();
          if (currentTime >= limitTime) {
            Serial.println("Time ran out, task failed.");
          }
        }
        digitalWrite(ledPin3, LOW); //darken led2
        break;
      default:
        Serial.println("error in alarm cases");
        break;
    }


    ++currentAlarm; //Increments alarm counter by 1
    active = digitalRead(activePin); //Checks if device is still active and should continue looping
    smellAlarm(0); //Put smell cartridge in neutral position
  }

  Serial.println("Device disarmed");
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
