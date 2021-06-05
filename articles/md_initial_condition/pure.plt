set term pngcairo
set output "pure.png"
set xlabel "{/Symbol r}"
set ylabel "{/Symbol r}_a"
unset key
p "pure.dat" w l, x
