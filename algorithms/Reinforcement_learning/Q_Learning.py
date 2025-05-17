def q_learning(start_state, goal_state):
    # Trong bài toán 8-puzzle, Q-learning không hiệu quả trong môi trường không lặp lại
    # Nên ta sẽ giả lập một phương pháp giả lập Q-learning với số bước hạn chế
    import random
    from utils import get_next_states, is_solvable, heuristic

    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0

    Q = {}  # Q-table: {(state, action): value}
    alpha = 0.5     # learning rate
    gamma = 0.9     # discount factor
    epsilon = 0.2   # exploration rate
    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    def get_zero_pos(state):
        idx = state.index('0')
        return idx // 3, idx % 3

    def apply_action(state, action):
        row, col = get_zero_pos(state)
        dr, dc = action
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            idx1 = row * 3 + col
            idx2 = new_row * 3 + new_col
            s = list(state)
            s[idx1], s[idx2] = s[idx2], s[idx1]
            return ''.join(s)
        return state

    max_episodes = 5000
    max_steps = 50
    best_path = [start_state]
    best_h = heuristic(start_state, goal_state)
    nodes_expanded = 0

    for episode in range(max_episodes):
        state = start_state
        path = [state]
        for step in range(max_steps):
            nodes_expanded += 1
            possible_actions = actions
            if random.random() < epsilon:
                action = random.choice(possible_actions)
            else:
                q_vals = [(Q.get((state, a), 0), a) for a in possible_actions]
                action = max(q_vals)[1]
            next_state = apply_action(state, action)
            reward = 100 if next_state == goal_state else -1
            next_q_vals = [Q.get((next_state, a), 0) for a in actions]
            max_next_q = max(next_q_vals)
            Q[(state, action)] = Q.get((state, action), 0) + alpha * (reward + gamma * max_next_q - Q.get((state, action), 0))
            path.append(next_state)
            state = next_state
            if state == goal_state:
                if len(path) < len(best_path) or best_h > 0:
                    best_path = path
                    best_h = 0
                break
        if best_h == 0:
            break

    if best_path[-1] != goal_state:
        return None, nodes_expanded, 0, 0
    return best_path, nodes_expanded, len(best_path) - 1, len(best_path) - 1
