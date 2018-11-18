int motor1=3;
int motor2=5;
int motor3=9;
int motor4=11;

int angle1=0;
int angle2=0;
int axisVal1=0;
int axisVal2=0;
int angleInput=0;

void setup() {
  // put your setup code here, to run once:

  Serial.begin(115200);

  pinMode(motor1, OUTPUT);
  pinMode(motor2, OUTPUT);
  pinMode(motor3, OUTPUT);
  pinMode(motor4, OUTPUT);

}

int readInteger() {
  byte int_buf[4];
  Serial.readBytes(int_buf, 4);
  int res = int_buf[0] << 24 | int_buf[1] << 16 | int_buf[2] << 8 | int_buf[3];
  return res;
}


void loop() {
  // put your main code here, to run repeatedly:

  if (Serial.available() > 0) {
    angleInput= readInteger();
    Serial.print("angleInput: ");
    Serial.print(angleInput);
    if(angleInput>=0 && angleInput<181){
      angle1=abs(angleInput-90);
      Serial.print(", angle 1:");
      Serial.print(angle1); 
      Serial.print(", angle 2: ");
      Serial.println(angle2);
    }
    else if(angleInput>180 && angleInput<361){
      angle2=abs(angleInput-270);
      Serial.print(", angle 1:");
      Serial.print(angle1); 
      Serial.print(", angle 2:");
      Serial.println(angle2); 
    }
    else{
      angle1=0;
      angle2=0;
    }
  }

  axisVal1=map(angle1,0, 90, 0, 255);
  axisVal2=map(angle2,0, 90, 0, 255);  

    analogWrite(motor1, axisVal2);
    analogWrite(motor2, axisVal1);
    analogWrite(motor3, axisVal2);
    analogWrite(motor4, axisVal1);

  //delay(10);


}
