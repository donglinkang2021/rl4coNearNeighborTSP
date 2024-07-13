"""

Genetic Algorithm for TSP

This module contains functions to solve the Traveling Salesman Problem using Genetic Algorithm.

note that:

- no matter the parents or children, both are tour: List[int], which is a list of city indices
- tour starts and ends at city 0
- in each generation, 
    - we have `pop_size` tours in the population, population = [tour1, tour2, ..., tourN]
    - firstly, we will select `elite_size` tours with the best fitness value to be the elite 
        - fitness = 1 / the total distance of the tour, the less dist, the better fitness
    - then we will ues elite as parents to generate new population, which is the same size as before
        - for each pair of parents, we will generate two children
        - we will add these two children to the elite list
    - finally, we will replace the old population with the new population
        - we will update the best tour and best distance if we find a better one
    - repeat the above steps for `generations` times

"""

import numpy as np
from .utils import calculate_total_distance
from typing import List, Tuple

__all__ = ['genetic_algorithm']

def initialize_population(
        pop_size: int, 
        num_cities: int
    ) -> List[List[int]]:
    population = []
    for _ in range(pop_size):
        tour = list(np.random.permutation(range(1, num_cities)))
        population.append(tour)
    return population

def selection(
        population: List[List[int]],
        fitness: List[float]
    ) -> List[int]:
    """select a parent based on fitness value of each individual in the population"""
    total_fitness = sum(fitness)
    pick = np.random.uniform(0, total_fitness)
    current = 0
    for i, f in enumerate(fitness):
        current += f
        if current > pick:
            return population[i]

def crossover(
        parent1: List[int],
        parent2: List[int]
    ) -> Tuple[List[int], List[int]]:
    """crossover parts of two parents to generate two children"""
    size = len(parent1)
    start, end = sorted(np.random.choice(range(size), 2, replace=False))
    child1 = [-1] * size
    child2 = [-1] * size

    child1[start:end] = parent1[start:end]
    child2[start:end] = parent2[start:end]

    fill_child(child1, parent2)
    fill_child(child2, parent1)

    return child1, child2

def fill_child(
        child: List[int],
        parent: List[int],
    ) -> None:
    """fill the rest of the child with genes from the other parent"""
    size = len(child)
    for i in range(size):
        if child[i] == -1:
            for gene in parent:
                if gene not in child:
                    child[i] = gene
                    break

def mutate(
        tour: List[int],
        mutation_rate: float
    ) -> List[int]:
    """swap two cities with a probability"""
    if len(tour) <= 2:
        return tour

    for i in range(len(tour) - 1):
        if np.random.rand() < mutation_rate:
            j = np.random.randint(0, len(tour) - 2)
            tour[i], tour[j] = tour[j], tour[i]
    return tour

def genetic_algorithm(
        distance_matrix: np.ndarray, 
        pop_size: int = 100, 
        elite_size: int = 20, 
        mutation_rate: float = 0.01, 
        generations: int = 500,
        is_print: bool = True
    ) -> Tuple[List[int], float]:
    num_cities = distance_matrix.shape[0]
    population = initialize_population(pop_size, num_cities)
    best_tour = None
    best_distance = float('inf')

    for generation in range(generations):
        fitness = [1 / calculate_total_distance([0, *tour, 0], distance_matrix) for tour in population]
        new_population = []

        elite_indices = np.argsort(fitness)[-elite_size:]
        elite = [population[i] for i in elite_indices]
        new_population.extend(elite)

        # generate new population
        while len(new_population) < pop_size:
            parent1 = selection(population, fitness)
            parent2 = selection(population, fitness)
            child1, child2 = crossover(parent1, parent2)
            new_population.append(mutate(child1, mutation_rate))
            if len(new_population) < pop_size:
                new_population.append(mutate(child2, mutation_rate))

        population = new_population

        # update best tour
        for tour in population:
            tour = [0, *tour, 0]
            distance = calculate_total_distance(tour, distance_matrix)
            if distance < best_distance:
                best_distance = distance
                best_tour = tour

        if is_print:
            print(f"Generation {generation+1}/{generations}, Best Distance: {best_distance}")

    return best_tour, best_distance