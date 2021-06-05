set term pngcairo
set output "atoms_defect.png"
unset key
splot "atoms_defect.dat" pt 6
