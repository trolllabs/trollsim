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


/*******************************************************************
  Variables for the experimenter to tweak alarm periods and haptic amplitude.
********************************************************************/

// Alarm 1 settings:
unsigned long A1OnPeriod = 1000;   //Period in [ms] alarm 1 is activated every loop
unsigned long A1OffPeriod = 2000; // Period in [ms] alarm 1 is off every loop
float A1Volume=-2; //Volume of audio alarm 1, in [dB]. Scale from -63,5dB (min) to 0dB (max).
int A1HapticAmplitude = 9;  //Amplitude in [V] of alarm 1's haptic feedback. Input valid from 0-9V.

// Alarm 2 settings:
unsigned long A2OnPeriod = 2000;   //Period in [ms] alarm 2 is activated every loop
unsigned long A2OffPeriod = 1000;  // Period in [ms] alarm 2 is off every loop
float A2Volume=-5.0; //Volume of audio alarm 2, in [dB]. Scale from -63,5dB (min) to 0dB (max).
int A2HapticAmplitude = 7;  //Amplitude in [V] of alarm 1's haptic feedback. Input valid from 0-9V.

// Alarm 3 settings:
unsigned long A3OnPeriod =  1500;  //Period in [ms] alarm 3 is activated every loop
unsigned long A3OffPeriod = 1500;  // Period in [ms] alarm 3 is off every loop
float A3Volume=-7; //Volume of audio alarm 3, in [dB]. Scale from -63,5dB (min) to 0dB (max).
int A3HapticAmplitude = 5;  //Amplitude in [V] of alarm 1's haptic feedback. Input valid from 0-9V.

// Audio alarm frequency and amplitude must be tweaked in socketaudio.py

//*******************************************************************

#include <Wire.h>
int alarmNumber = 0; //variable to hold alarm number
int alarmPeriod = 0; //variable holding alarm timeout period
int ledPin1 = 3;  //pin number 1st led (RED) (PWM)
int ledPin2 = 5;  //pin number 2nd led  (YELLOW) (PWM)
int ledPin3 = 6;  //pin number 3rd led  (GREEN) (PWM)
#define enA 10 //enable pin for haptic feedback
#define in1 11 //in1 pin for haptic feedback
#define in2 12 //in2 pin for haptic feedback
int voltageValue = 0; //variable to hold haptic motor voltage value
int pwmOutput = 0;  //variable to hold pwmOutput value to haptic motor

int alarm1State = LOW;
int alarm2State = LOW;
int alarm3State = LOW;

int newMessage = HIGH;
int soundMessageState=LOW;

unsigned long previousMillis = 0;
unsigned long currentMillis = 0;

