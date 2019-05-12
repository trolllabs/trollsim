

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

#include <Wire.h>

int alarmNumber = 0; //variable to hold alarm number

int ledPin1 = 5;  //pin number 1st led
int ledPin2 = 6;  //pin number 2nd led
int ledPin3 = 7;  //pin number 3rd led

#define enA 10 //enable pin for haptic feedback
#define in1 11 //in1 pin for haptic feedback
#define in2 12 //in2 pin for haptic feedback


int voltageValue = 0; //variable to hold haptic motor voltage value
int pwmOutput = 0;  //variable to hold pwmOutput value to haptic motor

/*******************************************************************
  Variables for the experimenter to tweak alarm periods and haptic amplitude.
********************************************************************/

// Alarm 1 settings:
int A1OnPeriod = 1000;   //Period in [ms] alarm 1 is activated every loop
int A1OffPeriod = 2000; // Period in [ms] alarm 1 is off every loop
int A1Amplitude = 2;  //Amplitude in [V] of alarm 1's haptic feedback. Input valid from 0-9V.

// Alarm 2 settings:
int A2OnPeriod = 2000;   //Period in [ms] alarm 2 is activated every loop
int A2OffPeriod = 1000;  // Period in [ms] alarm 2 is off every loop
int A2Amplitude = 3;  //Amplitude in [V] of alarm 1's haptic feedback. Input valid from 0-9V.

// Alarm 3 settings:
int A3OnPeriod =  1500;  //Period in [ms] alarm 3 is activated every loop
int A3OffPeriod = 1500;  // Period in [ms] alarm 3 is off every loop
int A3Amplitude = 4;  //Amplitude in [V] of alarm 1's haptic feedback. Input valid from 0-9V.

// Audio alarm frequency and amplitude must be tweaked in socketaudio.py

//*******************************************************************

void setup() {
  Wire.begin(1);                // join i2c bus with address #1
  Wire.onReceive(receiveEvent); // register event
  Serial.begin(9600);           // start serial for output
  pinMode(ledPin1, OUTPUT); //set pinmode on LED-pin 1
  pinMode(ledPin2, OUTPUT); //set pinmode on LED-pin 2
  pinMode(ledPin3, OUTPUT); //set pinmode on LED-pin 3

  pinMode(enA, OUTPUT); //set pinmode on enable pin for haptic feedback
  pinMode(in1, OUTPUT); //set pinmode on in1 pin for haptic feedback
  pinMode(in2, OUTPUT); //set pinmode on in2 pin for haptic feedback

  digitalWrite(in1, HIGH);//set initial (and final) direction of haptic motor current
  digitalWrite(in2, LOW); //set initial (and final) direction of haptic motor current

}

void loop() {
  //  Writing float:
  //  write_float(0xAA, 123.4141);

  //  Writing integer:
  //  write_int(0xAA, 5234);

  Serial.println("alarmNumber at start of loop is: ");
  Serial.println(alarmNumber);

  // Case 1-3 are for alarm scenario A (light, sound), case 4-6 are for alarm scenario B (light, sound, haptic)

  switch (alarmNumber) {
    case 1: //Alarm scenario 1A
      ledAlarm(alarmNumber);
      soundAlarm(alarmNumber);
      delay(A1OnPeriod);
      ledAlarm(0);
      soundAlarm(0);
      delay(A1OffPeriod);
      break;
    case 2: //Alarm scenario 2A
      ledAlarm(alarmNumber);
      soundAlarm(alarmNumber);
      delay(A1OnPeriod);
      ledAlarm(0);
      soundAlarm(0);
      delay(A1OffPeriod);
      break;
    case 3: //Alarm scenario 3A
      ledAlarm(alarmNumber);
      soundAlarm(alarmNumber);
      delay(A3OnPeriod);
      ledAlarm(0);
      soundAlarm(0);
      delay(A3OffPeriod);
      break;
    case 4: //Alarm scenario 1B
      ledAlarm(alarmNumber - 3);
      soundAlarm(alarmNumber - 3);
      hapticAlarm(alarmNumber - 3);
      delay(A1OnPeriod);
      ledAlarm(0);
      soundAlarm(0);
      hapticAlarm(0);
      delay(A1OffPeriod);
      break;
    case 5: //Alarm scenario 2B
      ledAlarm(alarmNumber - 3);
      soundAlarm(alarmNumber - 3);
      hapticAlarm(alarmNumber - 3);
      delay(A2OnPeriod);
      ledAlarm(0);
      soundAlarm(0);
      hapticAlarm(0);
      delay(A2OffPeriod);
      break;
    case 6: //Alarm scenario 3B
      ledAlarm(alarmNumber - 3);
      soundAlarm(alarmNumber - 3);
      hapticAlarm(alarmNumber - 3);
      delay(A3OnPeriod);
      ledAlarm(0);
      soundAlarm(0);
      hapticAlarm(0);
      delay(A3OffPeriod);
      break;
    case 0://Alarm scenario 0
      ledAlarm(0);
      hapticAlarm(0);
      break;
    default:
      Serial.println("Error in loop-switch input");
  }
  delay(1000);
}

// function that executes whenever data is received from master
// this function is registered as an event, see setup()
void receiveEvent(int howMany) {
  alarmNumber = Wire.read();    // receive byte as an integer
  Serial.println("Newly received alarmNumber is: ");
  Serial.print(alarmNumber);         // print the integer
}

void ledAlarm(int ledAlarmNumber) {
  switch (ledAlarmNumber) {
    case 1: //Alarm scenario 1
      digitalWrite(ledPin1, HIGH);
      digitalWrite(ledPin2, LOW);
      digitalWrite(ledPin3, LOW);
      break;
    case 2: //Alarm scenario 2
      digitalWrite(ledPin1, LOW);
      digitalWrite(ledPin2, HIGH);
      digitalWrite(ledPin3, LOW);
      break;
    case 3: //Alarm scenario 3
      digitalWrite(ledPin1, LOW);
      digitalWrite(ledPin2, LOW);
      digitalWrite(ledPin3, HIGH);
      break;
    case 0: //Disable alarms
      digitalWrite(ledPin1, LOW);
      digitalWrite(ledPin2, LOW);
      digitalWrite(ledPin3, LOW);
      break;

  }
}

void soundAlarm(int soundAlarmNumber) {
  switch (soundAlarmNumber) {
    case 1: //Alarm scenario 1
      write_int(16, 1);
      break;
    case 2: //Alarm scenario 2
      write_int(16, 2);
      break;
    case 3: //Alarm scenario 3
      write_int(16, 3);
      break;
    case 0: //Disable alarms
      write_int(16, 0);
      break;

  }
}


void hapticAlarm(int hapticAlarmNumber) {
  switch (hapticAlarmNumber) {
    case 1: //Alarm scenario 1
      voltageValue = A1Amplitude; // Set voltage to A1Amplitude.
      break;
    case 2: //Alarm scenario 2
      voltageValue = A2Amplitude; // Set voltage to A2Amplitude.
      break;
    case 3: //Alarm scenario 3
      voltageValue = A3Amplitude; // Set voltage to A3Amplitude.
      break;
    case 0: //Alarm scenario 4
      voltageValue = 0; // Set voltage to 0V
      break;
  }
  pwmOutput = map(voltageValue, 0, 10, 0 , 255); // Map the voltage value from 0 to 255
  analogWrite(enA, pwmOutput); // Send PWM signal to L298N Enable pin
}
