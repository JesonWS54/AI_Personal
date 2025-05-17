import heapq
from utils import get_next_states, is_solvable, reconstruct_path

def ucs(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0

    queue = [(0, start_state, None, 0)]
    visited = {start_state: 0}
    parents = {}
    heapq.heapify(queue)

    while queue:
        cost, current_state, parent, nodes = heapq.heappop(queue)
        if current_state == goal_state:
            path = reconstruct_path(parents, start_state, goal_state)
            return path, nodes, len(path) - 1, cost

        for next_state in get_next_states(current_state):
            new_cost = cost + 1
            if next_state not in visited or new_cost < visited[next_state]:
                visited[next_state] = new_cost
                parents[next_state] = current_state
                heapq.heappush(queue, (new_cost, next_state, current_state, nodes + 1))

    return None, 0, 0, 0
