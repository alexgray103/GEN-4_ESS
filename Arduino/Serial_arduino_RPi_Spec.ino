// Based on work down by Steven Cogswell
// Demo Code for SerialCommand Library
// May 2011

#include <SerialCommand.h> /* http://github.com/p-v-o-s/Arduino-SerialCommand */
///download the ZIP from github to get library and simple serial examples

// Spectrometer pins for controlling C12880MA Micro-spectrometer Hamamatsu 
#define SPEC_ST          6
#define SPEC_CLK         5
#define WHITE_LED        4

// ADS8321 external 16-bit ADC pseudo-SPI connection
#define CLK 9     // Clock 
#define DOUT 10       // MISO 
#define CS 7      // Selection Pin

// Stepper digital pins
#define step_pin 12
#define dir 13 // direction pin for motor
#define EN_x  8 // enable x motor 
#define EN_y 11 // enable y motor
#define limit_switch 3

// setup analog pins for the module read
#define analogpin1 A0
#define analogpin2 A1
#define analogpin3 A2

// define battery pin
#define battery_pin A7
#define charger_pin A6

// define pump stuff
#define pump_pin 11


SerialCommand sCmd(Serial);     // SerialCommand object

//#include <eRCaGuy_Timer2_Counter.h> /// used for timing of integration time 
#include <elapsedMillis.h>  // Integration time calculation
#include <digitalWriteFast.h>  /// look up github and add ZIP file to arduino

#define SPEC_CHANNELS    288 // New Spec Channel
uint16_t data[SPEC_CHANNELS];

// variable for timing the integration time
float delayTime = 1;
long integration_time = 120; // default integ time is 120 usec 
int integration_delay_ms;
long delay_timing_micro;//= integration_time % (integration_delay_ms*1000);

// variables for pulsing xenon flash lamp
int number_pulses = 1;
int pulse_rate = 60;
int pulse_delay = int((1000000/pulse_rate)/2);

//handle battery percent readoff 
int battery_percent;
int charging_check;


// stepper settings
bool direction_y = 0;
int step_resolution = 500; // step resolution in microns per step
unsigned long number_steps = step_resolution*1.6; // the actual number of steps to move desired distance
int movement_delay = 75; // determines speed of the stepper motors

//pump
int pump_handler;

void setup() {
  // Test for serial command to make sure there is still connection 
  pinModeFast(LED_BUILTIN, OUTPUT);      // Configure the onboard LED for output
  digitalWriteFast(LED_BUILTIN, LOW);    // default to LED off

  //Set desired pins to OUTPUT for spectrometer 
  pinModeFast(SPEC_CLK, OUTPUT);
  pinModeFast(SPEC_ST, OUTPUT);
  pinModeFast(WHITE_LED, OUTPUT);

// setup pins for motor control
  pinModeFast(step_pin, OUTPUT);
  pinModeFast(dir, OUTPUT);
  pinModeFast(EN_x, OUTPUT);
  pinModeFast(EN_y, OUTPUT);
  pinModeFast(limit_switch, INPUT);
  digitalWriteFast(limit_switch, HIGH);
  
  digitalWriteFast(step_pin, LOW);
  digitalWriteFast(dir, LOW);
  digitalWriteFast(EN_x, HIGH);
  digitalWriteFast(EN_y, HIGH);

  digitalWriteFast(SPEC_CLK, LOW); // Set SPEC_CLK High
  digitalWriteFast(SPEC_ST, LOW); // Set SPEC_ST Low
  digitalWriteFast(WHITE_LED, LOW);
  

  pinMode(CS, OUTPUT); 
  pinMode(DOUT, INPUT); 
  pinMode(CLK, OUTPUT); 

  pinMode(analogpin1, INPUT);
  pinMode(analogpin2, INPUT);
  pinMode(analogpin3, INPUT);

  pinMode(battery_pin, INPUT);

  pinMode(pump_pin, OUTPUT);
  digitalWrite(pump_pin, LOW);
  
  //disable device to start with 
  digitalWrite(CS,HIGH); 
  digitalWrite(CLK,LOW); 

  Serial.begin(115200);
  
  
  // Setup callbacks for SerialCommand commands
  sCmd.addCommand("ON",    LED_on);          // Turns LED on
  sCmd.addCommand("OFF",   LED_off);         // Turns LED off   
  sCmd.addCommand("set_integ",  integ_time);  
  sCmd.addCommand("read", read_value);   /// read the data
  sCmd.addCommand("pulse", pulse_number); 
  sCmd.addCommand("pulse_rate", pulse_rate_get);
  sCmd.addCommand("prime_pump", pump_primer);
  sCmd.addCommand("pump_read", pump_read);
  sCmd.addCommand("home", stepper_home); // get the stepper motors to go home
  sCmd.addCommand("y", y_movement);
  sCmd.addCommand("x", x_movement);
  sCmd.addCommand("step_size", step_size);
  sCmd.addCommand("module", module_get);
  sCmd.addCommand("battery", battery_check);
  
  
  
}

