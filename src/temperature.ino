#define NUM_MEASUREMENTS 10

const int sensorPin = A0;
const int intervalMs = 5000;

int sensorVals[NUM_MEASUREMENTS];
int i = 0;

float avgSensorVal;
float voltage;
float temperature;


/**
 * Calculates average sensor reading across NUM_MEASUREMENTS measurements under the
 * assumption that the average temperature is somewhat more trustworthy
 */
float avgVal(int sensorVals[]) {
  int sum = 0;

  for(int j=0; j<NUM_MEASUREMENTS; j++) {
    sum += sensorVals[j];
  }
  
  return sum/float(NUM_MEASUREMENTS);
}

void setup() {
  Serial.begin(9600);
}

/**
 * We read sensor value NUM_MEASUREMENTS with a delay `intervalMs` between individual measurements
 * Then we calculate average sensor value and transform it into temerature in degrees C 
 */
void loop() {
  sensorVals[i] = analogRead(sensorPin);
  delay(intervalMs);
  i++;

  if(i == NUM_MEASUREMENTS) {
    avgSensorVal = avgVal(sensorVals);

    // Taken from the Arduino handbook.
    voltage = (avgSensorVal / 1024.0) * 5.0;
    temperature = (voltage - .5) * 100;

    Serial.print("TMP:");
    Serial.println(temperature);
    i = 0;
  }
}