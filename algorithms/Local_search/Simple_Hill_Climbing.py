from utils import is_solvable, heuristic, get_next_states
import random

def simple_hill_climbing(start_state, goal_state, max_sideways=5, max_restarts=10):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0

    total_nodes_expanded = 0
    for restart in range(max_restarts):
        current_state = start_state
        path = [current_state]
        visited = set([current_state])
        current_h = heuristic(current_state, goal_state)
        sideways_moves = 0

        while current_state != goal_state:
            neighbors = get_next_states(current_state)
            best_neighbor = None
            best_h = current_h

            for neighbor in neighbors:
                if neighbor not in visited:
                    h = heuristic(neighbor, goal_state)
                    total_nodes_expanded += 1
                    if h < best_h or (h == best_h and sideways_moves < max_sideways):
                        best_neighbor = neighbor
                        best_h = h

            if best_neighbor:
                current_state = best_neighbor
                visited.add(current_state)
                path.append(current_state)
                if best_h == current_h:
                    sideways_moves += 1
                else:
                    sideways_moves = 0
                current_h = best_h
            else:
                break  # Local minimum or exhausted sideways moves

        if current_state == goal_state:
            return path, total_nodes_expanded, len(path) - 1, len(path) - 1

        # Random restart (chọn trạng thái ngẫu nhiên để thử lại)
        start_state = random.choice(list(visited))
    
    return None, total_nodes_expanded, 0, 0  # Không tìm được