void loop() {
  int num_bytes = sCmd.readSerial();      // fill the buffer
  if (num_bytes > 0){
    sCmd.processCommand();  // process the command
  }
  delayMicroseconds(1);
}


/// All function listed below 
void pump_read() {
  digitalWrite(pump_pin, HIGH);
  delay(500);
  digitalWrite(pump_pin, LOW);
}

void pump_primer() {
  int aNumber;
  char *arg;
  arg = sCmd.next();
  if (arg != NULL) {
    aNumber = atoi(arg);    // Converts a char string to an integer
    pump_handler = aNumber;
    
}
  if(pump_handler) {
    digitalWrite(pump_pin, HIGH);
    
  }
  else {
    digitalWrite(pump_pin, LOW);
    
  }
}
        
// Get the module number for the specified attachment 
void module_get() {
  // read the module detect pins 
  int pin1 = digitalRead(analogpin1);
  int pin2 = digitalRead(analogpin2);
  int pin3 = digitalRead(analogpin3);
 
  // convert binary to a decimal to send over serial
  int module = pin1 + pin2*2 +pin3*4;
  //Serial.println(pin1);
  //Serial.println(pin2);
  //Serial.println(pin3);
  // print to the serial
  Serial.print(module);
  Serial.print("\n");
}

void battery_check() {
   // read the module detect pins 
   int charging = analogRead(charger_pin);
   
   float percent = analogRead(battery_pin);
   //Serial.println(percent);
   float voltage = (percent/1023)*5;
   // map battery perecnt from 3.1-4.2Volts into a percent
   battery_percent=map(percent,580,755,0,100);
  

  // print battery level to serial
  Serial.println(battery_percent);
  //Serial.println(voltage);
/*
  if (charging) > 10 {
  Serial.print("150");
  Serial.print("\n");
  }
  else {
  Serial.print(battery_percent);
  Serial.print("\n");
  }
 */
}
void step_size () {
  int aNumber;
  char *arg;
  arg = sCmd.next();
  if (arg != NULL) {
    aNumber = atoi(arg);    // Converts a char string to an integer
    int step_resolution = aNumber;
    number_steps = step_resolution*1.6;
}
}

void y_movement(){
  int aNumber;
  char *arg;
  arg = sCmd.next();
  if (arg != NULL) {
    aNumber = atoi(arg);    // Converts a char string to an integer
    direction_y = aNumber;
    
  digitalWriteFast(EN_x, HIGH);
  digitalWriteFast(11, LOW);
  if (direction_y == 0) {
    digitalWriteFast(dir, HIGH);
  }
  else {
    digitalWriteFast(dir, LOW);
  }
   //Pull direction pin low to move "forward"
      for(int x= 0; x<number_steps; x++) {  //Loop the forward stepping enough times for motion to be visible
      digitalWriteFast(step_pin,HIGH); //Trigger one step forward
      delayMicroseconds(movement_delay);
      digitalWriteFast(step_pin,LOW); //Pull step pin low so it can be triggered again
      delayMicroseconds(movement_delay);
      }
  }
}

void x_movement(){  
  int aNumber;
  char *arg;
  arg = sCmd.next();
  if (arg != NULL) {
    aNumber = atoi(arg);    // Converts a char string to an integer
    int direction_x = aNumber;
    
  digitalWriteFast(EN_x, LOW);
  digitalWriteFast(11, HIGH);
  if (direction_x == 0) {
    digitalWriteFast(dir, HIGH);
  }
  else {
    digitalWriteFast(dir, LOW);
  }
   //Pull direction pin low to move "forward"
      for(int x= 0; x<number_steps; x++) {  //Loop the forward stepping enough times for motion to be visible
      digitalWriteFast(step_pin,HIGH); //Trigger one step forward
      delayMicroseconds(movement_delay);
      digitalWriteFast(step_pin,LOW); //Pull step pin low so it can be triggered again
      delayMicroseconds(movement_delay);
      }
  }
   }   

