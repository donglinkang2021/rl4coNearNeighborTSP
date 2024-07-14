import numpy as np
from method import calculate_distance_matrix
import time

def softmax(x):
    e_x = np.exp(x - np.max(x))  # 减去 np.max(x) 是为了数值稳定性
    return e_x / e_x.sum(axis=0)

def get_time_str():
    return time.strftime("%Y%m%d-%H%M%S", time.localtime())

def calc_avg_node_visit_time_multi_car(
        loc: np.ndarray, 
        routes: dict,
        env_args:dict
    ) -> float:

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

    dist = calculate_distance_matrix(loc)

    # 计算第一层次车辆的访问时间
    arrival_times1 = {i: 0 for i in [S]+D}  # 初始化第一层次车辆到达时间
    for vehicle in ugv_names:
        total_time = 0.0
        route = routes[vehicle]
        for i in range(1, len(route)):
            total_time += dist[route[i - 1], route[i]]
            arrival_times1[route[i]] = total_time

    # 计算第二层次车辆的访问时间
    arrival_times2 = {i: 0 for i in D+C}
    for vehicle in uav_names:
        route = routes[vehicle]
        depot = route[0]
        arrival_times2[depot] = arrival_times1[depot]
        total_time = arrival_times1[depot]  # 这里是关键，把total_time设置为第一阶段车辆到达当前depot的时间
        for i in range(1, len(route)):
            total_time += dist[route[i - 1], route[i]]
            arrival_times2[route[i]] = total_time

    # 计算平均访问时间
    avg_visit_time = np.mean([arrival_times2[i] for i in C])
    return avg_visit_time