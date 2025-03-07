set term pngcairo
set out "md.png"

f(x) = (a-b)*exp(-x/c)+b
a = 0.5
b = 0.8
c = 100

fit [50:] f(x) "temp.dat" via a,b,c

unset key
set xlabel "Time"
set ylabel "Temperature"
p "temp.dat" pt 6, f(x) lw 2.0 lc "black"
