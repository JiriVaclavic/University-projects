# Autonomous Hive Project

This project aims to create an electronically controlled autonomous beehive, initially designed using Arduino, but now updated to use the ESP32 microcontroller and the L293D motor driver. The primary objective is to create a low-cost, easily manufactured beehive system equipped with electronic monitoring and automation capabilities. The system is designed to minimize interventions in the beekeeping process and reduce stress on the bee colony.

## Project Overview

The Autonomous Hive integrates various sensors and motorized mechanisms to perform key tasks such as honey harvesting and hive ventilation. Sensor data is collected and visualized on a web-based interface using MQTT communication.

### Key Features

- **ESP32 Microcontroller:** Replacing the original Arduino setup, the project now uses the more powerful ESP32 to provide Wi-Fi capabilities and handle more complex tasks.
- **L293D Motor Driver:** The project now uses the L293D motor driver to control the motorized frames within the hive, which enables automated honey collection.
- **Integrated Sensors:** Temperature, humidity, and weight sensors are used to monitor hive conditions in real time.
- **Web-based Dashboard:** The collected data is sent to a web-based server and visualized using the ThingsBoard IoT platform.

## Hardware Components

- **ESP32 Microcontroller**
- **L293D Motor Driver**
- **Temperature and Humidity Sensors (DHT22)**
- **Weight Sensors**
- **Stepper Motors**
- **Custom 3D-printed Components**

## Software Overview

The project includes firmware for the ESP32, which handles sensor data collection, motor control, and communication with the web server. The code is structured to:

1. Collect data from all connected sensors.
2. Control motor movements for honey harvesting.
3. Send data to the web server via MQTT protocol.
4. React to commands received from the web server for automated hive management.

## Installation

1. **Hardware Setup:**
   - Connect the sensors and L293D motor driver to the ESP32 as specified in the wiring diagram.
   - Mount the stepper motors on the frames for honey extraction.

2. **Software Setup:**
   - Upload the `DIPLOMKA-OPONENT.ino` code to the ESP32 using the Arduino IDE or PlatformIO.
   - Ensure the correct libraries are installed:
     - `WiFi.h` for ESP32
     - `PubSubClient.h` for MQTT communication
     - `DHT.h` for temperature and humidity readings

3. **Server Setup:**
   - Configure the MQTT broker and the ThingsBoard dashboard to receive and visualize data.

## Changes from Previous Version

The previous version of this project utilized Arduino as the primary microcontroller and did not include the L293D motor driver for frame control. This has now been updated to the ESP32 platform for improved performance and expanded capabilities, such as enhanced connectivity and motor control through the L293D driver.

## Future Improvements

- Integration with additional environmental sensors.
- Implementation of more advanced honey harvesting mechanisms.
- Enhanced power management to ensure energy efficiency.

## Author

- **Jiří Václavič** - *Master’s Thesis at Brno University of Technology, Faculty of Information Technology*
- **URL** - https://hdl.handle.net/11012/248900
