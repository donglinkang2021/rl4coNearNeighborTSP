import numpy as np

# 贪心算法解决TSP问题
def greedy_algorithm(distance_matrix: np.ndarray):
    num_cities = distance_matrix.shape[0]
    visited = [False] * num_cities
    tour = [0]
    visited[0] = True
    for _ in range(num_cities - 1):
        last = tour[-1]
        next_city = np.argmin([distance_matrix[last, j] if not visited[j] else np.inf for j in range(num_cities)])
        tour.append(next_city)
        visited[next_city] = True
    tour.append(0)  # 回到起点
    return tour