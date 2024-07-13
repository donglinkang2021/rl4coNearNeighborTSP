from method import TSPMethod
from config import get_env_args, get_setting
from plot import plot_vehicle_routes
import json
import numpy as np

# generate random data
np.random.seed(1234)
dataset_size = 10000
tsp_size = 300
data = np.random.uniform(size=(dataset_size, tsp_size, 2)).astype(np.float32)

method = TSPMethod.NEAREST_NEIGHBOR
setting = 'setting4'
n_poi, n_depots, n_UGVs, n_UAVs = get_setting(setting)
env_args = get_env_args(n_poi, n_depots, n_UGVs, n_UAVs)
filename = f'result/2EVRP-{method.phrase}-{n_poi}user-{n_depots}busstop-{n_UGVs}UGVs-{n_UAVs}UAVs.json'

with open(filename, 'r') as f:
    vehicle_routes_list = json.load(f)

sample_idx = 0
sample_loc = data[sample_idx]
sample_routes = vehicle_routes_list[sample_idx]
plot_vehicle_routes(
    sample_loc, 
    sample_routes, 
    n_depots,
    filename=filename.replace('.json', f'_{sample_idx}.png'), 
    env_args=env_args
)

