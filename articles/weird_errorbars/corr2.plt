set term pngcairo
set out "corr2.png"

set log x
set xlabel "n"
set ylabel "Data"

p [8:] "corr2.dat" w errorbars pt 6
