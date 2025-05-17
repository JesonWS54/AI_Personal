from utils import is_solvable, heuristic, get_next_states
import heapq

def greedy_search(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0
    queue = [(heuristic(start_state, goal_state), start_state, [start_state], 0)]
    visited = set()
    heapq.heapify(queue)
    while queue:
        _, current_state, path, nodes = heapq.heappop(queue)
        if current_state == goal_state:
            return path, nodes, len(path) - 1, len(path) - 1
        if current_state not in visited:
            visited.add(current_state)
            for next_state in get_next_states(current_state):
                if next_state not in visited:
                    heapq.heappush(queue, (heuristic(next_state, goal_state), next_state, path + [next_state], nodes + 1))
    return None, 0, 0, 0