import time
from collections import deque
from utils import find_zero, get_next_states

class AC3Solver:
    def __init__(self, initial_state, delay=0.5, log_callback=None, domain_callback=None):
        self.initial_state = initial_state  # Chuỗi 9 ký tự, ví dụ: "123045786"
        self.delay = delay
        self.log_callback = log_callback
        self.domain_callback = domain_callback
        self.domains = {}
        self.arcs = deque()
        self.neighbors = {}
        self.domain_reductions = 0

    def initialize(self, goal_state):
        """Thiết lập domain và các ràng buộc"""
        positions = [(row, col) for row in range(3) for col in range(3)]
        
        # Khởi tạo domain: mỗi ô có thể chứa mọi giá trị từ 0-8
        for pos in positions:
            self.domains[pos] = set(range(9))  # {0, 1, 2, 3, 4, 5, 6, 7, 8}
        
        # Áp dụng ràng buộc từ initial_state và goal_state
        for i, pos in enumerate(positions):
            self.domains[pos] &= {int(self.initial_state[i])}  # Giới hạn bởi initial_state
            self.domains[pos] |= {int(goal_state[i])}  # Cho phép giá trị từ goal_state

        # Thêm các giá trị từ các trạng thái có thể đạt được từ initial_state
        zero_pos = find_zero(self.initial_state)
        possible_states = get_next_states(self.initial_state)
        for state in possible_states:
            for i, pos in enumerate(positions):
                self.domains[pos] |= {int(state[i])}

        # Thiết lập neighbors cho ràng buộc all-different
        for pos in positions:
            self.neighbors[pos] = [p for p in positions if p != pos]

        # Tạo hàng đợi arc
        self.arcs = deque([(xi, xj) for xi in positions for xj in self.neighbors[xi]])

        self._log("Khởi tạo domain và hàng đợi arc.")
        self._notify_domain()

    def _log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def _notify_domain(self):
        if self.domain_callback:
            self.domain_callback(self.domains)

    def enforce_arc_consistency(self):
        """Thuật toán AC-3 chính"""
        while self.arcs:
            xi, xj = self.arcs.popleft()

            if self._revise(xi, xj):
                if not self.domains[xi]:
                    self._log(f"Domain của {xi} rỗng — không còn lời giải hợp lệ.")
                    return False
                for xk in self.neighbors[xi]:
                    if xk != xj:
                        self.arcs.append((xk, xi))
        self._log("Kết thúc AC-3. Domain đã được thu hẹp.")
        return True

    def _revise(self, xi, xj):
        """Xem xét và loại bỏ giá trị không hợp lệ khỏi domain của xi"""
        revised = False
        to_remove = set()

        for val in self.domains[xi]:
            # Nếu không có giá trị nào trong domain của xj khác val, loại val
            if not any(val != other for other in self.domains[xj]):
                to_remove.add(val)

        if to_remove:
            self.domains[xi] -= to_remove
            self.domain_reductions += len(to_remove)
            revised = True
            self._log(f"Loại khỏi domain {xi}: {to_remove}")
            self._notify_domain()
            time.sleep(self.delay)

        return revised

    def get_domains(self):
        return self.domains

    def get_reduction_count(self):
        return self.domain_reductions

    def get_state(self):
        """Chuyển domain thành chuỗi trạng thái"""
        state = ['0'] * 9
        for (row, col), domain in self.domains.items():
            if len(domain) == 1:
                state[row * 3 + col] = str(next(iter(domain)))
        return ''.join(state)

    def solve(self, goal_state):
        """Chạy AC-3 và trả về domains để Backtracking sử dụng"""
        self.initialize(goal_state)
        success = self.enforce_arc_consistency()
        if success:
            return self.domains, self.domain_reductions
        return None, 0