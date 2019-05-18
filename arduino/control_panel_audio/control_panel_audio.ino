int bPin1 = 3;
int bPin2 = 5;
int bPin3 = 7;


bool bVal1 = LOW; //value read from button 1
bool bVal2 = LOW; //value read from button 2
bool bVal3 = LOW; //value read from button 3


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
  pinMode(bPin1, INPUT);
  pinMode(bPin2, INPUT);
  pinMode(bPin3, INPUT);

  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  bVal1 = buttonCheck(bVal1, bPin1);
  if (bVal1 == HIGH) {
    Serial.println("Button 1 pushed");
  }
  bVal2 = buttonCheck(bVal2, bPin2);
  if (bVal2 == HIGH) {
    Serial.println("Button 2 pushed");
  }
  bVal3 = buttonCheck(bVal3, bPin3);
  if (bVal3 == HIGH) {
    Serial.println("Button 3 pushed");
  }
  delay(100);
}
