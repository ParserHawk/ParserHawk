from z3 import *

# Create an integer variable x
x = Int('x')

# Define the two functions f(x) and g(x) as expressions
f_x = x + 1
g_x = 2 * x

# Create the solver
solver = Solver()

# Add the constraint that f(x) should not be equal to g(x)
solver.add(f_x != g_x)

# Check if there's a solution where f(x) != g(x)
if solver.check() == sat:
    model = solver.model()
    print("Counterexample found:")
    print(model)
else:
    print("No counterexample found, f(x) is always equal to g(x).")
