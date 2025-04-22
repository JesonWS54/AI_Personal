import pygame
import time
from collections import deque
import heapq
import tkinter as tk
from tkinter import messagebox
import random
import math

pygame.init()

# Kích thước giao diện (có thể thay đổi)
WIDTH = 900
HEIGHT = 700
CELL_SIZE = 100
GRID_SIZE = 3

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("8-Puzzle Solver by Nguyen Thanh Khang")

# Màu sắc
BG_COLOR = (44, 62, 80)         # Xanh đậm (#2C3E50)
TILE_COLOR = (255, 165, 0)      # Cam
EMPTY_COLOR = (127, 140, 141)   # Xám nhạt (#7F8C8D)
BORDER_COLOR = (255, 255, 255)  # Trắng
BUTTON_COLOR = (189, 195, 199)  # Xám (#BDC3C7)
BUTTON_COLOR = (189, 195, 199)  # Xám (#BDC3C7)
BUTTON_HOVER = (100, 100, 100)  # Xám đậm hơn (#646464) để nổi bật hơn
SOLVE_BUTTON_COLOR = (39, 174, 96)  # Xanh lá (#27AE60)
SOLVE_BUTTON_HOVER = (88, 214, 141)
TEXT_COLOR = (0, 0, 0)          # Đen cho số
TITLE_COLOR = (255, 255, 255)   # Trắng cho tiêu đề
SOLVED_COLOR = (46, 204, 113)   # Xanh lá nhạt (#2ECC71)
SOLVING_COLOR = (255, 165, 0)   # Cam neon
NOT_SOLVED_COLOR = (231, 76, 60) # Đỏ (#E74C3C)
PANEL_COLOR = (52, 73, 94, 200) # Xanh đậm mờ (#34495E)

# Font chữ
TITLE_FONT = pygame.font.SysFont("Roboto", 40, bold=True)
BUTTON_FONT = pygame.font.SysFont("Roboto", 24)
TIMER_FONT = pygame.font.SysFont("Roboto", 20, bold=True)
LABEL_FONT = pygame.font.SysFont("Roboto", 20, bold=True)

# Trạng thái ban đầu và mục tiêu
start_state = "123045786"
goal_state = "123456780"
start_input = start_state
goal_input = goal_state
input_active = None

def find_zero(state):
    idx = state.index('0')
    return idx // 3, idx % 3

def get_next_states(state):
    row, col = find_zero(state)
    next_states = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            old_idx = row * 3 + col
            new_idx = new_row * 3 + new_col
            state_tuple = tuple(state)
            next_state = list(state_tuple)
            next_state[old_idx], next_state[new_idx] = next_state[new_idx], next_state[old_idx]
            next_states.append(''.join(next_state))
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

