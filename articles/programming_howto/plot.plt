set term pngcairo
set out "L16.png"

set style data linespoints
set xlabel "p"
set ylabel "P"

p "L16.dat" pt 6

