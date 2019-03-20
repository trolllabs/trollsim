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

void setup() {
	// put your setup code here, to run once:
	Serial.begin(115200);
}

void loop() {
	//  Writing float:
	//  write_float(0xAA, 123.4141);

	//  Writing integer:
	//  write_int(0xAA, 5234);
}

