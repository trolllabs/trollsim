#define FLEX_ID  1
#define ROLL_ID  2
#define PITCH_ID 3
#define YAW_ID   4
float flex_output;
float roll_output;
float pitch_output;
float yaw_output;
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

void write_float2(char id, float value, int start_i, byte packet[]) {
	binaryFloat reading;
	reading.floatingPoint = value;

	packet[start_i] = id;
	packet[start_i + 1] = reading.binary[3];
	packet[start_i + 2] = reading.binary[2];
	packet[start_i + 3] = reading.binary[1];
	packet[start_i + 4] = reading.binary[0];
	packet[start_i + 5] = '\n';
}

void write_all(float flex, float roll, float pitch, float yaw) {
	byte res[packet_size*4];
	write_float2(FLEX_ID, flex, packet_size*0, res);
	write_float2(ROLL_ID, roll, packet_size*1, res);
	write_float2(PITCH_ID, pitch, packet_size*2, res);
	write_float2(YAW_ID, yaw, packet_size*3, res);
	//  res[packet_size*4] = '\n';

	Serial.write(res, packet_size*4);
}



///////////////////////////////////////////////////////////////////////////////////////
//THIS IS A DEMO SOFTWARE JUST FOR EXPERIMENT PURPOER IN A NONCOMERTIAL ACTIVITY
//Version: 1.0 (AUG, 2016)

//Gyro - Arduino UNO R3
//VCC  -  5V
//GND  -  GND
//SDA  -  A4
//SCL  -  A5
//INT - port-2

#include <Wire.h>
//Declaring some global variables for the horizontal sensor
int gyro_x_h, gyro_y_h, gyro_z_h;
long gyro_x_cal_h, gyro_y_cal_h, gyro_z_cal_h;
boolean set_gyro_angles_h;

long acc_x_h, acc_y_h, acc_z_h, acc_total_vector_h;
float angle_pitch_acc_h, angle_roll_acc_h, angle_yaw_acc_h;

float angle_roll_h, angle_pitch_h, angle_yaw_h;
int angle_roll_buffer_h, angle_pitch_buffer_h, angle_yaw_buffer_h;
float angle_roll_output_h, angle_pitch_output_h, angle_yaw_output_h;

long loop_timer_h;
int temp_h;

//Declaring some global variables for the vertical sensor
int gyro_x_v, gyro_y_v, gyro_z_v;
long gyro_x_cal_v, gyro_y_cal_v, gyro_z_cal_v;
boolean set_gyro_angles_v;

long acc_x_v, acc_y_v, acc_z_v, acc_total_vector_v;
float angle_pitch_acc_v, angle_roll_acc_v, angle_yaw_acc_v;

float angle_roll_v, angle_pitch_v, angle_yaw_v;
int angle_roll_buffer_v, angle_pitch_buffer_v, angle_yaw_buffer_v;
float angle_roll_output_v, angle_pitch_output_v, angle_yaw_output_v;

long loop_timer_v;
int temp_v;

//Declaring some global variables for the flex sensor
int flexSensorPin=0;
float flexSensorValue=0;

void setup() {
	Wire.begin();                                                        //Start I2C as master
	setup_mpu_6050_registers_h();                                          //Setup the registers of the horizontal MPU-6050
	setup_mpu_6050_registers_v();                                          //Setup the registers of the vertical MPU-6050
	for (int cal_int = 0; cal_int < 1000 ; cal_int ++){                  //Read the raw acc and gyro data from the MPU-6050 for 1000 times
		read_mpu_6050_data_h();
		gyro_x_cal_h += gyro_x_h;                                              //Add the gyro x offset to the gyro_x_cal variable
		gyro_y_cal_h += gyro_y_h;                                          //Add the gyro y offset to the gyro_y_cal variable
		gyro_z_cal_h += gyro_z_h;                                              //Add the gyro z offset to the gyro_z_cal variable
		read_mpu_6050_data_v();
		gyro_x_cal_v += gyro_x_v;                                              //Add the gyro x offset to the gyro_x_cal variable
		gyro_y_cal_v += gyro_y_v;                                          //Add the gyro y offset to the gyro_y_cal variable
		gyro_z_cal_v += gyro_z_v;                                              //Add the gyro z offset to the gyro_z_cal variable
		delay(3);                                                          //Delay 3us to have 250Hz for-loop
	}
	// divide by 1000 to get avarage offset
	gyro_x_cal_h /= 1000;
	gyro_y_cal_h /= 1000;
	gyro_z_cal_h /= 1000;
	gyro_x_cal_v /= 1000;
	gyro_y_cal_v /= 1000;
	gyro_z_cal_v /= 1000;
	Serial.begin(115200);
	loop_timer_h = micros();                                               //Reset the loop timer
	loop_timer_v = micros();
}

