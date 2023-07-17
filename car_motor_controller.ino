//Pin numbers definition
const int IN1 = 2;
const int IN2 = 3;
const int IN3 = 4;
const int IN4 = 5;
// Right Motor
const int ENA = 9;
// Left Motor
const int ENB = 10;

String input;

void setup() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  Serial.begin(9600);
  Serial.setTimeout(.1);
}

// straight command - both wheels at full speed
void forward() {
  analogWrite(ENA, 210);
  analogWrite(ENB, 210);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

// right command - slow right hand motor, left motor continues at full speed
void right() {
  analogWrite(ENA, 100);
  analogWrite(ENB, 210);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

// right command - slow left hand motor, right motor continues at full speed
void left() {
  analogWrite(ENA, 210);
  analogWrite(ENB, 100);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

// stop - both wheels given 0 rpms
void stop() {
    analogWrite(ENA, 0);
    analogWrite(ENB, 0);
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
}

void loop() {
  if(Serial.available()) {

    input = Serial.readStringUntil('\n');
    input.trim();
    String direction;

    if(input.equals("3")) {
      right();
      delay(100);
      direction = "right";
    } else if(input.equals("2")) {
      left();
      delay(100);
      direction = "left";
    } else if(input.equals("1")) {
      direction = "straight";
      forward();
      delay(100);
    } else if(input.equals("0")) {
      direction = "stop";
      stop();
    }

    // send command from Arduino back to processor for confirmation
    Serial.println(direction);
  }

}