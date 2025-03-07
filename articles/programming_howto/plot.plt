set term pngcairo
set out "L16.png"

set style data linespoints
set xlabel "p"
set ylabel "P"

p "L16.dat" pt 6

set out "finite_size.png"

p "L08.dat" pt 6 t "L= 8"\
, "L16.dat" pt 6 t "  16"\
, "L32.dat" pt 6 t "  32"\
