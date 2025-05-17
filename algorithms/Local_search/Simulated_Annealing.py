from utils import is_solvable, get_next_states, manhattan_distance
import random
import math

def simulated_annealing(start_state, goal_state, T_init=100.0, alpha=0.995, T_min=0.01, max_steps=1000):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0

    current_state = start_state
    current_h = manhattan_distance(current_state, goal_state)
    best_state = current_state
    best_h = current_h
    path = [current_state]
    visited = set([current_state])
    nodes_expanded = 0
    T = T_init

    for step in range(max_steps):
        if current_state == goal_state:
            return path, nodes_expanded, len(path) - 1, len(path) - 1

        neighbors = get_next_states(current_state)
        nodes_expanded += len(neighbors)
        next_state = random.choice(neighbors)
        next_h = manhattan_distance(next_state, goal_state)

        delta_e = current_h - next_h

        if delta_e > 0 or random.random() < math.exp(delta_e / T):
            current_state = next_state
            current_h = next_h
            path.append(current_state)
            visited.add(current_state)

            if current_h < best_h:
                best_state = current_state
                best_h = current_h

        T *= alpha
        if T < T_min:
            break

    if best_state == goal_state:
        return path, nodes_expanded, len(path) - 1, len(path) - 1
    else:
        return None, nodes_expanded, 0, 0
