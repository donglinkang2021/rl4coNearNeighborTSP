import debugpy; debugpy.connect(('10.1.114.56', 5678))
import numpy as np

def softmax(x, axis=-1):
    e_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return e_x / e_x.sum(axis=axis, keepdims=True)

x = np.array([1.0, 2.0, 3.0])
print(x)
print(softmax(x))

dist_matrix = np.array([
    [0, 1, 2], 
    [1, 0, 3], 
    [2, 3, 0]
])
print(dist_matrix)
print(softmax(dist_matrix, 0))
