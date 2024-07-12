from config import *
import numpy as np

def calc_avg_node_visit_time_multi_car(
        loc: np.ndarray, 
        routes: dict,
    ):

    dist = {(i, j): np.linalg.norm(np.array(loc[i]) - np.array(loc[j])) for i in range(n) for j in range(n) if i != j}

    # 计算第一层次车辆的访问时间
    arrival_times1 = {i: 0 for i in [S]+D}  # 初始化第一层次车辆到达时间
    for vehicle in UGVs:
        total_time = 0.0
        route = routes[vehicle]
        for i in range(1, len(route)):
            total_time += dist[route[i - 1], route[i]]
            arrival_times1[route[i]] = total_time

    # 计算第二层次车辆的访问时间
    arrival_times2 = {i: 0 for i in D+C}
    for vehicle in UAVs:
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