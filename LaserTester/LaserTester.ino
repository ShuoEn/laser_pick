#include <Wire.h>
#include <EEPROM.h>
#include <Digital_Light_TSL2561.h>
#define ADDR 3
#define LED 5
#define LASER_PIN 6
#define uart Serial 

uint16_t targetBrightness = 200;
uint8_t power = 0;
bool ready = true;

void setup() {
  // put your setup code here, to run once:
  Wire.begin();
  Serial.begin(115200);
  uart.setTimeout(20);
  TSL2561.init();
  pinMode(LED, OUTPUT);
  pinMode(LASER_PIN, OUTPUT);
  analogWrite(LED, power);
  digitalWrite(LASER_PIN, HIGH);
  targetBrightness = getBrightness();
  setBrightness(100);
  analogWrite(LED, 80);
}

void loop() {
    static uint8_t stable = 0;
    
    //uint16_t currentBrightness = TSL2561.readVisibleLux();
    if (uart.available() > 0 && ready) {
        if (uart.find("tool "))
        {
            String mode = uart.readStringUntil(' ');
            if (mode == "set")
            {
                String cmd = uart.readStringUntil(' ');
                uint16_t input = 0;
                input = uart.parseInt();
                if (input > 0 && input < 60000)
                {
                    setBrightness(input);
                    stable = 0;
                    uart.print(input + "ok\n");
                }

            }
            else if (mode == "ping")
            {
                uart.print("pong\n");
            }
            else if (mode == "read")
            {

                Serial.print("LED Power:");
                Serial.print(power);
                Serial.print("\tCurrent Brightness:");
                //Serial.print(currentBrightness);
                Serial.print("\tTarget Brightness:");
                Serial.println(targetBrightness);
            }
            else if (mode == "laser_on")
            {
                digitalWrite(LASER_PIN, HIGH);
                uart.print("ok\n");
            }
            else if (mode == "laser_off")
            {
                digitalWrite(LASER_PIN, LOW);
                uart.print("ok\n");
            }else if (mode == "set_pwm")
            {
                //String cmd = uart.readStringUntil(' ');
                int input = 0;
                input = uart.parseInt();
                if (input >= 0 && input <= 255)
                {
                    analogWrite(LED, input);
                    uart.print(input + " ok\n");
                }

            }
        }

    }
    
    //if (stable > 10) {
    //    ready = true;
    //    return;
    //}
    //    
    //if (abs(currentBrightness - targetBrightness) < 10)
    //    stable++;
    //if (currentBrightness > targetBrightness)
    //    power--;
    //else if (power < 255)
    //    power++;
    //analogWrite(LED, power);
    //
    //delay(20);
  

}

void setBrightness(uint16_t val)
{
  targetBrightness = val;
  EEPROM.write(ADDR, val >> 8);
  EEPROM.write(ADDR + 1, val & 0xFF);
}

uint16_t getBrightness()
{
  return (EEPROM.read(ADDR) << 8) + EEPROM.read(ADDR + 1);
}

