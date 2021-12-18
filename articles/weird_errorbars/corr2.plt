set term pngcairo
set out "corr2.png"

set log x
set xlabel "n"
set ylabel "Data"

p [8:] "corr2.dat" w errorbars pt 6

unset key
set out "corr2_line.png"

p [8:] "corr2.dat" w errorbars pt 6, 0.5 lt 1 lc "black"
