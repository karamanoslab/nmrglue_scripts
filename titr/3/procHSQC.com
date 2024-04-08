#!/bin/csh

bruk2pipe -in ./ser \
  -bad 0.0 -ext -aswap -AMX -decim 1584 -dspfvs 20 -grpdly 67.987060546875  \
  -xN              1024  -yN               256  \
  -xT               512   -yT              128  \
  -xMODE            DQD  -yMODE    States-TPPI  \
  -xSW         8116.833 -ySW          1702.820  \
  -xOBS         600.102  -yOBS          60.814  \
  -xCAR           4.696  -yCAR         121.500  \
  -xLAB              HN  -yLAB             15N  \
  -ndim               2  -aq2D          States  \
  -out ./test.fid -verb -ov


  nmrPipe -in ./test.fid \
| nmrPipe  -fn POLY -time                            \
#| nmrPipe  -fn SOL                                        \
| nmrPipe -fn GMB -gb 0.25 -lb -20 -c 0.5                  \
#| nmrPipe -fn SP -off 0.50 -end 0.95 -pow 2 -c 0.5        \
#| nmrPipe -fn GMB -gb 0.35 -lb -30 -c 0.5                  \
| nmrPipe -fn ZF -size 4096 -verb                         \
| nmrPipe -fn FT -auto -verb                              \
| nmrPipe -fn PS -p0  -53.2  -p1 0.0 -di                    \
| nmrPipe -fn EXT -x1 11.0ppm -xn 6.0ppm -sw -verb          \
| nmrPipe -fn TP                                          \
#| nmrPipe -fn SMILE -xT -xP0 -xP1                                \
| nmrPipe -fn SP -off 0.5 -end 0.95 -pow 2 -c 0.5         \
| nmrPipe -fn ZF -size 1024 -verb                         \
| nmrPipe -fn FT -auto -verb                                    \
| nmrPipe -fn PS -p0 -90.0 -p1 180.0 -di                      \
| nmrPipe -fn POLY -auto -ord 2                           \
#| nmrPipe -fn REV                                         \
| nmrPipe -fn TP                                          \
| nmrPipe -fn POLY -auto -ord 2                           \
     -verb -ov -out test.ft2

