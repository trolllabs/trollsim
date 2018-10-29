// the setup routine runs once when you press reset:
void setup() {
  Serial.begin(115200);  
}

// the loop routine runs over and over again forever:
void loop() {

  float conductance = getSkinConductance();
  float ECGvolt=getECG();    
  Serial.print(conductance, 2);  
  Serial.print(",");         
  Serial.println(ECGvolt,2);
  
  // wait for a second  
  delay(10);            
}


float getSkinConductance(void)
  {
    // Local variable declaration.   
    float resistance;
    float conductance;
    delay(1);
    
    // Read an analogic value from analogic2 pin.
    float sensorValue = analogRead(A2);
    float voltage = sensorValue*5.0/1023;

    conductance = 2*((voltage - 0.5) / 100000);

    // Conductance calculation
    resistance = 1 / conductance; 
    conductance = conductance * 1000000;
    delay(1);
    
    if (conductance > 1.0)  return conductance;
    else return -1.0;
  }

float getECG(){
  float analog0;
  analog0=analogRead(0);
  return analog0=(float)analog0*5/1023.0;
}
