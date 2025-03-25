import pygame
import time
from collections import deque
import heapq
import threading
import tkinter as tk
from tkinter import messagebox
pygame.init()

# Kích thước giao diện
WIDTH = 900
HEIGHT = 700
CELL_SIZE = 100
GRID_SIZE = 3
GRID_OFFSET_X = 300  # Đặt bảng puzzle ở giữa
GRID_OFFSET_Y = 150

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("8-Puzzle Solver by Nguyen Thanh Khang")

# Màu sắc
BG_COLOR = (30, 30, 30)         # Đen đậm (giống hình)
TILE_COLOR = (0, 120, 255)      # Xanh dương
EMPTY_COLOR = (50, 50, 50)      # Xám đậm cho ô trống
BORDER_COLOR = (255, 255, 255)  # Viền trắng
BUTTON_COLOR = (50, 50, 50)     # Nút xám đậm
BUTTON_HOVER = (70, 70, 70)     # Hover sáng hơn
BUTTON_CLICK = (30, 30, 30)     # Click tối hơn
TEXT_COLOR = (255, 255, 255)    # Chữ trắng
SOLVED_COLOR = (0, 255, 0)      # Xanh lá cho "SOLVED!"
SOLVING_COLOR = (255, 215, 0)   # Vàng cho "SOLVING..."
NOT_SOLVED_COLOR = (255, 0, 0)  # Đỏ cho "CLICK TO SOLVE!"

# Font chữ
TITLE_FONT = pygame.font.SysFont("Arial", 40, bold=True)
BUTTON_FONT = pygame.font.SysFont("Arial", 24)
TIMER_FONT = pygame.font.SysFont("Arial", 20, bold=True)

# Trạng thái ban đầu và mục tiêu
start_state = "265087431"
goal_state = "123456780"

# Biến để lưu trạng thái nhập liệu
start_input = start_state
goal_input = goal_state
input_active = None  # None, "start", hoặc "goal"

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

def bfs(start_state, goal_state):
    queue = deque([(start_state, [start_state], 0)])  # (state, path, nodes_expanded)
    visited = {start_state}
    while queue:
        current_state, path, nodes = queue.popleft()
        if current_state == goal_state:
            return path, nodes, len(path) - 1, len(path) - 1  # path, nodes_expanded, search_depth, path_cost
        for next_state in get_next_states(current_state):
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, path + [next_state], nodes + 1))
    return None, 0, 0, 0

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

# Thêm vào đầu hàm ucs


def ucs(start_state, goal_state):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0
    queue = [(0, start_state, None, 0)]  # (cost, state, parent, nodes_expanded)
    visited = {start_state: 0}  # Lưu trạng thái và chi phí thấp nhất
    parents = {}  # Lưu cha của mỗi trạng thái
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
    return path[::-1]  # Đảo ngược để từ start đến goal