void setup() {
  Wire.begin(1);                // join i2c bus with address #1
  Wire.onReceive(receiveEvent); // register event
  Serial.begin(115200);           // start serial for output
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
  // Case 1-3 are for alarm scenario A (light, sound), case 4-6 are for alarm scenario B (light, sound, haptic)

  switch (alarmNumber) {
    case 1: //Alarm scenario 1A
      if ((alarm1State == LOW && currentMillis - previousMillis >= A1OffPeriod) || newMessage == HIGH) {
        previousMillis = currentMillis;
        ledAlarm(alarmNumber);
        soundAlarm(alarmNumber);
        alarm1State = HIGH;
        newMessage = LOW;
      }
      else if (alarm1State == HIGH && currentMillis - previousMillis >= A1OnPeriod) {
        previousMillis = currentMillis;
        ledAlarm(0);
        soundAlarm(0);
        alarm1State = LOW;
        newMessage = LOW;
      }
      break;
    case 2: //Alarm scenario 1A
      if ((alarm2State == LOW && currentMillis - previousMillis >= A1OffPeriod) || newMessage == HIGH) {
        previousMillis = currentMillis;
        ledAlarm(alarmNumber);
        soundAlarm(alarmNumber);
        alarm2State = HIGH;
        newMessage = LOW;
      }
      else if (alarm2State == HIGH && currentMillis - previousMillis >= A1OnPeriod) {
        previousMillis = currentMillis;
        ledAlarm(0);
        soundAlarm(0);
        alarm2State = LOW;
        newMessage = LOW;
      }
      break;
    case 3: //Alarm scenario 1A
      if ((alarm3State == LOW && currentMillis - previousMillis >= A1OffPeriod) || newMessage == HIGH) {
        previousMillis = currentMillis;
        ledAlarm(alarmNumber);
        soundAlarm(alarmNumber);
        alarm3State = HIGH;
        newMessage = LOW;
      }
      else if (alarm3State == HIGH && currentMillis - previousMillis >= A1OnPeriod) {
        previousMillis = currentMillis;
        ledAlarm(0);
        soundAlarm(0);
        alarm3State = LOW;
        newMessage = LOW;
      }
      break;
    case 4: //Alarm scenario 1B
      if ((alarm1State == LOW && currentMillis - previousMillis >= A1OffPeriod) || newMessage == HIGH) {
        previousMillis = currentMillis;
        ledAlarm(alarmNumber - 3);
        soundAlarm(alarmNumber - 3);
        hapticAlarm(alarmNumber - 3);
        alarm1State = HIGH;
        newMessage = LOW;
      }
      else if (alarm1State == HIGH && currentMillis - previousMillis >= A1OnPeriod) {
        previousMillis = currentMillis;
        ledAlarm(0);
        soundAlarm(0);
        hapticAlarm(0);
        alarm1State = LOW;
        newMessage = LOW;
      }
      break;
    case 5: //Alarm scenario 2B
      if ((alarm2State == LOW && currentMillis - previousMillis >= A1OffPeriod) || newMessage == HIGH) {
        previousMillis = currentMillis;
        ledAlarm(alarmNumber-3);
        soundAlarm(alarmNumber-3);
        hapticAlarm(alarmNumber - 3);
        alarm2State = HIGH;
        newMessage = LOW;
      }
      else if (alarm2State == HIGH && currentMillis - previousMillis >= A1OnPeriod) {
        previousMillis = currentMillis;
        ledAlarm(0);
        soundAlarm(0);
        hapticAlarm(0);
        alarm2State = LOW;
        newMessage = LOW;
      }
      break;
    case 6: //Alarm scenario 3B
      if ((alarm3State == LOW && currentMillis - previousMillis >= A1OffPeriod) || newMessage == HIGH) {
        previousMillis = currentMillis;
        ledAlarm(alarmNumber-3);
        soundAlarm(alarmNumber-3);
        hapticAlarm(alarmNumber - 3);
        alarm3State = HIGH;
        newMessage = LOW;
      }
      else if (alarm3State == HIGH && currentMillis - previousMillis >= A1OnPeriod) {
        previousMillis = currentMillis;
        ledAlarm(0);
        soundAlarm(0);
        hapticAlarm(0);
        alarm3State = LOW;
        newMessage = LOW;
      }
      break;
    case 0://Alarm scenario 0
      ledAlarm(0);
      hapticAlarm(0);

      if(soundMessageState==LOW){
        soundAlarm(0);
        soundMessageState=HIGH;
      }     
      break;
    default:
      Serial.println("Error in loop-switch input");
  }
  delay(100);
  currentMillis = millis(); //update timer
}

// function that executes whenever data is received from master
// this function is registered as an event, see setup()
void receiveEvent(int howMany) {
  alarmNumber = Wire.read();    // receive byte as an integer
  newMessage = HIGH;
  soundMessageState=LOW;
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
  write_int(17, soundAlarmNumber); //Sends packet requesting the correct sound alarm
  switch (soundAlarmNumber) {
    case 1: //Alarm scenario 1
      write_float(19,A1Volume); //Sets alarm volume for alarm to A1Volume
      break;
    case 2: //Alarm scenario 2
      write_float(19,A2Volume); //Sets alarm volume for alarm to A2Volume
      break;
    case 3: //Alarm scenario 3
      write_float(19,A3Volume); //Sets alarm volume for alarm to A3Volume
      break;
      break;

  }
}

void hapticAlarm(int hapticAlarmNumber) {
  switch (hapticAlarmNumber) {
    case 1: //Alarm scenario 1
      voltageValue = A1HapticAmplitude; // Set voltage to A1HapticAmplitude.
      break;
    case 2: //Alarm scenario 2
      voltageValue = A2HapticAmplitude; // Set voltage to A2HapticAmplitude.
      break;
    case 3: //Alarm scenario 3
      voltageValue = A3HapticAmplitude; // Set voltage to A3HapticAmplitude.
      break;
    case 0: //Alarm scenario 4
      voltageValue = 0; // Set voltage to 0V
      break;
  }
  pwmOutput = map(voltageValue, 0, 10, 0 , 255); // Map the voltage value from 0 to 255
  analogWrite(enA, pwmOutput); // Send PWM signal to L298N Enable pin
}
