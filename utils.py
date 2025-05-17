# utils.py
# Các hàm tiện ích chung được sử dụng trong các thuật toán và GUI

from collections import deque

def find_zero(state):
    idx = state.index('0')
    return idx // 3, idx % 3

def get_next_states(state):
    if len(state) != 9:
        return []  # Trả về rỗng nếu không hợp lệ

    index = state.index("0")
    row, col = divmod(index, 3)
    next_states = []

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_idx = new_row * 3 + new_col
            state_list = list(state)
            state_list[index], state_list[new_idx] = state_list[new_idx], state_list[index]
            next_states.append(''.join(state_list))

    return next_states


def is_solvable(state, goal_state):
    def count_inversions(s):
        s = [int(x) for x in s if x != '0']
        inversions = 0
        for i in range(len(s)):
            for j in range(i + 1, len(s)):
                if s[i] > s[j]:
                    inversions += 1
        return inversions
    return (count_inversions(state) % 2) == (count_inversions(goal_state) % 2)

def heuristic(state, goal_state):
    goal_pos = {goal_state[i]: (i // 3, i % 3) for i in range(9)}
    return sum(abs(goal_pos[state[i]][0] - i // 3) + abs(goal_pos[state[i]][1] - i % 3)
               for i in range(9) if state[i] != '0')

def manhattan_distance(state, goal):
    total = 0
    for i in range(9):
        if state[i] != '0':
            val = int(state[i])
            goal_pos = goal.index(str(val))
            curr_row, curr_col = i // 3, i % 3
            goal_row, goal_col = goal_pos // 3, goal_pos % 3
            total += abs(curr_row - goal_row) + abs(curr_col - goal_col)
    return total

def reconstruct_path(parents, start, goal):
    path = [goal]
    while path[-1] != start:
        path.append(parents[path[-1]])
    return path[::-1]

def apply_action_to_state(state, action):
    row, col = find_zero(state)
    new_row, new_col = row, col

    if action == "Up" and row > 0:
        new_row -= 1
    elif action == "Down" and row < 2:
        new_row += 1
    elif action == "Left" and col > 0:
        new_col -= 1
    elif action == "Right" and col < 2:
        new_col += 1
    else:
        return None  # hành động không hợp lệ

    old_idx = row * 3 + col
    new_idx = new_row * 3 + new_col
    state_list = list(state)
    state_list[old_idx], state_list[new_idx] = state_list[new_idx], state_list[old_idx]
    return ''.join(state_list)


def apply_action_to_belief(belief_state, action):
    new_states = set()
    for state in belief_state:
        new_state = apply_action_to_state(state, action)
        new_states.add(new_state)
    return frozenset(new_states)

def belief_heuristic(belief, goal_state):
    return min(heuristic(state, goal_state) for state in belief)


def get_possible_actions(state):
    actions = []
    row, col = divmod(state.index('0'), 3)
    if row > 0: actions.append("Up")
    if row < 2: actions.append("Down")
    if col > 0: actions.append("Left")
    if col < 2: actions.append("Right")
    return actions

def get_action_results(state, action):
    results = set()
    intended = apply_action_to_state(state, action)
    if intended and intended != state:
        results.add(intended)

    # mô phỏng sai lệch hành động với 10% xác suất
    import random
    if random.random() < 0.1:
        other_actions = [a for a in get_possible_actions(state) if a != action]
        if other_actions:
            alt = apply_action_to_state(state, random.choice(other_actions))
            if alt and alt != state:
                results.add(alt)
    return results



def get_possible_actions(state):
    actions = []
    row, col = divmod(state.index('0'), 3)
    if row > 0:
        actions.append("Up")
    if row < 2:
        actions.append("Down")
    if col > 0:
        actions.append("Left")
    if col < 2:
        actions.append("Right")
    return actions
