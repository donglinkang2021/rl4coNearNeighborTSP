# import debugpy; debugpy.connect(('10.1.114.56', 5678))

import matplotlib.pyplot as plt
import numpy as np
import traceback
import argparse
import os
import time
from datetime import timedelta
from gurobi.utils import run_all_in_pool
from gurobi.utils.data_utils import check_extension, load_dataset, save_dataset
import re
from gurobipy import *


def get_vehicle_routes(X, Y, env_args):
    
    n_UGVs = env_args.get('n_UGVs')
    n_vehicles = env_args.get('n_vehicles')
    S = env_args.get('S')
    D = env_args.get('D')
    C = env_args.get('C')

    routes = {f'v{k}': [] for k in range(n_vehicles)}

    for k in range(n_UGVs):  # 第一阶段
        vehicle_key = f'v{k}'
        visited = [False] * len([S]+D)
        current_node = 0
        route = [current_node]
        visited[current_node] = True
        while True:
            next_node = None
            for j in [S]+D:
                if current_node != j and X[current_node, j, vehicle_key].x > 0.5:
                    next_node = j
                    break
            if next_node is None or visited[next_node]:
                break
            route.append(next_node)
            visited[next_node] = True
            current_node = next_node
        routes[vehicle_key] = route
    
    for k in range(n_UGVs, n_vehicles):  # 第二阶段
        vehicle_key = f'v{k}'
        visited = [True] * len([S]) + [False] * len(D+C)
        current_node = [j for j in D if Y[vehicle_key, j].x > 0.5][0]
        route = [current_node]
        visited[current_node] = True
        while True:
            next_node = None
            for j in D+C:
                if current_node != j and X[current_node, j, vehicle_key].x > 0.5:
                    next_node = j
                    break
            if next_node is None or visited[next_node]:
                break
            route.append(next_node)
            visited[next_node] = True
            current_node = next_node
        routes[vehicle_key] = route
    return routes

