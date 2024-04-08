#!/bin/sh
# The next line restarts using nmrWish \
exec nmrWish "$0" -- "$@"

message .msg -relief raised -bg blue -fg white \
 -width 30c -text "Detecting Peaks ..."

pack    .msg
update

set tabName  test.tab
set specName ./test.ft2
set tabCount 1

set tabDir [file dirname $tabName]

if {![file exists $tabDir]} {file mkdir $tabDir}


set thisSpecName $specName
set thisTabName  $tabName

set x1      1
set xN      1515
set xInc    1515
set xExtra  2
set xLast   [expr $xN + $xExtra + 1]

set y1      1
set yN      1024
set yInc    1024
set yExtra  2
set yLast   [expr $yN + $yExtra + 1]

    set yFirst  $y1

while {$yFirst <= 1 + $yN - $yExtra} \
   {
    set yNext [expr $yFirst+$yInc+2*$yExtra-1]
    if {$yNext > $yLast} {set yNext $yLast}

    set xFirst  $x1

while {$xFirst <= 1 + $xN - $xExtra} \
   {
    set xNext [expr $xFirst+$xInc+2*$xExtra-1]
    if {$xNext > $xLast} {set xNext $xLast}

    readROI -roi 1 \
       -ndim 2 -in $thisSpecName \
       -x X_AXIS $xFirst $xNext           \
       -y Y_AXIS $yFirst $yNext           \
       -verb

    pkFindROI -roi 1 \
      -sigma 40942.3 -pChi 0.0001 -plus 1.27098e+06 -minus -1.27098e+06 \
      -dx        2     2 \
      -idx       2     2 \
      -tol    4.00  4.00 \
      -hiAdj  1.20  1.80 \
      -lw    15.00  0.00 \
       -sinc -mask -out $thisTabName -verb

    set xFirst [expr 1 + $xNext - 2*$xExtra]
   }
    set yFirst [expr 1 + $yNext - 2*$yExtra]
   }

exit
