import numpy as np
from .utils import calculate_total_distance
from typing import List, Tuple

__all__ = ['simulated_annealing']

def simulated_annealing(
        distance_matrix: np.ndarray, 
        initial_temp: float = 1000, 
        cooling_rate: float = 0.995, 
        max_iter: int = 10000,
        is_print: bool = True
    ) -> Tuple[List[int], float]:
    num_cities = distance_matrix.shape[0]
    tour = list(np.random.permutation(range(1, num_cities)))
    
    best_tour = [0, *tour, 0]
    current_distance = calculate_total_distance(best_tour, distance_matrix)
    best_distance = current_distance
    
    temperature = initial_temp

    for i in range(max_iter):
        if temperature <= 0:
            break
        
        # generate a new neighbor solution
        # just swap two cities
        new_tour = tour.copy()
        city1, city2 = np.random.randint(0, len(new_tour), size=2)
        new_tour[city1], new_tour[city2] = new_tour[city2], new_tour[city1]
        new_distance = calculate_total_distance([0, *new_tour, 0], distance_matrix)
        
        # accept new solution with probability
        acceptance_probability = np.exp((current_distance - new_distance) / temperature)
        if new_distance < current_distance or np.random.rand() < acceptance_probability:
            tour = new_tour
            current_distance = new_distance
        
        # update best solution
        if current_distance < best_distance:
            best_tour = [0, *tour, 0]
            best_distance = current_distance
        
        # update temperature
        temperature *= cooling_rate

        if is_print and i % 200 == 0:
            print(f"Iteration {i+1}/{max_iter}, Best Distance: {best_distance}")
    
    return best_tour, best_distance