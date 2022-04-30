from .road import Road
from copy import deepcopy
from .vehicle_generator import VehicleGenerator
from .traffic_signal import TrafficSignal
from numpy import ones
from .utils import *
from random import sample


class Simulation:
    def __init__(self, config={}):
        self.t = 0.0  # Time keeping
        self.frame_count = 0  # Frame count keeping
        self.dt = 1 / 60  # Simulation time step
        self.roads = []  # Array to store roads
        self.generators = []
        self.traffic_signals = []

        # Update configuration with parameters from config
        for attr, val in config.items():
            setattr(self, attr, val)

    def set_default_config(self):
        self.road_dicts = [dict() for x in range(self.num_vertices)]

    def create_road(self, start, end, color, car_friendly=False, i=-1):
        road = Road(start, end, color, car_friendly, i)
        self.roads.append(road)
        # self.road_dicts[self.vertex_dict[start]][self.vertex_dict[end]] = i
        return road

    def load_vertices_from_file(self, filename):
        with open(filename, 'r') as file:
            # mode = -1
            vertex_index = 0
            for line in file.readlines():
                if line[0] == '#':
                    # mode += 1
                    continue
                a, b = line.split(':')
                points = a.split(',') + b.split(',')
                a1, a2, b1, b2 = [int(x) * self.scale_factor + self.offset for x in points]
                a, b = (a1, a2), (b1, b2)

                if a not in self.vertex_dict.keys():
                    self.vertex_dict[a] = vertex_index
                    self.reverse_vertex_dict[vertex_index] = a
                    vertex_index += 1
                if b not in self.vertex_dict.keys():
                    self.vertex_dict[b] = vertex_index
                    self.reverse_vertex_dict[vertex_index] = b
                    vertex_index += 1
            self.num_vertices = vertex_index
            file.close()
        self.set_default_config()
        self.create_graphs()
        self.load_roads_from_file(filename)

    def create_graphs(self):
        # create walking graph representation and car graph representation
        self.walk_graph = ones(shape=(self.num_vertices, self.num_vertices)) * self.INF
        self.car_graph = self.walk_graph.copy()
        self.sidewalk_matrix = [dict() for x in range(self.num_vertices)]
        self.road_matrix = [dict() for x in range(self.num_vertices)]

    def load_roads_from_file(self, filename):
        with open(filename, 'r') as file:
            mode = -1
            road_index = 0
            for line in file.readlines():
                if line[0] == '#':
                    mode += 1
                    continue

                # convert file co-ords to sim co-ords
                a, b = line.split(':')
                points = a.split(',') + b.split(',')
                a1, a2, b1, b2 = [int(x) * self.scale_factor + self.offset for x in points]
                a, b = (a1, a2), (b1, b2)

                # create road between given vertices
                # If mode = 0 should be a one-way, mode = 1 means two-way, mode = 2 means sidewalk
                ai, bi = self.vertex_dict[a], self.vertex_dict[b]
                sidewalk = self.create_road(a, b, mode, True, road_index)
                road_index += 1
                self.walk_graph[ai, bi] = sidewalk.length / self.walk_max_velocity
                self.sidewalk_matrix[ai][bi] = [sidewalk]

                if mode != 2:  # mode 2 = walk / bike
                    road = self.create_road(a, b, mode, False, road_index)
                    road_index += 1
                    self.car_graph[ai, bi] = road.length / self.car_max_velocity
                    self.road_matrix[ai][bi] = [road]

                if mode != 0:  # If mode != 0, the road is two way
                    sidewalk = self.create_road(b, a, mode, True, road_index)
                    road_index += 1
                    self.walk_graph[bi, ai] = sidewalk.length
                    self.sidewalk_matrix[bi][ai] = [sidewalk]
                    if mode != 2:  # mode 2 = walk / bike\
                        road = self.create_road(b, a, mode, False, road_index)
                        road_index += 1
                        self.car_graph[bi, ai] = road.length
                        self.road_matrix[bi][ai] = [road]
            file.close()

    def plan_paths(self):
        floyd_warshall(self.walk_graph, self.car_graph, self.num_vertices, self.sidewalk_matrix, self.road_matrix)

    def trip_generation(self):
        vehicles = []

        # num vertices could be hard coded
        # start_v_weights = generate_weights(len(self.vertices_to_path_to))  # likelihood of choosing vertex as start
        # end_v_weights = generate_weights(self.num_vertices)  # likelihood of choosing vertex as end

        weights = []

        while self.num_random_trips > 0:
            # start_vertex, end_vertex = sample(list(vertices_to_path_to), weights=start_v_weights, k=2)
            start_vertex, end_vertex = sample(range(self.num_vertices), k=2)  # chooses start road and end road

            walk_length = self.walk_graph[start_vertex, end_vertex]
            # time estimate to get into car so people don't always take car
            car_length = self.car_graph[start_vertex, end_vertex] + self.car_delay

            # gets the shortest path from start road to end road from path_matrix
            if walk_length < car_length:
                walk_path = self.sidewalk_matrix[start_vertex][end_vertex]
                path = [sidewalk.index for sidewalk in walk_path]
                vehicles.append({"path": path, 'vehicle_type': vehicle_selector('walk')})
            else:
                car_path = self.road_matrix[start_vertex][end_vertex]
                path = [road.index for road in car_path]
                vehicles.append({"path": path, 'vehicle_type': vehicle_selector('drive')})
            # converts path coordinates to road
            # vehicles.append({"path": path, 'vehicle_type': utils.vehicle_selector(path)})
            weights.append(1)  # every car type is equally likely to be generated
            self.num_random_trips -= 1
        return vehicles, weights

    def create_gen(self, config={}):
        gen = VehicleGenerator(self, config)
        self.generators.append(gen)
        return gen

    def create_signal(self, roads, config={}):
        roads = [[self.roads[i] for i in road_group] for road_group in roads]
        sig = TrafficSignal(roads, config)
        self.traffic_signals.append(sig)
        return sig

    def update(self):
        # Update every road
        for road in self.roads:
            road.update(self.dt)

        # Add vehicles
        for gen in self.generators:
            gen.update()

        for signal in self.traffic_signals:
            signal.update(self)

        # Check roads for out of bounds vehicle
        for road in self.roads:
            # If road has no vehicles, continue
            if len(road.vehicles) == 0: continue
            # If not
            vehicle = road.vehicles[0]
            # If first vehicle is out of road bounds
            if vehicle.x >= road.length:
                # If vehicle has a next road
                if vehicle.current_road_index + 1 < len(vehicle.path):
                    # Update current road to next road
                    vehicle.current_road_index += 1
                    # Create a copy and reset some vehicle properties
                    new_vehicle = deepcopy(vehicle)
                    new_vehicle.x = 0
                    # Add it to the next road
                    next_road_index = vehicle.path[vehicle.current_road_index]
                    self.roads[next_road_index].vehicles.append(new_vehicle)
                # In all cases, remove it from its road
                road.vehicles.popleft()
                # Increment time
        self.t += self.dt
        self.frame_count += 1

    # def path_converter(self, coord_list):
    #     path = []
    #     for start, end in coord_list:
    #         path.append(self.road_dicts[start][end])
    #     return path

    def run(self, steps):
        for _ in range(steps):
            self.update()