void loop(){
	// Horizontal sensor from here
	read_mpu_6050_data_h();
	//Subtract the offset values from the raw gyro values
	gyro_x_h -= gyro_x_cal_h;
	gyro_y_h -= gyro_y_cal_h;
	gyro_z_h -= gyro_z_cal_h;

	//Gyro angle calculations . Note 0.0000611 = 1 / (250Hz x 65.5)
	angle_roll_h += gyro_x_h * 0.0000611;                                   //Calculate the traveled roll angle and add this to the angle_roll variable
	angle_pitch_h += gyro_y_h * 0.0000611;                                    //Calculate the traveled pitch angle and add this to the angle_pitch variable
	//angle_yaw_h += gyro_z_h * 0.0000611;                                     //Calculate the traveled yaw angle and add this to the angle_yaw variable
	//0.000001066 = 0.0000611 * (3.142(PI) / 180degr) The Arduino sin function is in radians
	angle_roll_h += angle_pitch_h * sin(gyro_z_h * 0.000001066);               //If the IMU has yawed transfer the pitch angle to the roll angel
	angle_pitch_h -= angle_roll_h * sin(gyro_z_h * 0.000001066);               //If the IMU has yawed transfer the roll angle to the pitch angel

	//Accelerometer angle calculations
	acc_total_vector_h = sqrt((acc_x_h*acc_x_h)+(acc_y_h*acc_y_h)+(acc_z_h*acc_z_h));  //Calculate the total accelerometer vector
	//57.296 = 1 / (3.142 / 180) The Arduino asin function is in radians
	angle_pitch_acc_h = asin((float)acc_x_h/acc_total_vector_h)* -57.296;       //Calculate the pitch angle
	angle_roll_acc_h = asin((float)acc_y_h/acc_total_vector_h)* 57.296;       //Calculate the roll angle

	angle_roll_acc_h -= 0.0;                                              //Accelerometer calibration value for roll
	angle_pitch_acc_h -= 0.0;                                               //Accelerometer calibration value for pitch

	if(set_gyro_angles_h){                                                 //If the IMU is already started
		angle_roll_h = angle_roll_h * 0.9996 + angle_roll_acc_h * 0.0004;     //Correct the drift of the gyro roll angle with the accelerometer roll angle
		angle_pitch_h = angle_pitch_h * 0.9996 + angle_pitch_acc_h * 0.0004;        //Correct the drift of the gyro pitch angle with the accelerometer pitch angle
	}
	else{                                                                //At first start
		angle_roll_h = angle_roll_acc_h;                                     //Set the gyro roll angle equal to the accelerometer roll angle
		angle_pitch_h = angle_pitch_acc_h;                                       //Set the gyro pitch angle equal to the accelerometer pitch angle
		set_gyro_angles_h = true;                                            //Set the IMU started flag
	}

	//To dampen the roll and pitch angles a complementary filter is used
	angle_roll_output_h = angle_roll_output_h * 0.9 + angle_roll_h * 0.1;   //Take 90% of the output roll value and add 10% of the raw roll value
	angle_pitch_output_h = angle_pitch_output_h * 0.9 + angle_pitch_h * 0.1*-1;      //Take 90% of the output pitch value and add 10% of the raw pitch value

	//Vertical sensor from here and down

	read_mpu_6050_data_v();
	//Subtract the offset values from the raw gyro values
	gyro_x_v -= gyro_x_cal_v;
	gyro_y_v -= gyro_y_cal_v;
	gyro_z_v -= gyro_z_cal_v;

	//Gyro angle calculations . Note 0.0000611 = 1 / (250Hz x 65.5)
	angle_roll_v += gyro_x_v * 0.0000611;                                   //Calculate the traveled roll angle and add this to the angle_roll variable
	angle_pitch_v += gyro_y_v * 0.0000611;                                    //Calculate the traveled pitch angle and add this to the angle_pitch variable
	//angle_yaw_v += gyro_z_v * 0.0000611;                                     //Calculate the traveled yaw angle and add this to the angle_yaw variable
	//0.000001066 = 0.0000611 * (3.142(PI) / 180degr) The Arduino sin function is in radians
	angle_roll_v += angle_pitch_v * sin(gyro_z_v * 0.000001066);               //If the IMU has yawed transfer the pitch angle to the roll angel
	angle_pitch_v -= angle_roll_v * sin(gyro_z_v * 0.000001066);               //If the IMU has yawed transfer the roll angle to the pitch angel

	//Accelerometer angle calculations
	acc_total_vector_v = sqrt((acc_x_v*acc_x_v)+(acc_y_v*acc_y_v)+(acc_z_v*acc_z_v));  //Calculate the total accelerometer vector
	//57.296 = 1 / (3.142 / 180) The Arduino asin function is in radians
	angle_pitch_acc_v = asin((float)acc_x_v/acc_total_vector_v)* -57.296;       //Calculate the pitch angle
	//angle_roll_acc_v = asin((float)acc_y_v/acc_total_vector_v)* 57.296;       //Calculate the roll angle
	//angle_yaw_acc_v = asin((float)acc_z_v/acc_total_vector_v)* -57.296;       //Calculate the yaw angle

	angle_roll_acc_v -= 0.0;                                              //Accelerometer calibration value for roll
	//angle_pitch_acc_v -= 0.0;                                               //Accelerometer calibration value for pitch
	//angle_yaw_acc_v -= 0.0;                                                //Accelerometer calibration value for yaw

	if(set_gyro_angles_v){                                                 //If the IMU is already started
		angle_roll_v = angle_roll_v * 0.9996 + angle_roll_acc_v * 0.0004;     //Correct the drift of the gyro roll angle with the accelerometer roll angle
		//angle_pitch_v = angle_pitch_v * 0.9996 + angle_pitch_acc_v * 0.0004;        //Correct the drift of the gyro pitch angle with the accelerometer pitch angle
		//angle_yaw_v = angle_yaw_v * 0.9996 + angle_yaw_acc_v * 0.0004;           //Correct the drift of the gyro yaw angle with the accelerometer yaw angle
	}
	else{                                                                //At first start
		angle_roll_v = angle_roll_acc_v;                                     //Set the gyro roll angle equal to the accelerometer roll angle
		//angle_pitch_v = angle_pitch_acc_v;                                       //Set the gyro pitch angle equal to the accelerometer pitch angle
		//angle_yaw_v = angle_yaw_acc_v;                                         //Set the gyro yaw angle equal to the accelerometer yaw angle
		set_gyro_angles_v = true;                                            //Set the IMU started flag
	}

	//To dampen the roll and pitch angles a complementary filter is used
	angle_roll_output_v = angle_roll_output_v * 0.9 + angle_roll_v * 0.1;   //Take 90% of the output roll value and add 10% of the raw roll value
	//angle_pitch_output_v = angle_pitch_output_v * 0.9 + angle_pitch_v * 0.1*-1;      //Take 90% of the output pitch value and add 10% of the raw pitch value
	//angle_yaw_output_v = angle_yaw_output_v * 0.9 + angle_yaw_v * 0.1;      //Take 90% of the output pitch value and add 10% of the raw pitch value

	// read and print value of flex sensor
	flex_output = analogRead(flexSensorPin);
	flex_output = fractionMap(flex_output,17,40,1,0); //read value of flex sensor

	if (flex_output > 1)
		flex_output = 1.0;
	else if (flex_output < 0.1)
		flex_output = 0.0;

	roll_output = remap(angle_roll_output_h, 60, false);
	pitch_output = remap(angle_pitch_output_h, 60, false);
	yaw_output = remap(angle_roll_output_v, 60, true);


	//  Serial.print(FLEX_ID); Serial.print(';'); Serial.println(flex_output);
	//  Serial.print(ROLL_ID); Serial.print(';'); Serial.println(roll_output);
	//  Serial.print(PITCH_ID); Serial.print(';'); Serial.println(pitch_output);
	//  Serial.print(YAW_ID); Serial.print(';'); Serial.println(yaw_output);

	write_all(flex_output, roll_output, pitch_output, yaw_output);
	Serial.flush();
	//  Serial.println(flex_output);
	//	write_float(FLEX_ID, flex_output);
	//	write_float(ROLL_ID, roll_output);
	//	write_float(PITCH_ID, pitch_output);
	//	write_float(YAW_ID, yaw_output);

	while(micros() - loop_timer_h < 4000);                                 //Wait until the loop_timer reaches 4000us (250Hz) before starting the next loop
	loop_timer_h = micros();//Reset the loop timer
	loop_timer_v = micros();//Reset the loop timer


}

