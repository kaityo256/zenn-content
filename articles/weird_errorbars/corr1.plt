set term pngcairo
set out "corr1.png"

set log x
set xlabel "n"
set ylabel "Data"

p [8:] "corr1.dat" w errorbars pt 6

unset key
set out "corr1_line.png"
p [8:] "corr1.dat" w errorbars pt 6, 0.5 lt 1 lc "black"
