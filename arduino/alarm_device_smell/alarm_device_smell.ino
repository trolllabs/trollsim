#include <Servo.h>
#define in1 11 //first pin for fan control
#define in2 12 // second pin for fan controol
Servo myservo;  // create servo object to control a servo
int val = 0; //value to be randomized

bool active = 0; //0 or 1, decides if it will trigger alarms or not
int alarms = 10; //number of alarms that will be triggered in total before device becomes inactive again
int currentAlarm = 0; //counter counting how many alarms have happened
int minPeriod = 0; // input in seconds here minimum time period between alarms
int maxPeriod = 10; // input in seconds here maximum time period between alarms
int randomAlarm = 0;

long currentTime = 0; //var to store current time using millis(), to be updated throughout
long startTime = 0; //time when alarm starts
long responseTime = 0; //response time to react to alarm
long alarmPeriod = 20000; //var in milliseconds that decides how long the alarm should sound before alarm task is failed due to no action.

int activePin = 9; //digital pin triggering device on/off.
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
int smellPin = 10; //pin for servo controlling smell device

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

}

void loop() {
  // put your main code here, to run repeatedly:
  active = digitalRead(activePin); //Read value of on-switch
  if (active == HIGH) {
    Serial.println("Device armed");
  }
  while (active == HIGH && currentAlarm < alarms) {      //Condition to execute when device is on/armed.
    currentTime = millis(); //reading of current time

    long randomPeriod = random(minPeriod, maxPeriod); //randomized waiting time untill first alarm is triggered

    long limitTime = currentTime + randomPeriod + alarmPeriod; //time where alarm task is failed due to no action
    randomAlarm = random(1, 4);
    delay(1000 * randomPeriod);

    switch (randomAlarm) {
      case 1: //Alarm scenario 1
        Serial.println("Alarm 1 triggered");
        startTime = millis();
        digitalWrite(ledPin1, HIGH); //light led1
        //audioAlarm(1); //play alarm sound 1
        smellAlarm(0); //trigger smell alarm 1

        while (currentTime < limitTime) {
          bVal1 = buttonCheck(bVal1, bPin1);
          bVal2 = buttonCheck(bVal2, bPin2);
          bVal3 = buttonCheck(bVal3, bPin3);

          if (bVal1 == HIGH) {
            Serial.println("Button 1 was pushed, task passed.");
            break;
          }
          if (bVal2 == HIGH) {
            Serial.println("Button 2 was pushed, task failed.");
            break;
          }
          if (bVal3 == HIGH) {
            Serial.println("Button 3 was pushed, task failed.");
            break;
          }
          responseTime = millis() - startTime;
          currentTime == millis();
        }
        if (currentTime >= limitTime) {
          Serial.println("Time ran out, task failed.");
        }
        Serial.print("Response time: ");
        Serial.println(responseTime);
        Serial.print("Button values: ");
        Serial.print(bVal1);
        Serial.print(", ");
        Serial.print(bVal2);
        Serial.print(", ");
        Serial.println(bVal3);
        digitalWrite(ledPin1, LOW); //darken led1
        break;
      case 2: //Alarm scenario 2
        Serial.println("Alarm 2 triggered");
        startTime = millis();
        digitalWrite(ledPin2, HIGH); //light led2
        //audioAlarm(2); //play alarm sound 2
        smellAlarm(2); //trigger smell alarm 2
        while (currentTime < limitTime) {
          bVal1 = buttonCheck(bVal1, bPin1);
          bVal2 = buttonCheck(bVal2, bPin2);
          bVal3 = buttonCheck(bVal3, bPin3);

          if (bVal1 == HIGH) {
            Serial.println("Button 1 was pushed, task failed.");
            break;
          }
          if (bVal2 == HIGH) {
            Serial.println("Button 2 was pushed, task passed.");
            break;
          }
          if (bVal3 == HIGH) {
            Serial.println("Button 3 was pushed, task failed.");
            break;
          }
          responseTime = millis() - startTime;
          currentTime == millis();
        }
        if (currentTime >= limitTime) {
          Serial.println("Time ran out, task failed.");
        }
        Serial.print("Time: ");
        Serial.println(responseTime);
        Serial.print("Button values: ");
        Serial.print(bVal1);
        Serial.print(", ");
        Serial.print(bVal2);
        Serial.print(", ");
        Serial.println(bVal3);
        digitalWrite(ledPin2, LOW); //darken led2
        break;
      case 3: //Alarm scenario 3
        Serial.println("Alarm 3 triggered");
        startTime = millis();
        digitalWrite(ledPin3, HIGH); //light led3
        //audioAlarm(3); //play alarm sound 3
        smellAlarm(3); //trigger smell alarm 3

        while (currentTime < limitTime) {
          bVal1 = buttonCheck(bVal1, bPin1);
          bVal2 = buttonCheck(bVal2, bPin2);
          bVal3 = buttonCheck(bVal3, bPin3);

          if (bVal1 == HIGH) {
            Serial.println("Button 1 was pushed, task failed.");
            break;
          }
          if (bVal2 == HIGH) {
            Serial.println("Button 2 was pushed, task failed.");
            break;
          }
          if (bVal3 == HIGH) {
            Serial.println("Button 3 was pushed, task passed.");
            break;
          }
          currentTime == millis();
          responseTime = millis() - startTime;
        }
        if (currentTime >= limitTime) {
          Serial.println("Time ran out, task failed.");
        }
        Serial.print("Time: ");
        Serial.println(responseTime);
        Serial.print("Button values: ");
        Serial.print(bVal1);
        Serial.print(", ");
        Serial.print(bVal2);
        Serial.print(", ");
        Serial.println(bVal3);
        digitalWrite(ledPin3, LOW); //darken led3
        break;
      default:
        Serial.println("error in alarm cases");
        break;
    }


    active = digitalRead(activePin); //Checks if device is still active and should continue looping
    currentAlarm = currentAlarm + 1; //Increments alarm counter by 1
    smellAlarm(1); //trigger smell alarm 0
    Serial.print("This was alarm number: ");
    Serial.println(currentAlarm);
    Serial.println("---------------------------");
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

void smellAlarm(int randomAlarm) {
  switch (randomAlarm) {
    case 1: //Alarm scenario 1
      Serial.println("smellAlarm 1 triggered");
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      myservo.write(60);
      break;
    case 2: //Alarm secnario 2
      Serial.println("smellAlarm 2 triggered");
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      myservo.write(120);
      break;
    case 3: //ALarm scenario 3
      Serial.println("smellAlarm 3 triggered");
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      myservo.write(180);
      break;
    default:
      Serial.println("Returned to 0");
      digitalWrite(in1, LOW);
      digitalWrite(in2, HIGH);
      myservo.write(0);
      break;
  }
}


