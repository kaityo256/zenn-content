# frozen_string_literal: true

def check(cpp, n_dim)
  astr = '[1]' * n_dim
  s = <<"CPPSRC"
  #include <cstdio>
  #include <typeinfo>
  int a#{astr};
  int main(){
    printf("%s\\n",typeid(a).name());
    //printf("%d\\n",sizeof(a));
  }
CPPSRC
  File.open('test.cc', 'w') do |f|
    f.puts s
  end
  #if system("g++-14 test.cc 2> /dev/null")
  if system("#{cpp} test.cc 2> /dev/null") 
    puts "#{n_dim} OK"
    false
  else
    puts "#{n_dim} NG"
    true
  end
end

def check_clang
  (10_000..20_000).bsearch do |n|
    check('clang++',n)
  end
end

def check_gcc
  (10_000..1_000_000).bsearch do |n|
    check('g++-14', n)
  end
end

def keisoku
    n = 1000
    for i in 1..10 do
      start_time = Time.now
      check("g++", n)
      end_time = Time.now
      puts "#{n} #{end_time - start_time}"
      n *= 2
    end
end

# check_clang
# check_gcc

# check('g++-14', 320_000)

# check('g++',100)