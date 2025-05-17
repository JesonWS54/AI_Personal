from collections import deque

def get_neighbors(state):
    neighbors = []
    idx = state.index('0')
    row, col = divmod(idx, 3)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in moves:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_idx = new_row * 3 + new_col
            state_list = list(state)
            state_list[idx], state_list[new_idx] = state_list[new_idx], state_list[idx]
            neighbors.append(''.join(state_list))
    return neighbors

def apply_action_to_belief_state(belief_state, action):
    new_belief_state = set()
    for state in belief_state:
        idx = state.index('0')
        row, col = divmod(idx, 3)
        dr, dc = action
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_idx = new_row * 3 + new_col
            state_list = list(state)
            state_list[idx], state_list[new_idx] = state_list[new_idx], state_list[idx]
            new_belief_state.add(''.join(state_list))
    return new_belief_state

def belief_state_search(initial_belief, goal, progress_callback=None):
    queue = deque()
    queue.append((initial_belief, []))
    visited = set()
    visited.add(frozenset(initial_belief))
    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # UP, DOWN, LEFT, RIGHT
    step = 0

    while queue:
        belief_state, path = queue.popleft()
        if progress_callback:
            progress_callback(step, step / 1000.0)
        step += 1

        if len(belief_state) == 1 and goal in belief_state:
            return path + [set(belief_state)], len(visited), len(path), len(path)

        for action in actions:
            new_belief_state = apply_action_to_belief_state(belief_state, action)
            frozen_new = frozenset(new_belief_state)
            if frozen_new not in visited:
                visited.add(frozen_new)
                queue.append((new_belief_state, path + [set(belief_state)]))


    return [], len(visited), 0, 0

def run(belief_states, goal_state, progress_callback=None):
    return belief_state_search(belief_states, goal_state, progress_callback)