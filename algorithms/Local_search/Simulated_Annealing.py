from utils import is_solvable, get_next_states, manhattan_distance
import random
import math

def simulated_annealing(start_state, goal_state, T_init=1000.0, alpha=0.99, T_min=0.01, max_steps=5000):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0

    current_state = start_state
    current_h = manhattan_distance(current_state, goal_state)
    best_state = current_state
    best_h = current_h
    path = [current_state]
    best_path = path.copy()
    visited = set([current_state])
    nodes_expanded = 0
    T = T_init

    for step in range(max_steps):
        if current_state == goal_state:
            return path, nodes_expanded, len(path) - 1, len(path) - 1

        neighbors = [n for n in get_next_states(current_state) if n not in visited]
        if not neighbors:
            break

        # Ưu tiên chọn hàng xóm tốt nhất
        neighbors.sort(key=lambda s: manhattan_distance(s, goal_state))
        next_state = neighbors[0]
        next_h = manhattan_distance(next_state, goal_state)

        delta_e = current_h - next_h

        # Cho phép đi xuống nếu có xác suất chấp nhận
        if delta_e > 0 or random.random() < math.exp(delta_e / T):
            current_state = next_state
            current_h = next_h
            path.append(current_state)
            visited.add(current_state)

            if current_h < best_h:
                best_state = current_state
                best_h = current_h
                best_path = path.copy()

        T *= alpha
        if T < T_min:
            break

    if best_h == 0:
        return best_path, nodes_expanded, len(best_path) - 1, len(best_path) - 1
    else:
        return None, nodes_expanded, 0, 0
