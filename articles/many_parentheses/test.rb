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
  return system("icpc test.cpp")
end

check(ARGV[0].to_i)