def heuristic(state, goal_state):
    goal_pos = {goal_state[i]: (i // 3, i % 3) for i in range(9)}
    return sum(abs(goal_pos[state[i]][0] - i // 3) + abs(goal_pos[state[i]][1] - i % 3)
               for i in range(9) if state[i] != '0')

def dfs(start_state, goal_state):
    stack = [(start_state, [start_state], 0)]  # (state, path, nodes_expanded)
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

def dls_iterative(start_state, goal_state, depth_limit):
    stack = [(start_state, [start_state], 0)]  # (state, path, depth)
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

def ids(start_state, goal_state):
    depth = 0
    nodes_expanded = 0
    while True:
        result, new_nodes = dls_iterative(start_state, goal_state, depth)
        nodes_expanded += new_nodes
        if result:
            return result, nodes_expanded, depth, len(result) - 1
        depth += 1

def mahatan(state, goal_state):
    goal_pos = {goal_state[i]: (i // 3, i % 3) for i in range(9)}
    return sum(abs(goal_pos[state[i]][0] - i // 3) + abs(goal_pos[state[i]][1] - i % 3)
               for i in range(9) if state[i] != '0')

def greedy_search(start_state, goal_state):
    queue = [(mahatan(start_state, goal_state), start_state, [start_state], 0)]  # (h, state, path, nodes_expanded)
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
                    heapq.heappush(queue, (mahatan(next_state, goal_state), next_state, path + [next_state], nodes + 1))
    return None, 0, 0, 0

def astar(start_state, goal_state):
    queue = [(mahatan(start_state, goal_state), 0, start_state, [start_state], 0)]  # (f, g, state, path, nodes_expanded)
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
    # Hàm tính f(n) = g(n) + h(n)
    def f_cost(state, g):
        return g + mahatan(state, goal_state)

    # Hàm tìm kiếm đệ quy với ngưỡng
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

    # Kiểm tra tính khả thi
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0

    # Khởi tạo
    threshold = mahatan(start_state, goal_state)
    path = [start_state]
    visited = {start_state}
    nodes_expanded = [0]  # Dùng list để có thể thay đổi giá trị trong hàm đệ quy
    max_depth = 0

    # Vòng lặp chính của IDA*
    while True:
        new_threshold, result = search(start_state, 0, threshold, path, visited, nodes_expanded)
        if result is not None:
            max_depth = len(result) - 1
            return result, nodes_expanded[0], max_depth, max_depth
        if new_threshold == float('inf'):
            return None, nodes_expanded[0], 0, 0
        threshold = new_threshold

def draw_board(state, screen):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            idx = i * GRID_SIZE + j
            num = state[idx]
            rect = pygame.Rect(GRID_OFFSET_X + j * CELL_SIZE, GRID_OFFSET_Y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if num == '0':
                pygame.draw.rect(screen, EMPTY_COLOR, rect)
            else:
                pygame.draw.rect(screen, TILE_COLOR, rect)
                text = BUTTON_FONT.render(num, True, TEXT_COLOR)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 2)

def draw_button(screen, text, rect, is_hover=False, is_clicked=False, is_solving=False):
    color = BUTTON_CLICK if is_clicked else BUTTON_HOVER if is_hover else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=5)
    # Nếu là nút "Solve Puzzle", hiển thị trạng thái (On) hoặc (Off)
    if "Solve Puzzle" in text:
        display_text = f"Solve Puzzle ({'On' if is_solving else 'Off'})"
    else:
        display_text = text
    text_surf = BUTTON_FONT.render(display_text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def draw_input_box(screen, text, rect, is_active=False):
    color = (100, 100, 100) if is_active else (50, 50, 50)
    pygame.draw.rect(screen, color, rect, border_radius=5)
    text_surf = BUTTON_FONT.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def draw_dropdown(screen, selected, rect, options, is_open, mouse_pos, draw_options_only=False):
    if not draw_options_only:
        # Vẽ nút chính
        is_main_hover = rect.collidepoint(mouse_pos)
        draw_button(screen, selected, rect, is_main_hover, pygame.mouse.get_pressed()[0] and is_main_hover)
        # Vẽ mũi tên xuống
        pygame.draw.polygon(screen, TEXT_COLOR, [
            (rect.right - 20, rect.centery - 5),
            (rect.right - 10, rect.centery - 5),
            (rect.right - 15, rect.centery + 5)
        ])
    # Vẽ menu thả xuống nếu đang mở
    if is_open and draw_options_only:
        for i, option in enumerate(options):
            option_rect = pygame.Rect(rect.x, rect.y + (i + 1) * rect.height, rect.width, rect.height)
            is_option_hover = option_rect.collidepoint(mouse_pos)
            # Sử dụng draw_button để vẽ ô với hiệu ứng hover
            draw_button(screen, option, option_rect, is_option_hover, pygame.mouse.get_pressed()[0] and is_option_hover)

def draw_results(screen, elapsed_time, nodes_expanded, search_depth, path_cost, total_steps, solved, solving):
    # Tiêu đề Results
    result_text = TIMER_FONT.render("Results", True, TEXT_COLOR)
    screen.blit(result_text, (650, 150))

    # Hiển thị trạng thái giải puzzle
    if solving:
        solution_text = TIMER_FONT.render("SOLVING...", True, SOLVING_COLOR)
    elif solved:
        solution_text = TIMER_FONT.render("SOLVED!", True, SOLVED_COLOR)
    else:
        solution_text = TIMER_FONT.render("NOT SOLVED YET!", True, NOT_SOLVED_COLOR)
    screen.blit(solution_text, (650, 190))

    # Hiển thị thời gian chạy (Runtime)
    runtime_text = f"Runtime: {elapsed_time:.2f} sec"
    runtime_surf = TIMER_FONT.render(runtime_text, True, TEXT_COLOR)
    screen.blit(runtime_surf, (650, 225))  # Đặt ngay dưới dòng trạng thái (y=200 + 25)

    # Search Depth
    depth_text = f"Search Depth: {search_depth}"
    depth_surf = TIMER_FONT.render(depth_text, True, TEXT_COLOR)
    screen.blit(depth_surf, (650, 260))

    # Path to Goal
    path_text = f"Path to Goal: {total_steps}"
    path_surf = TIMER_FONT.render(path_text, True, TEXT_COLOR)
    screen.blit(path_surf, (650, 300))

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
    root.withdraw()  # Ẩn cửa sổ chính của tkinter
    result = messagebox.askokcancel("Thông báo", message)
    root.destroy()
    return result

# Các thuật toán
algorithms = {
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
    "IDS": ids,
    "Greedy": greedy_search,
    "A*": astar,
    "IDA*": ida_star
}
selected_algorithm = "DFS"
path = None
current_state = start_state
current_step = 0
auto_play = False
auto_speed = 0.5  # Tốc độ tự động chạy (giây mỗi bước)
last_step_time = 0
running = True
solved = False
solving = False
is_solving = False  # Trạng thái của nút "Solve Puzzle" (On/Off)
timer_start = None
elapsed_time = 0
nodes_expanded = 0
search_depth = 0
path_cost = 0
total_steps = 0
is_shuffled = False
message = ""
clock = pygame.time.Clock()

# Vùng bên trái
start_rect = pygame.Rect(50, 190, 200, 40)
goal_rect = pygame.Rect(50, 270, 200, 40)
algo_rect = pygame.Rect(50, 350, 200, 40)

# Vùng bên phải (cùng với Results)
solve_rect = pygame.Rect(650, 350, 200, 40)  # Đặt ở x=650, y=400 (dưới Results)
reset_rect = pygame.Rect(650, 400, 200, 40)  # Đặt ở x=650, y=450 (dưới Solve Puzzle)

# Vùng giữa
prev_rect = pygame.Rect(GRID_OFFSET_X + CELL_SIZE * 1 - 50, GRID_OFFSET_Y + CELL_SIZE * 3 + 50, 80, 40)
next_rect = pygame.Rect(GRID_OFFSET_X + CELL_SIZE * 2 - 30, GRID_OFFSET_Y + CELL_SIZE * 3 + 50, 80, 40)

# Dropdown state
dropdown_open = False

while running:
    clock.tick(60)

    screen.fill(BG_COLOR)

    # Tiêu đề
    title_text = TITLE_FONT.render("8-Puzzle Solver", True, TEXT_COLOR)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    rect = pygame.Rect(GRID_OFFSET_X + j * CELL_SIZE, GRID_OFFSET_Y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    if rect.collidepoint(mouse_x, mouse_y):
                        current_state = swap_tiles(current_state, (i, j))
                        if current_state != start_state:  # Nếu trạng thái thay đổi so với ban đầu
                            is_shuffled = True  # Đánh dấu là đã xáo trộn
                        break  # Thoát vòng lặp nếu đã xử lý bảng puzzle

            if algo_rect.collidepoint(event.pos):
                dropdown_open = not dropdown_open

            elif dropdown_open:
                # Ưu tiên xử lý chọn thuật toán khi menu thả xuống đang mở
                for i, algo in enumerate(algorithms.keys()):
                    option_rect = pygame.Rect(algo_rect.x, algo_rect.y + (i + 1) * algo_rect.height, algo_rect.width, algo_rect.height)
                    if option_rect.collidepoint(event.pos):
                        selected_algorithm = algo
                        dropdown_open = False
                        break  # Thoát vòng lặp sau khi chọn thuật toán

                if not algo_rect.collidepoint(event.pos):
                    dropdown_open = False
            else:
                # Xử lý nút Prev/Next
                if prev_rect.collidepoint(event.pos) and path is not None and current_step > 0:
                    auto_play = False  # Tắt auto_play khi nhấn thủ công
                    current_step -= 1
                    current_state = path[current_step]
                elif next_rect.collidepoint(event.pos) and path is not None and current_step < len(path) - 1:
                    auto_play = False  # Tắt auto_play khi nhấn thủ công
                    current_step += 1
                    current_state = path[current_step]
                # Xử lý input Start State
                elif start_rect.collidepoint(event.pos):
                    input_active = "start"
                elif goal_rect.collidepoint(event.pos):
                    input_active = "goal"
                else:
                    input_active = None
                # Xử lý nút Solve
                if solve_rect.collidepoint(event.pos):
                    if not is_solving:  # Nếu đang ở trạng thái "Off", bắt đầu giải
                        if is_shuffled:  # Kiểm tra xem có xáo trộn không
                            if not show_message_box(screen, "Please reset before solving!"):
                                running = True
                        else:
                            is_solving = True
                            start_state = start_input
                            goal_state = goal_input
                            solving = True
                            path, nodes_expanded, search_depth, path_cost = algorithms[selected_algorithm](start_state, goal_state)
                            if not path:
                                print("Không tìm thấy lời giải!")
                                path = [start_state]
                                total_steps = 0
                                solved = False
                                solving = False
                                is_solving = False  # Quay lại trạng thái "Off" nếu không có lời giải
                            else:
                                total_steps = len(path) - 1
                                print(f"Solved with {selected_algorithm} in {total_steps} steps.")
                                auto_play = True  # Bật chế độ tự động chạy
                                solved = False  # Reset solved để thời gian chạy
                            current_step = 0
                            current_state = start_state
                            timer_start = time.time()
                            last_step_time = time.time()
                    else:  # Nếu đang ở trạng thái "On", dừng giải
                        is_solving = False
                        auto_play = False
                        solving = False
                        solved = False
                        timer_start = None
                        elapsed_time = 0
                # Xử lý nút Reset
                elif reset_rect.collidepoint(event.pos):
                    start_input = "265087431"
                    goal_input = "123456780"
                    start_state = start_input
                    goal_state = goal_input
                    path = None
                    current_step = 0
                    current_state = start_state
                    auto_play = False
                    solved = False
                    solving = False
                    is_solving = False  # Reset trạng thái nút "Solve Puzzle"
                    timer_start = None
                    elapsed_time = 0
                    nodes_expanded = 0
                    search_depth = 0
                    path_cost = 0
                    total_steps = 0
                    is_shuffled = False
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

    # Cập nhật thời gian
    if timer_start is not None and not solved:
        elapsed_time = time.time() - timer_start

    # Tự động chạy các bước giải
    if auto_play and path is not None and current_step < len(path) - 1:
        current_time = time.time()
        if current_time - last_step_time >= auto_speed:
            current_step += 1
            current_state = path[current_step]
            last_step_time = current_time
            if current_step == len(path) - 1:
                auto_play = False
                solved = True  # Đánh dấu puzzle đã được giải xong
                solving = False
                is_solving = False  # Quay lại trạng thái "Off" khi giải xong

    draw_board(current_state, screen)

    # Vẽ vùng bên trái
    start_label = TIMER_FONT.render("Initial state", True, TEXT_COLOR)
    screen.blit(start_label, (50, 160))
    draw_input_box(screen, start_input, start_rect, input_active == "start")

    goal_label = TIMER_FONT.render("Goal state", True, TEXT_COLOR)
    screen.blit(goal_label, (50, 240))
    draw_input_box(screen, goal_input, goal_rect, input_active == "goal")

    algo_label = TIMER_FONT.render("Choose Algorithm", True, TEXT_COLOR)
    screen.blit(algo_label, (50, 320))

    # Vẽ nút chính của menu thả xuống (không vẽ các tùy chọn)
    mouse_pos = pygame.mouse.get_pos()
    draw_dropdown(screen, selected_algorithm, algo_rect, list(algorithms.keys()), dropdown_open, mouse_pos, draw_options_only=False)

    # Vẽ các tùy chọn của menu thả xuống (nếu đang mở)
    if dropdown_open:
        draw_dropdown(screen, selected_algorithm, algo_rect, list(algorithms.keys()), dropdown_open, mouse_pos, draw_options_only=True)

    # Vẽ vùng giữa
    is_prev_hover = prev_rect.collidepoint(mouse_pos)
    is_next_hover = next_rect.collidepoint(mouse_pos)
    draw_button(screen, "Prev", prev_rect, is_prev_hover, pygame.mouse.get_pressed()[0] and is_prev_hover)
    draw_button(screen, "Next", next_rect, is_next_hover, pygame.mouse.get_pressed()[0] and is_next_hover)

    # Vẽ vùng bên phải
    draw_results(screen, elapsed_time, nodes_expanded, search_depth, path_cost, total_steps, solved, solving)

    # Vẽ các nút "Solve Puzzle" và "Reset" ở vùng bên phải (dưới Results)
    is_solve_hover = solve_rect.collidepoint(mouse_pos)
    is_reset_hover = reset_rect.collidepoint(mouse_pos)
    draw_button(screen, "Solve Puzzle", solve_rect, is_solve_hover, pygame.mouse.get_pressed()[0] and is_solve_hover, is_solving)
    draw_button(screen, "Reset", reset_rect, is_reset_hover, pygame.mouse.get_pressed()[0] and is_reset_hover)
    
    # Kiểm tra trạng thái solved
    if current_state == goal_state:
        solved = True
        solving = False
        timer_start = None  # Dừng thời gian khi giải xong

    pygame.display.flip()

pygame.quit()