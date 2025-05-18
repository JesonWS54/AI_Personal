# algorithms/Constrained_searching/Backtracking.py
import time
import random
from algorithms.Constrained_searching.AC_3 import AC3Solver
from utils import is_solvable

class CSPBacktracking:
    def __init__(self, start_state, goal_state, visualization_callback=None, status_callback=None, delay=0.3):
        self.start_state = start_state  # Chuỗi 9 ký tự
        self.goal_state = goal_state  # Chuỗi 9 ký tự
        self.visualization_callback = visualization_callback
        self.status_callback = status_callback
        self.delay = delay
        self.backtracks = 0
        self.states_explored = 0
        self.domains = None

    def initialize_domains(self):
        """Khởi tạo domain bằng AC-3"""
        solver = AC3Solver(self.start_state)
        self.domains, reductions = solver.solve(self.goal_state)
        if self.domains is None:
            return False
        self.states_explored += reductions
        return True

    def is_complete(self, assignment):
        return len(assignment) == 9

    def is_valid(self, assignment):
        values = list(assignment.values())
        return len(values) == len(set(values)) and all(0 <= v <= 8 for v in values)

    def select_unassigned_variable(self, assignment):
        for row in range(3):
            for col in range(3):
                if (row, col) not in assignment:
                    return (row, col)
        return None

    def order_domain_values(self, var, assignment):
        if self.domains and var in self.domains:
            domain = list(self.domains[var])
            random.shuffle(domain)
            return domain
        return list(range(9))

    def backtrack(self, assignment, path):
        self.states_explored += 1

        if self.is_complete(assignment):
            state_str = ''.join(str(assignment.get((r, c), 0)) for r in range(3) for c in range(3))
            path.append(state_str)
            return True

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value

            state_str = ''.join(str(assignment.get((r, c), 0)) for r in range(3) for c in range(3))
            path.append(state_str)

            if self.visualization_callback:
                state = self.create_state_from_assignment(assignment)
                self.visualization_callback(state)
                time.sleep(self.delay)

            if self.status_callback:
                self.status_callback(f"Thử gán ({var[0]}, {var[1]}) = {value}")

            if self.is_valid(assignment):
                if self.backtrack(assignment, path):
                    return True

            if self.status_callback:
                self.status_callback(f"Quay lui ({var[0]}, {var[1]}) = {value}")

            del assignment[var]
            self.backtracks += 1
            path.pop()

            if self.visualization_callback:
                state = self.create_state_from_assignment(assignment)
                self.visualization_callback(state)
                time.sleep(self.delay)

        return False

    def create_state_from_assignment(self, assignment):
        state = [[0 for _ in range(3)] for _ in range(3)]
        for (row, col), value in assignment.items():
            state[row][col] = value
        return state

    def solve(self):
        if not is_solvable(self.start_state, self.goal_state):
            return [], 0, 0, 0

        if not self.initialize_domains():
            return [], 0, 0, 0

        assignment = {}
        self.backtracks = 0
        self.states_explored = 0
        path = [self.start_state]

        # Hiển thị trạng thái ban đầu
        if self.visualization_callback:
            state = [[int(self.start_state[r * 3 + c]) for c in range(3)] for r in range(3)]
            self.visualization_callback(state)
            time.sleep(self.delay)

        success = self.backtrack(assignment, path)
        if not success:
            return [self.start_state], self.states_explored, 0, 0

        return path, self.states_explored, len(path) - 1, len(path) - 1

def run(start_state, goal_state, progress_callback=None):
    solver = CSPBacktracking(start_state, goal_state)
    path, states_explored, depth, cost = solver.solve()
    return path, states_explored, depth, cost