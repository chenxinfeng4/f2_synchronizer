const int LED_PIN = 13;
const int LED_PIN2 = 12;
void setup() {
  // initialize serial communication at 9600 bits per second
  Serial.begin(9600);
  Serial.println("Hello from Arduino-Evt-TTL-tagger");

  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_PIN, OUTPUT);
  pinMode(LED_PIN2, OUTPUT);
  digitalWrite(LED_PIN, LOW);
}

void do_action(char act_code) {
  // doing something
  if(act_code == 'a'){
    Serial.println("Hello from Arduino-Evt-TTL-tagger");
  }
  else if(act_code == 'b'){
    Serial.println("Doing.");
    digitalWrite(LED_PIN2, HIGH);
    delay(300);
    digitalWrite(LED_PIN2, LOW);
  }
  else if(act_code == 'c'){
    Serial.println("Doing.");
    digitalWrite(LED_PIN2, HIGH);
    delay(100);
    digitalWrite(LED_PIN2, LOW);
    delay(50);
    digitalWrite(LED_PIN2, HIGH);
    delay(100);
    digitalWrite(LED_PIN2, LOW);
  }
  else if(act_code == '\r' || act_code == '\n'){
    ;
  }
  else{
    Serial.println("Doing nothing.");
  }
}


void loop() {
  // read the serial input
  while(Serial.available()){
    char act_code = Serial.read();
    do_action(act_code);
  }
}