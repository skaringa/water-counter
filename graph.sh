#!/bin/sh
rrdtool graph counter.gif \
  -s 'now -1 day' -e 'now' \
  -w 800 -h 600 \
  -A -Y \
  DEF:counter=water.rrd:counter:LAST \
  VDEF:lastcount=counter,LAST \
  "GPRINT:lastcount:%6.3lf m³" \
  LINE2:counter#000000:"Zählerstand [m³]"
display counter.gif&
rrdtool graph consum.gif \
  -s 'now -1 day' -e 'now' \
  -w 800 -h 600 \
  DEF:consum=water.rrd:consum:AVERAGE \
  CDEF:consumltr=consum,60000,* \
  CDEF:conpd=consumltr,60,*,24,* \
  VDEF:conpdtotal=conpd,AVERAGE \
  "GPRINT:conpdtotal:Total %4.0lf l/d" \
  LINE2:consumltr#00FF00:"Verbrauch [l/min]" 
display consum.gif&
