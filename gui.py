import pygame
import tkinter as tk
from tkinter import messagebox

pygame.init()

BG_COLOR = (44, 62, 80)
TILE_COLOR = (255, 165, 0)
EMPTY_COLOR = (127, 140, 141)
BORDER_COLOR = (255, 255, 255)
OBSERVATION_BORDER_COLOR = (255, 0, 0)
BUTTON_COLOR = (189, 195, 199)
BUTTON_HOVER = (100, 100, 100)
SOLVE_BUTTON_COLOR = (39, 174, 96)
SOLVE_BUTTON_HOVER = (88, 214, 141)
TEXT_COLOR = (0, 0, 0)
TITLE_COLOR = (255, 255, 255)
SOLVED_COLOR = (46, 204, 113)
SOLVING_COLOR = (255, 165, 0)
NOT_SOLVED_COLOR = (231, 76, 60)
PANEL_COLOR = (52, 73, 94, 200)

TITLE_FONT = pygame.font.SysFont("Roboto", 40, bold=True)
BUTTON_FONT = pygame.font.SysFont("Roboto", 24)
TIMER_FONT = pygame.font.SysFont("Roboto", 20, bold=True)
LABEL_FONT = pygame.font.SysFont("Roboto", 20, bold=True)

CELL_SIZE = 100
GRID_SIZE = 3
MAX_VISIBLE_ALGOS = 3

GRID_OFFSET_X = 0
GRID_OFFSET_Y = 0
results_pos = (0, 0)
algo_display_offset = 0

