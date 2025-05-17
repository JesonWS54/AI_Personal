from utils import get_next_states, is_solvable

def ids(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0

    depth = 0
    nodes_expanded = 0
    
    while True:
        result, new_nodes = dls_iterative(start_state, goal_state, depth)
        nodes_expanded += new_nodes
        if result:
            return result, nodes_expanded, depth, len(result) - 1
        depth += 1

def dls_iterative(start_state, goal_state, depth_limit):
    stack = [(start_state, [start_state], 0)]
    visited = set()
    nodes_expanded = 0
    
    while stack:
        state, path, depth = stack.pop()
        if state == goal_state:
            return path, nodes_expanded
        if depth < depth_limit and state not in visited:
            visited.add(state)
            for next_state in get_next_states(state):
                if next_state not in visited:
                    stack.append((next_state, path + [next_state], depth + 1))
                    nodes_expanded += 1

    return None, nodes_expanded
