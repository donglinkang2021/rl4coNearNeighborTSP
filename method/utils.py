import numpy as np
from scipy.spatial.distance import cdist
from typing import List, Tuple

__all__ = [
    'euclidean_distance',
    'calculate_total_distance',
    'calculate_distance_matrix',
    'kmeans',
    'neighbor_aggregation',
]

def neighbor_aggregation(x:np.ndarray) -> np.ndarray:
    dist_matrix = euclidean_distance(x, x)
    dist_matrix = softmax(dist_matrix, axis=-1)
    return dist_matrix @ x

def softmax(x:np.ndarray, axis:int=-1) -> np.ndarray:
    exp_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return exp_x / exp_x.sum(axis=axis, keepdims=True)

def euclidean_distance(X:np.ndarray, Y:np.ndarray) -> np.ndarray:
    return cdist(X, Y, metric='euclidean')

def calculate_total_distance(
        tour:list, 
        distance_matrix: np.ndarray
    ) -> float:
    return sum(distance_matrix[tour[i], tour[i + 1]] for i in range(len(tour) - 1))

def calculate_distance_matrix(cities: np.ndarray) -> np.ndarray:
    return euclidean_distance(cities, cities)

def kmeans(
        X:np.ndarray, k:int, max_iters:int=100
    ) -> Tuple[np.ndarray, np.ndarray]:
    """codeboos [n_samples, d_features], code [n_samples,]"""
    # Randomly initialize k cluster codebooks
    n_samples, d_features = X.shape
    codebooks = X[np.random.choice(n_samples, k, replace=False)]
    
    for _ in range(max_iters):
        # Compute the distance between each data point and the codebooks
        distances = euclidean_distance(X, codebooks)
        
        # Assign each data point to the closest centroid
        code = np.argmin(distances, axis=1)
        
        # Compute the new codebooks
        new_codebooks = np.array([X[code == i].mean(axis=0) for i in range(k)])
        
        # Check for convergence
        if np.all(codebooks == new_codebooks):
            break
        codebooks = new_codebooks
        
    return codebooks, code