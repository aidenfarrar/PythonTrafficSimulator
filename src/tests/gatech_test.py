from trafficSimulator import *
from pickle import dump, load
from numpy import ones
from scipy.spatial import distance
from random import sample, choices
from trafficSimulator import utils

# Create simulation


# Add multiple roads


roads = []
scale_factor = 15
offset = 40
vertex_dict = {}
reverse_vertex_dict = {}
vertex_index = 0

INF = 9999
try:
    with open('num_vertices', 'rb') as file:
        num_vertices = load(file)
except:
    num_vertices = 78

graph = ones(shape=(num_vertices, num_vertices)) * INF
path_matrix = [dict() for x in range(num_vertices)]

with open("gt-model.txt", 'r') as file:
    file.readline()
    mode = 0
    for line in file.readlines():
        if line[0] == '#':
            mode += 1
            continue
        a, b = line.split(':')
        points = a.split(',') + b.split(',')
        a1, a2, b1, b2 = [int(x) * scale_factor + offset for x in points]
        # a1, a2, b1, b2 = [int(x) for x in points]
        a, b = (a1, a2), (b1, b2)
        if a not in vertex_dict.keys():
            vertex_dict[a] = vertex_index
            reverse_vertex_dict[vertex_index] = a
            graph[vertex_index, vertex_index] = 0
            vertex_index += 1
        if b not in vertex_dict.keys():
            vertex_dict[b] = vertex_index
            reverse_vertex_dict[vertex_index] = b
            graph[vertex_index, vertex_index] = 0
            vertex_index += 1
        ai, bi = vertex_dict[a], vertex_dict[b]
        dist = distance.euclidean(a, b)
        graph[ai, bi] = dist
        path_matrix[ai][bi] = [(ai, bi)]
        roads.append((a, b, mode, mode == 2))
        if mode != 0:
            roads.append((b, a, mode, mode == 2))
            graph[bi, ai] = dist
            path_matrix[bi][ai] = [(bi, ai)]

with open('num_vertices', 'wb') as file:
    dump(vertex_index, file)
    print('updated')

sim = Simulation(num_vertices=num_vertices, vertex_dict=vertex_dict)


# path_matrix with shortest path destinations
utils.floyd_warshall(graph, num_vertices, path_matrix)

sim.create_roads(roads)

num_random_paths = 100
vehicles = []

# num vertices could be hard coded
start_v_weights = utils.generate_weights(num_vertices)  # likelihood of choosing vertex as start
end_v_weights = utils.generate_weights(num_vertices)  # likelihood of choosing vertex as end

weights = []

while num_random_paths > 0:
    start_vertex, end_vertex = choices(range(num_vertices), weights=start_v_weights)[0], choices(range(num_vertices), weights=end_v_weights)[0]  # chooses start road and end road

    # prevent same start and end vertex
    while start_vertex == end_vertex:
        end_vertex = choices(range(num_vertices), weights=end_v_weights)[0]

    path = path_matrix[start_vertex][end_vertex]  # gets the shortest path from start road to end road from path_matrix
    path = sim.path_converter(path)  # converts path coordinates to road
    vehicles.append({"path": path, 'vehicle_type': utils.vehicle_selector(path)})
    weights.append(1)  # every car type is equally likely to be generated
    num_random_paths -= 1

sim.create_gen({
    'vehicle_rate': 100,
    'vehicles': vehicles,
    'weights': weights
})

# Start simulation
win = Window(sim)
win.offset = (-150, -110)
win.run(steps_per_update=5)
