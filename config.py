n_poi = 3       # user
n_depots = 4     # bus stop
n_UGVs = 1
n_UAVs = 1


n = n_poi + n_depots + 1
n_vehicles = n_UGVs + n_UAVs
env_args = {
    'n_poi': n_poi,
    'n_depots': n_depots,
    'n': n,
    'n_UAVs': n_UAVs,
    'n_UGVs': n_UGVs,
    'n_vehicles': n_vehicles,
    'S': 0,
    'D': list(range(1, n_depots+1)),
    'C': list(range(1+n_depots, n)),
    'UGVs': [f'v{k}' for k in range(n_UGVs)],
    'UAVs': [f'v{k}' for k in range(n_UGVs, n_vehicles)],
    'K': [f'v{k}' for k in range(n_vehicles)],
}