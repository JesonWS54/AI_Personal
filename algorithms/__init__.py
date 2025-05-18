# algorithms/__init__.py
from utils import get_next_states, heuristic, is_solvable
from utils import get_possible_actions, get_action_results

from algorithms.Constrained_searching.Backtracking import run as run_csp_backtracking
from algorithms.Constrained_searching.AC_3 import AC3Solver

from algorithms.Constrained_searching.Testing import run as run_min_conflicts
from algorithms.Informed_Searching.A_Star import astar
from algorithms.Informed_Searching.Greedy_Cost_Search import greedy_search
from algorithms.Informed_Searching.IDA_Star import ida_star
from algorithms.Local_search.Simple_Hill_Climbing import simple_hill_climbing
from algorithms.Local_search.Steepest_Ascent_Hill_Climbing import steepest_hill_climbing
from algorithms.Local_search.Stochastic_Hill_Climbing import stochastic_hill_climbing
from algorithms.Local_search.Simulated_Annealing import simulated_annealing
from algorithms.Local_search.Local_Beam_Search import beam_search
from algorithms.Local_search.Genetic_Algorithm import genetic_algorithm
from algorithms.Searching_in_an_uncertain_environment.And_Or_Search import and_or_search
from algorithms.Searching_in_an_uncertain_environment.Belief_State_Search import belief_state_search
from algorithms.Searching_in_an_uncertain_environment.Searching_With_Partial_Observation import partial_observation_search
from algorithms.Searching_in_an_uninformed_environment.BFS import bfs
from algorithms.Searching_in_an_uninformed_environment.DFS import dfs
from algorithms.Searching_in_an_uninformed_environment.IDS import ids
from algorithms.Searching_in_an_uninformed_environment.UCS import ucs
from algorithms.Reinforcement_learning.Q_Learning import q_learning

def run_ac3(start_state, goal_state):
    return run_csp_backtracking(start_state, goal_state)

algorithms = {
    "BFS": bfs,
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
    "Genetic Algorithm": genetic_algorithm,
    "Q-Learning": q_learning,
    "And-Or Search": lambda s, g: and_or_search(s, g, get_possible_actions, get_action_results),
    "Belief State Search": belief_state_search,
    "Partial Obs. Search": lambda s, g, p=None: partial_observation_search({s}, g, known_tile_index=0, known_tile_value='1', progress_callback=p),
    "CSP Backtracking": run_csp_backtracking,
    "AC-3": run_ac3,
    "Min-Conflicts": run_min_conflicts,
}