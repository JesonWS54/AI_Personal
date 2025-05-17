from utils import is_solvable, heuristic, get_next_states

def ida_star(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0

    def f_cost(state, g):
        return g + heuristic(state, goal_state)

    def search(state, g, threshold, path, visited, nodes_expanded):
        f = f_cost(state, g)
        if f > threshold:
            return f, None
        if state == goal_state:
            return f, path
        min_threshold = float('inf')
        for next_state in get_next_states(state):
            if next_state not in visited:
                visited.add(next_state)
                nodes_expanded[0] += 1
                new_path = path + [next_state]
                new_f, result = search(next_state, g + 1, threshold, new_path, visited, nodes_expanded)
                if result is not None:
                    return new_f, result
                min_threshold = min(min_threshold, new_f)
                visited.remove(next_state)
        return min_threshold, None

    threshold = heuristic(start_state, goal_state)
    path = [start_state]
    visited = {start_state}
    nodes_expanded = [0]

    while True:
        new_threshold, result = search(start_state, 0, threshold, path, visited, nodes_expanded)
        if result is not None:
            return result, nodes_expanded[0], len(result) - 1, len(result) - 1
        if new_threshold == float('inf'):
            return None, nodes_expanded[0], 0, 0
        threshold = new_threshold