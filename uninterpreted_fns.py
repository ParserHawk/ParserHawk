from z3 import *

f = Function('f', IntSort(), IntSort())
x, y = Ints('x y')

solver = Solver()
solver.add(ForAll([x], f(x) > 0))  # f is always positive
solver.add(f(1) == 2)
solver.add(f(2) == f(1) + 1)

print(solver.check())
if solver.check() == sat:
    model = solver.model()
    print(model)
