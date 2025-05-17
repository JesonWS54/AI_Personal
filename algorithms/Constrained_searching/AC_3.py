from collections import deque

class CSP:
    def __init__(self, variables, domains, constraints, neighbors):
        self.variables = variables
        self.domains = domains
        self.constraints = constraints
        self.neighbors = neighbors

    def constraint_function(self, X_i, a, X_j, b):
        return a != b  # ràng buộc: giá trị phải khác nhau

def ac3(start_state, goal_state=None):
    # Đây chỉ là demo logic đơn giản, bạn nên thay bằng AC-3 thực sự nếu cần

    # AC-3 không có "path", nên ta giả lập đường đi là giữ nguyên start_state
    path = [start_state]
    nodes_expanded = 0
    search_depth = 0
    path_cost = 0
    return path, nodes_expanded, search_depth, path_cost


def revise(csp, X_i, X_j):
    revised = False
    for a in csp.domains[X_i][:]:
        if not any(csp.constraint_function(X_i, a, X_j, b) for b in csp.domains[X_j]):
            csp.domains[X_i].remove(a)
            revised = True
    return revised