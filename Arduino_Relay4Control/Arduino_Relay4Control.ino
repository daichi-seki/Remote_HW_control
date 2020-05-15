#include <MsTimer2.h>
#include <EEPROM.h>

#define ON (1)
#define OFF (0)

#define REQON_RELAYON (1)
#define REQON_RELAYOFF (0)

#define BIT_REQ1 (B00000001)
#define BIT_REQ2 (B00000010)
#define BIT_REQ3 (B00000100)
#define BIT_REQ4 (B00001000)
#define BIT_SUM4 (B00001111)

#define MASK_REQ1(input) (input & BIT_REQ1)
#define MASK_REQ2(input) (input & BIT_REQ2)
#define MASK_REQ3(input) (input & BIT_REQ3)
#define MASK_REQ4(input) (input & BIT_REQ4)

#define MASK_RELAY1(input) (input & BIT_REQ1)
#define MASK_RELAY2(input) (input & BIT_REQ2)
#define MASK_RELAY3(input) (input & BIT_REQ3)
#define MASK_RELAY4(input) (input & BIT_REQ4)

#define ONEBYTE_MAX (0xFF)
#define MIN2MS(tim_min) (tim_min * 60 * 1000)

#define EEPROM_USE (OFF)
#define NVM_ADDR (0x00)
#define NVM_NODATA (ONEBYTE_MAX)

//Function prottype
void Relay_SetEach4(int , int , int , int );
void Relay_SetALL(int);
void Relay_SetALLOFF();
void Led_BlinkSec(int);
void Led_BlinkFastSec(int);
void NvM_Write(unsigned char);

//Pin assign
const int Relay1_Pin =  2;
const int Relay2_Pin =  3;
const int Relay3_Pin =  4;
const int Relay4_Pin =  5;

//Relay timeout
const long unsigned int Relay_timeout_min = 60;

//Req Relay type (Mapping Req and Relay (NO or NC))
const int Relay1_def =  REQON_RELAYOFF;
const int Relay2_def =  REQON_RELAYOFF;
const int Relay3_def =  REQON_RELAYON;
const int Relay4_def =  REQON_RELAYON;

unsigned char NVM_RAM;

//Init func
void setup() {

  Serial.begin( 9600 );
  pinMode(Relay1_Pin, OUTPUT);
  pinMode(Relay2_Pin, OUTPUT);
  pinMode(Relay3_Pin, OUTPUT);
  pinMode(Relay4_Pin, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);

#if EEPROM_USE == ON
  // Read latest Relay status
  NVM_RAM = EEPROM.read(NVM_ADDR);

  if ((NVM_RAM != NVM_NODATA) && (NVM_RAM <= BIT_SUM4)) {
    // Valid data
    Relay_SetEach4(MASK_RELAY1(NVM_RAM), MASK_RELAY2(NVM_RAM), MASK_RELAY3(NVM_RAM), MASK_RELAY4(NVM_RAM));
  } else {
    // Invalid data
    Relay_SetALLOFF();
    Led_BlinkFastSec(3);
  }
#else
  Relay_SetALLOFF();
  Led_BlinkFastSec(3);
#endif

}

void loop() {
  unsigned char data = 0;

  //Wait for receiving data
  while ( Serial.available() ) {

    //Read Data untill new line character
    String input_str = Serial.readStringUntil(0x0A);

    //Convert ASCII to Integer
    int input_int = input_str.toInt();

    //Use only Integer
    if ((input_str == "0" || input_int != 0) && (input_int < ONEBYTE_MAX)) {  // Distinguish Strings and Integer

      // sendback to PC
      Serial.print(input_int);
      // Manage received Request
      Manage_request(input_int);

      // put RelayOFF timer (1hour)
      MsTimer2::stop();
      MsTimer2::set(MIN2MS(Relay_timeout_min), Relay_SetALLOFF); // keep Relay on 1 hour
      MsTimer2::start();

      //Led low frequency blinking
      Led_BlinkSec(3);
    } else {
      //Exception case (Recevive data is Not mumerical value)
      Serial.print("Out of Range : " + input_int);
      //Relay OFF
      Relay_SetALLOFF();
      //Blink LED
      Led_BlinkSec(3);
    }
  }
}

