# algorithms/Searching_in_an_uncertain_environment/Searching_With_Partial_Observation.py
from collections import deque

def is_consistent(state, known_tile_index, known_value):
    return state[known_tile_index] == known_value

def apply_action(state, action):
    idx = state.index('0')
    row, col = divmod(idx, 3)
    dr, dc = action
    new_row, new_col = row + dr, col + dc
    if 0 <= new_row < 3 and 0 <= new_col < 3:
        new_idx = new_row * 3 + new_col
        state_list = list(state)
        state_list[idx], state_list[new_idx] = state_list[new_idx], state_list[idx]
        return ''.join(state_list)
    return None

def apply_action_to_belief(belief_state, action, known_index=None, known_value=None):
    new_belief = set()
    for state in belief_state:
        new_state = apply_action(state, action)
        if new_state and (known_index is None or is_consistent(new_state, known_index, known_value)):
            new_belief.add(new_state)
    return new_belief

def partial_observation_search(initial_belief, goal, known_tile_index=0, known_tile_value='1', progress_callback=None):
    queue = deque()
    queue.append((initial_belief, []))
    visited = set()
    visited.add(frozenset(initial_belief))
    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    step = 0

    while queue:
        belief_state, path = queue.popleft()
        if progress_callback:
            progress_callback(step, step / 1000.0)
        step += 1

        if len(belief_state) == 1 and goal in belief_state:
            return path + [frozenset(belief_state)], len(visited), len(path), len(path)

        for action in actions:
            new_belief = apply_action_to_belief(belief_state, action, known_tile_index, known_tile_value)
            frozen_new = frozenset(new_belief)
            if new_belief and frozen_new not in visited:
                visited.add(frozen_new)
                queue.append((new_belief, path + [frozenset(belief_state)]))

    return [], len(visited), 0, 0


def run(belief_states, goal_state, progress_callback=None):
    return partial_observation_search(belief_states, goal_state, known_tile_index=0, known_tile_value='1', progress_callback=progress_callback)
