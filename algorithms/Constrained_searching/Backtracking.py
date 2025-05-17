def backtracking(start_state, goal_state):
    def heuristic(state, goal):
        return sum(abs((int(val) - 1) - i) for i, val in enumerate(state) if val != '0')

    def get_next_states(state):
        idx = state.index('0')
        row, col = divmod(idx, 3)
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < 3 and 0 <= c < 3:
                new_idx = r * 3 + c
                lst = list(state)
                lst[idx], lst[new_idx] = lst[new_idx], lst[idx]
                neighbors.append(''.join(lst))
        return neighbors

    def is_solvable(state):
        s = [int(x) for x in state if x != '0']
        inv = sum(1 for i in range(len(s)) for j in range(i + 1, len(s)) if s[i] > s[j])
        return inv % 2 == 0

    def recursive(state, path, visited):
        if state == goal_state:
            return path
        for next_state in sorted(get_next_states(state), key=lambda s: heuristic(s, goal_state)):
            if next_state not in visited:
                visited.add(next_state)
                res = recursive(next_state, path + [next_state], visited)
                if res:
                    return res
        return None

    if not is_solvable(start_state):
        return None, 0, 0, 0

    visited = set([start_state])
    path = recursive(start_state, [start_state], visited)
    if path:
        return path, len(path), len(path) - 1, len(path) - 1
    return None, 0, 0, 0