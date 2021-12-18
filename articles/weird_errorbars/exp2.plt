set term pngcairo
set out "exp2.png"

set xlabel "t"
set ylabel "Data"

p "exp2.dat" w errorbars pt 6
