from algorithms.Constrained_searching.AC_3 import ac3, CSP
from algorithms.Constrained_searching.Backtracking import backtracking

def backtracking_with_ac3(start_state, goal_state):
    variables = [f'X{i}' for i in range(9)]
    domains = {var: [str(i) for i in range(9)] for var in variables}
    neighbors = {var: set(variables) - {var} for var in variables}
    constraints = []
    csp = CSP(variables, domains, constraints, neighbors)

    for i, val in enumerate(start_state):
        domains[variables[i]] = [val]

    if not ac3(csp):
        return None, 0, 0, 0

    return backtracking(start_state, goal_state)
