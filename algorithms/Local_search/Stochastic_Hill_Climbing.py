from utils import is_solvable, heuristic, get_next_states
import random

def stochastic_hill_climbing(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0

    current_state = start_state
    path = [current_state]
    nodes_expanded = 0
    visited = set([current_state])

    while current_state != goal_state:
        neighbors = get_next_states(current_state)
        unvisited_neighbors = [n for n in neighbors if n not in visited]

        if not unvisited_neighbors:
            return path, nodes_expanded, len(path) - 1, len(path) - 1

        current_h = heuristic(current_state, goal_state)
        better_neighbors = [n for n in unvisited_neighbors if heuristic(n, goal_state) < current_h]

        nodes_expanded += len(unvisited_neighbors)

        if better_neighbors:
            current_state = random.choice(better_neighbors)
        else:
            current_state = random.choice(unvisited_neighbors)

        visited.add(current_state)
        path.append(current_state)

    return path, nodes_expanded, len(path) - 1, len(path) - 1