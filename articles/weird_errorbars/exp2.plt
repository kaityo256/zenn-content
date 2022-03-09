set term pngcairo
set out "exp2.png"

set xlabel "t"
set ylabel "Data"

p "exp2.dat" w errorbars pt 6

set out "exp2_line.png"

unset key
p "exp2.dat" w errorbars pt 6, exp(-x/3) lt 1 lc "black"
