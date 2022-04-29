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
vertices_to_path_to = set()

INF = 9999
try:
    with open('num_vertices', 'rb') as file:
        num_vertices = load(file)
        print(num_vertices)
except:
    num_vertices = 95

walk_graph = ones(shape=(num_vertices, num_vertices)) * INF
car_graph = ones(shape=(num_vertices, num_vertices)) * INF
walk_path_matrix = [dict() for x in range(num_vertices)]
car_path_matrix = [dict() for x in range(num_vertices)]

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
            walk_graph[vertex_index, vertex_index] = 0
            if mode != 2: #mode 2 = walk / bike
                vertices_to_path_to.add(a)
                car_graph[vertex_index, vertex_index] = 0
            vertex_index += 1
        if b not in vertex_dict.keys():
            vertex_dict[b] = vertex_index
            reverse_vertex_dict[vertex_index] = b
            walk_graph[vertex_index, vertex_index] = 0
            if mode != 2: #mode 2 = walk / bike
                vertices_to_path_to.add(b)
                car_graph[vertex_index, vertex_index] = 0
            vertex_index += 1
        ai, bi = vertex_dict[a], vertex_dict[b]
        dist = distance.euclidean(a, b)
        walk_graph[ai, bi] = dist
        if mode != 2:  # mode 2 = walk / bike
            car_graph[ai, bi] = dist
            car_path_matrix[ai][bi] = [(ai, bi)]
        walk_path_matrix[ai][bi] = [(ai, bi)]
        roads.append((a, b, mode, mode == 2))
        if mode != 0:
            roads.append((b, a, mode, mode == 2))
            walk_graph[bi, ai] = dist
            walk_path_matrix[bi][ai] = [(bi, ai)]
            if mode != 2:  # mode 2 = walk / bike
                car_graph[bi, ai] = dist
                car_path_matrix[bi][ai] = [(bi, ai)]

with open('num_vertices', 'wb') as file:
    dump(vertex_index, file)
    print('updated')

sim = Simulation(num_vertices=num_vertices, vertex_dict=vertex_dict)


# path_matrix with shortest path destinations
utils.floyd_warshall(walk_graph, car_graph, num_vertices, walk_path_matrix,  car_path_matrix)

sim.create_roads(roads)

num_random_paths = 100
vehicles = []

# num vertices could be hard coded
start_v_weights = utils.generate_weights(len(vertices_to_path_to))  # likelihood of choosing vertex as start
end_v_weights = utils.generate_weights(num_vertices)  # likelihood of choosing vertex as end

weights = []

while num_random_paths > 0:
    start_vertex, end_vertex = choices(list(vertices_to_path_to), weights=start_v_weights, k=2)  # chooses start road and end road
    start_vertex = vertex_dict[start_vertex]
    end_vertex = vertex_dict[end_vertex]

    #time estimate to get into car so people don't always take car
    car_delay = 100

    walk_length = walk_graph[start_vertex, end_vertex] / 2
    car_length = car_graph[start_vertex, end_vertex] / 3 + car_delay

    walk_path = walk_path_matrix[start_vertex][end_vertex]
    car_path = car_path_matrix[start_vertex][end_vertex]

    # gets the shortest path from start road to end road from path_matrix
    if walk_length < car_length:
        path = sim.path_converter(walk_path)
        vehicles.append({"path": path, 'vehicle_type': utils.vehicle_selector('walk')})
    else:
        path = sim.path_converter(car_path)
        vehicles.append({"path": path, 'vehicle_type': utils.vehicle_selector('drive')})
    # converts path coordinates to road
    # vehicles.append({"path": path, 'vehicle_type': utils.vehicle_selector(path)})
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
