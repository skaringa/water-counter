#!/usr/bin/env python

# Script to detect leakages in water consumption by reading the timestamps
# and counter values from a database.
# The script assumes that during a period of some hours of a day should
# be absolute no water consumption.
# The script detects the longest pause of water consumption. If its duration
# is below a given threshold, then a warning message is printed.

import os
import csv
import rrdtool as rrd
from datetime import datetime
from math import *

# Path to RRD with counter values
count_rrd = "{0}/water.rrd".format(os.path.dirname(os.path.abspath(__file__)))

# Alternative: Path to output of rrdtool fetch
count_fetch = "{0}/water.fetch.txt".format(os.path.dirname(os.path.abspath(__file__)))

# Length of the minimum duration without water consumption in seconds 
min_pause = 3 * 60 * 60 # 3 hours

# Verbose output
verbose = True

# Read the rrd specified in count_rrd.
# Returns array of (timestamp, counter).
def read_rrd():
  result = []
  ((start, stop, step), head, data) = rrd.fetch(count_rrd, 'LAST', '-s', 'now - 1 day', '-e', 'now')
  t = start
  for row in data:
    if row[0]:
      result.append((t, row[0])) 
    t += step
  return result

# Read the text file specified in count_fetch.
# The text file is the output of command 'rrdtool fetch'.
# Returns array of (timestamp, counter).
def read_fetch_output():
  result = []
  with open(count_fetch, 'r') as f:
    reader = csv.reader(f, delimiter=' ')
    for row in reader:
      if len(row) == 3:
        value = int(row[0][:-1]), float(row[1])  
        if not isnan(value[1]):
          result.append(value) 
  return result

# Detect all pauses which last longer than min_pause.
# Param data: array of (timestamp, counter)
# Returns array of dictionaries {start, duration}.
def detect_pauses(data):
  result = []
  (start_time, start_counter) = data[0]
  (end_time, end_counter) = data[-1]
  data.append((end_time + 1, end_counter + 1)) # ensure that counter increments
  for (ts, counter) in data:
    if counter > start_counter:
      duration = ts - start_time
      if duration > min_pause:
        result.append({'start' : start_time, 'duration' : duration})
      start_time = ts
      start_counter = counter
  return result

# MAIN
def main():
  #counter = read_fetch_output()
  counter = read_rrd()
  pauses = detect_pauses(counter)
  if verbose:
    for p in pauses:
      print("Pause starting at {0:%Y-%m-%d %H:%M:%S}: {1:.1f} hours"
        .format(datetime.fromtimestamp(p['start']), p['duration']/3600.0))
  if len(pauses) == 0:
    print("Possible leak detected! There is no break of at least {0} hours."
      .format(min_pause/3600.0))

if __name__ == '__main__':
  main()
