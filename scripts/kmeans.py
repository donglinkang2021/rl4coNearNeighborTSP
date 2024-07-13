from method import kmeans
import matplotlib.pyplot as plt
import numpy as np

data = np.random.rand(100, 2)

codebooks, code = kmeans(data, 3)
print(codebooks)
print(code)

cmap = 'rainbow'
plt.figure(figsize=(6, 6))
plt.scatter(data[:, 0], data[:, 1], c=code, cmap=cmap)
plt.scatter(codebooks[:, 0], codebooks[:, 1], c='black', s = 50, marker='x')
plt.savefig('images/kmeans.png')
print('K-means clustering is done! The result is saved as images/kmeans.png')