void setup_mpu_6050_registers_h(){
	//Activate the horisontal MPU-6050
	Wire.beginTransmission(0x68);                                        //Start communicating with the MPU-6050
	Wire.write(0x6B);                                                    //Send the requested starting register
	Wire.write(0x00);                                                    //Set the requested starting register
	Wire.endTransmission();
	//Configure the accelerometer (+/-8g)
	Wire.beginTransmission(0x68);                                        //Start communicating with the MPU-6050
	Wire.write(0x1C);                                                    //Send the requested starting register
	Wire.write(0x10);                                                    //Set the requested starting register
	Wire.endTransmission();
	//Configure the gyro (500dps full scale)
	Wire.beginTransmission(0x68);                                        //Start communicating with the MPU-6050
	Wire.write(0x1B);                                                    //Send the requested starting register
	Wire.write(0x08);                                                    //Set the requested starting register
	Wire.endTransmission();
}

void setup_mpu_6050_registers_v(){
	//Activate the vertical MPU-6050
	Wire.beginTransmission(0x69);                                        //Start communicating with the MPU-6050
	Wire.write(0x6B);                                                    //Send the requested starting register
	Wire.write(0x00);                                                    //Set the requested starting register
	Wire.endTransmission();
	//Configure the accelerometer (+/-8g)
	Wire.beginTransmission(0x69);                                        //Start communicating with the MPU-6050
	Wire.write(0x1C);                                                    //Send the requested starting register
	Wire.write(0x10);                                                    //Set the requested starting register
	Wire.endTransmission();
	//Configure the gyro (500dps full scale)
	Wire.beginTransmission(0x69);                                        //Start communicating with the MPU-6050
	Wire.write(0x1B);                                                    //Send the requested starting register
	Wire.write(0x08);                                                    //Set the requested starting register
	Wire.endTransmission();
}

