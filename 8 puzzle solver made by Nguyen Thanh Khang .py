import pygame
import time
from collections import deque
import heapq

pygame.init()

WIDTH = 750
HEIGHT = 700
CELL_SIZE = 150
GRID_SIZE = 3
GRID_OFFSET_X = (WIDTH - GRID_SIZE * CELL_SIZE - 150) // 2
GRID_OFFSET_Y = (HEIGHT - GRID_SIZE * CELL_SIZE - 120) // 2

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("8-Puzzle Solver made by Nguyen Thanh Khang")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (50, 150, 200)
RED = (255, 0, 0)
RED_HOVER = (220, 50, 50)
RED_CLICK = (180, 0, 0)
GREEN = (0, 255, 0)

BUTTON_FONT = pygame.font.Font(None, 36)
TIMER_FONT = pygame.font.Font(None, 30)

start_state = "265087431"
goal_state = "123456780"

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
            state_list = list(state)
            old_idx = row * 3 + col
            new_idx = new_row * 3 + new_col
            state_list[old_idx], state_list[new_idx] = state_list[new_idx], state_list[old_idx]
            next_states.append(''.join(state_list))
    return next_states

def bfs(start_state):
    queue = deque([(start_state, [start_state])])
    visited = {start_state}
    while queue:
        current_state, path = queue.popleft()
        if current_state == goal_state:
            return path
        for next_state in get_next_states(current_state):
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, path + [next_state]))
    return None

def ucs(start_state):
    queue = [(0, start_state, [start_state])] 
    visited = set() 
    heapq.heapify(queue)
    while queue:
        cost, current_state, path = heapq.heappop(queue)
        if current_state == goal_state:
            return path
        if current_state not in visited:
            visited.add(current_state)
            for next_state in get_next_states(current_state):
                if next_state not in visited:
                    new_cost = cost + 1  
                    heapq.heappush(queue, (new_cost, next_state, path + [next_state]))
    return None

