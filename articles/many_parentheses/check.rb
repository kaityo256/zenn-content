def check(n)
  s1 = "("*n
  s2 = ")"*n
  open("test.cpp","w") do |f|
  f.puts <<EOS
#include <cstdio>
int main(){
#{s1}printf("Hello World\\n")#{s2};
}
EOS
  end
  if system("clang++ -fbracket-depth=10000 test.cpp 2> /dev/null")
    puts "#{n} OK"
    false
  else
    puts "#{n} NG"
    true
  end
end

(1000..10000).bsearch do |n| 
  check(n)
end
