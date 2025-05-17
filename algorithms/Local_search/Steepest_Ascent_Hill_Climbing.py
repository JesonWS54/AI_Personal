from utils import is_solvable, heuristic, get_next_states
import random

def steepest_hill_climbing(start_state, goal_state, max_sideways=5, max_restarts=10):
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
            next_candidates = []
            best_h = current_h

            for neighbor in neighbors:
                if neighbor not in visited:
                    h = heuristic(neighbor, goal_state)
                    total_nodes_expanded += 1
                    if h < best_h:
                        best_h = h
                        next_candidates = [neighbor]
                    elif h == best_h:
                        next_candidates.append(neighbor)

            if next_candidates:
                chosen = random.choice(next_candidates)
                visited.add(chosen)
                path.append(chosen)

                if best_h == current_h:
                    sideways_moves += 1
                    if sideways_moves > max_sideways:
                        break
                else:
                    sideways_moves = 0
                    current_h = best_h

                current_state = chosen
            else:
                break  # No better neighbor found

        if current_state == goal_state:
            return path, total_nodes_expanded, len(path) - 1, len(path) - 1

        # Random restart from one of visited states
        start_state = random.choice(list(visited))

    return None, total_nodes_expanded, 0, 0
