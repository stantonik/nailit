#define K_SPACE_PIN 2

bool is_pressed = false;
unsigned long last_debounce_time = 0;
const unsigned long debounce_delay = 50;

void setup() 
{
        Serial.begin(9600);
        pinMode(K_SPACE_PIN, INPUT);

        last_debounce_time = millis();
}

void loop() 
{
        unsigned long current_time = millis();

        if (current_time - last_debounce_time > debounce_delay) 
        {
                last_debounce_time = current_time;

                int button_state = digitalRead(K_SPACE_PIN);
                if (button_state == 0 && !is_pressed) 
                {
                                Serial.println((int)(' '));
                                is_pressed = true;
                } 
                else if (button_state == 1 && is_pressed) 
                {
                        is_pressed = false;
                }
        }
}

