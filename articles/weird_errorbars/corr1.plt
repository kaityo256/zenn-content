set term pngcairo
set out "corr1.png"

set log x
set xlabel "n"
set ylabel "Data"

p [8:] "corr1.dat" w errorbars pt 6
