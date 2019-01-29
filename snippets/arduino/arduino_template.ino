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
	res[1] = reading.binary[0];
	res[2] = reading.binary[1];
	res[3] = reading.binary[2];
	res[4] = reading.binary[3];
	res[5] = '\n';

	Serial.write(res, packet_size);
}

void write_int32(char id, int value16) {
	long value32 = (long) value16;

	byte res[packet_size];
	res[0] = id;
	res[1] = value32 & 255;
	res[2] = (value32 >> 8)  & 255;
	res[3] = (value32 >> 16) & 255;
	res[4] = (value32 >> 24) & 255;
	res[5] = '\n';

	Serial.write(res, packet_size);
}

void setup() {
	// put your setup code here, to run once:
	Serial.begin(115200);
}

void loop() {
	//  Writing float:
	//  write_float(0xAA, 123.4141);

	//  Writing integer:
	//  write_int32(0xAA, 5234);
}

