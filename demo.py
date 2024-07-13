# import debugpy; debugpy.connect(('10.1.114.56', 5678))

import numpy as np
from config import get_env_args, get_setting, settings
from utils import calc_avg_node_visit_time_multi_car
from method import (
    kmeans, 
    euclidean_distance, 
    TSPMethod,
    solve
)
import json
from tqdm import tqdm

def solve_tsp(
        loc:np.ndarray, 
        method:TSPMethod, 
        env_args:dict
    )->dict:

    # config
    n_poi = env_args['n_poi']
    n_depots = env_args['n_depots']
    n = env_args['n']
    n_UAVs = env_args['n_UAVs']
    n_UGVs = env_args['n_UGVs']
    n_vehicles = env_args['n_vehicles']
    S = env_args['S']
    D = env_args['D']
    C = env_args['C']
    ugv_names = env_args['UGVs']
    uav_names = env_args['UAVs']
    K = env_args['K']

    # we only consider the first n nodes
    loc = loc[:n] 

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
        
        dist_matrix = euclidean_distance(locs, locs)
        route = solve(dist_matrix, method)
        ugv_depot[ugv_names[i]]['route'] = locs_idxs[route].tolist()

    vehicle_routes = {}
    for vehicle, info in ugv_depot.items():
        vehicle_routes[vehicle] = info['route']
    for vehicle, info in uav_poi.items():
        vehicle_routes[vehicle] = info['route']

    return vehicle_routes


def main():

    # generate random data
    np.random.seed(1234)
    dataset_size = 10000
    tsp_size = 300
    data = np.random.uniform(size=(dataset_size, tsp_size, 2)).astype(np.float32)

    # solution
    method = TSPMethod.NEAREST_NEIGHBOR
    settings_list = settings.keys()

    pbar = tqdm(
        total=len(settings_list)*dataset_size,
        desc='Solving',
        dynamic_ncols=True
    )

    avg_time_dict = {}
    for setting in settings_list:
        n_poi, n_depots, n_UGVs, n_UAVs = get_setting(setting)
        env_args = get_env_args(n_poi, n_depots, n_UGVs, n_UAVs)

        vehicle_routes_list = []
        avg_time_list = []
        for i in range(dataset_size):
            loc = data[i]
            vehicle_routes = solve_tsp(loc, method, env_args)
            try :
                avg_time = calc_avg_node_visit_time_multi_car(loc, vehicle_routes, env_args)
            except KeyError:
                print(f'KeyError: {setting} dataset {i}')
            vehicle_routes_list.append(vehicle_routes)
            avg_time_list.append(avg_time)
            pbar.update(1)
        
        filename = f'result/2EVRP-{method.phrase}-{n_poi}user-{n_depots}busstop-{n_UGVs}UGVs-{n_UAVs}UAVs.json'
        with open(filename, 'w') as f:
            json.dump(vehicle_routes_list, f)
        print(f'{filename} saved')

        avg_time_dict[setting] = np.mean(avg_time_list)
    pbar.close()
    with open('result/avg_time.json', 'w') as f:
        json.dump(avg_time_dict, f)
    print('avg_time.json saved')

if __name__ == '__main__':
    main()
    
# nohup python demo.py > demo.log 2>&1 &