def solve_euclidian_vrp_gurobi(points, threads=0, timeout=None, gap=None, env_args=None):

    n_poi = env_args['n_poi']
    n_depots = env_args['n_depots']
    n = env_args['n']
    n_UGVs = env_args['n_UGVs']
    n_UAVs = env_args['n_UAVs']
    n_vehicles = env_args['n_vehicles']
    S = env_args['S']
    D = env_args['D']
    C = env_args['C']
    UGVs = env_args['UGVs']
    UAVs = env_args['UAVs']
    K = env_args['K']
    
    dist = {(i, j): np.sqrt(sum((points[i][k] - points[j][k])**2 for k in range(2))) for i in range(n) for j in range(n) if i != j}

    m = Model()
    m.Params.outputFlag = False

    X = m.addVars(n, n, K, vtype=GRB.BINARY, name='X')
    Y = m.addVars(K, n, vtype=GRB.BINARY, name='Y')
    U1 = m.addVars([S]+D, vtype=GRB.CONTINUOUS, name='U1')
    U2 = m.addVars(D+C, vtype=GRB.CONTINUOUS, name='U2')




    # key: 第一层次车辆的可访问结点为[S]+D
    # 第一层次需求覆盖约束（每个depot被有且仅有一个第一层次车辆服务）
    m.addConstrs(quicksum(Y[ugv, depot] for ugv in UGVs) == 1 for depot in D) 
    # 第一层次车辆数量约束
    m.addConstr( quicksum(Y[ugv, S] for ugv in UGVs) == n_UGVs)
    # 第一层次流平衡
    m.addConstrs(quicksum(X[i, j, ugv] for j in [S]+D if i != j) == quicksum(X[j, i, ugv] for j in [S]+D if i != j) for i in [S]+D for ugv in UGVs)
    # 第一层次决策变量关联
    m.addConstrs(quicksum(X[i, j, ugv] for j in [S]+D if i != j) == Y[ugv, i] for i in [S]+D for ugv in UGVs)

    # key: 第二层次车辆的可访问结点为D+C
    # 第二层次需求覆盖约束（每个客户被有且仅有一个第二层次车辆服务）
    m.addConstrs(quicksum(Y[uav, i] for uav in UAVs) == 1 for i in C) 
    # 第二层次车辆数量约束 (每辆车从一个depot出发)
    m.addConstrs(quicksum(Y[uav, depot] for depot in D) == 1 for uav in UAVs) 
    # 第二层次流平衡
    m.addConstrs(quicksum(X[i, j, uav] for j in D+C if i != j) == quicksum(X[j, i, uav] for j in D+C if i != j) for i in D+C for uav in UAVs)
    # 第二层次决策变量关联
    m.addConstrs(quicksum(X[i, j, uav] for j in D+C if i != j) == Y[uav, i] for i in D+C for uav in UAVs)
    
    # 添加MTZ约束防止子环
    m.addConstrs(U1[i] - U1[j] + len([S]+D) * X[i, j, ugv] <= len([S]+D) - 1 for i in D for j in D for ugv in UGVs if i != j)  # 这里不太懂为啥i、j是in D，不过先照葫芦画瓢
    m.addConstr(U1[S] == 0)

    m.addConstrs(U2[i] - U2[j] + len(D+C) * X[i, j, uav] <= len(D+C) - 1 for i in C for j in C for uav in UAVs if i != j) 
    m.addConstrs(U2[depot] == 0 for depot in D)


    # 测试：用路程最小化的目标函数可以跑通
    # z1 = quicksum( dist[i, j] * X[i, j, 'v0'] for i in [S]+D for j in [S]+D if i != j)
    # m.setObjective(z1, GRB.MINIMIZE)

    # 初始化并设置到达时间变量
    arrival_times1 = m.addVars(UGVs, [S]+D, vtype=GRB.CONTINUOUS, name='arrival_times1') 
    arrival_times2 = m.addVars(UAVs, D+C, vtype=GRB.CONTINUOUS, name='arrival_times2') 

    # 设置第一层次车辆到达时间
    for k in UGVs:
        m.addConstr(arrival_times1[k, S] == 0)
        for i in [S]+D:
            for j in [S]+D:
                if i != j and j not in [S]:
                    M = 1e2
                    m.addConstr(arrival_times1[k, j] >= arrival_times1[k, i] + dist[i, j] - (1 - X[i, j, k]) * M)

    # 设置第二层次车辆到达时间
    for k in UAVs:
        for depot in D:
            m.addConstr(arrival_times2[k, depot] == quicksum(arrival_times1[ugv, depot]*Y[ugv, depot] for ugv in UGVs))  
        for i in D+C:
            for j in D+C:
                if i != j and j not in D:
                    M = 1e2
                    m.addConstr(arrival_times2[k, j] >= arrival_times2[k, i] + dist[i, j] - (1 - X[i, j, k]) * M)

    # 目标函数：最小化用户平均到达时间
    m.setObjective(quicksum(arrival_times2[k, j] for k in UAVs for j in C) / len(C), GRB.MINIMIZE)

    

    m.Params.threads = threads
    m.Params.timeLimit = timeout
    
    m.optimize()

    # 检查是合法解
    for k in K:
        for i in range(n):
            for j in range(n):
                if i != j :
                    if X[i,j,k].x > 0.5: 
                        print("X[{},{},{}]=1".format(i,j,k))

    for k in K:
        for i in range(n):
            # if Y[k, i].x > 0.5: 
            print(f'Y[{k},{i}]={Y[k, i].x}')

    routes = get_vehicle_routes(X, Y, env_args)
    for vehicle, route in routes.items():
        print(f"route for {vehicle}: {route}")

    # (optional:) 这里还缺一个对solved_arrival_times的assert检查，必须按route访问顺序递增

    return m.objVal, routes


