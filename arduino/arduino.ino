// Nano PWM: 3, 5, 6, 9, 10, and 11. Provide 8-bit PWM output with the analogWrite() function.

int sensor_moist = A0;
int sensor_temp = A2;
int sensor_light = A1;

int driver_led = 11;
int driver_pump = 10;

int threshold_moist = 300;
int threshold_upper_light = 590;
int threshold_lower_light = 650;

int value_moist;
int value_light; // light -> lower ; dark -> higher

int time_pump = 1; // 1 sec now (water flow rate is about 24mL/sec)
int intensity_led = 0;

// for serial connection with Raspberry Pi
byte data1;
byte data2;
int data;

void setup() {
  pinMode(sensor_moist, INPUT);
  pinMode(sensor_temp, INPUT);
  pinMode(sensor_light, INPUT);
  
  pinMode(driver_led, OUTPUT);
  pinMode(driver_pump, OUTPUT);
  digitalWrite(driver_led, LOW);
  digitalWrite(driver_pump, LOW);
  
  Serial.begin(9600);
}

void loop() {
  // read data from sensor
  value_moist = analogRead(sensor_moist);
  value_light = analogRead(sensor_light);
  
  // print data
  Serial.print("Moisture: ");
  Serial.println(value_moist);
  Serial.print("Light: ");
  Serial.println(value_light);
  
  // read data from raspberry pi
  if (Serial.available()) {
    char command = Serial.read();
    if (command=='l'){
      
      // receive data
      data1 = Serial.read();
      data2 = Serial.read();
      data=data1*256+data2;
      
      // update threshold value
      threshold_upper_light=data;
      threshold_lower_light=data+60;
      if (threshold_lower_light>1023){
        threshold_lower_light=1023;
      }
      
      Serial.print("Light Upper Threshold: ");
      Serial.println(threshold_upper_light);
      
    } else if (command=='w'){
      Serial.println("Water!");
    } else {
      Serial.println(command);
    }
  }  
  
  // response action of moist
  if ( value_moist > threshold_moist ) {
//    if (false) {
    // pump water
    digitalWrite(driver_pump,HIGH);
    delay(time_pump*1000);
    digitalWrite(driver_pump,LOW);
  }
 

  // response action of light 
  while (value_light > threshold_lower_light ) {
    intensity_led+=5;
    if (intensity_led > 255){
      intensity_led = 255;
      break;
    }
    analogWrite(driver_led,intensity_led);
    delay(10);
    value_light = analogRead(sensor_light);
  }
  while (value_light < threshold_upper_light ) {
    intensity_led-=5;
    if (intensity_led < 0){
      intensity_led = 0;
      break;
    }
    analogWrite(driver_led,intensity_led);
    delay(10);
    value_light = analogRead(sensor_light);
  }
  
  Serial.print("LED Intensity: ");
  Serial.println(intensity_led);

  delay(1000);
}
