from utils import is_solvable, heuristic, get_next_states
import heapq

def beam_search(start_state, goal_state, beam_width=2, max_nodes=10000):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0

    queue = [(heuristic(start_state, goal_state), start_state, [start_state])]
    nodes_expanded = 0
    visited = set([start_state])

    while queue and nodes_expanded < max_nodes:
        next_level = []

        for h, state, path in queue:
            if state == goal_state:
                return path, nodes_expanded, len(path) - 1, len(path) - 1

            for neighbor in get_next_states(state):
                if neighbor not in visited:
                    visited.add(neighbor)
                    nodes_expanded += 1
                    next_level.append((heuristic(neighbor, goal_state), neighbor, path + [neighbor]))

        # Không còn nhánh nào để mở rộng
        if not next_level:
            break

        # Chỉ giữ lại beam_width nhánh tốt nhất
        next_level.sort(key=lambda x: x[0])
        queue = next_level[:beam_width]

    return None, nodes_expanded, 0, 0
