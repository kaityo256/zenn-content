#include <vector>

struct Callee;

class Caller {
public:
  void add(Callee *c) {
    v.push_back(c);
  }
  void call_all();
  static Caller &get_instance();

private:
  std::vector<Callee *> v;
  Caller(){};
};

struct Callee {
  virtual void func() = 0;
  Callee() {
    Caller::get_instance().add(this);
  }
};
