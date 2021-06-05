set term pngcairo
set output "atoms_pure.png"
unset key
splot "atoms_pure.dat" pt 6