def solve_gurobi(directory, name, loc, disable_cache=False, timeout=None, gap=None, env_args=None):
    n_poi = env_args['n_poi']
    n_depots = env_args['n_depots']
    n = env_args['n']
    n_UGVs = env_args['n_UGVs']
    n_UAVs = env_args['n_UAVs']

    filename = f'images/2EVRP多车-{n_poi}user-{n_depots}busstop-{n_UGVs}UGVs-{n_UAVs}UAVs_limit={timeout}.png'
    print(f'>>>Save Traj to {filename}')
    # filename = f'gurobi/traj_png/debug.png'

    if not n == len(loc):  # hard code
        print(f'>>>减小问题实例规模为{n}<<<')
        loc = loc[:n]

    try:
        problem_filename = os.path.join(directory, "{}.gurobi{}{}.pkl".format(
            name, "" if timeout is None else "t{}".format(timeout), "" if gap is None else "gap{}".format(gap)))

        if os.path.isfile(problem_filename) and not disable_cache:
            (cost, routes, duration) = load_dataset(problem_filename)
        else:
            start = time.time()
            cost, routes = solve_euclidian_vrp_gurobi(loc, threads=1, timeout=timeout, gap=gap, env_args=env_args)
            duration = time.time() - start
            save_dataset((cost, routes, duration), problem_filename)

        avg_visit_time = calc_avg_node_visit_time_multi_car(loc, routes, env_args)  
        assert abs(avg_visit_time - cost) <= 1e-5, "Cost is incorrect"

        plot_vehicle_routes(loc, routes, env_args, filename)

        return avg_visit_time, routes, duration

    except Exception as e:
        print("Exception occurred")
        print("Exception type:", type(e).__name__)
        print("Exception message:", e)
        traceback.print_exc()
        raise ValueError

def calc_avg_node_visit_time_multi_car(loc, routes, env_args):

    n_poi = env_args['n_poi']
    n_depots = env_args['n_depots']
    n = env_args['n']
    n_UGVs = env_args['n_UGVs']
    n_UAVs = env_args['n_UAVs']
    n_vehicles = env_args['n_vehicles']
    S = env_args['S']
    D = env_args['D']
    C = env_args['C']
    UGVs = env_args['UGVs']
    UAVs = env_args['UAVs']
    K = env_args['K']


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

def plot_vehicle_routes(loc, routes, env_args, filename):

    n_depots = env_args['n_depots']


    plt.figure(figsize=(10, 10))
    colors = plt.cm.get_cmap('tab20', len(routes))    

    for idx, (vehicle, route) in enumerate(routes.items()):
        route_locs = np.array([loc[node] for node in route])
        plt.plot(route_locs[:, 0], route_locs[:, 1], marker='o', color=colors(idx), label=f'{vehicle}')

        for i in range(len(route) - 1):
            plt.arrow(
                route_locs[i, 0], route_locs[i, 1],
                route_locs[i+1, 0] - route_locs[i, 0], 
                route_locs[i+1, 1] - route_locs[i, 1],
                head_width=0.02, 
                length_includes_head=True, 
                color=colors(idx)
            )

    # 绘制出发点
    plt.plot(loc[0][0], loc[0][1], 'rp', markersize=10, label='Start Point')
    
    # 绘制各个depot
    for depot in range(1, n_depots):
        plt.plot(loc[depot][0], loc[depot][1], 'ks', markersize=10, label=f'Depot {depot}')

    plt.legend()
    plt.title("Vehicle Routes")
    plt.xlabel("X coordinate")
    plt.ylabel("Y coordinate")
    plt.grid()
    
    plt.savefig(filename)
    print(f"Plot saved as {filename}")


