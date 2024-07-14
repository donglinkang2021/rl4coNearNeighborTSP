
import debugpy; debugpy.connect(('10.1.114.56', 5678))
from scipy.spatial.distance import cdist
import numpy as np
np.random.seed(1234)
X = np.random.rand(5, 2)
Y = np.random.rand(5, 2)

distance = cdist(X, Y, metric='euclidean')
print(distance)
