#include <MsTimer2.h>

#define ON 1
#define OFF 0

#define ReqON_RelayON 1
#define ReqON_RelayOFF 0

void Relay_SetEach4(int , int , int , int );
void Relay_SetALL(int);
void Relay_SetALLOFF();

//Pin assign
const int Relay1_Pin =  2;
const int Relay2_Pin =  3;
const int Relay3_Pin =  4;
const int Relay4_Pin =  5;

//Req Relay type (Mapping Req and Relay (NO or NC))
const int Relay1_def =  ReqON_RelayOFF;
const int Relay2_def =  ReqON_RelayOFF;
const int Relay3_def =  ReqON_RelayON;
const int Relay4_def =  ReqON_RelayON;

void setup() {
  Serial.begin( 9600 );
  pinMode(Relay1_Pin, OUTPUT);
  pinMode(Relay2_Pin, OUTPUT);
  pinMode(Relay3_Pin, OUTPUT);
  pinMode(Relay4_Pin, OUTPUT);
  Relay_SetALLOFF();
}

void loop() {

  int Is_received;

  while ( Serial.available() ) {
    String input_str = Serial.readStringUntil(10);

    int input_int = input_str.toInt();
    if (input_str == "0" || input_int != 0) {
      // if integer is receivced
      
      // sendback to PC
      Serial.print(input_int);
      // control Relay
      Manage_request(input_int);

      // put RelayOFF timer (1hour)
      MsTimer2::stop();
      MsTimer2::set(3600000, Relay_SetALLOFF); // keep Relay on 1 hour
      MsTimer2::start();
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
  rcv_req1 = (input_int & B00000001) != 0 ? ON : OFF;
  rcv_req2 = (input_int & B00000010) != 0 ? ON : OFF;
  rcv_req3 = (input_int & B00000100) != 0 ? ON : OFF;
  rcv_req4 = (input_int & B00001000) != 0 ? ON : OFF;

  // make inverted request
  rev_rcv_req1 = (rcv_req1 == ON) ? OFF : ON;
  rev_rcv_req2 = (rcv_req2 == ON) ? OFF : ON;
  rev_rcv_req3 = (rcv_req3 == ON) ? OFF : ON;
  rev_rcv_req4 = (rcv_req4 == ON) ? OFF : ON;

  // decide Relay ON or OFF by Recieved request
  req_Relay1 = (Relay1_def == ReqON_RelayON) ? rcv_req1 : rev_rcv_req1;
  req_Relay2 = (Relay2_def == ReqON_RelayON) ? rcv_req2 : rev_rcv_req2;
  req_Relay3 = (Relay3_def == ReqON_RelayON) ? rcv_req3 : rev_rcv_req3;
  req_Relay4 = (Relay4_def == ReqON_RelayON) ? rcv_req4 : rev_rcv_req4;

  //Control relay
  Relay_SetEach4(req_Relay1, req_Relay2, req_Relay3, req_Relay4);
}

void Relay_SetEach4(int req_Relay1, int req_Relay2, int req_Relay3, int req_Relay4) {

  // LOW = Relay-ON, HIGH = Relay-OFF
  digitalWrite(Relay1_Pin, (req_Relay1 != OFF) ? LOW : HIGH);
  digitalWrite(Relay2_Pin, (req_Relay2 != OFF) ? LOW : HIGH);
  digitalWrite(Relay3_Pin, (req_Relay3 != OFF) ? LOW : HIGH);
  digitalWrite(Relay4_Pin, (req_Relay4 != OFF) ? LOW : HIGH);

}

void Relay_SetALL(int val) {
  Relay_SetEach4(val, val, val, val);
}

void Relay_SetALLOFF() {
  Relay_SetEach4(OFF, OFF, OFF, OFF);
}