def heuristic(state):
    goal_pos = {goal_state[i]: (i // 3, i % 3) for i in range(9)}
    return sum(abs(goal_pos[state[i]][0] - i // 3) + abs(goal_pos[state[i]][1] - i % 3)
               for i in range(9) if state[i] != '0')

def dfs(start_state):  
    stack = [(start_state, [start_state])]
    visited = set()
    while stack:
        current_state, path = stack.pop()
        if current_state == goal_state:
            return path
        if current_state not in visited:
            visited.add(current_state)
            next_states = get_next_states(current_state)
            next_states.sort(key=heuristic)
            for next_state in reversed(next_states):
                if next_state not in visited:
                    stack.append((next_state, path + [next_state]))
    return None

def dls(state, path, depth_limit, visited):
    if state == goal_state:
        return path
    if depth_limit == 0:
        return None
    visited.add(state)
    for next_state in get_next_states(state):
        if next_state not in visited:
            result = dls(next_state, path + [next_state], depth_limit - 1, visited)
            if result:
                return result
    visited.remove(state)
    return None

def ids_generator(start_state):
    depth = 0
    while True:
        visited = set()
        result = dls(start_state, [start_state], depth, visited)
        if result:
            yield result
            break
        depth += 1
        yield None

def draw_board(state, screen):
    screen.fill(WHITE)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            idx = i * GRID_SIZE + j
            num = state[idx]
            rect = pygame.Rect(GRID_OFFSET_X + j * CELL_SIZE, GRID_OFFSET_Y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if num == '0':
                pygame.draw.rect(screen, GRAY, rect)
            else:
                pygame.draw.rect(screen, BLUE, rect)
                text = BUTTON_FONT.render(num, True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

def draw_button(screen, text, rect, is_hover=False, is_clicked=False):
    color = RED_CLICK if is_clicked else RED_HOVER if is_hover else RED
    pygame.draw.rect(screen, color, rect)
    text_surf = BUTTON_FONT.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    pygame.draw.rect(screen, BLACK, rect, 2)

def draw_menu_button(screen, text, rect, is_selected=False, is_hover=False):
    color = GREEN if is_selected else RED_HOVER if is_hover else RED
    pygame.draw.rect(screen, color, rect)
    text_surf = BUTTON_FONT.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    pygame.draw.rect(screen, BLACK, rect, 2)

def draw_timer(screen, elapsed_time):
    time_text = f"Time: {elapsed_time:.2f}s"
    timer_surf = TIMER_FONT.render(time_text, True, BLACK)
    timer_rect = timer_surf.get_rect(topleft=(WIDTH - 150, HEIGHT - 30))
    screen.blit(timer_surf, timer_rect)

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

algorithms = {
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
    "IDS": None
}
selected_algorithm = "DFS"
path = algorithms[selected_algorithm](start_state)
if not path:
    print("Không tìm thấy lời giải!")
    exit()

current_state = start_state
current_step = 0
auto_solve = False
auto_speed = 0.6
running = True
solved = False
ids_gen = None
ids_running = False
timer_start = None
elapsed_time = 0
last_step_time = 0

clock = pygame.time.Clock()

menu_buttons = {}
menu_y_start = GRID_OFFSET_Y
for i, algo in enumerate(algorithms.keys()):
    menu_buttons[algo] = pygame.Rect(WIDTH - 140, menu_y_start + i * 50, 120, 40)

while running:
    clock.tick(60)

    screen.fill(WHITE)
    next_rect = pygame.Rect(WIDTH // 2 - 125 - 75, HEIGHT - 100, 250, 40)
    auto_rect = pygame.Rect(WIDTH // 2 - 125 - 75, HEIGHT - 50, 250, 40)
    reset_rect = pygame.Rect(WIDTH // 2 - 125 - 75, HEIGHT - 150, 250, 40)

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
            if next_rect.collidepoint(event.pos) and current_step < len(path) - 1:
                current_step += 1
                current_state = path[current_step]
            elif auto_rect.collidepoint(event.pos):
                auto_solve = not auto_solve
                if auto_solve:
                    timer_start = time.time()
                    last_step_time = time.time()
                else:
                    timer_start = None
            elif reset_rect.collidepoint(event.pos):
                current_step = 0
                current_state = start_state
                auto_solve = False
                solved = False
                ids_running = False
                ids_gen = None
                timer_start = None
                elapsed_time = 0
            for algo, rect in menu_buttons.items():
                if rect.collidepoint(mouse_x, mouse_y):
                    selected_algorithm = algo
                    current_step = 0
                    current_state = start_state
                    auto_solve = False
                    solved = False
                    timer_start = None
                    elapsed_time = 0
                    if algo == "IDS":
                        ids_gen = ids_generator(start_state)
                        ids_running = True
                        path = [start_state]
                    else:
                        ids_running = False
                        ids_gen = None
                        path = algorithms[algo](start_state)
                        if not path:
                            print(f"Không tìm thấy lời giải với {algo}!")
                            path = [start_state]

    if ids_running and ids_gen:
        result = next(ids_gen)
        if result:
            path = result
            ids_running = False
            ids_gen = None

    draw_board(current_state, screen)
    if current_state == goal_state:
        solved = True

    if solved:
        font = pygame.font.Font(None, 50)
        text = font.render("SOLVED!", True, RED)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2 - 75, HEIGHT // 2 - 50))

    mouse_pos = pygame.mouse.get_pos()
    is_next_hover = next_rect.collidepoint(mouse_pos)
    is_auto_hover = auto_rect.collidepoint(mouse_pos)
    is_reset_hover = reset_rect.collidepoint(mouse_pos)
    
    draw_button(screen, "Next Step", next_rect, is_next_hover, pygame.mouse.get_pressed()[0] and is_next_hover)
    draw_button(screen, "Auto Solve" + (" (ON)" if auto_solve else " (OFF)"), auto_rect, is_auto_hover, pygame.mouse.get_pressed()[0] and is_auto_hover)
    draw_button(screen, "Reset", reset_rect, is_reset_hover, pygame.mouse.get_pressed()[0] and is_reset_hover)

    for algo, rect in menu_buttons.items():
        is_hover = rect.collidepoint(mouse_pos)
        draw_menu_button(screen, algo, rect, algo == selected_algorithm, is_hover)
    
    # Chỉ cập nhật thời gian khi chưa giải xong và Auto Solve đang bật
    if timer_start is not None and auto_solve and not solved:
        elapsed_time = time.time() - timer_start
    draw_timer(screen, elapsed_time)

    pygame.display.flip()
    
    if auto_solve and current_step < len(path) - 1:
        current_time = time.time()
        if current_time - last_step_time >= auto_speed:
            current_step += 1
            current_state = path[current_step]
            last_step_time = current_time

pygame.quit()