def update_positions(WIDTH, HEIGHT):
    CELL_SIZE = min(WIDTH // 7, HEIGHT // 7)
    GRID_OFFSET_X = WIDTH // 4 - (CELL_SIZE * 3) // 2 + 170
    GRID_OFFSET_Y = HEIGHT // 6
    positions = {
        "input_width": WIDTH // 4,
        "button_width": WIDTH // 8,
        "button_height": HEIGHT // 15,
        "start_rect": pygame.Rect(WIDTH // 4 - (WIDTH // 4) // 2 - 70 + 240, GRID_OFFSET_Y + CELL_SIZE * 3 + 100, WIDTH // 4, HEIGHT // 15),
        "goal_rect": pygame.Rect(WIDTH // 4 - (WIDTH // 4) // 2 - 70 + 240, GRID_OFFSET_Y + CELL_SIZE * 3 + 150, WIDTH // 4, HEIGHT // 15),
        "algo_rect": pygame.Rect(GRID_OFFSET_X + 400, GRID_OFFSET_Y + CELL_SIZE * 3 + 100, WIDTH // 4, HEIGHT // 15),
        "solve_rect": pygame.Rect(WIDTH // 4 - WIDTH // 8 - 1 - 72 + 240, GRID_OFFSET_Y + CELL_SIZE * 3 + 200, WIDTH // 8, HEIGHT // 15),
        "reset_rect": pygame.Rect(WIDTH // 4 + 10 - 72 + 240, GRID_OFFSET_Y + CELL_SIZE * 3 + 200, WIDTH // 8, HEIGHT // 15),
        "prev_rect": pygame.Rect(GRID_OFFSET_X + 400, GRID_OFFSET_Y + CELL_SIZE * 3 + 200, 80, 40),
        "next_rect": pygame.Rect(GRID_OFFSET_X + CELL_SIZE * 3 + 200, GRID_OFFSET_Y + CELL_SIZE * 3 + 200, 80, 40),
        "results_pos": (GRID_OFFSET_X + CELL_SIZE * 3 + 90, GRID_OFFSET_Y + 70)
    }
    return CELL_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y, positions

def draw_title(screen, WIDTH):
    title_text = TITLE_FONT.render("8-Puzzle Solver", True, TITLE_COLOR)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 40))

def draw_board(state, screen, CELL_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y, selected_algorithm, latest_observation=None):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            idx = i * GRID_SIZE + j
            num = state[idx]
            rect = pygame.Rect(GRID_OFFSET_X + j * CELL_SIZE, GRID_OFFSET_Y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            tile_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            tile_color = EMPTY_COLOR + (255,) if num == '0' else TILE_COLOR + (150,) if selected_algorithm == "Belief State Search" else TILE_COLOR + (255,)
            pygame.draw.rect(tile_surface, tile_color, (0, 0, CELL_SIZE, CELL_SIZE))
            screen.blit(tile_surface, (GRID_OFFSET_X + j * CELL_SIZE, GRID_OFFSET_Y + i * CELL_SIZE))
            if num != '0':
                text = BUTTON_FONT.render(num, True, TEXT_COLOR)
                screen.blit(text, text.get_rect(center=rect.center))
            border_color = OBSERVATION_BORDER_COLOR if selected_algorithm == "Belief State Search" and latest_observation == (i, j) else BORDER_COLOR
            border_width = 4 if selected_algorithm == "Belief State Search" and latest_observation == (i, j) else 2
            pygame.draw.rect(screen, border_color, rect, border_width)

def draw_belief_states(states, title, y_offset, screen, WIDTH, small_grid_size=60):
    font = pygame.font.Font(None, 24)
    screen.blit(font.render(title, True, (255, 255, 255)), (WIDTH * 0.05, y_offset - 30))
    for idx, state in enumerate(states):
        pos_x = WIDTH * 0.05 + (idx % 5) * (3 * small_grid_size + 20)
        pos_y = y_offset + (idx // 5) * (3 * small_grid_size + 40)
        draw_small_board(state, (pos_x, pos_y), screen, f"State {idx+1}", small_grid_size)

def draw_small_board(state, position, screen, label, grid_size=60):
    x_offset, y_offset = position
    font = pygame.font.Font(None, 20)
    screen.blit(font.render(label, True, (255, 255, 255)), (x_offset, y_offset - 15))
    for i in range(3):
        for j in range(3):
            idx = i * 3 + j
            value = state[idx]
            rect = pygame.Rect(x_offset + j * grid_size, y_offset + i * grid_size, grid_size, grid_size)
            color = EMPTY_COLOR if value == '0' else TILE_COLOR
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)
            if value != '0':
                text = pygame.font.Font(None, 22).render(value, True, TEXT_COLOR)
                screen.blit(text, text.get_rect(center=rect.center))

def draw_input_box(screen, text, rect, is_active=False):
    color = (70, 70, 70) if is_active else (50, 50, 50)
    pygame.draw.rect(screen, color, rect, border_radius=5)
    text_surf = BUTTON_FONT.render(text, True, TITLE_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def draw_button(screen, text, rect, is_hover=False, is_clicked=False, is_solving=False, is_solve_button=False):
    color = SOLVE_BUTTON_HOVER if is_solve_button and is_hover else SOLVE_BUTTON_COLOR if is_solve_button else BUTTON_HOVER if is_hover else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=5)
    text_surf = BUTTON_FONT.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def draw_dropdown(screen, selected, rect, options, is_open, mouse_pos, draw_options_only=False, algo_display_offset=0):
    offset = max(0, min(algo_display_offset, len(options) - MAX_VISIBLE_ALGOS))
    up_rect = down_rect = None
    if not draw_options_only:
        is_main_hover = rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, BUTTON_COLOR if not is_main_hover else BUTTON_HOVER, rect, border_radius=5)
        text_surf = BUTTON_FONT.render(selected, True, TEXT_COLOR)
        screen.blit(text_surf, text_surf.get_rect(center=rect.center))
        pygame.draw.polygon(screen, TEXT_COLOR, [(rect.right - 20, rect.centery - 5), (rect.right - 10, rect.centery - 5), (rect.right - 15, rect.centery + 5)])
        return None, None
    if is_open and draw_options_only:
        for i in range(algo_display_offset, min(algo_display_offset + MAX_VISIBLE_ALGOS, len(options))):
            option_idx = i - algo_display_offset
            option_rect = pygame.Rect(rect.x, rect.y + (option_idx + 1) * rect.height, rect.width, rect.height)
            is_option_hover = option_rect.collidepoint(mouse_pos)
            pygame.draw.rect(screen, TEXT_COLOR if not is_option_hover else BUTTON_HOVER, option_rect, border_radius=5)
            text_surf = BUTTON_FONT.render(options[i], True, TITLE_COLOR)
            screen.blit(text_surf, text_surf.get_rect(center=option_rect.center))
        if len(options) > MAX_VISIBLE_ALGOS:
            up_rect = pygame.Rect(rect.x + rect.width - 30, rect.y + rect.height, 30, 30)
            pygame.draw.rect(screen, BUTTON_COLOR, up_rect, border_radius=5)
            pygame.draw.polygon(screen, TEXT_COLOR, [(up_rect.centerx - 5, up_rect.centery + 5), (up_rect.centerx + 5, up_rect.centery + 5), (up_rect.centerx, up_rect.centery - 5)])
            down_rect = pygame.Rect(rect.x + rect.width - 30, rect.y + (MAX_VISIBLE_ALGOS + 1) * rect.height - 30, 30, 30)
            pygame.draw.rect(screen, BUTTON_COLOR, down_rect, border_radius=5)
            pygame.draw.polygon(screen, TEXT_COLOR, [(down_rect.centerx - 5, down_rect.centery - 5), (down_rect.centerx + 5, down_rect.centery - 5), (down_rect.centerx, down_rect.centery + 5)])
    return up_rect, down_rect

def draw_results(screen, elapsed_time, nodes_expanded, search_depth, path_cost, total_steps, solved, solving, results_pos, belief_size=0, goal_prob=0, latest_observation=None):
    panel_rect = pygame.Rect(results_pos[0], results_pos[1], 200, 220)
    panel_surface = pygame.Surface((200, 220), pygame.SRCALPHA)
    panel_surface.fill(PANEL_COLOR)
    screen.blit(panel_surface, (results_pos[0], results_pos[1]))
    pygame.draw.rect(screen, BORDER_COLOR, panel_rect, 2)
    result_text = LABEL_FONT.render("Results", True, TITLE_COLOR)
    screen.blit(result_text, (results_pos[0] + 20, results_pos[1] + 10))
    status_text = "SOLVING..." if solving else "SOLVED!" if solved else "NOT SOLVED YET!"
    status_color = SOLVING_COLOR if solving else SOLVED_COLOR if solved else NOT_SOLVED_COLOR
    solution_text = TIMER_FONT.render(status_text, True, status_color)
    screen.blit(solution_text, (results_pos[0] + 20, results_pos[1] + 40))
    screen.blit(TIMER_FONT.render(f"Runtime: {elapsed_time:.2f} sec", True, TITLE_COLOR), (results_pos[0] + 20, results_pos[1] + 70))
    screen.blit(TIMER_FONT.render(f"Search Depth: {search_depth}", True, TITLE_COLOR), (results_pos[0] + 20, results_pos[1] + 100))
    screen.blit(TIMER_FONT.render(f"Path to Goal: {total_steps}", True, TITLE_COLOR), (results_pos[0] + 20, results_pos[1] + 130))

def swap_tiles(state, pos):
    from utils import find_zero
    row, col = pos
    zero_row, zero_col = find_zero(state)
    if abs(row - zero_row) + abs(col - zero_col) == 1:
        state_list = list(state)
        zero_idx = zero_row * 3 + zero_col
        click_idx = row * 3 + col
        state_list[zero_idx], state_list[click_idx] = state_list[click_idx], state_list[zero_idx]
        return ''.join(state_list)
    return state

def show_message_box(message):
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askokcancel("Thông báo", message)
    root.destroy()
    return result


# Tạo class riêng trong file mới (hoặc cuối file gui.py)
class SensorlessScreen:
    def __init__(self, screen, width, height, solution_steps):
        self.screen = screen
        self.width = width
        self.height = height
        self.solution = solution_steps  # List of sets
        self.current_step = 0

        self.NEXT_BUTTON = pygame.Rect(self.width * 0.8, self.height * 0.3, 150, 50)
        self.PREV_BUTTON = pygame.Rect(self.width * 0.8, self.height * 0.4, 150, 50)
        self.BACK_BUTTON = pygame.Rect(self.width * 0.8, self.height * 0.5, 150, 50)

    def draw(self):
        self.screen.fill((44, 62, 80))  # giống màu nền gốc

        draw_title(self.screen, self.width)
        draw_belief_states(list(self.solution[0]), "Initial Belief State", self.height * 0.15, self.screen, self.width)

        if self.current_step > 0:
            draw_belief_states(list(self.solution[self.current_step]), f"Belief Step {self.current_step}", self.height * 0.5, self.screen, self.width)

        # Nút
        draw_button(self.screen, "Next", self.NEXT_BUTTON, is_hover=self.NEXT_BUTTON.collidepoint(pygame.mouse.get_pos()))
        draw_button(self.screen, "Previous", self.PREV_BUTTON, is_hover=self.PREV_BUTTON.collidepoint(pygame.mouse.get_pos()))
        draw_button(self.screen, "Back to Main", self.BACK_BUTTON, is_hover=self.BACK_BUTTON.collidepoint(pygame.mouse.get_pos()))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.NEXT_BUTTON.collidepoint(event.pos):
                if self.current_step < len(self.solution) - 1:
                    self.current_step += 1
            elif self.PREV_BUTTON.collidepoint(event.pos):
                if self.current_step > 0:
                    self.current_step -= 1
            elif self.BACK_BUTTON.collidepoint(event.pos):
                return False  # quay về giao diện chính
        return True


class PartialObservationScreen:
    def __init__(self, screen, width, height, solution_steps):
        self.screen = screen
        self.width = width
        self.height = height
        self.solution = solution_steps
        self.current_step = 0

        self.NEXT_BUTTON = pygame.Rect(self.width * 0.8, self.height * 0.3, 150, 50)
        self.PREV_BUTTON = pygame.Rect(self.width * 0.8, self.height * 0.4, 150, 50)
        self.BACK_BUTTON = pygame.Rect(self.width * 0.8, self.height * 0.5, 150, 50)

    def draw(self):
        self.screen.fill((44, 62, 80))
        draw_title(self.screen, self.width)
        draw_belief_states(list(self.solution[0]), "Initial Belief State", self.height * 0.15, self.screen, self.width)

        if self.current_step > 0:
            draw_belief_states(list(self.solution[self.current_step]), f"Step {self.current_step}", self.height * 0.5, self.screen, self.width)

        draw_button(self.screen, "Next", self.NEXT_BUTTON, is_hover=self.NEXT_BUTTON.collidepoint(pygame.mouse.get_pos()))
        draw_button(self.screen, "Previous", self.PREV_BUTTON, is_hover=self.PREV_BUTTON.collidepoint(pygame.mouse.get_pos()))
        draw_button(self.screen, "Back to Main", self.BACK_BUTTON, is_hover=self.BACK_BUTTON.collidepoint(pygame.mouse.get_pos()))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.NEXT_BUTTON.collidepoint(event.pos):
                if self.current_step < len(self.solution) - 1:
                    self.current_step += 1
            elif self.PREV_BUTTON.collidepoint(event.pos):
                if self.current_step > 0:
                    self.current_step -= 1
            elif self.BACK_BUTTON.collidepoint(event.pos):
                return False
        return True



class QLearningScreen:
    def __init__(self, screen, width, height, solution_steps):
        self.screen = screen
        self.width = width
        self.height = height
        self.solution = solution_steps  # List of strings (states)
        self.current_step = 0

        self.NEXT_BUTTON = pygame.Rect(self.width * 0.8, self.height * 0.3, 150, 50)
        self.PREV_BUTTON = pygame.Rect(self.width * 0.8, self.height * 0.4, 150, 50)
        self.BACK_BUTTON = pygame.Rect(self.width * 0.8, self.height * 0.5, 150, 50)

    def draw(self):
        self.screen.fill((44, 62, 80))  # Màu nền

        # Căn giữa bảng puzzle
        center_x = self.width // 2 - (CELL_SIZE * 3) // 2
        center_y = self.height // 2 - (CELL_SIZE * 3) // 2 - 50

        # Vẽ bảng
        state = self.solution[self.current_step]
        for i in range(3):
            for j in range(3):
                idx = i * 3 + j
                num = state[idx]
                rect = pygame.Rect(center_x + j * CELL_SIZE, center_y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                color = EMPTY_COLOR if num == '0' else TILE_COLOR
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
                if num != '0':
                    font = pygame.font.Font(None, 48)
                    text = font.render(num, True, TEXT_COLOR)
                    self.screen.blit(text, text.get_rect(center=rect.center))

        # Vẽ bước hiện tại
        step_text = TITLE_FONT.render(f"Step: {self.current_step}/{len(self.solution) - 1}", True, (255, 255, 255))
        self.screen.blit(step_text, (center_x, center_y + CELL_SIZE * 3 + 20))

        # ✅ Thêm dòng chữ mô tả Q-learning
        msg_text = TITLE_FONT.render("Q-learning found a solution path", True, (255, 255, 255))
        self.screen.blit(msg_text, (center_x, center_y + CELL_SIZE * 3 + 50))

        # Nút điều khiển
        draw_button(self.screen, "Next", self.NEXT_BUTTON, is_hover=self.NEXT_BUTTON.collidepoint(pygame.mouse.get_pos()))
        draw_button(self.screen, "Previous", self.PREV_BUTTON, is_hover=self.PREV_BUTTON.collidepoint(pygame.mouse.get_pos()))
        draw_button(self.screen, "Back to Main", self.BACK_BUTTON, is_hover=self.BACK_BUTTON.collidepoint(pygame.mouse.get_pos()))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.NEXT_BUTTON.collidepoint(event.pos):
                if self.current_step < len(self.solution) - 1:
                    self.current_step += 1
            elif self.PREV_BUTTON.collidepoint(event.pos):
                if self.current_step > 0:
                    self.current_step -= 1
            elif self.BACK_BUTTON.collidepoint(event.pos):
                return False
        return True
