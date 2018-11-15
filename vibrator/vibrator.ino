int motor1=3;
int motor2=5;
int motor3=9;
int motor4=11;

void setup() {
  // put your setup code here, to run once:

  pinMode(motor1, OUTPUT);
  pinMode(motor2, OUTPUT);
  pinMode(motor3, OUTPUT);
  pinMode(motor4, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:

  analogWrite(motor1, 255);
  analogWrite(motor2, 0);
  analogWrite(motor3, 255);
  analogWrite(motor4, 0);
  delay(1000);
  analogWrite(motor1, 0);
  analogWrite(motor2, 255);
  analogWrite(motor3, 0);
  analogWrite(motor4, 255);
  delay(1000);
  
  
}
