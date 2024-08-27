from z3 import *

# Create a Z3 solver
solver = Solver()

# Define a global Z3 integer variable
x = Int('x')

# Define a function f(x) = x + 1
f = Function('f', IntSort(), IntSort())

# Add a constraint that f(x) should equal x + 1
solver.add(ForAll([x], f(x) == x + 1))

# Create another global variable y
y = Int('y')

y = f(x)
y = f(y)
y = f(y)

# # Use the function to modify the value of y
# solver.add(y == f(x))

# Add a constraint to solve for x when y = 10
solver.add(y == 10)

# Check if the constraints are satisfiable
if solver.check() == sat:
    model = solver.model()
    print("x:", model[x])
    # print("y:", model[y])
    print("f(x):", model.eval(f(x)))
else:
    print("Unsatisfiable")
