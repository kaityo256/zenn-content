set term pngcairo
set out "langevin_raw.png"

set xla "t"
set yla "v"

p "langevin_raw.dat" w l