def dfs(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0
    stack = [(start_state, [start_state], 0)]
    visited = set()
    while stack:
        current_state, path, nodes = stack.pop()
        if current_state == goal_state:
            return path, nodes, len(path) - 1, len(path) - 1
        if current_state not in visited:
            visited.add(current_state)
            next_states = get_next_states(current_state)
            next_states.sort(key=lambda x: heuristic(x, goal_state))
            for next_state in reversed(next_states):
                if next_state not in visited:
                    stack.append((next_state, path + [next_state], nodes + 1))
    return None, 0, 0, 0

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

def reconstruct_path(parents, start, goal):
    path = [goal]
    while path[-1] != start:
        path.append(parents[path[-1]])
    return path[::-1]

def ids(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0
    depth = 0
    nodes_expanded = 0
    while True:
        result, new_nodes = dls_iterative(start_state, goal_state, depth)
        nodes_expanded += new_nodes
        if result:
            return result, nodes_expanded, depth, len(result) - 1
        depth += 1

def dls_iterative(start_state, goal_state, depth_limit):
    stack = [(start_state, [start_state], 0)]
    visited = set()
    nodes_expanded = 0
    while stack:
        state, path, depth = stack.pop()
        if state == goal_state:
            return path, nodes_expanded
        if depth < depth_limit and state not in visited:
            visited.add(state)
            for next_state in get_next_states(state):
                if next_state not in visited:
                    stack.append((next_state, path + [next_state], depth + 1))
                    nodes_expanded += 1
    return None, nodes_expanded

def greedy_search(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0
    queue = [(heuristic(start_state, goal_state), start_state, [start_state], 0)]
    visited = set()
    heapq.heapify(queue)
    while queue:
        _, current_state, path, nodes = heapq.heappop(queue)
        if current_state == goal_state:
            return path, nodes, len(path) - 1, len(path) - 1
        if current_state not in visited:
            visited.add(current_state)
            for next_state in get_next_states(current_state):
                if next_state not in visited:
                    heapq.heappush(queue, (heuristic(next_state, goal_state), next_state, path + [next_state], nodes + 1))
    return None, 0, 0, 0

def astar(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0
    queue = [(heuristic(start_state, goal_state), 0, start_state, [start_state], 0)]
    visited = set()
    heapq.heapify(queue)
    while queue:
        _, g, current_state, path, nodes = heapq.heappop(queue)
        if current_state == goal_state:
            return path, nodes, len(path) - 1, g
        if current_state not in visited:
            visited.add(current_state)
            for next_state in get_next_states(current_state):
                if next_state not in visited:
                    new_g = g + 1
                    new_f = new_g + heuristic(next_state, goal_state)
                    heapq.heappush(queue, (new_f, new_g, next_state, path + [next_state], nodes + 1))
    return None, 0, 0, 0

def ida_star(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0
    def f_cost(state, g):
        return g + heuristic(state, goal_state)
    def search(state, g, threshold, path, visited, nodes_expanded):
        f = f_cost(state, g)
        if f > threshold:
            return f, None
        if state == goal_state:
            return f, path
        min_threshold = float('inf')
        for next_state in get_next_states(state):
            if next_state not in visited:
                visited.add(next_state)
                nodes_expanded[0] += 1
                new_path = path + [next_state]
                new_f, result = search(next_state, g + 1, threshold, new_path, visited, nodes_expanded)
                if result is not None:
                    return new_f, result
                min_threshold = min(min_threshold, new_f)
                visited.remove(next_state)
        return min_threshold, None
    threshold = heuristic(start_state, goal_state)
    path = [start_state]
    visited = {start_state}
    nodes_expanded = [0]
    max_depth = 0
    while True:
        new_threshold, result = search(start_state, 0, threshold, path, visited, nodes_expanded)
        if result is not None:
            max_depth = len(result) - 1
            return result, nodes_expanded[0], max_depth, max_depth
        if new_threshold == float('inf'):
            return None, nodes_expanded[0], 0, 0
        threshold = new_threshold

def simple_hill_climbing(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0
    current_state = start_state
    path = [current_state]
    nodes_expanded = 0
    visited = set([current_state])
    while current_state != goal_state:
        neighbors = get_next_states(current_state)
        found_better = False
        for neighbor in neighbors:
            if neighbor not in visited:
                nodes_expanded += 1
                h = heuristic(neighbor, goal_state)
                current_h = heuristic(current_state, goal_state)
                if h < current_h:
                    current_state = neighbor
                    visited.add(current_state)
                    path.append(current_state)
                    found_better = True
                    break
        if not found_better and neighbors:
            unvisited_neighbors = [n for n in neighbors if n not in visited]
            if unvisited_neighbors:
                current_state = random.choice(unvisited_neighbors)
                visited.add(current_state)
                path.append(current_state)
                nodes_expanded += 1
            else:
                return path, nodes_expanded, len(path) - 1, len(path) - 1
    return path, nodes_expanded, len(path) - 1, len(path) - 1

def steepest_hill_climbing(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0
    current_state = start_state
    path = [current_state]
    nodes_expanded = 0
    visited = set([current_state])
    while current_state != goal_state:
        neighbors = get_next_states(current_state)
        best_neighbor = None
        best_heuristic = heuristic(current_state, goal_state)
        for neighbor in neighbors:
            if neighbor not in visited:
                nodes_expanded += 1
                h = heuristic(neighbor, goal_state)
                if h < best_heuristic:
                    best_heuristic = h
                    best_neighbor = neighbor
        if best_neighbor:
            current_state = best_neighbor
            visited.add(current_state)
            path.append(current_state)
        elif neighbors:
            unvisited_neighbors = [n for n in neighbors if n not in visited]
            if unvisited_neighbors:
                current_state = random.choice(unvisited_neighbors)
                visited.add(current_state)
                path.append(current_state)
                nodes_expanded += 1
            else:
                return path, nodes_expanded, len(path) - 1, len(path) - 1
    return path, nodes_expanded, len(path) - 1, len(path) - 1


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
        
        current_heuristic = heuristic(current_state, goal_state)
        
        better_neighbors = []
        for neighbor in unvisited_neighbors:
            h = heuristic(neighbor, goal_state)
            if h < current_heuristic:  
                better_neighbors.append((neighbor, h))
            nodes_expanded += 1
        
        if better_neighbors:
            next_state = random.choice([n[0] for n in better_neighbors])
            current_state = next_state
            visited.add(current_state)
            path.append(current_state)
        else:
            return path, nodes_expanded, len(path) - 1, len(path) - 1
    
    return path, nodes_expanded, len(path) - 1, len(path) - 1

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

def simulated_annealing(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0
    
    current_state = start_state
    best_state = start_state
    best_h = manhattan_distance(start_state, goal_state)
    T = 5 * best_h  # Tỷ lệ với heuristic ban đầu
    alpha = 0.995   # Làm nguội chậm hơn một chút
    T_min = 0.5
    path = [current_state]
    best_path = [current_state]
    nodes_expanded = 0
    max_iterations = 20000
    iteration = 0
    
    while T > T_min and iteration < max_iterations:
        neighbors = get_next_states(current_state)
        nodes_expanded += len(neighbors)
        
        # Chọn láng giềng với ưu tiên trạng thái tốt hơn
        neighbor_heuristics = [(n, manhattan_distance(n, goal_state)) for n in neighbors]
        neighbor_heuristics.sort(key=lambda x: x[1])  # Sắp xếp theo heuristic
        if random.random() < 0.7:  # 70% chọn trạng thái tốt nhất
            next_state = neighbor_heuristics[0][0]
        else:
            next_state = random.choice(neighbors)
        
        current_h = manhattan_distance(current_state, goal_state)
        next_h = manhattan_distance(next_state, goal_state)
        delta_E = next_h - current_h
        
        # Cập nhật trạng thái tốt nhất
        if next_h < best_h:
            best_state = next_state
            best_h = next_h
            best_path = path + [next_state]
        
        # Chấp nhận trạng thái mới
        if delta_E <= 0 or random.random() < math.exp(-delta_E / T):
            current_state = next_state
            path.append(current_state)
        
        # Kiểm tra nếu đạt mục tiêu
        if current_state == goal_state:
            search_depth = len(path) - 1
            path_cost = len(path) - 1
            return path, nodes_expanded, search_depth, path_cost
        
        T *= alpha
        iteration += 1
    
    # Nếu không đạt mục tiêu, trả về đường đi tốt nhất
    search_depth = len(best_path) - 1
    path_cost = len(best_path) - 1
    return best_path, nodes_expanded, search_depth, path_cost

def beam_search(start_state, goal_state, beam_width=2):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0
    
    queue = [(heuristic(start_state, goal_state), start_state, [start_state], 0)]
    visited = set([start_state])
    nodes_expanded = 0
    
    while queue:
        current_level = queue
        queue = []
        for h, current_state, path, cost in current_level:
            if current_state == goal_state:
                return path, nodes_expanded, len(path) - 1, cost
            next_states = get_next_states(current_state)
            nodes_expanded += len(next_states)
        
            for next_state in next_states:
                if next_state not in visited:
                    visited.add(next_state)
                    new_cost = cost + 1
                    new_h = heuristic(next_state, goal_state)
                    queue.append((new_h, next_state, path + [next_state], new_cost))
        
        queue.sort(key=lambda x: x[0])  
        queue = queue[:beam_width]  
    return None, nodes_expanded, 0, 0

def and_or_search(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0
    
    # Hàm phụ để tìm kiếm OR
    def or_search(state, path, visited, nodes_expanded):
        if state == goal_state:
            return path, nodes_expanded
        if state in visited:
            return None, nodes_expanded
        
        visited.add(state)
        next_states = get_next_states(state)
        # Sắp xếp theo heuristic để ưu tiên trạng thái tốt hơn
        next_states.sort(key=lambda x: heuristic(x, goal_state))
        
        for next_state in next_states:
            if next_state not in visited:
                nodes_expanded += 1
                result, new_nodes = or_search(next_state, path + [next_state], visited, nodes_expanded)
                nodes_expanded = new_nodes
                if result is not None:
                    return result, nodes_expanded
        return None, nodes_expanded
    
    visited = set()
    path = [start_state]
    nodes_expanded = 0
    
    # Gọi tìm kiếm OR từ trạng thái ban đầu
    result, nodes_expanded = or_search(start_state, path, visited, nodes_expanded)
    
    if result is None:
        return None, nodes_expanded, 0, 0
    
    search_depth = len(result) - 1
    path_cost = len(result) - 1
    return result, nodes_expanded, search_depth, path_cost

def genetic_algorithm(start_state, goal_state, population_size=50, max_generations=1000, mutation_rate=0.1):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0

    # Các hướng di chuyển
    moves = ["Up", "Down", "Left", "Right"]

    # Hàm áp dụng một bước di chuyển
    def apply_move(state, move):
        row, col = find_zero(state)
        if move == "Up" and row > 0:
            new_row, new_col = row - 1, col
        elif move == "Down" and row < 2:
            new_row, new_col = row + 1, col
        elif move == "Left" and col > 0:
            new_row, new_col = row, col - 1
        elif move == "Right" and col < 2:
            new_row, new_col = row, col + 1
        else:
            return state  # Bước không hợp lệ
        old_idx = row * 3 + col
        new_idx = new_row * 3 + new_col
        state_list = list(state)
        state_list[old_idx], state_list[new_idx] = state_list[new_idx], state_list[old_idx]
        return ''.join(state_list)

    # Hàm áp dụng chuỗi di chuyển
    def apply_moves(start, moves_list):
        state = start
        path = [state]
        for move in moves_list:
            new_state = apply_move(state, move)
            if new_state == state:  # Bước không hợp lệ
                break
            state = new_state
            path.append(state)
        return state, path

    # Hàm tạo cá thể ngẫu nhiên
    def generate_individual(length):
        return [random.choice(moves) for _ in range(length)]

    # Hàm tạo quần thể
    def generate_population(size, length):
        return [generate_individual(length) for _ in range(size)]

    # Hàm fitness
    def fitness(moves_list):
        final_state, _ = apply_moves(start_state, moves_list)
        h = heuristic(final_state, goal_state)
        penalty = len(moves_list) * 0.1  # Phạt độ dài chuỗi
        return h + penalty

    # Hàm lai ghép
    def crossover(parent1, parent2):
        split = random.randint(1, len(parent1) - 1)
        child = parent1[:split] + parent2[split:]
        return child

    # Hàm đột biến
    def mutate(moves_list):
        moves_list = moves_list.copy()
        for i in range(len(moves_list)):
            if random.random() < mutation_rate:
                moves_list[i] = random.choice(moves)
        return moves_list

    # Khởi tạo
    max_moves = 50  # Giới hạn số bước tối đa
    population = generate_population(population_size, max_moves)
    nodes_expanded = population_size
    best_fitness = float('inf')
    best_path = [start_state]

    for generation in range(max_generations):
        # Đánh giá fitness
        fitness_scores = [(ind, fitness(ind)) for ind in population]
        fitness_scores.sort(key=lambda x: x[1])

        # Kiểm tra giải pháp
        best_individual, best_fitness = fitness_scores[0]
        final_state, path = apply_moves(start_state, best_individual)
        if final_state == goal_state:
            return path, nodes_expanded, len(path) - 1, len(path) - 1

        # Cập nhật best_path
        if fitness(best_individual) < best_fitness:
            best_fitness = fitness(best_individual)
            best_path = path

        # Chọn lọc
        elite_size = population_size // 4
        new_population = [ind for ind, _ in fitness_scores[:elite_size]]

        # Lai ghép và đột biến
        while len(new_population) < population_size:
            parent1, parent2 = random.sample([ind for ind, _ in fitness_scores[:elite_size * 2]], 2)
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)
            nodes_expanded += 1

        population = new_population

    return best_path, nodes_expanded, len(best_path) - 1, len(best_path) - 1

def belief_state_search(initial_belief_states, goal_state):
    if not any(is_solvable(state, goal_state) for state in initial_belief_states):
        return None, 0, 0, 0
    
    # Chọn một trạng thái đại diện để theo dõi đường đi
    initial_state = next(state for state in initial_belief_states if is_solvable(state, goal_state))
    initial_belief = frozenset(initial_belief_states)
    # Sử dụng A* thay vì BFS, với f = g + h
    queue = [(heuristic(initial_state, goal_state), 0, initial_belief, initial_state, [(initial_belief, initial_state)], [])]
    visited = {initial_belief: 0}  # Lưu chi phí g nhỏ nhất
    nodes_expanded = 0
    actions = ["Up", "Down", "Left", "Right"]
    
    def apply_action_to_state(state, action):
        row, col = find_zero(state)
        if action == "Up" and row > 0:
            new_row, new_col = row - 1, col
        elif action == "Down" and row < 2:
            new_row, new_col = row + 1, col
        elif action == "Left" and col > 0:
            new_row, new_col = row, col - 1
        elif action == "Right" and col < 2:
            new_row, new_col = row, col + 1
        else:
            return state
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
    
    def belief_heuristic(belief):
        # Heuristic là giá trị nhỏ nhất của Manhattan Distance từ các trạng thái trong belief đến goal_state
        return min(heuristic(state, goal_state) for state in belief)
    
    heapq.heapify(queue)
    while queue:
        _, g, current_belief, current_state, path, action_path = heapq.heappop(queue)
        
        # Kiểm tra xem bất kỳ trạng thái nào trong current_belief có khớp với goal_state không
        if goal_state in current_belief:
            # Thêm goal_state vào cuối đường đi
            state_path = [state for _, state in path]
            if state_path[-1] != goal_state:
                state_path.append(goal_state)
            return state_path, nodes_expanded, len(state_path) - 1, g
        
        for action in actions:
            next_belief = apply_action_to_belief(current_belief, action)
            next_state = apply_action_to_state(current_state, action)
            new_g = g + 1
            if next_belief not in visited or new_g < visited[next_belief]:
                visited[next_belief] = new_g
                nodes_expanded += 1
                h = belief_heuristic(next_belief)
                f = new_g + h
                heapq.heappush(queue, (f, new_g, next_belief, next_state, path + [(next_belief, next_state)], action_path + [action]))
    
    return None, nodes_expanded, 0, 0

# Hàm giao diện
def update_positions():
    global GRID_OFFSET_X, GRID_OFFSET_Y, start_rect, goal_rect, algo_rect, solve_rect, reset_rect, prev_rect, next_rect, results_pos, input_width, button_width, button_height
    CELL_SIZE = min(WIDTH // 5, HEIGHT // 5)
    GRID_OFFSET_X = WIDTH // 4 - (CELL_SIZE * 3) // 2 + 170
    GRID_OFFSET_Y = HEIGHT // 6

    # Kích thước các thành phần
    input_width = WIDTH // 4
    button_width = WIDTH // 8
    button_height = HEIGHT // 15

    # Vị trí các thành phần dưới lưới (dời lên trên)
    start_rect = pygame.Rect(WIDTH // 4 - input_width // 2 - 70 + 170, GRID_OFFSET_Y + CELL_SIZE * 3 - 70, input_width, button_height)
    goal_rect = pygame.Rect(WIDTH // 4 - input_width // 2 - 70 + 170, GRID_OFFSET_Y + CELL_SIZE * 3 + 10, input_width, button_height)
    algo_rect = pygame.Rect(GRID_OFFSET_X + 450 + 3, GRID_OFFSET_Y + CELL_SIZE * 3 - 70, input_width, button_height)  # Căn với prev_rect
    solve_rect = pygame.Rect(WIDTH // 4 - button_width - 1 - 72 + 170, GRID_OFFSET_Y + CELL_SIZE * 3 + 70, button_width, button_height)
    reset_rect = pygame.Rect(WIDTH // 4 + 10 - 72 + 170, GRID_OFFSET_Y + CELL_SIZE * 3 + 70, button_width, button_height)
    prev_rect = pygame.Rect(GRID_OFFSET_X + 450 + 3, GRID_OFFSET_Y + CELL_SIZE * 3 + 16, 80, 40)
    next_rect = pygame.Rect(GRID_OFFSET_X + CELL_SIZE * 3 + 170 + 3, GRID_OFFSET_Y + CELL_SIZE * 3 + 16, 80, 40)
    results_pos = (GRID_OFFSET_X + CELL_SIZE * 3 + 15 + 40, GRID_OFFSET_Y + 70)

def draw_board(state, screen):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            idx = i * GRID_SIZE + j
            num = state[idx]
            rect = pygame.Rect(GRID_OFFSET_X + j * CELL_SIZE, GRID_OFFSET_Y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            # Thêm bóng đổ
            shadow_surface = pygame.Surface((CELL_SIZE + 5, CELL_SIZE + 5), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 50), (5, 5, CELL_SIZE, CELL_SIZE))
            screen.blit(shadow_surface, (GRID_OFFSET_X + j * CELL_SIZE, GRID_OFFSET_Y + i * CELL_SIZE))
            # Vẽ ô
            if num == '0':
                pygame.draw.rect(screen, EMPTY_COLOR, rect)
            else:
                pygame.draw.rect(screen, TILE_COLOR, rect)
                text = BUTTON_FONT.render(num, True, TEXT_COLOR)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 2)

def draw_button(screen, text, rect, is_hover=False, is_clicked=False, is_solving=False, is_solve_button=False):
    # Chọn màu dựa trên trạng thái hover và loại nút
    color = SOLVE_BUTTON_HOVER if is_solve_button and is_hover else SOLVE_BUTTON_COLOR if is_solve_button else BUTTON_HOVER if is_hover else BUTTON_COLOR
    
    # Vẽ bóng đổ
    shadow_surface = pygame.Surface((rect.width + 5, rect.height + 5), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 50), (5, 5, rect.width, rect.height), border_radius=5)
    screen.blit(shadow_surface, (rect.x, rect.y))
    
    # Vẽ nút với màu đã chọn
    pygame.draw.rect(screen, color, rect, border_radius=5)
    
    # Thêm hiệu ứng gradient (tùy chọn, làm sáng hơn khi hover)
    gradient_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        alpha = 50 - (y * 50 // rect.height)  # Gradient nhẹ hơn
        pygame.draw.line(gradient_surface, (255, 255, 255, alpha), (0, y), (rect.width, y))
    screen.blit(gradient_surface, (rect.x, rect.y))
    
    # Vẽ văn bản
    display_text = f"{text} ({'On' if is_solving else 'Off'})" if "Solve" in text else text
    text_surf = BUTTON_FONT.render(display_text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def draw_input_box(screen, text, rect, is_active=False):
    color = (70, 70, 70) if is_active else (50, 50, 50)
    pygame.draw.rect(screen, color, rect, border_radius=5)
    text_surf = BUTTON_FONT.render(text, True, TITLE_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def draw_dropdown(screen, selected, rect, options, is_open, mouse_pos, draw_options_only=False):
    global algo_display_offset
    num_options = len(options)
    algo_display_offset = max(0, min(algo_display_offset, num_options - MAX_VISIBLE_ALGOS))
    if not draw_options_only:
        is_main_hover = rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, BUTTON_COLOR if not is_main_hover else BUTTON_HOVER, rect, border_radius=5)
        text_surf = BUTTON_FONT.render(selected, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
        pygame.draw.polygon(screen, TEXT_COLOR, [
            (rect.right - 20, rect.centery - 5),
            (rect.right - 10, rect.centery - 5),
            (rect.right - 15, rect.centery + 5)
        ])
    if is_open and draw_options_only:
        for i in range(algo_display_offset, min(algo_display_offset + MAX_VISIBLE_ALGOS, num_options)):
            option_idx = i - algo_display_offset
            option_rect = pygame.Rect(rect.x, rect.y + (option_idx + 1) * rect.height, rect.width, rect.height)
            is_option_hover = option_rect.collidepoint(mouse_pos)
            pygame.draw.rect(screen, TEXT_COLOR if not is_option_hover else BUTTON_HOVER, option_rect, border_radius=5)
            text_surf = BUTTON_FONT.render(options[i], True, TITLE_COLOR)
            text_rect = text_surf.get_rect(center=option_rect.center)
            screen.blit(text_surf, text_rect)
        up_rect = down_rect = None
        if num_options > MAX_VISIBLE_ALGOS:
            up_rect = pygame.Rect(rect.x + rect.width - 30, rect.y + rect.height, 30, 30)
            is_up_hover = up_rect.collidepoint(mouse_pos)
            pygame.draw.rect(screen, BUTTON_HOVER if is_up_hover else BUTTON_COLOR, up_rect, border_radius=5)
            pygame.draw.polygon(screen, TEXT_COLOR, [(up_rect.centerx - 5, up_rect.centery + 5), (up_rect.centerx + 5, up_rect.centery + 5), (up_rect.centerx, up_rect.centery - 5)])
            down_rect = pygame.Rect(rect.x + rect.width - 30, rect.y + (MAX_VISIBLE_ALGOS + 1) * rect.height - 30, 30, 30)
            is_down_hover = down_rect.collidepoint(mouse_pos)
            pygame.draw.rect(screen, BUTTON_HOVER if is_down_hover else BUTTON_COLOR, down_rect, border_radius=5)
            pygame.draw.polygon(screen, TEXT_COLOR, [(down_rect.centerx - 5, down_rect.centery - 5), (down_rect.centerx + 5, down_rect.centery - 5), (down_rect.centerx, down_rect.centery + 5)])
        return up_rect, down_rect
    return None, None

def draw_results(screen, elapsed_time, nodes_expanded, search_depth, path_cost, total_steps, solved, solving):
    # Vẽ khung cho Results
    panel_rect = pygame.Rect(results_pos[0], results_pos[1], 200, 150)
    panel_surface = pygame.Surface((200, 150), pygame.SRCALPHA)
    panel_surface.fill(PANEL_COLOR)
    screen.blit(panel_surface, (results_pos[0], results_pos[1]))
    pygame.draw.rect(screen, BORDER_COLOR, panel_rect, 2)

    result_text = LABEL_FONT.render("Results", True, TITLE_COLOR)
    screen.blit(result_text, (results_pos[0] + 20, results_pos[1] + 10))
    status_text = "SOLVING..." if solving else "SOLVED!" if solved else "NOT SOLVED YET!"
    status_color = SOLVING_COLOR if solving else SOLVED_COLOR if solved else NOT_SOLVED_COLOR
    solution_text = TIMER_FONT.render(status_text, True, status_color)
    screen.blit(solution_text, (results_pos[0] + 20, results_pos[1] + 40))
    runtime_text = f"Runtime: {elapsed_time:.2f} sec"
    screen.blit(TIMER_FONT.render(runtime_text, True, TITLE_COLOR), (results_pos[0] + 20, results_pos[1] + 70))
    depth_text = f"Search Depth: {search_depth}"
    screen.blit(TIMER_FONT.render(depth_text, True, TITLE_COLOR), (results_pos[0] + 20, results_pos[1] + 100))
    path_text = f"Path to Goal: {total_steps}"
    screen.blit(TIMER_FONT.render(path_text, True, TITLE_COLOR), (results_pos[0] + 20, results_pos[1] + 130))

# #def draw_minimap(screen, path, current_step):
#     if path and current_step < len(path):
#         mini_cell_size = 20
#         state = path[current_step]
#         x = GRID_OFFSET_X + CELL_SIZE * 3 + 50
#         y = GRID_OFFSET_Y + 180
#         for r in range(3):
#             for c in range(3):
#                 num = state[r * 3 + c]
#                 rect = pygame.Rect(x + c * mini_cell_size, y + r * mini_cell_size, mini_cell_size, mini_cell_size)
#                 color = TILE_COLOR if num != '0' else EMPTY_COLOR
#                 pygame.draw.rect(screen, color, rect)
#                 if num != '0':
#                     text = pygame.font.SysFont("Roboto", 12).render(num, True, TEXT_COLOR)
#                     screen.blit(text, text.get_rect(center=rect.center))
#                 pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

def animate_swap(screen, state1, state2, duration=0.2):
    zero_pos1 = find_zero(state1)
    zero_pos2 = find_zero(state2)
    idx1 = zero_pos1[0] * 3 + zero_pos1[1]
    idx2 = zero_pos2[0] * 3 + zero_pos2[1]
    num = state1[idx2]
    start_x = GRID_OFFSET_X + zero_pos1[1] * CELL_SIZE
    start_y = GRID_OFFSET_Y + zero_pos1[0] * CELL_SIZE
    end_x = GRID_OFFSET_X + zero_pos2[1] * CELL_SIZE
    end_y = GRID_OFFSET_Y + zero_pos2[0] * CELL_SIZE
    steps = int(duration * 60)
    for i in range(steps + 1):
        screen.fill(BG_COLOR)
        draw_board(state1, screen)
        x = start_x + (end_x - start_x) * i / steps
        y = start_y + (end_y - start_y) * i / steps
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, TILE_COLOR, rect)
        text = BUTTON_FONT.render(num, True, TEXT_COLOR)
        screen.blit(text, text.get_rect(center=rect.center))
        pygame.display.flip()
        clock.tick(60)

def swap_tiles(state, pos):
    row, col = pos
    zero_row, zero_col = find_zero(state)
    if abs(row - zero_row) + abs(col - zero_col) == 1:
        state_list = list(state)
        zero_idx = zero_row * 3 + zero_col
        click_idx = row * 3 + col
        state_list[zero_idx], state_list[click_idx] = state_list[click_idx], state_list[zero_idx]
        return ''.join(state_list)
    return state

def show_message_box(screen, message):
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askokcancel("Thông báo", message)
    root.destroy()
    return result

# Các biến toàn cục
algorithms = {"BFS": bfs, 
              "DFS": dfs, 
              "UCS": ucs, 
              "IDS": ids, 
              "Greedy": greedy_search, 
              "A*": astar, 
              "IDA*": ida_star, 
              "SIMPLE HC": simple_hill_climbing, 
              "STEEPEST HC": steepest_hill_climbing,
              "STOCHASTIC HC": stochastic_hill_climbing,
              "SA": simulated_annealing,
              "Beam Search": beam_search,
              "And-Or Search": and_or_search, 
              "Genetic Algorithm": genetic_algorithm,
              "Belief State Search": belief_state_search
              }
selected_algorithm = "BFS"
path = None
current_state = start_state
current_step = 0
auto_play = False
auto_speed = 0.5
last_step_time = 0
running = True
solved = False
solving = False
is_solving = False
timer_start = None
elapsed_time = 0
nodes_expanded = 0
search_depth = 0
path_cost = 0
total_steps = 0
is_shuffled = False
clock = pygame.time.Clock()
MAX_VISIBLE_ALGOS = 3
algo_display_offset = 0
solved_message_printed = False
dropdown_open = False

# Cập nhật vị trí ban đầu
update_positions()

# Vòng lặp chính
while running:
    clock.tick(60)
    screen.fill(BG_COLOR)

    # Xử lý sự kiện thay đổi kích thước cửa sổ
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.size
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            update_positions()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    rect = pygame.Rect(GRID_OFFSET_X + j * CELL_SIZE, GRID_OFFSET_Y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    if rect.collidepoint(mouse_x, mouse_y):
                        new_state = swap_tiles(current_state, (i, j))
                        if new_state != current_state:
                            #animate_swap(screen, current_state, new_state)
                            current_state = new_state
                            is_shuffled = True
                        break
            if algo_rect.collidepoint(event.pos):
                dropdown_open = not dropdown_open
            elif dropdown_open:
                num_options = len(algorithms.keys())
                up_rect, down_rect = draw_dropdown(screen, selected_algorithm, algo_rect, list(algorithms.keys()), dropdown_open, (mouse_x, mouse_y), True)
                if up_rect and up_rect.collidepoint(event.pos) and algo_display_offset > 0:
                    algo_display_offset -= 1
                elif down_rect and down_rect.collidepoint(event.pos) and algo_display_offset < num_options - MAX_VISIBLE_ALGOS:
                    algo_display_offset += 1
                else:
                    for i in range(algo_display_offset, min(algo_display_offset + MAX_VISIBLE_ALGOS, num_options)):
                        option_idx = i - algo_display_offset
                        option_rect = pygame.Rect(algo_rect.x, algo_rect.y + (option_idx + 1) * algo_rect.height, algo_rect.width, algo_rect.height)
                        if option_rect.collidepoint(event.pos):
                            selected_algorithm = list(algorithms.keys())[i]
                            dropdown_open = False
                            break
                    if not algo_rect.collidepoint(event.pos):
                        dropdown_open = False
            else:
                if prev_rect.collidepoint(event.pos) and path and current_step > 0:
                    auto_play = False
                    #animate_swap(screen, current_state, path[current_step - 1])
                    current_step -= 1
                    current_state = path[current_step]
                elif next_rect.collidepoint(event.pos) and path and current_step < len(path) - 1:
                    auto_play = False
                    #animate_swap(screen, current_state, path[current_step + 1])
                    current_step += 1
                    current_state = path[current_step]
                elif start_rect.collidepoint(event.pos):
                    input_active = "start"
                elif goal_rect.collidepoint(event.pos):
                    input_active = "goal"
                else:
                    input_active = None
                if solve_rect.collidepoint(event.pos):
                    if not is_solving:
                        if is_shuffled:
                            if not show_message_box(screen, "Please reset before solving!"):
                                running = True
                        else:
                            is_solving = True
                            start_state = start_input
                            goal_state = goal_input
                            solving = True
                            if selected_algorithm == "Belief State Search":
                                belief_states = [start_state]
                                neighbors = get_next_states(start_state)
                                for neighbor in neighbors:
                                    if len(belief_states) < 3:
                                        belief_states.append(neighbor)
                                if not any(is_solvable(state, goal_state) for state in belief_states):
                                    show_message_box(screen, "No solvable state in belief set!")
                                    is_solving = False
                                    solving = False
                                else:
                                    path, nodes_expanded, search_depth, path_cost = algorithms[selected_algorithm](belief_states, goal_state)
                                    # Debug path
                                    if path:
                                        print("Belief State Search path:", path)
                            else:
                                if not is_solvable(start_state, goal_state):
                                    show_message_box(screen, "This puzzle is not solvable!")
                                    is_solving = False
                                    solving = False
                                else:
                                    path, nodes_expanded, search_depth, path_cost = algorithms[selected_algorithm](start_state, goal_state)
                                    # Debug path
                                    if path:
                                        print(f"{selected_algorithm} path:", path)
                            if not path:
                                show_message_box(screen, "No solution found!")
                                path = [start_state]
                                total_steps = 0
                                solved = False
                                solving = False
                                is_solving = False
                                solved_message_printed = False
                            else:
                                total_steps = len(path) - 1
                                if not solved_message_printed:
                                    print(f"Solved with {selected_algorithm} in {total_steps} steps.")
                                    solved_message_printed = True
                                auto_play = True
                                solved = False
                            current_step = 0
                            current_state = start_state
                            timer_start = time.time()
                            last_step_time = time.time()
                    else:
                        is_solving = False
                        auto_play = False
                        solving = False
                        solved = False
                        solved_message_printed = False
                        timer_start = None
                        elapsed_time = 0
                elif reset_rect.collidepoint(event.pos):
                    start_input = start_state
                    goal_input = goal_state
                    start_state = start_input
                    goal_state = goal_input
                    path = None
                    current_step = 0
                    current_state = start_state
                    auto_play = False
                    solved = False
                    solving = False
                    is_solving = False
                    timer_start = None
                    elapsed_time = 0
                    nodes_expanded = 0
                    search_depth = 0
                    path_cost = 0
                    total_steps = 0
                    is_shuffled = False
                    algo_display_offset = 0
                    solved_message_printed = False
        elif event.type == pygame.KEYDOWN and input_active:
            if event.key == pygame.K_BACKSPACE:
                if input_active == "start" and len(start_input) > 0:
                    start_input = start_input[:-1]
                elif input_active == "goal" and len(goal_input) > 0:
                    goal_input = goal_input[:-1]
            elif event.unicode.isdigit() and event.unicode in "012345678":
                if input_active == "start" and len(start_input) < 9:
                    start_input += event.unicode
                elif input_active == "goal" and len(goal_input) < 9:
                    goal_input += event.unicode

    if timer_start and not solved:
        elapsed_time = time.time() - timer_start

    if auto_play and path and current_step < len(path) - 1:
        current_time = time.time()
        if current_time - last_step_time >= auto_speed:
            #animate_swap(screen, current_state, path[current_step + 1])
            current_step += 1
            current_state = path[current_step]
            last_step_time = current_time
            if current_step == len(path) - 1:
                auto_play = False
                solved = True
                solving = False
                is_solving = False

    title_text = TITLE_FONT.render("8-Puzzle Solver", True, TITLE_COLOR)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 40))

    draw_board(current_state, screen)

    start_label = LABEL_FONT.render("Initial State", True, TITLE_COLOR)
    screen.blit(start_label, (start_rect.x, start_rect.y - 30))
    draw_input_box(screen, start_input, start_rect, input_active == "start")
    goal_label = LABEL_FONT.render("Goal State", True, TITLE_COLOR)
    screen.blit(goal_label, (goal_rect.x, goal_rect.y - 30))
    draw_input_box(screen, goal_input, goal_rect, input_active == "goal")
    algo_label = LABEL_FONT.render("Algorithm", True, TITLE_COLOR)
    screen.blit(algo_label, (algo_rect.x, algo_rect.y - 30))
    mouse_pos = pygame.mouse.get_pos()


    draw_results(screen, elapsed_time, nodes_expanded, search_depth, path_cost, total_steps, solved, solving)
    is_solve_hover = solve_rect.collidepoint(mouse_pos)
    is_reset_hover = reset_rect.collidepoint(mouse_pos)
    draw_button(screen, "Solve", solve_rect, is_solve_hover, pygame.mouse.get_pressed()[0] and is_solve_hover, is_solving, True)
    draw_button(screen, "Reset", reset_rect, is_reset_hover, pygame.mouse.get_pressed()[0] and is_reset_hover)
    # Vẽ các nút Prev và Next
    is_prev_hover = prev_rect.collidepoint(mouse_pos)
    is_next_hover = next_rect.collidepoint(mouse_pos)
    draw_button(screen, "Prev", prev_rect, is_prev_hover, pygame.mouse.get_pressed()[0] and is_prev_hover)
    draw_button(screen, "Next", next_rect, is_next_hover, pygame.mouse.get_pressed()[0] and is_next_hover)
    # Vẽ dropdown sau cùng
    draw_dropdown(screen, selected_algorithm, algo_rect, list(algorithms.keys()), dropdown_open, mouse_pos, False)
    if dropdown_open:
        draw_dropdown(screen, selected_algorithm, algo_rect, list(algorithms.keys()), dropdown_open, mouse_pos, True)

    if current_state == goal_state and not solved:
        solved = True
        solving = False
        timer_start = None
        auto_play = False
        is_solving = False

    pygame.display.flip()

pygame.quit()