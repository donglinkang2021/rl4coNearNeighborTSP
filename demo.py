# import debugpy; debugpy.connect(('10.1.114.56', 5678))

import numpy as np
from config import *
from method import (
    kmeans, 
    euclidean_distance, 
    TSPMethod,
    solve
)

method = TSPMethod.GENETIC_ALGORITHM
filename = f'images/2EVRP-{method.phrase}-{n_poi}user-{n_depots}busstop-{n_UGVs}UGVs-{n_UAVs}UAVs.png'

# generate random data
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
centroids_uav, code_poi = kmeans(poi_locs, n_UAVs) # (n_UAVs, 2), (n_poi,)

# get UAVs starting location(the nearest bus stop)
bus_stops_locs = loc[bus_stops_idxs]
centorid_depot_distance = euclidean_distance(centroids_uav, bus_stops_locs) # (n_UAVs, n_depots)
uav_selected_idxs = np.argmin(centorid_depot_distance, axis=1) # (n_UAVs,)
uav_start_idxs = bus_stops_idxs[uav_selected_idxs] # (n_UAVs,)

# get n_UAVs sub dataset
uav_poi = {}
for i in range(n_UAVs):
    uav_poi[uav_names[i]] = {
        'start_idxs': uav_start_idxs[i],
        'poi_idxs': poi_idxs[code_poi == i].tolist()
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
    route = solve(dist_matrix, method)
    uav_poi[uav_names[i]]['route'] = locs_idxs[route].tolist()

# get UGV routes
# we have uav_start_idxs as bus stops
# and n_UGVs UGV must start from S
uav_start_locs = loc[uav_start_idxs]
centorids_ugv, code_uav = kmeans(uav_start_locs, n_UGVs) # (n_UGVs, 2), (n_UAVs,)

ugv_depot = {}
for i in range(n_UGVs):
    ugv_depot[ugv_names[i]] = {
        'start_idxs': S,
        'depot_idxs': uav_start_idxs[code_uav == i].tolist()
    }

# get UGV routes
for i in range(n_UGVs):
    start_idxs = ugv_depot[ugv_names[i]]['start_idxs']
    depot_idxs = ugv_depot[ugv_names[i]]['depot_idxs']
    locs_idxs = [start_idxs] + depot_idxs
    locs_idxs = np.array(locs_idxs)
    locs = loc[locs_idxs]
    print(locs.shape)
    
    dist_matrix = euclidean_distance(locs, locs)
    route = solve(dist_matrix, method)
    ugv_depot[ugv_names[i]]['route'] = locs_idxs[route].tolist()

vehicle_routes = {}
for vehicle, info in ugv_depot.items():
    vehicle_routes[vehicle] = info['route']
for vehicle, info in uav_poi.items():
    vehicle_routes[vehicle] = info['route']

print(vehicle_routes)

uav_start_idxs = uav_start_idxs.tolist()
from plot import plot_vehicle_routes
plot_vehicle_routes(loc, vehicle_routes, uav_start_idxs, filename)
from utils import calc_avg_node_visit_time_multi_car
avg_visit_time = calc_avg_node_visit_time_multi_car(loc, vehicle_routes)
print(f"Average node visit time: {avg_visit_time}")

