from utils import is_solvable, heuristic, find_zero
import random

def genetic_algorithm(start_state, goal_state, pop_size=50, max_gen=100, mutation_rate=0.1):
    if not is_solvable(start_state, goal_state):
        return None, 0, 0, 0

    moves = ["Up", "Down", "Left", "Right"]

    def apply_move(state, move):
        row, col = find_zero(state)
        delta = {"Up": (-1, 0), "Down": (1, 0), "Left": (0, -1), "Right": (0, 1)}
        dr, dc = delta.get(move, (0, 0))
        new_r, new_c = row + dr, col + dc
        if 0 <= new_r < 3 and 0 <= new_c < 3:
            new_idx = new_r * 3 + new_c
            idx = row * 3 + col
            state = list(state)
            state[idx], state[new_idx] = state[new_idx], state[idx]
            return ''.join(state)
        return state

    def fitness(chrom):
        state = start_state
        for m in chrom:
            state = apply_move(state, m)
        return heuristic(state, goal_state)

    def mutate(chrom):
        return [random.choice(moves) if random.random() < mutation_rate else m for m in chrom]

    def crossover(p1, p2):
        idx = random.randint(1, len(p1)-1)
        return p1[:idx] + p2[idx:]

    population = [[random.choice(moves) for _ in range(30)] for _ in range(pop_size)]
    nodes_expanded = 0

    for _ in range(max_gen):
        population.sort(key=fitness)
        if fitness(population[0]) == 0:
            state = start_state
            path = [state]
            for m in population[0]:
                state = apply_move(state, m)
                path.append(state)
                if state == goal_state:
                    return path, nodes_expanded, len(path)-1, len(path)-1
        new_pop = population[:pop_size // 5]
        while len(new_pop) < pop_size:
            p1, p2 = random.sample(population[:pop_size//2], 2)
            child = mutate(crossover(p1, p2))
            new_pop.append(child)
            nodes_expanded += 1
        population = new_pop

    return None, nodes_expanded, 0, 0