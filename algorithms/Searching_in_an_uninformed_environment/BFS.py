from collections import deque
from utils import get_next_states, is_solvable

def bfs(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0
    
    queue = deque([(start_state, [start_state], 0)])
    visited = {start_state}
    
    while queue:
        current_state, path, nodes = queue.popleft()
        if current_state == goal_state:
            return path, nodes, len(path) - 1, len(path) - 1
        
        for next_state in get_next_states(current_state):
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, path + [next_state], nodes + 1))

    return None, 0, 0, 0