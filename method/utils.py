import numpy as np
from scipy.spatial.distance import cdist

__all__ = [
    'calculate_total_distance',
    'calculate_distance_matrix'
]

def calculate_total_distance(
        tour:list, 
        distance_matrix: np.ndarray
    ) -> float:
    return sum(distance_matrix[tour[i], tour[i + 1]] for i in range(len(tour) - 1))

def calculate_distance_matrix(cities: np.ndarray) -> np.ndarray:
    return cdist(cities, cities, metric='euclidean')