void stepper_home() {
  // move y "home" first then move x home til a switch is pulled low
  digitalWriteFast(EN_x, HIGH);
  digitalWriteFast(11, LOW);
  digitalWriteFast(dir, LOW);
   // keep moving motor until limit switch is hit then move back 1mm in y direction
      elapsedMicros stepper_start = 0;
      // give the steppers 10 seconds to home and then stop them
      while(stepper_start < 10000000) {
       if (digitalRead(limit_switch) == LOW) {
        break;
       }
      digitalWriteFast(step_pin,HIGH); //Trigger one step forward
      delayMicroseconds(movement_delay);
      digitalWriteFast(step_pin,LOW); //Pull step pin low so it can be triggered again
      delayMicroseconds(movement_delay);
      }
      // after home is found move back out 4mm
      digitalWriteFast(dir, HIGH);
      delay(500);
      for(int x = 0; x < 1600*5.5; x++) {
      digitalWriteFast(step_pin,HIGH); //Trigger one step forward
      delayMicroseconds(movement_delay);
      digitalWriteFast(step_pin,LOW); //Pull step pin low so it can be triggered again
      delayMicroseconds(movement_delay);
      }

      
  digitalWriteFast(EN_x, LOW);
  digitalWriteFast(11, HIGH);
  digitalWriteFast(dir, LOW);
  
   // keep moving motor until limit switch is hit then move back 4mm in y direction
      elapsedMicros stepper_start_2 = 0;
      while(stepper_start_2 < 10000000) {
       if (digitalRead(limit_switch) == LOW) {
        break;
       }
      digitalWriteFast(step_pin,HIGH); //Trigger one step forward
      delayMicroseconds(movement_delay);
      digitalWriteFast(step_pin,LOW); //Pull step pin low so it can be triggered again
      delayMicroseconds(movement_delay);
      }
      // after home is found move back out 1mm
      digitalWriteFast(dir, HIGH);
      delay(500);
      for(int x = 0; x < 1600*7; x++) {
      digitalWriteFast(step_pin,HIGH); //Trigger one step forward
      delayMicroseconds(movement_delay);
      digitalWriteFast(step_pin,LOW); //Pull step pin low so it can be triggered again
      delayMicroseconds(movement_delay);
      }
   }

int read_adc(){
  uint16_t adcvalue = 0;
  digitalWrite(CS, HIGH);
  
  digitalWrite(CS,LOW);       
  
  for(int i = 0; i<=6; i++){
    digitalWrite(CLK,HIGH); 
    delayMicroseconds(1);     
    digitalWrite(CLK,LOW);
    delayMicroseconds(1);  
  }

  //read bits from adc
  for (int i=15; i>=0; i--){
    //cycle clock
    
    digitalWrite(CLK,HIGH);
    adcvalue |= digitalRead(DOUT)<<i; 
    delayMicroseconds(1);   
    digitalWrite(CLK,LOW);
    delayMicroseconds(1); 

    //Serial.print(digitalRead(DOUT));
  }
  digitalWrite(CS,HIGH);
  //Serial.println("  ");

  //          //turn off device
  //Serial.print(digitalRead(DOUT));
  return adcvalue;
}

void LED_on() {
  Serial.println("LED on");
  digitalWriteFast(LED_BUILTIN, HIGH);
}

void LED_off() {
  Serial.println("LED off");
  digitalWriteFast(LED_BUILTIN, LOW);
}


void integ_time() {
  long aNumber;
  char *arg;

  arg = sCmd.next();
  if (arg != NULL) {
    aNumber = atol(arg);    // Converts a char string to an integer
    integration_time = aNumber;
    
    //Serial.println(integration_time);
    // calculate delays for all integration timing
    integration_delay_ms = integration_time/1000;
    delay_timing_micro = max(0, (integration_time % ((long) integration_delay_ms*1000)) - 120);
      //Serial.println(delay_timing_micro);
      //Serial.println(integration_delay_ms);
      
      if(delay_timing_micro == 0){
        if(integration_delay_ms == 0){
          delay_timing_micro = max(0, (integration_time - 120));
        }
        else {
          integration_delay_ms -= 1;
          delay_timing_micro = 880;
        }
    }
  }
}

void pulse_number() {
  int aNumber;
  char *arg;

  arg = sCmd.next();
  if (arg != NULL) {
    aNumber = atoi(arg);    // Converts a char string to an integer
    number_pulses = aNumber;
  }
}

void pulse_rate_get() {
  int aNumber;
  char *arg;

  arg = sCmd.next();
  if (arg != NULL) {
    aNumber = atoi(arg);    // Converts a char string to an integer
    pulse_rate = aNumber;
    pulse_delay = int((1000000/pulse_rate)/2);
  }
}

