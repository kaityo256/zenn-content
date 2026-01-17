set term png
set out "langevin.png"

set xla "t"
set yla "v"

p "langevin.dat" w e pt 6
