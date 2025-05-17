from utils import get_next_states, is_solvable, heuristic

def dfs(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0

    stack = [(start_state, [start_state], 0)]
    visited = set()
    
    while stack:
        current_state, path, nodes = stack.pop()
        if current_state == goal_state:
            return path, nodes, len(path) - 1, len(path) - 1
        if current_state not in visited:
            visited.add(current_state)
            next_states = get_next_states(current_state)
            next_states.sort(key=lambda x: heuristic(x, goal_state))
            for next_state in reversed(next_states):
                if next_state not in visited:
                    stack.append((next_state, path + [next_state], nodes + 1))

    return None, 0, 0, 0