void read_value()
{

  // Get timing for 48 clock pulses that will be incorporated into integration time 
elapsedMicros duration_48 = 0;

for(int i = 0; i < 12; i++) {
    digitalWriteFast(SPEC_CLK, HIGH);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, LOW);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, HIGH);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, LOW);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, HIGH);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, LOW);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, HIGH);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, LOW);
    delayMicroseconds(delayTime);
    
  }
  int timer_usec = duration_48;


// start the actual sequence to meaasure
// Start clock cycle and set start pulse to signal start
  digitalWriteFast(SPEC_CLK, HIGH);
  delayMicroseconds(delayTime);
  digitalWriteFast(SPEC_CLK, LOW);
  digitalWriteFast(SPEC_ST, HIGH);
  delayMicroseconds(delayTime);

  // 3 clock pulses before integration starts
  digitalWriteFast(SPEC_CLK, HIGH);
  delayMicroseconds(delayTime);
  digitalWriteFast(SPEC_CLK, LOW);
  delayMicroseconds(delayTime);
  digitalWriteFast(SPEC_CLK, HIGH);
  delayMicroseconds(delayTime);
  digitalWriteFast(SPEC_CLK, LOW);
  delayMicroseconds(delayTime);
  digitalWriteFast(SPEC_CLK, HIGH);
  delayMicroseconds(delayTime);
  digitalWriteFast(SPEC_CLK, LOW);
  

  
elapsedMicros integ_start = 0;
if (number_pulses > 0) {
  for(int i = 0; i < number_pulses; i++) {
     digitalWriteFast(WHITE_LED, HIGH);
     delayMicroseconds(10);
     
     // turn off lamp then wait longer for more flashes if needed
     digitalWriteFast(WHITE_LED, LOW);

        
     // if more than one pulse add an extra delay to allow for recharging of the flash lamp 
     if(number_pulses > 1) {
      delayMicroseconds(pulse_delay-160); // subtract 160 due to timing of other operations in program 
      delayMicroseconds(pulse_delay);
}
}
}
else {
  delay(integration_delay_ms);
  delayMicroseconds(delay_timing_micro);
}
      

//int integration_delay_ms = integration_time/1000;
//int delay_timing_micro = integration_time % (integration_delay_ms*1000);
//Serial.println(integration_delay_ms);
//Serial.println(delay_timing_micro);
/*
if (number_pulses == 0) {
  if((integration_delay_ms)  > 0 ) {
        delay(integration_delay_ms);
        delayMicroseconds(delay_timing_micro);
  }
  else {
    delayMicroseconds(integration_time);
  }
}
 */
//int integ_timer_final = integ_timer;

  // set ST pin low to signal end of integration after 48 more CLK pulses
digitalWriteFast(SPEC_ST, LOW);
  // 48 clock pulses to keep sampling (part of integration time) 
  elapsedMicros clock_timer = 0;
for(int i = 0; i < 12; i++) {
    digitalWriteFast(SPEC_CLK, HIGH);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, LOW);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, HIGH);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, LOW);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, HIGH);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, LOW);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, HIGH);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, LOW);
    delayMicroseconds(delayTime);
    
  }
  float final_time = integ_start;
  //digitalWriteFast(WHITE_LED, LOW);

for(int i = 0; i < 10; i++) {
    digitalWriteFast(SPEC_CLK, HIGH);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, LOW);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, HIGH);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, LOW);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, HIGH);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, LOW);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, HIGH);
    delayMicroseconds(delayTime);
    digitalWriteFast(SPEC_CLK, LOW);
    delayMicroseconds(delayTime);
  }
 delay(1);

  //Read from SPEC_VIDEO
  //analogReadResolution(12);
  for(int i = 0; i < SPEC_CHANNELS; i++){
      uint16_t readvalue = read_adc();
      data[i] = readvalue;
      digitalWriteFast(SPEC_CLK, HIGH);
      delayMicroseconds(delayTime);
      digitalWriteFast(SPEC_CLK, LOW);
      delayMicroseconds(delayTime);

  }
  //check timing of pulses (uncomment to see timing in serial window)
  //Serial.println(timer_usec);   // time for 48 clock pulses
  //Serial.println(final_time);


  
  //Set SPEC_ST to high
  //digitalWriteFast(SPEC_ST, HIGH);
  
  for (int i = 0; i < SPEC_CHANNELS-1; i++){
    Serial.print(data[i]);
    Serial.print(',');
    
  }
  Serial.print(data[SPEC_CHANNELS - 1]);
  Serial.print("\n");
  
}
