set term pngcairo
set output "gcc.png"

set xlabel "Dimension"
set ylabel "Time"
unset key
set log xy

p [:1e6] "test.dat" pt 6,1e-8*x**2 lc "black"
