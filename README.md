# water-counter
Monitor a water meter with Arduino and infrared light sensor to capture counter value and consumption of water.

![Water meter with infrared light barrier](https://www.kompf.de/tech/images/watir.jpg)


The software consists of two parts:

* Data acquisition part running on an Arduino Pro Mini. It controls the infrared light barrier, detects trigger levels and communicates with the Raspberry Pi over serial connection.
* Data recording part running on a the Raspberry Pi. It retrieves the data from the Arduino over serial port and stores counter and consumption values into a round robin database.

There is a blog in german language that explains use case and function: [Infrarot Lichtschranke mit Arduino und Raspberry Pi zum Auslesen des Wasserzählers](https://www.kompf.de/tech/watir.html).


## Commands from host (RasPi) to Arduino

* __D__ - retrieve and print raw data
* __T__ - enter trigger mode and print trigger data (0/1)
* __S__ _low_ _high_ - Set trigger levels (e.g. 85 90)
* __C__ - Cancel data acquisition and enter command mode

Arduino is in trigger mode upon start - Send __C__ to enter command mode

## Schematics

![Schematics](https://www.kompf.de/tech/images/reflsensormini.png)


## Construction

![Construction](https://www.kompf.de/tech/images/watraspi.jpg)