void read_mpu_6050_data_h(){                                             //Subroutine for reading the raw horizontal gyro and accelerometer data
	Wire.beginTransmission(0x68);                                        //Start communicating with the MPU-6050
	Wire.write(0x3B);                                                    //Send the requested starting register
	Wire.endTransmission();                                              //End the transmission
	Wire.requestFrom(0x68,14);                                           //Request 14 bytes from the MPU-6050
	while(Wire.available() < 14);                                        //Wait until all the bytes are received
	acc_x_h = Wire.read()<<8|Wire.read();
	acc_y_h = Wire.read()<<8|Wire.read();
	acc_z_h = Wire.read()<<8|Wire.read();
	temp_h = Wire.read()<<8|Wire.read();
	gyro_x_h = Wire.read()<<8|Wire.read();
	gyro_y_h = Wire.read()<<8|Wire.read();
	gyro_z_h = Wire.read()<<8|Wire.read();
}

void read_mpu_6050_data_v(){                                             //Subroutine for reading the raw vertical gyro and accelerometer data
	Wire.beginTransmission(0x69);                                        //Start communicating with the MPU-6050
	Wire.write(0x3B);                                                    //Send the requested starting register
	Wire.endTransmission();                                              //End the transmission
	Wire.requestFrom(0x69,14);                                           //Request 14 bytes from the MPU-6050
	while(Wire.available() < 14);                                        //Wait until all the bytes are received
	acc_x_v = Wire.read()<<8|Wire.read();
	acc_y_v = Wire.read()<<8|Wire.read();
	acc_z_v = Wire.read()<<8|Wire.read();
	temp_v = Wire.read()<<8|Wire.read();
	gyro_x_v = Wire.read()<<8|Wire.read();
	gyro_y_v = Wire.read()<<8|Wire.read();
	gyro_z_v = Wire.read()<<8|Wire.read();
}

double fractionMap(double x, double in_min, double in_max, double out_min, double out_max) {
	return (x - in_min)*(out_max - out_min)/(in_max - in_min) + out_min;
}

double remap(double value, double halfrange, bool invert) {
	if (invert)
		return fractionMap(value, halfrange, -halfrange, -1, 1);
	else
		return fractionMap(value, -halfrange, halfrange, -1, 1);
}
