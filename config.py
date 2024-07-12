settings = {
    "setting1": {
        "n_poi": 200,
        "n_depots": 40,
        "n_UGVs": 1,
        "n_UAVs": 10,
    },
    "setting2": {
        "n_poi": 200,
        "n_depots": 20,
        "n_UGVs": 2,
        "n_UAVs": 5,
    },
    "setting3": {
        "n_poi": 100,
        "n_depots": 20,
        "n_UGVs": 1,
        "n_UAVs": 5,
    }
}

n_poi = 3           # user
n_depots = 4        # bus stop
n_UGVs = 1
n_UAVs = 1


n = n_poi + n_depots + 1                            # number of nodes
n_vehicles = n_UGVs + n_UAVs                        # number of vehicles
S = 0                                               # start point index
D = list(range(1, n_depots+1))                      # bus stops index
C = list(range(1+n_depots, n))                      # POIs index
UGVs = [f'v{k}' for k in range(n_UGVs)]             # UGVs names
UAVs = [f'v{k}' for k in range(n_UGVs, n_vehicles)] # UAVs names
K = [f'v{k}' for k in range(n_vehicles)]            # vehicles names

env_args = {'n_poi': n_poi, 'n_depots': n_depots, 'n': n, 'n_UAVs': n_UAVs, 'n_UGVs': n_UGVs, 'n_vehicles': n_vehicles, 'S': S, 'D': D, 'C': C, 'UGVs': UGVs, 'UAVs': UAVs, 'K': K}
print(env_args)

filename = f'images/2EVRP-NearNeighbor-{n_poi}user-{n_depots}busstop-{n_UGVs}UGVs-{n_UAVs}UAVs.png'

# some rename for easy understanding
start_point_index = S
bus_stops_indices = D
poi_indices = C
ugv_names = UGVs
uav_names = UAVs
vehicle_names = K
