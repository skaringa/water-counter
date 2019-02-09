#!/usr/bin/python -u
#
# wairc.py
# 
# Program to read the water counter using a reflective light sensor
# This is the data recording part running on a Raspberry Pi.
# It retrieves data from the Arduino over serial and stores
# counter and consumption values into a round robin database.

# Copyright 2015-16 Martin Kompf
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import sys
import os
import re
import argparse
import serial
import rrdtool

# Serial port of arduino
#port = '/dev/ttyAMA0'
port = '/dev/serial0'

# counter unit: 1 revolution = x m^3
trigger_step = 0.001

# Path to RRD with counter values
count_rrd = "%s/water.rrd" % (os.path.dirname(os.path.abspath(__file__)))


# Create the Round Robin Database
def create_rrd():
  print 'Creating RRD: ' + count_rrd
  # Create RRD to store counter and consumption:
  # Counter is GAUGE (m^3)
  # Consumption is ABSOLUTE (m^3/s)
  # 1 value per minute for 3 days
  # 1 value per day for 30 days
  # 1 value per week for 10 years
  # Consolidation LAST for counter
  # Consolidation AVERAGE for consumption
  try:
    rrdtool.create(count_rrd, 
      '--no-overwrite',
      '--step', '60',
      'DS:counter:GAUGE:86400:0:1000000',
      'DS:consum:ABSOLUTE:86400:0:1000000',
      'RRA:LAST:0.5:1:4320',
      'RRA:AVERAGE:0.5:1:4320',
      'RRA:LAST:0.5:1440:30',
      'RRA:AVERAGE:0.5:1440:30',
      'RRA:LAST:0.5:10080:520',
      'RRA:AVERAGE:0.5:10080:520')
  except Exception as e:
    print 'Error ' + str(e)

# Get the last counter value from the rrd database
def last_rrd_count():
  val = 0.0
  handle = os.popen("rrdtool lastupdate " + count_rrd)
  for line in handle:
    m = re.match(r"^[0-9]*: ([0-9.]*) [0-9.]*", line)
    if m:
      val = float(m.group(1))
      break
  handle.close()
  return val

# Main
def main():
  # Check command args
  parser = argparse.ArgumentParser(description='Program to read the water meter using a reflective light sensor.')
  parser.add_argument('-c', '--create', action='store_true', default=False, help='Create rrd database if necessary')
  args = parser.parse_args()

  if args.create:
    create_rrd()

  # Open serial line
  ser = serial.Serial(port, 9600)
  if not ser.isOpen():
    print "Unable to open serial port %s" % port
    sys.exit(1)

  trigger_state = 0
  counter = last_rrd_count()
  print "restoring counter to %f" % counter

  while(1==1):
    # Read line from arduino and convert to trigger value
    line = ser.readline()
    line = line.strip()

    old_state = trigger_state
    if line == '1':
      trigger_state = 1
    elif line == '0':
      trigger_state = 0
    if old_state == 1 and trigger_state == 0:
      # trigger active -> update count rrd
      counter += trigger_step
      update = "N:%.3f:%.3f" % (counter, trigger_step)
      #print update
      rrdtool.update(count_rrd, update)

if __name__ == '__main__':
  main()
