int motor1=3;
int motor2=5;
int motor3=9;
int motor4=11;

int angle1=0;
int axisVal1=0;

void setup() {
  // put your setup code here, to run once:

  Serial.begin(9600);

  pinMode(motor1, OUTPUT);
  pinMode(motor2, OUTPUT);
  pinMode(motor3, OUTPUT);
  pinMode(motor4, OUTPUT);

}




void loop() {
  // put your main code here, to run repeatedly:

  if (Serial.available() > 0) {
    angle1= Serial.read();
  }

  axisVal1=map(abs(angle1),0, 180, 0, 255);

    analogWrite(motor1, axisVal1);
    analogWrite(motor2, axisVal1);
    analogWrite(motor3, axisVal1);
    analogWrite(motor4, axisVal1);

  delay(1000);


}
