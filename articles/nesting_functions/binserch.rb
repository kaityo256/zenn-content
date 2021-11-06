def make_src(n)
  str = <<"EOS"
  int f(int i) { return i; }
  int hoge() { return #{'f('*n}f(1)#{')'*n}; }
EOS
    File.open("test.c","w") do |f|
    f.puts(str)
    end
end

def check(n)
  make_src(n)
  return !system("gcc -O3 -S test.c 2> /dev/null")
end

n = (10..100000).bsearch {|n| check(n)}
puts "GCC dies by #{n} times nested functions."
