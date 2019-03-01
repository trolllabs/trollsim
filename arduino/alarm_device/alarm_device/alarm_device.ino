bool active = 0; //0 or 1, decides if it will trigger alarms or not
int alarms = 0; //number of alarms that will be triggered in total before device becomes inactive again
int minPeriod = 0; // input in seconds here minimum time period between alarms
int maxPeriod = 10; // input in seconds here maximum time period between alarms

long currentTime = 0; //var to store current time using millis(), to be updated throughout
long alarmPeriod = 20000; //var in milliseconds that decides how long the alarm should sound before alarm task is failed due to no action.

int activePin = 1; //digital pin triggering device on/off.
int bPin1 = 2; //pin number 1st button
int bPin2 = 3; //pin number 2nd button
int bPin3 = 4; //pin number 3rd button
bool bVal1 = LOW; //value read from button 1
bool bVal2 = LOW; //value read from button 2
bool bVal3 = LOW; //value read from button 3
int ledPin1 = 5;  //pin number 1st led
int ledPin2 = 6;  //pin number 2nd led
int ledPin3 = 7;  //pin number 3rd led
int speakerPin = 8; //pin number speaker

void setup() {
  // put your setup code here, to run once:

  pinMode(activePin, INPUT);
  pinMode(bPin1, INPUT);
  pinMode(bPin2, INPUT);
  pinMode(bPin3, INPUT);
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
  pinMode(ledPin3, OUTPUT);
  pinMode(speakerPin, OUTPUT); //should this be defined as output, or will this interfere with the tone() function?

  Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
  active = digitalRead(activePin); //Read value of on-switch
  while (active == HIGH) {        //Condition to execute when device is on/armed.
    Serial.print("Device armed");
    currentTime = millis(); //reading of current time

    long randomPeriod = random(minPeriod, maxPeriod); //randomized waiting time untill first alarm is triggered

    long limitTime = currentTime + randomPeriod + alarmPeriod; //time where alarm task is failed due to no action
    int randomAlarm = random(1, 3);
    delay(1000 * randomPeriod);

    switch (randomAlarm) {
      case 1: //Alarm scenario 1
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

          Serial.print("Alarm 1 triggered");
          audioAlarm(1); //play alarm sound 1
          digitalWrite(ledPin1, HIGH); //light led1
          currentTime == millis();
        }
        if (currentTime >= limitTime) {
          Serial.println("Time ran out, task failed.");
        }


        Serial.println(currentTime);
        Serial.print(bVal1);
        Serial.print(bVal2);
        Serial.print(bVal3);
        digitalWrite(ledPin1, LOW); //darken led1

        break;
      case 2: //Alarm scenario 2
        while (bVal1 == LOW && bVal2 == LOW && bVal3 == LOW && currentTime < limitTime) {
          Serial.print("Alarm 2 triggered");
          audioAlarm(2); //play alarm sound 2
          digitalWrite(ledPin2, HIGH); //light led2

          bVal1 = buttonCheck(bVal1, bPin1);
          bVal2 = buttonCheck(bVal2, bPin2);
          bVal3 = buttonCheck(bVal3, bPin3);
          currentTime == millis();
        }
        Serial.println(currentTime);
        Serial.print(bVal1);
        Serial.print(bVal2);
        Serial.print(bVal3);
        digitalWrite(ledPin2, LOW); //darken led2

        if (bVal1 == HIGH) {
          Serial.println("Button 1 was pushed, task failed.");
        }
        if (bVal2 == HIGH) {
          Serial.println("Button 2 was pushed, task passed.");
        }
        if (bVal3 == HIGH) {
          Serial.println("Button 3 was pushed, task failed.");
        }
        if (currentTime >= limitTime) {
          Serial.println("Time ran out, task failed.");
        }
        break;
      case 3: //Alarm scenario 3
        while (bVal1 == LOW && bVal2 == LOW && bVal3 == LOW && currentTime < limitTime) {
          Serial.print("Alarm 3 triggered");
          audioAlarm(3); //play alarm sound 3
          digitalWrite(ledPin3, HIGH); //light led3

          bVal1 = buttonCheck(bVal1, bPin1);
          bVal2 = buttonCheck(bVal2, bPin2);
          bVal3 = buttonCheck(bVal3, bPin3);
          currentTime == millis();
        }
        Serial.println(currentTime);
        Serial.print(bVal1);
        Serial.print(bVal2);
        Serial.print(bVal3);
        digitalWrite(ledPin3, LOW); //darken led3

        if (bVal1 == HIGH) {
          Serial.println("Button 1 was pushed, task failed.");
        }
        if (bVal2 == HIGH) {
          Serial.println("Button 2 was pushed, task failed.");
        }
        if (bVal3 == HIGH) {
          Serial.println("Button 3 was pushed, task passed.");
        }
        if (currentTime >= limitTime) {
          Serial.println("Time ran out, task failed.");
        }
        break;
      default:
        Serial.println("error in alarm cases");
        break;
    }


    active = digitalRead(activePin); //Checks if device is still active and should continue looping
  }
  Serial.print("Device disarmed");
  delay(3000);

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

void audioAlarm(int alarmNumber) {
  if (alarmNumber == 1) {
    //Alarm 1
    tone(speakerPin, 440, 200);
    delay(1000);
    tone(speakerPin, 200, 200);
    delay(1000);
    tone(speakerPin, 100, 200);
    delay(1000);
  }
  if (alarmNumber == 2) {
    //Alarm 2
    tone(speakerPin, 100, 50);
    delay(1000);
    tone(speakerPin, 200, 50);
    delay(1000);
    tone(speakerPin, 440, 50);
  }
  if (alarmNumber == 3) {
    //Alarm 3
    tone(speakerPin, 100, 50);
    delay(200);
    tone(speakerPin, 200, 50);
    delay(200);
    tone(speakerPin, 440, 50);
  }
}
