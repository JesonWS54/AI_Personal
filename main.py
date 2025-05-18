import pygame
import time
import threading
from gui import *
from utils import *
from algorithms import algorithms  
import random

# Khởi tạo Pygame
pygame.init()
WIDTH = 900
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("8-Puzzle Solver")

# Biến trạng thái
start_state = "123045786"
goal_state = "123456780"
start_input = start_state
goal_input = goal_state
input_active = None
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
dropdown_open = False
is_paused = False
belief_states = set([start_state])
latest_observation = None
goal_probability = 0
computing = False
progress_text = ""
search_thread = None
sensorless_screen = None
active_screen = "main"

CELL_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y, positions = update_positions(WIDTH, HEIGHT)

def run_belief_state_search(belief_states, goal_state, result_container):
    def progress_callback(step, sim_progress):
        global progress_text
        progress_text = f"Computing... Step {step}, Simulations: {sim_progress:.0%}"

    try:
        path, nodes_expanded, search_depth, path_cost = algorithms["Belief State Search"](belief_states, goal_state, progress_callback)
        result_container['path'] = path
        result_container['nodes_expanded'] = nodes_expanded
        result_container['search_depth'] = search_depth
        result_container['path_cost'] = path_cost
    except Exception as e:
        result_container['error'] = str(e)

def run_partial_observation_search(belief_states, goal_state, result_container):
    def progress_callback(step, sim_progress):
        global progress_text
        progress_text = f"Partial Obs... Step {step}, Simulations: {sim_progress:.0%}"

    try:
        path, nodes_expanded, search_depth, path_cost = algorithms["Partial Obs. Search"](belief_states, goal_state, progress_callback)
        result_container['path'] = path
        result_container['nodes_expanded'] = nodes_expanded
        result_container['search_depth'] = search_depth
        result_container['path_cost'] = path_cost
    except Exception as e:
        result_container['error'] = str(e)


