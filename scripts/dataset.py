import numpy as np

np.random.seed(1234)
dataset_size = 10000
tsp_size = 300
data = np.random.uniform(size=(dataset_size, tsp_size, 2)).astype(np.float32)
x = np.load("data/tsp300_test_seed1234.npz")
locations = x["locs"]
print(locations.shape)

# test the difference between the two datasets
print("Difference: ", np.sum(np.abs(data - locations)))
idx = 2
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 8))
plt.scatter(locations[idx, :, 0], locations[idx, :, 1])
plt.title("Vehicle Routes")
plt.xlabel("X coordinate")
plt.ylabel("Y coordinate")
plt.grid()
plt.savefig("images/tsp300_test_seed1234.png")
print("Saved to images/tsp300_test_seed1234.png")

"""
这里证明了我们生成的数据集和原始数据集是一样的
(10000, 300, 2)
Difference:  0.0
Saved to images/tsp300_test_seed1234.png
"""