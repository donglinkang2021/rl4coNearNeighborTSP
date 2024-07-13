# import debugpy; debugpy.connect(('10.1.114.56', 5678))

import numpy as np
from config import *
from method import (
    kmeans, 
    euclidean_distance, 
    greedy_algorithm, 
    simulated_annealing,
    genetic_algorithm
)
np.random.seed(1234)
dataset_size = 10000
tsp_size = 300
data = np.random.uniform(size=(dataset_size, tsp_size, 2)).astype(np.float32)

loc = data[0]
loc = loc[:n] # we only consider the first n nodes

# for UAVs
poi_idxs = np.array(C)
bus_stops_idxs = np.array(D)

# get each poi centroid for UAVs
poi_locs = loc[poi_idxs]
codebooks, code = kmeans(poi_locs, n_UAVs) # (n_UAVs, 2), (n_poi,)

# get UAVs starting location(the nearest bus stop)
bus_stops_locs = loc[bus_stops_idxs]
centorid_depot_distance = euclidean_distance(codebooks, bus_stops_locs) # (n_UAVs, n_depots)
uav_selected_idxs = np.argmin(centorid_depot_distance, axis=1) # (n_UAVs,)
uav_start_idxs = bus_stops_idxs[uav_selected_idxs] # (n_UAVs,)

# get n_UAVs sub dataset
uav_poi = {}
for i in range(n_UAVs):
    uav_poi[uav_names[i]] = {
        'start_idxs': uav_start_idxs[i],
        'poi_idxs': list(poi_idxs[code == i])
    }

# get UAV routes
for i in range(n_UAVs):
    start_idxs = uav_poi[uav_names[i]]['start_idxs']
    poi_idxs = uav_poi[uav_names[i]]['poi_idxs']
    locs_idxs = [start_idxs] + poi_idxs
    locs_idxs = np.array(locs_idxs)
    locs = loc[locs_idxs]
    print(locs.shape)
    
    dist_matrix = euclidean_distance(locs, locs)
    method = 'Greedy'
    route = greedy_algorithm(dist_matrix)
    # method = 'Annealing'
    # route, _ = simulated_annealing(dist_matrix, is_print=False)
    # method = 'Genetic'
    # route, _ = genetic_algorithm(dist_matrix, is_print=False) 
    uav_poi[uav_names[i]]['route'] = list(locs_idxs[route])

print(uav_poi)

import matplotlib
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 10))
colors = matplotlib.colormaps['tab20']
plt.plot(loc[0][0], loc[0][1], 'rp', markersize=10, label='Start Point')
for i in range(n_UAVs):
    vehicle_name = uav_names[i]
    start_idxs = uav_poi[vehicle_name]['start_idxs']
    start_locs = loc[start_idxs]
    route = uav_poi[uav_names[i]]['route']
    route_locs = loc[route]
    # Bus stops
    plt.plot(
        start_locs[0],
        start_locs[1],
        'ks', 
        markersize=10, 
        label=f'Depot {uav_names[i]}'
    )
    plt.plot(
        route_locs[:, 0], route_locs[:, 1], 
        marker='o', color=colors(i), 
        label=f'{vehicle_name}'
    )
    for j in range(len(route_locs) - 1):
        plt.arrow(
            route_locs[j, 0], route_locs[j, 1],
            route_locs[j+1, 0] - route_locs[j, 0], 
            route_locs[j+1, 1] - route_locs[j, 1],
            head_width=0.02, 
            length_includes_head=True, 
            color=colors(i)
        )

plt.grid()
plt.legend()
filename = f'images/2EVRP-{method}-{n_poi}user-{n_depots}busstop-{n_UGVs}UGVs-{n_UAVs}UAVs.png'
plt.savefig(filename)
print(f'Image saved to {filename}')

