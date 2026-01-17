set term png
set out "langevin2.png"

set xla "t"
set yla "v"

p "langevin2.dat" w e pt 6

unset key
set out "langevin2_line.png"

p "langevin2.dat" w e pt 6, 0 lt 1 lc "black"