void Manage_request(int input_int) {
  int rcv_req1 = OFF;
  int rcv_req2 = OFF;
  int rcv_req3 = OFF;
  int rcv_req4 = OFF;

  int rev_rcv_req1 = ON;
  int rev_rcv_req2 = ON;
  int rev_rcv_req3 = ON;
  int rev_rcv_req4 = ON;

  int req_Relay1 = OFF;
  int req_Relay2 = OFF;
  int req_Relay3 = OFF;
  int req_Relay4 = OFF;

  // extract request
  rcv_req1 = MASK_REQ1(input_int) != 0 ? ON : OFF;
  rcv_req2 = MASK_REQ2(input_int) != 0 ? ON : OFF;
  rcv_req3 = MASK_REQ3(input_int) != 0 ? ON : OFF;
  rcv_req4 = MASK_REQ4(input_int) != 0 ? ON : OFF;

  // make inverted request
  rev_rcv_req1 = (rcv_req1 == ON) ? OFF : ON;
  rev_rcv_req2 = (rcv_req2 == ON) ? OFF : ON;
  rev_rcv_req3 = (rcv_req3 == ON) ? OFF : ON;
  rev_rcv_req4 = (rcv_req4 == ON) ? OFF : ON;

  // decide Relay ON or OFF by Recieved request
  req_Relay1 = (Relay1_def == REQON_RELAYON) ? rcv_req1 : rev_rcv_req1;
  req_Relay2 = (Relay2_def == REQON_RELAYON) ? rcv_req2 : rev_rcv_req2;
  req_Relay3 = (Relay3_def == REQON_RELAYON) ? rcv_req3 : rev_rcv_req3;
  req_Relay4 = (Relay4_def == REQON_RELAYON) ? rcv_req4 : rev_rcv_req4;

  //Control relay
  Relay_SetEach4(req_Relay1, req_Relay2, req_Relay3, req_Relay4);
}

void Relay_SetEach4(int req_Relay1, int req_Relay2, int req_Relay3, int req_Relay4) {
  unsigned char raw_req = 0xFF;

  // LOW = Relay-ON, HIGH = Relay-OFF
  digitalWrite(Relay1_Pin, (req_Relay1 != OFF) ? LOW : HIGH);
  digitalWrite(Relay2_Pin, (req_Relay2 != OFF) ? LOW : HIGH);
  digitalWrite(Relay3_Pin, (req_Relay3 != OFF) ? LOW : HIGH);
  digitalWrite(Relay4_Pin, (req_Relay4 != OFF) ? LOW : HIGH);

  //Store data to EEPROM
  raw_req = (unsigned char)((BIT_REQ1 * req_Relay1) + (BIT_REQ2 * req_Relay2) + (BIT_REQ3 * req_Relay3) + (BIT_REQ4 * req_Relay4));
  NvM_Write(raw_req);
}

void Relay_SetALL(int val) {
  Relay_SetEach4(val, val, val, val);
}

void Relay_SetALLOFF() {
  Relay_SetEach4(OFF, OFF, OFF, OFF);
}

void Led_BlinkSec(int sec) {
  for (int i = 0; i < sec; i++) {
    digitalWrite(LED_BUILTIN, LOW);
    delay(300);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(700);
    digitalWrite(LED_BUILTIN, LOW);
  }
}
void Led_BlinkFastSec(int sec) {
  for (int i = 0; i < (sec * 20); i++) {
    digitalWrite(LED_BUILTIN, LOW);
    delay(25);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(25);
    digitalWrite(LED_BUILTIN, LOW);
  }
}

void NvM_Write(unsigned char Relay_req) {
  if (Relay_req != NVM_RAM) {

#if EEPROM_USE == ON
    EEPROM.update(NVM_ADDR, Relay_req);
#endif

    NVM_RAM = Relay_req;
  } else {
    // No need to update
  }
}
