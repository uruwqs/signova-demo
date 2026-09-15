
# SIGNOVA DEMO

This is a computer-only prototype of the Signova smart-glove concept.

## What it demonstrates

Simulated sensor readings from TWO gloves are processed as one combined
feature vector. The program then:

1. receives simulated flex-sensor + IMU values;
2. combines LEFT and RIGHT hand data;
3. classifies the gesture;
4. displays the recognized Russian word;
5. speaks the word through the computer speakers.

The demo currently includes:
- Привет
- Спасибо
- Да
- Нет

## Run

Install Python 3.10+.

Open a terminal in this folder:

    pip install -r requirements.txt

Then:

    python signova.py

## Important

This is an APPROXIMATE DEMO, not yet the final ML system.

The simulated data imitate:
- 5 flex sensors per glove;
- accelerometer axes;
- gyroscope axes.

For the real prototype, `simulate_sensor_frame()` will be replaced by
Bluetooth/serial input from the two ESP32 boards.

The final architecture is:

LEFT glove:
5 flex + MPU-9250/6500 -> ESP32
RIGHT glove:
5 flex + MPU-9250/6500 -> ESP32

Both ESP32 boards -> Bluetooth -> computer
computer -> preprocessing -> ML classifier -> text -> speech

No microphone, speaker, display, Arduino Uno, or separate Bluetooth module
is required on the glove in the first laptop-centered version.