def get_env_env_args(args):
    n = args.n_poi + args.n_depots + 1
    n_vehicles = args.n_UGVs + args.n_UAVs
    env_args = {
    'n_poi': args.n_poi,
    'n_depots': args.n_depots,
    'n': n,
    'n_UAVs': args.n_UAVs,
    'n_UGVs': args.n_UGVs,
    'n_vehicles': n_vehicles,
    'S': 0,
    'D': list(range(1, args.n_depots+1)),
    'C': list(range(1+args.n_depots, n)),
    'UGVs': [f'v{k}' for k in range(args.n_UGVs)],
    'UAVs': [f'v{k}' for k in range(args.n_UGVs, n_vehicles)],
    'K': [f'v{k}' for k in range(n_vehicles)],
    }

    print('>>>env_args:\n', env_args)
    return env_args

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("method",
                        help="Name of the method to evaluate, 'nn', 'gurobi' or '(nearest|random|farthest)_insertion'")
    parser.add_argument("datasets", nargs='+', help="Filename of the dataset(s) to evaluate")
    parser.add_argument("-f", action='store_true', help="Set true to overwrite")
    parser.add_argument("-o", default=None, help="Name of the results file to write")
    parser.add_argument("--cpus", type=int, help="Number of CPUs to use, defaults to all cores")
    parser.add_argument('--no_cuda', action='store_true', help='Disable CUDA (only for Tsiligirides)')
    parser.add_argument('--disable_cache', action='store_true', help='Disable caching')
    parser.add_argument('--max_calc_batch_size', type=int, default=1000, help='Size for subbatches')
    parser.add_argument('--progress_bar_mininterval', type=float, default=0.1, help='Minimum interval')
    parser.add_argument('-n', type=int, help="Number of instances to process")
    parser.add_argument('--offset', type=int, help="Offset where to start processing")
    parser.add_argument('--results_dir', default='results', help="Name of results directory")

    parser.add_argument('--debug', default=False, action='store_true', help="Debug mode")

    # env args
    parser.add_argument('--n_poi', type=int, default=100, help="Number of points of interest (POIs)")
    parser.add_argument('--n_depots', type=int, default=10, help="Number of depots")
    parser.add_argument('--n_UGVs', type=int, default=2, help="Number of UGVs")
    parser.add_argument('--n_UAVs', type=int, default=5, help="Number of UAVs")

    # args
    parser.add_argument('--timeout', type=int, default=20, help="Timeout for gurobi")

    opts = parser.parse_args()

    env_args = get_env_env_args(opts)

    assert opts.o is None or len(opts.datasets) == 1, "Cannot specify result filename with more than one dataset"

    for dataset_path in opts.datasets:

        assert os.path.isfile(check_extension(dataset_path)), "File does not exist!"

        dataset_basename, ext = os.path.splitext(os.path.split(dataset_path)[-1])

        if opts.o is None:
            results_dir = os.path.join(opts.results_dir, "tsp", dataset_basename)
            os.makedirs(results_dir, exist_ok=True)

            out_file = os.path.join(results_dir, "{}{}{}-{}{}".format(
                dataset_basename,
                "offs{}".format(opts.offset) if opts.offset is not None else "",
                "n{}".format(opts.n) if opts.n is not None else "",
                opts.method, ext
            ))
        else:
            out_file = opts.o

        assert opts.f or not os.path.isfile(
            out_file), "File already exists! Try running with -f option to overwrite."

        match = re.match(r'^([a-z_]+)(\d*)$', opts.method)
        assert match
        method = match[1]
        runs = 1 if match[2] == '' else int(match[2])

        if method in ("gurobi"):

            target_dir = os.path.join(results_dir, "{}-{}".format(
                dataset_basename,
                opts.method
            ))
            assert opts.f or not os.path.isdir(target_dir), \
                "Target dir already exists! Try running with -f option to overwrite."

            if not os.path.isdir(target_dir):
                os.makedirs(target_dir)

            dataset = [(instance, ) for instance in load_dataset(dataset_path)]

            if opts.debug:
                dataset = dataset[:1]

            use_multiprocessing = False

            def run_func(args):
                return solve_gurobi(*args, disable_cache=opts.disable_cache,
                                    timeout=opts.timeout,
                                    gap=None, env_args=env_args)


            results, parallelism = run_all_in_pool(
                run_func,
                target_dir, dataset, opts, use_multiprocessing=use_multiprocessing
            )

        else:
            assert False, "Unknown method: {}".format(opts.method)

        costs, routes_all_instance, durations = zip(*results)
        print("Average cost: {} +- {}".format(np.mean(costs), 2 * np.std(costs) / np.sqrt(len(costs))))
        print("Average serial duration: {} +- {}".format(
            np.mean(durations), 2 * np.std(durations) / np.sqrt(len(durations))))
        print("Average parallel duration: {}".format(np.mean(durations) / parallelism))
        print("Calculated total duration: {}".format(timedelta(seconds=int(np.sum(durations) / parallelism))))

        save_dataset((results, parallelism), out_file)
