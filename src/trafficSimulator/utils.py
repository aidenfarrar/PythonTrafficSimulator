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

def floyd_warshall(graph, num_vertices, path_matrix):
    """
    populates path_matrix with shortest path destinations
    :param graph: graph of the road network
    :param num_vertices: number of vertices/start points in the road network
    :param path_matrix: stores shortest paths from vertex i to j
    :return: updated path_matrix
    """
    graph_copy = graph.copy()
    for k in range(num_vertices):
        for i in range(num_vertices):
            for j in range(num_vertices):
                detour = graph_copy[i, k] + graph_copy[k, j]
                if graph_copy[i, j] > detour:
                    graph_copy[i, j] = detour
                    path_matrix[i][j] = path_matrix[i][k] + path_matrix[k][j]


def vehicle_selector(path):
    """
    selects vehicle type for paths
    :param path:  current path
    :return: name of vehicle type
    """
    if len(path) > 10:
        return choices(["car", "bus"], weights=[50, 50])[0]  # placeholder 50 percent chance for bus to be generated
    elif len(path) > 3:
        return 'bike'
    else:
        return 'walk'
