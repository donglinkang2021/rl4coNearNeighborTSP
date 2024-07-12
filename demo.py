import numpy as np
from config import *
from method import kmeans
np.random.seed(1234)
dataset_size = 10000
tsp_size = 300
data = np.random.uniform(size=(dataset_size, tsp_size, 2)).astype(np.float32)

loc = data[0]
loc = loc[:n] # we only consider the first n nodes

# for UAVs
poi_locs = loc[poi_indices]
bus_stops_locs = loc[bus_stops_indices]

codebooks, code = kmeans(poi_locs, n_UAVs)

print(codebooks, code)