# Main loop
while running:
    clock.tick(60)
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if active_screen == "sensorless":
            if not sensorless_screen.handle_event(event):
                active_screen = "main"
                solving = is_solving = False
                sensorless_screen = None
            continue

        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.size
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            CELL_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y, positions = update_positions(WIDTH, HEIGHT)

        elif event.type == pygame.MOUSEBUTTONDOWN and not computing:
            mouse_x, mouse_y = event.pos

            if selected_algorithm != "Belief State Search":
                for i in range(3):
                    for j in range(3):
                        rect = pygame.Rect(GRID_OFFSET_X + j * CELL_SIZE, GRID_OFFSET_Y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        if rect.collidepoint(mouse_x, mouse_y):
                            new_state = swap_tiles(current_state, (i, j))
                            if new_state != current_state:
                                current_state = new_state
                                is_shuffled = True
                            break

            if positions['algo_rect'].collidepoint(event.pos):
                dropdown_open = not dropdown_open
            elif dropdown_open:
                num_options = len(algorithms.keys())
                up_rect, down_rect = draw_dropdown(screen, selected_algorithm, positions['algo_rect'], list(algorithms.keys()), dropdown_open, (mouse_x, mouse_y), True, algo_display_offset)
                if up_rect and up_rect.collidepoint(event.pos):
                    algo_display_offset = max(0, algo_display_offset - 1)
                elif down_rect and down_rect.collidepoint(event.pos):
                    algo_display_offset = min(len(algorithms) - MAX_VISIBLE_ALGOS, algo_display_offset + 1)
                else:
                    for i in range(algo_display_offset, min(algo_display_offset + MAX_VISIBLE_ALGOS, num_options)):
                        option_rect = pygame.Rect(positions['algo_rect'].x, positions['algo_rect'].y + (i - algo_display_offset + 1) * positions['algo_rect'].height, positions['algo_rect'].width, positions['algo_rect'].height)
                        if option_rect.collidepoint(event.pos):
                            selected_algorithm = list(algorithms.keys())[i]
                            dropdown_open = False
                            break
            else:
                if positions['prev_rect'].collidepoint(event.pos) and path and current_step > 0:
                    current_step -= 1
                    current_state = random.choice(list(path[current_step]))
                    auto_play = False
                elif positions['next_rect'].collidepoint(event.pos) and path and current_step < len(path) - 1:
                    current_step += 1
                    current_state = next(iter(path[current_step]))
                    auto_play = False
                elif positions['start_rect'].collidepoint(event.pos):
                    input_active = "start"
                elif positions['goal_rect'].collidepoint(event.pos):
                    input_active = "goal"
                elif positions['solve_rect'].collidepoint(event.pos):
                    if solving:
                        auto_play = not auto_play
                        is_paused = not auto_play
                    elif not is_solving:
                        if is_shuffled:
                            show_message_box("Please reset before solving!")
                        else:
                            is_solving = True
                            start_state = start_input
                            goal_state = goal_input
                            solving = True
                            is_paused = False

                            if selected_algorithm in ["Belief State Search", "Partial Obs. Search"]:
                                belief_states = set([start_state] + get_next_states(start_state)[:2])
                                if not any(is_solvable(state, goal_state) for state in belief_states):
                                    show_message_box("No solvable state in belief set!")
                                    solving = is_solving = False
                                else:
                                    computing = True
                                    result_container = {}
                                    search_thread = threading.Thread(
    target=run_belief_state_search if selected_algorithm == "Belief State Search" else run_partial_observation_search,
    args=(belief_states, goal_state, result_container)
)
                                    search_thread.start()
                                    timer_start = time.time()
                                    progress_text = "Computing... Initializing"
                            else:
                                if not is_solvable(start_state, goal_state):
                                    show_message_box("This puzzle is not solvable!")
                                    solving = is_solving = False
                                else:
                                    path, nodes_expanded, search_depth, path_cost = algorithms[selected_algorithm](start_state, goal_state)
                                    if not path:
                                        show_message_box("No solution found!")
                                        path = [start_state]
                                        total_steps = 0
                                        solved = solving = is_solving = False
                                    else:
                                        total_steps = len(path) - 1
                                        auto_play = True
                                        solved = False
                                        current_step = 0
                                        current_state = start_state
                                        timer_start = time.time()
                                        last_step_time = time.time()

                elif positions['reset_rect'].collidepoint(event.pos):
                    start_input = start_state
                    goal_input = goal_state
                    start_state = start_input
                    goal_state = goal_input
                    path = None
                    current_step = 0
                    current_state = start_state
                    auto_play = False
                    solved = solving = is_solving = computing = False
                    timer_start = None
                    elapsed_time = 0
                    nodes_expanded = 0
                    search_depth = 0
                    path_cost = 0
                    total_steps = 0
                    is_shuffled = False
                    algo_display_offset = 0
                    belief_states = set([start_state])
                    latest_observation = None
                    goal_probability = 0
                    progress_text = ""
                    search_thread = None

        elif event.type == pygame.KEYDOWN and input_active and not computing:
            if event.key == pygame.K_BACKSPACE:
                if input_active == "start":
                    start_input = start_input[:-1]
                elif input_active == "goal":
                    goal_input = goal_input[:-1]
            elif event.unicode.isdigit() and event.unicode in "012345678":
                if input_active == "start" and len(start_input) < 9:
                    start_input += event.unicode
                elif input_active == "goal" and len(goal_input) < 9:
                    goal_input += event.unicode

    if computing and search_thread and not search_thread.is_alive():
        computing = False
        search_thread = None
        if 'error' in result_container:
            show_message_box(f"Error: {result_container['error']}")
            path = [start_state]
            total_steps = 0
            solved = solving = is_solving = False
        else:
            path = result_container.get('path', [start_state])
            nodes_expanded = result_container.get('nodes_expanded', 0)
            search_depth = result_container.get('search_depth', 0)
            path_cost = result_container.get('path_cost', 0)
            belief_states = set.union(*path) if path else set()
            goal_probability = 1.0 if path and path[-1] == goal_state else 0.0
            if not path:
                show_message_box("No solution found!")
                path = [set([start_state])]
                solved = solving = is_solving = False
            else:
                sensorless_screen = SensorlessScreen(screen, WIDTH, HEIGHT, path)
                active_screen = "sensorless"

    if timer_start and not solved and not is_paused:
        elapsed_time = time.time() - timer_start

    if auto_play and path and current_step < len(path) - 1:
        current_time = time.time()
        if current_time - last_step_time >= auto_speed:
            current_step += 1
            if isinstance(path[current_step], set):
                current_state = next(iter(path[current_step]))
            else:
                current_state = path[current_step]

            last_step_time = current_time
            if current_step == len(path) - 1:
                auto_play = False
                solved = True
                solving = is_solving = False
    if active_screen == "sensorless":
        sensorless_screen.draw()
    else:
        draw_title(screen, WIDTH)
        # print("DEBUG TYPE OF current_state:", type(current_state))
        # print("DEBUG VALUE OF current_state:", current_state)

        draw_board(current_state, screen, CELL_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y, selected_algorithm, latest_observation)
        draw_input_box(screen, start_input, positions['start_rect'], input_active == "start")
        draw_input_box(screen, goal_input, positions['goal_rect'], input_active == "goal")
        solve_label = "Solve (On)" if auto_play else "Solve (Pause)" if solving else "Solve (Off)"
        draw_button(screen, solve_label, positions['solve_rect'], positions['solve_rect'].collidepoint(pygame.mouse.get_pos()), is_solving, is_solving, True)
        draw_button(screen, "Reset", positions['reset_rect'], positions['reset_rect'].collidepoint(pygame.mouse.get_pos()))
        draw_button(screen, "Prev", positions['prev_rect'], positions['prev_rect'].collidepoint(pygame.mouse.get_pos()))
        draw_button(screen, "Next", positions['next_rect'], positions['next_rect'].collidepoint(pygame.mouse.get_pos()))
        draw_results(screen, elapsed_time, nodes_expanded, search_depth, path_cost, total_steps, solved, solving, positions['results_pos'], len(belief_states), goal_probability, latest_observation)
        draw_dropdown(screen, selected_algorithm, positions['algo_rect'], list(algorithms.keys()), dropdown_open, pygame.mouse.get_pos(), dropdown_open, algo_display_offset)
        if dropdown_open:
            draw_dropdown(screen, selected_algorithm, positions['algo_rect'], list(algorithms.keys()), dropdown_open, pygame.mouse.get_pos(), False, algo_display_offset)


    if computing:
        progress_surface = TIMER_FONT.render(progress_text, True, TITLE_COLOR)
        screen.blit(progress_surface, (WIDTH // 2 - progress_surface.get_width() // 2, HEIGHT - 50))

    pygame.display.flip()

pygame.quit()