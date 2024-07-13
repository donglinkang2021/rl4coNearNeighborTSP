import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from typing import List

def plot_vehicle_routes(
        loc: np.ndarray, 
        routes: dict, 
        uav_start_idxs: List[int], 
        filename: str
    ):

    plt.figure(figsize=(10, 10))
    colors = matplotlib.colormaps['tab20']    

    # Plot vehicle routes
    for idx, (vehicle, route) in enumerate(routes.items()):
        # vehicle = f'v{i}', route: List[int]
        route_locs = np.array([loc[node] for node in route])
        plt.plot(
            route_locs[:, 0], route_locs[:, 1], 
            marker='o', color=colors(idx), 
            label=f'{vehicle}'
        )

        for i in range(len(route) - 1):
            plt.arrow(
                route_locs[i, 0], route_locs[i, 1],
                route_locs[i+1, 0] - route_locs[i, 0], 
                route_locs[i+1, 1] - route_locs[i, 1],
                head_width=0.02, 
                length_includes_head=True, 
                color=colors(idx)
            )

    # Start point
    plt.plot(loc[0][0], loc[0][1], 'rp', markersize=10, label='Start Point')
    
    # this will plot all the bus stops
    # Bus stops
    # for depot in range(1, n_depots+1):
    #     plt.plot(
    #         loc[depot][0], loc[depot][1], 'ks', 
    #         markersize=10, label=f'Depot {depot}'
    #     )
    
    for i, depot_idx in enumerate(uav_start_idxs):
        plt.plot(
            loc[depot_idx][0], loc[depot_idx][1], 'ks', 
            markersize=10, label=f'Depot {i}'
        )

    plt.legend() # hope this place to the outside of the plot
    # plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.title("Vehicle Routes")
    plt.xlabel("X coordinate")
    plt.ylabel("Y coordinate")
    plt.grid()
    
    plt.savefig(filename)
    print(f"Plot saved as {filename}")