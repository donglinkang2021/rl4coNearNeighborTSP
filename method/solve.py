import numpy as np
from enum import IntEnum
from .annealing import simulated_annealing
from .greedy import greedy_algorithm
from .genetic import genetic_algorithm
from typing import List

__all__ = ['TSPMethod', 'solve']

class TSPMethod(IntEnum):
    
    def __new__(cls, value, phrase, description=''):
        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.phrase = phrase
        obj.description = description
        return obj
    
    NEAREST_NEIGHBOR = 0, 'Nearest_Neighbor', 'Greedy algorithm, start from a random vertex, choose the nearest vertex'
    SIMULATED_ANNEALING = 1, 'Simulated_Annealing', 'Randomly select a vertex, if the new route is shorter, accept it with a probability'
    GENETIC_ALGORITHM = 2, 'Genetic_Algorithm', 'Define the gene, crossover, mutation, and selection, and evolve the population'

def solve(
        dist_matrix:np.ndarray, 
        method:TSPMethod = TSPMethod.NEAREST_NEIGHBOR
    ) -> List[int]:
    if method == TSPMethod.NEAREST_NEIGHBOR:
        route = greedy_algorithm(dist_matrix)
    elif method == TSPMethod.SIMULATED_ANNEALING:
        route, _ = simulated_annealing(dist_matrix, is_print=False)
    elif method == TSPMethod.GENETIC_ALGORITHM:
        route, _ = genetic_algorithm(dist_matrix, is_print=False)
    return route