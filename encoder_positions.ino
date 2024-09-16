#define INPUT_ENCOD_A    21                                // *** MEGA PIN21 (***=adapt with input pin)
#define INPUT_ENCOD_B    20                                // *** MEGA PIN20
#define INPUT_ENCOD_D    2                                 // *** MEGA PIN2 (***=adapt with input pin)
#define INPUT_ENCOD_C    3                                 // *** MEGA PIN3 (***=adapt with input pin)
#define INPUT_ENCOD_E    19                                // *** MEGA PIN19 (***=adapt with input pin)
#define INPUT_ENCOD_F    18                                // *** MEGA PIN18 (***=adapt with input pin)
#define SignalA          B00000001                         // *** MEGA PIN20 = PORT_D  bit0 = B00000001
#define SignalB          B00000010                         // *** MEGA PIN21 = PORT_D  bit1 = B00000010
#define SignalAB         B00000011                         // *** both signals
#define SignalD          B00010000                         // *** MEGA PIN2 = PORT_E  bit4 = B00010000
#define SignalC          B00100000                         // *** MEGA PIN3 = PORT_E  bit5 = B00100000
#define SignalCD         B00110000                         // *** both signals
#define SignalE          B00000100                         // *** MEGA PIN19 = PORT_E  bit2 = B00000100
#define SignalF          B00001000                         // *** MEGA PIN18 = PORT_E  bit3 = B00001000
#define SignalEF         B00001100                         // *** both signals
volatile int             ISRencodPos;                      // encoder 1 position
volatile int             ISRencod2Pos;                     // encoder 2 position
volatile int             ISRencod3Pos;                     // encoder 3 position
int                      encodLastPos;                     // previous position encoder 1
int                      encod2LastPos;                    // previous position encoder 2
int                      encod3LastPos;                    // previous position encoder 3
byte                     LastPort8 = SignalA;              // previous A/B state
byte                     LastPort82 = SignalC;             // previous C/D state
byte                     LastPort9 = SignalE;              // previous E/F state


void setup(void) {                                            
  pinMode(INPUT_ENCOD_A, INPUT_PULLUP);                     // use internal pull-up resistor, pin 21
  pinMode(INPUT_ENCOD_B, INPUT_PULLUP);                     // use internal pull-up resistor, pin 20
  pinMode(INPUT_ENCOD_C, INPUT_PULLUP);                     // use internal pull-up resistor, pin 3
  pinMode(INPUT_ENCOD_D, INPUT_PULLUP);                     // use internal pull-up resistor, pin 2
  pinMode(INPUT_ENCOD_E, INPUT_PULLUP);                     // use internal pull-up resistor, pin 19
  pinMode(INPUT_ENCOD_F, INPUT_PULLUP);                     // use internal pull-up resistor, pin 18
  attachInterrupt(digitalPinToInterrupt(INPUT_ENCOD_A), ExtInt, CHANGE);
  attachInterrupt(digitalPinToInterrupt(INPUT_ENCOD_B), ExtInt, CHANGE);
  attachInterrupt(digitalPinToInterrupt(INPUT_ENCOD_C), ExtInt2, CHANGE);
  attachInterrupt(digitalPinToInterrupt(INPUT_ENCOD_D), ExtInt2, CHANGE);
  attachInterrupt(digitalPinToInterrupt(INPUT_ENCOD_E), ExtInt3, CHANGE);
  attachInterrupt(digitalPinToInterrupt(INPUT_ENCOD_F), ExtInt3, CHANGE);
  Serial.begin(9600);                                       // baud rate of serial port

  // this is the headline for the csv file
  Serial.println(F("Set Name,Argument,SENSOR/ANGLE,SENSOR2/ANGLE,SENSOR3/ANGLE"));
}                                                             


void ExtInt() {                                               // OPTICAL ENCODER ext interrupt pin 20, 21
     byte Port8  =  PIND & SignalAB;                          // *** PIND (PORT INPUT D)  ***for Mega***
      LastPort8 ^=  Port8;
  if (LastPort8 & SignalA)   ISRencodPos++;                   // Rotation -> {ISRencodPos++; Sense = 1;}
  if (LastPort8 & SignalB)   ISRencodPos--;                   // Rotation <- {ISRencodPos--; Sense = 0;}
  if (    Port8 && (Port8 != SignalAB)) Port8 ^= SignalAB;    // (swap A-B)
      LastPort8  =  Port8;                                    // mieux vaut faire court
}
void ExtInt2() {                                              // OPTICAL ENCODER ext interrupt pin 2, 3
     byte Port82  =  PINE & SignalCD;                         // *** PINE (PORT INPUT E)  ***for Mega***
      LastPort82 ^=  Port82;
  if (LastPort82 & SignalC)   ISRencod2Pos++;                 // Rotation -> {ISRencod2Pos++; Sense = 1;}
  if (LastPort82 & SignalD)   ISRencod2Pos--;                 // Rotation <- {ISRencod2Pos--; Sense = 0;}
  if (    Port82 && (Port82 != SignalCD)) Port82 ^= SignalCD; // (swap C-D)
      LastPort82  =  Port82;                                  // mieux vaut faire court
}
void ExtInt3() {                                              // OPTICAL ENCODER ext interrupt pin 18, 19
     byte Port9  =  PIND & SignalEF;                          // *** PIND (PORT INPUT D)  ***for Mega***
      LastPort9 ^=  Port9;
  if (LastPort9 & SignalE)   ISRencod3Pos++;                  // Rotation -> {ISRencod3Pos++; Sense = 1;}
  if (LastPort9 & SignalF)   ISRencod3Pos--;                  // Rotation <- {ISRencod3Pos--; Sense = 0;}
  if (    Port9 && (Port9 != SignalEF)) Port9 ^= SignalEF;    // (swap E-F)
      LastPort9  =  Port9;                                    // mieux vaut faire court
}

void loop(void)                                               // MAIN LOOP
{
  noInterrupts();
    int encodPosition = ISRencodPos;
    int encod2Position = ISRencod2Pos;
    int encod3Position = ISRencod3Pos; 
    unsigned long timestamp = millis();            // timestamp in ms, may have to change sensor and motor parameters in creo to msec
    int SetName = 1;                               // Set Name, value can be anything
  interrupts();

  if (encodLastPos != encodPosition) {             // encoder 1 changes
    encodLastPos = encodPosition;   
  }       
  if (encod2LastPos != encod2Position) {           // encoder 2 changes
    encod2LastPos = encod2Position;
  }
  if (encod3LastPos != encod3Position) {           // encoder 3 changes
    encod3LastPos = encod3Position;
  }
  Serial.print(SetName), Serial.print(F(",")),
  Serial.print(timestamp), Serial.print(F(",")),
  Serial.print(encodPosition/6.666666666), Serial.print(F(",")),
  Serial.print(encod2Position/6.666666666), Serial.print(F(",")),
  Serial.println(encod3Position/6.666666666);
}
