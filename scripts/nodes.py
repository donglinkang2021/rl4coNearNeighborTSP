import numpy as np
import matplotlib.pyplot as plt
from config import *

np.random.seed(1234)
dataset_size = 10000
tsp_size = 300
data = np.random.uniform(size=(dataset_size, tsp_size, 2)).astype(np.float32)

loc = data[0]
loc = loc[:n] # we only consider the first n nodes

# Plot the nodes
plt.figure(figsize=(10, 10))
plt.plot(loc[:, 0], loc[:, 1], 'o')
for i, txt in enumerate(range(n)):
    plt.annotate(txt, (loc[i, 0] + 0.005, loc[i, 1] + 0.005), fontsize=12)

# Start point
plt.plot(loc[0][0], loc[0][1], 'rp', markersize=10, label='Start Point')

# Bus stops
for depot in range(1, n_depots):
    plt.plot(
        loc[depot][0], loc[depot][1], 'ks', 
        markersize=10, label=f'Depot {depot}'
    )

plt.legend()
plt.title("Nodes")
plt.xlabel("X coordinate")
plt.ylabel("Y coordinate")
plt.grid()
plt.savefig('images/Nodes.png')
print("Plot saved as images/Nodes.png")