# Thermal Comfort Dashboard

This utility is designed as a part of python course project.

> The objective of this utility is to have a tool that would estimate thermal comfort a person based upon ASHRAE 55 standard.

The utility collects live temperature, humidity and CO2 data from a sensor connected to the system via USB.
In this case the sensor is a custom device based on STM32 microcontroller and sensirion SCD40 sensor.

The communication protocol used over UART is modbus.
Register address 0 to 5 are used as data from device address 0(STM32).

***Note:***
STM32 nucleo series of boards have UART access of MCU to connected debugger. This feature makes it possible to power the device and get data wothout much complexity

***Assumptions:***
1. sensation is figured out using PMV_PPD method. Mean Radiant Temperature is assumed to be 25 C.
2. Readings are assumed to be accurate. But device may need to be calibrated externally.


### Installation Steps

> pip install pymodbus

> pip install pymodbus[serial]

> pip install pythermalcomfort

***Note:*** pythermalcomfort package needs ***python version 3.9 to 3.12***

> pip install matplotlib


### How to run

> python main.py

### User Interface

![Screenshot of UI](images/ui.jpg)

### Connection of Hardware

![plug USB into PC](https://www.dmcinfo.com/Portals/0/STM32%20Nucleo%20Development%20Board%20and%20USB%20Mini%20B%20Cable_1.jpg)

### Verify hardware is detected
![device manager should have STMicro](images/detect1.jpg)
![device manager should have STMicro](images/detect2.jpg)
