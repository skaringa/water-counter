#!/usr/bin/python -u
#
# catserial.py
#
# Utility to receive raw data values from Arduino and print them to stdout
#

import serial
import sys

# Serial port of arduino
#port = '/dev/ttyAMA0'
port = '/dev/serial0'

# Main
def main():
  # Open serial line
  ser = serial.Serial(port, 9600)
  if not ser.isOpen():
    print("Unable to open serial port %s" % port)
    sys.exit(1)
  # set data mode
  ser.write(b'C\r\n')
  ser.write(b'D\r\n')
  while(1==1):
    # Read line from arduino and print it
    line = ser.readline()
    line = line.strip()
    print(line)

if __name__ == '__main__':
  main()
