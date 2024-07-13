from method import TSPMethod, solve, euclidean_distance, calculate_total_distance
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(1234)
data = np.random.rand(100, 2)

method = TSPMethod.GENETIC_ALGORITHM
dist_matrix = euclidean_distance(data, data)
route = solve(dist_matrix, method)
total_distance = calculate_total_distance(route, dist_matrix)

plt.figure(figsize=(6, 6))
plt.scatter(data[:, 0], data[:, 1], c='blue')

for i in range(len(route) - 1):
    plt.arrow(
        data[route[i]][0], data[route[i]][1],
        data[route[i+1]][0] - data[route[i]][0], 
        data[route[i+1]][1] - data[route[i]][1],
        head_width=0.02, head_length=0.02, fc='red', ec='red'
    )

plt.title(f'{method.phrase} TSP, Total Distance: {total_distance:.4f}')

image_name = f'images/{method.phrase}.png'
plt.savefig(image_name)
print(f'TSP is done! The result is saved as {image_name}')

