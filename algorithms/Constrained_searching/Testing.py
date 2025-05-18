# algorithms/Constrained_searching/Testing.py
import time
import random
from utils import is_solvable

class CSPMinConflicts:
    def __init__(self, start_state, goal_state, visualization_callback=None, status_callback=None, delay=0.3, max_iterations=5000):
        self.start_state = start_state  # Chuỗi 9 ký tự
        self.goal_state = goal_state  # Chuỗi 9 ký tự
        self.visualization_callback = visualization_callback
        self.status_callback = status_callback
        self.delay = delay
        self.max_iterations = max_iterations
        self.iterations = 0
        self.states_explored = 0
        self.current_assignment = {}
        self.positions = [(row, col) for row in range(3) for col in range(3)]
        self.goal_assignment = self.state_to_assignment(goal_state)

    def state_to_assignment(self, state):
        """Chuyển chuỗi trạng thái thành assignment"""
        assignment = {}
        for i, (row, col) in enumerate(self.positions):
            assignment[(row, col)] = int(state[i])
        return assignment

    def initialize_assignment(self):
        """Khởi tạo phân công từ start_state"""
        return self.state_to_assignment(self.start_state)

    def is_complete(self, assignment):
        """Kiểm tra xem phân công có đạt goal_state không"""
        state_str = ''.join(str(assignment.get((r, c), 0)) for r in range(3) for c in range(3))
        return state_str == self.goal_state

    def count_conflicts(self, var, value, assignment):
        """Đếm số xung đột khi gán value cho var, thêm heuristic"""
        temp_assignment = assignment.copy()
        temp_assignment[var] = value
        value_counts = {}
        for v in temp_assignment.values():
            value_counts[v] = value_counts.get(v, 0) + 1
        conflicts = sum(max(0, count - 1) for count in value_counts.values())
        missing_values = sum(1 for v in range(9) if v not in value_counts)
        # Thêm heuristic: số ô sai vị trí so với goal_state
        misplaced = sum(1 for pos, val in temp_assignment.items() if val != self.goal_assignment.get(pos, val) and val != 0)
        return conflicts + missing_values + misplaced

    def is_variable_conflicting(self, var, assignment):
        """Kiểm tra xem biến có xung đột không"""
        if var not in assignment:
            return False
        value = assignment[var]
        for other_var, other_value in assignment.items():
            if other_var != var and other_value == value:
                return True
        return False

    def conflicting_variables(self, assignment):
        """Tìm các biến đang xung đột"""
        return [var for var in assignment if self.is_variable_conflicting(var, assignment)]

    def find_zero(self, assignment):
        """Tìm vị trí ô trống (giá trị 0)"""
        for pos, value in assignment.items():
            if value == 0:
                return pos
        return None

    def get_neighbors(self, pos):
        """Lấy các vị trí liền kề của ô trống"""
        row, col = pos
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 3 and 0 <= new_col < 3:
                neighbors.append((new_row, new_col))
        return neighbors

    def min_conflicts_value(self, var, assignment):
        """Tìm giá trị gây ít xung đột nhất cho var, chỉ từ các ô liền kề ô trống"""
        current_value = assignment[var]
        min_conflicts = float('inf')
        min_values = []
        
        # Tìm ô trống
        zero_pos = self.find_zero(assignment)
        if not zero_pos:
            return current_value
        
        # Lấy các ô liền kề ô trống
        neighbors = self.get_neighbors(zero_pos)
        valid_values = [assignment.get(n, None) for n in neighbors if n in assignment and assignment[n] != current_value]
        valid_values = [v for v in valid_values if v is not None]
        
        if not valid_values:
            return current_value

        for value in valid_values:
            conflict_count = self.count_conflicts(var, value, assignment)
            if conflict_count < min_conflicts:
                min_conflicts = conflict_count
                min_values = [value]
            elif conflict_count == min_conflicts:
                min_values.append(value)
        
        return random.choice(min_values) if min_values else current_value

    def create_state_from_assignment(self, assignment):
        """Tạo trạng thái 2D từ assignment"""
        state = [[0 for _ in range(3)] for _ in range(3)]
        for (row, col), value in assignment.items():
            state[row][col] = value
        return state

    def random_restart(self):
        """Tạo phân công ngẫu nhiên từ start_state bằng cách hoán đổi ngẫu nhiên"""
        assignment = self.initialize_assignment()
        for _ in range(10):  # Thực hiện 10 hoán đổi ngẫu nhiên
            zero_pos = self.find_zero(assignment)
            if not zero_pos:
                break
            neighbors = self.get_neighbors(zero_pos)
            if neighbors:
                swap_pos = random.choice(neighbors)
                assignment[zero_pos], assignment[swap_pos] = assignment[swap_pos], assignment[zero_pos]
        return assignment

    def solve(self):
        """Giải bài toán 8-puzzle bằng Min-Conflicts"""
        if not is_solvable(self.start_state, self.goal_state):
            if self.status_callback:
                self.status_callback("Trạng thái không khả thi!")
            return [self.start_state], 0, 0, 0

        self.current_assignment = self.initialize_assignment()
        path = [self.start_state]
        self.iterations = 0
        self.states_explored = 1
        restart_count = 0
        max_restarts = 5

        if self.visualization_callback:
            state = self.create_state_from_assignment(self.current_assignment)
            self.visualization_callback(state)
            time.sleep(self.delay)

        if self.status_callback:
            conflicts = self.count_conflicts(None, None, self.current_assignment)
            self.status_callback(f"Trạng thái ban đầu - Số xung đột: {conflicts}")

        while self.iterations < self.max_iterations:
            self.iterations += 1
            self.states_explored += 1

            if self.is_complete(self.current_assignment):
                state_str = ''.join(str(self.current_assignment.get((r, c), 0)) for r in range(3) for c in range(3))
                path.append(state_str)
                if self.status_callback:
                    self.status_callback(f"Đã đạt goal_state sau {self.iterations} lần lặp!")
                return path, self.states_explored, len(path) - 1, len(path) - 1

            conflicting = self.conflicting_variables(self.current_assignment)
            if not conflicting:
                if self.status_callback:
                    self.status_callback("Không còn biến xung đột, thử khởi động lại...")
                if restart_count < max_restarts:
                    self.current_assignment = self.random_restart()
                    restart_count += 1
                    state_str = ''.join(str(self.current_assignment.get((r, c), 0)) for r in range(3) for c in range(3))
                    path.append(state_str)
                    self.states_explored += 1
                    if self.status_callback:
                        self.status_callback(f"Khởi động lại #{restart_count} - Trạng thái mới")
                    if self.visualization_callback:
                        state = self.create_state_from_assignment(self.current_assignment)
                        self.visualization_callback(state)
                        time.sleep(self.delay)
                    continue
                else:
                    if self.status_callback:
                        self.status_callback("Đã đạt tối đa số lần khởi động lại!")
                    break

            var = random.choice(conflicting)
            value = self.min_conflicts_value(var, self.current_assignment)
            old_value = self.current_assignment[var]
            self.current_assignment[var] = value

            state_str = ''.join(str(self.current_assignment.get((r, c), 0)) for r in range(3) for c in range(3))
            path.append(state_str)

            conflicts = self.count_conflicts(None, None, self.current_assignment)
            if self.status_callback:
                self.status_callback(f"Lặp #{self.iterations}: Đổi ô {var} từ {old_value} → {value}. Xung đột: {conflicts}")

            if self.visualization_callback:
                state = self.create_state_from_assignment(self.current_assignment)
                self.visualization_callback(state)
                time.sleep(self.delay)

        if self.status_callback:
            self.status_callback(f"Không đạt goal_state sau {self.max_iterations} lần lặp!")
        return path, self.states_explored, len(path) - 1, len(path) - 1

def run(start_state, goal_state, progress_callback=None):
    solver = CSPMinConflicts(start_state, goal_state)
    return solver.solve()