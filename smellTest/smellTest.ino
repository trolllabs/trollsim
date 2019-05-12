
#include <Servo.h>
#define in1 11 //first pin for fan control
#define in2 12 // second pin for fan controol
Servo myservo;  // create servo object to control a servo
int val = 0; //value to be randomized

void setup() {
  myservo.attach(10);  // attaches the servo on pin 10 to the servo object
  Serial.begin(9600); //begin serial communication
}

void loop() {
  //val = random(1, 4);
  smellAlarm(1);
  delay(4000);
  //smellAlarm(0);// returns servo to initial position
  //delay(2000);
  smellAlarm(2);
  delay(4000);
  //smellAlarm(0);// returns servo to initial position
  //delay(2000);
  smellAlarm(3);
  delay(4000);
  smellAlarm(0);// returns servo to initial position
  Serial.println("The device is now back in 0 position");
  delay(4000);


}

void smellAlarm(int randomAlarm) {
  switch (randomAlarm) {
    case 1: //Alarm scenario 1
      Serial.println("Alarm 1 triggered");
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      myservo.write(60);
      break;
    case 2: //Alarm secnario 2
      Serial.println("Alarm 2 triggered");
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      myservo.write(120);
      break;
    case 3: //ALarm scenario 3
      Serial.println("Alarm 3 triggered");
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



