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



int bPin1 = 3;
int bPin2 = 5;
int bPin3 = 7;


bool bVal1 = LOW; //value read from button 1
bool bVal2 = LOW; //value read from button 2
bool bVal3 = LOW; //value read from button 3

unsigned long currentTime = 0;
unsigned long timeOfPrint = 0;
unsigned long timeSincePrint = 0;


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
  currentTime = millis();
  timeSincePrint = currentTime - timeOfPrint;
  bVal1 = buttonCheck(bVal1, bPin1);
  if (bVal1 == HIGH && timeSincePrint > 500) {
    write_int(20,1);
    timeOfPrint = millis();
  }
  bVal2 = buttonCheck(bVal2, bPin2);
  if (bVal2 == HIGH && timeSincePrint > 500) {
       write_int(20,1);
    timeOfPrint = millis();
  }
  bVal3 = buttonCheck(bVal3, bPin3);
  if (bVal3 == HIGH && timeSincePrint > 500) {
       write_int(20,1);
    timeOfPrint = millis();
  }
}
