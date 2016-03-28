#!/bin/sh
rrdtool graph counter.gif \
  -s 'now -20 hour' -e 'now' \
  -X 0 -A \
  DEF:counter=water.rrd:counter:LAST \
  LINE2:counter#000000:"Zählerstand [m³]"
display counter.gif&
rrdtool graph consum.gif \
  -s 'now -20 hour' -e 'now' \
  DEF:consum=water.rrd:consum:AVERAGE \
  CDEF:consumltr=consum,60000,* \
  LINE2:consumltr#00FF00:"Verbrauch [l/min]" 
display consum.gif&
