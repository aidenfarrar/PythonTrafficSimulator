from random import choices


def generate_weights(num_vertices, config=None):
    """
    generates weights for path selection. Bigger weight means higher chance of selection for vertex
    :param num_vertices: number or vertices in the road system
    :param config: the generation config
    :return: list of weights for vertices mapped vertex -> weight
    """
    # place holder
    return [1 for i in range(num_vertices)]

def floyd_warshall(walk_graph, car_graph, num_vertices, walk_path_matrix, car_path_matrix):
    """
    populates path_matrix with shortest path destinations
    :param graph: graph of the road network
    :param num_vertices: number of vertices/start points in the road network
    :param path_matrix: stores shortest paths from vertex i to j
    :return: updated path_matrix
    """
    # walk_graph_copy = walk_graph.copy()
    # car_graph_copy = car_graph.copy()
    for k in range(num_vertices):
        for i in range(num_vertices):
            for j in range(num_vertices):
                walk_detour = walk_graph[i, k] + walk_graph[k, j]
                car_detour = car_graph[i, k] + car_graph[k, j]
                if walk_graph[i, j] > walk_detour:
                    walk_graph[i, j] = walk_detour
                    walk_path_matrix[i][j] = walk_path_matrix[i][k] + walk_path_matrix[k][j]
                if car_graph[i, j] > car_detour:
                    car_graph[i, j] = car_detour
                    car_path_matrix[i][j] = car_path_matrix[i][k] + car_path_matrix[k][j]


def vehicle_selector(trip_type):
    """
    selects vehicle type for paths
    :param path:  current path
    :return: name of vehicle type
    """
    if trip_type == 'drive':
        return choices(["car", "bus"], weights=[50, 50])[0]  # placeholder 50 percent chance for bus to be generated
    else:
        return choices(["walk", "bike"], weights=[85, 15])[0]  # placeholder 30 percent chance for bike to be generated
