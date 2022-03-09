set term pngcairo
set out "exp1.png"

set xlabel "t"
set ylabel "Data"

p "exp1.dat" w errorbars pt 6

set out "exp1_line.png"

unset key
p "exp1.dat" w errorbars pt 6, exp(-x/3) lt 1 lc "black"

