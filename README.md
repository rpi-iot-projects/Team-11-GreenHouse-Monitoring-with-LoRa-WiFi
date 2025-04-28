# Team-11-GreenHouse-Monitoring-with-LoRa

This project monitors the greenhouse environment parameters located in remote and distant places using LoRa communication

## Table of contents
- [Overview]
- [Hardware components]
- [Software and dependencies]
- [Usage]
- [Results and Demonstration]

## Overview
Our objective is to connect the remote and isolated sensors to the internet.
There are many outdoor applications where sensors need to be deployed in the fields, typically far away from Wi-Fi access and several hundreds of meters apart. Connecting these sensors to cloud server for monitoring applications is challenging. Remote greenhouses is one example, which this project is trying to solve. We will use LoRa communication protocol, a long-range low data rate communication protocol suited for IOT applications. In Line-of-sight applications, the range can reach few kilometers as well. The sensor data from greenhouse is transmitted to gateway (home), where there is easy Wi-Fi access. Then from here, we can upload the sensor data to cloud server using internet.
Another problem is, with all smart sensors connecting directly to Wi-Fi, the limited number of slots in Wi-Fi routers are being inefficiently used. We will aggregrate multiple sensor data into a single packet, and also connect multiple greenhouses to a single gateway. This way, only one Wi-Fi slot is used (by the gateway). 

The main features of this project are use of LoRa communication and using a single Wi-Fi slot for multiple sensors.

# Hardware components
- Raspberry Pi Model 3 b (used as gateway)
- RP2040 RFM95 (raspberry pi pico with LoRa module)
- DHT11 (temperature and humidity sensor)
- HW-080 (soil moisture sensor)

# Software and dependencies
- python (version= 3.11.2)
- circuitpython (version= 9.2.5)
- Mu editor (version= 1.2.0), for running circuitpython
- Thingsboard cloud server

# Results and demonstration
Demo video (and ppt) link: https://rpi.app.box.com/folder/317046255833?s=932mhb8brdomopio452novqzz9ot1tnb
