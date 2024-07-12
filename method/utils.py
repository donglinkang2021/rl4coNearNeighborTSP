import numpy as np
from scipy.spatial.distance import cdist
from typing import List, Tuple

__all__ = [
    'calculate_total_distance',
    'calculate_distance_matrix',
    'kmeans'
]

def calculate_total_distance(
        tour:list, 
        distance_matrix: np.ndarray
    ) -> float:
    return sum(distance_matrix[tour[i], tour[i + 1]] for i in range(len(tour) - 1))

def calculate_distance_matrix(cities: np.ndarray) -> np.ndarray:
    return cdist(cities, cities, metric='euclidean')

def kmeans(
        X:np.ndarray, k:int, max_iters:int=100
    ) -> Tuple[np.ndarray, np.ndarray]:
    # Randomly initialize k cluster codebooks
    n_samples, d_features = X.shape
    codebooks = X[np.random.choice(n_samples, k, replace=False)]
    
    for _ in range(max_iters):
        # Compute the distance between each data point and the codebooks
        distances = cdist(X, codebooks, 'euclidean')
        
        # Assign each data point to the closest centroid
        code = np.argmin(distances, axis=1)
        
        # Compute the new codebooks
        new_codebooks = np.array([X[code == i].mean(axis=0) for i in range(k)])
        
        # Check for convergence
        if np.all(codebooks == new_codebooks):
            break
        codebooks = new_codebooks
        
    return codebooks, code