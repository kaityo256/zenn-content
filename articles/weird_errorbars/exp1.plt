set term pngcairo
set out "exp1.png"

set xlabel "t"
set ylabel "Data"

p "exp1.dat" w errorbars pt 6
