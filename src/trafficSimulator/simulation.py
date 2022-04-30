from .road import Road
from copy import deepcopy
from .vehicle_generator import VehicleGenerator
from .traffic_signal import TrafficSignal
from numpy import ones, argmin
from .utils import *
from random import sample, random


class Simulation:
    def __init__(self, config={}):
        self.t = 0.0  # Time keeping
        self.frame_count = 0  # Frame count keeping
        self.dt = 1 / 60  # Simulation time step
        self.roads = []  # Array to store roads
        self.generators = []
        self.traffic_signals = []
        self.vertex_dict = {}
        self.reverse_vertex_dict = {}
        self.vertices_to_path_to = set()

        self.total_trips = 0
        self.total_trip_time = 0

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
                self.walk_graph[ai, bi] = sidewalk.length #/ self.walk_max_velocity
                self.sidewalk_matrix[ai][bi] = [sidewalk]

                if mode != 2:  # mode 2 = walk / bike
                    road = self.create_road(a, b, mode, False, road_index)
                    # # End Vertex
                    # if b == (25, 29):
                    #     # Possible Start Vertices
                    #     if a == (22, 29) or a == (30, 29) or a == (25, 36) or a == (25, 21):
                    #         print(a, b)
                    #         print(road.index)
                    road_index += 1
                    self.car_graph[ai, bi] = road.length #/ self.car_max_velocity
                    self.road_matrix[ai][bi] = [road]

                if mode != 0:  # If mode != 0, the road is two way
                    sidewalk = self.create_road(b, a, mode, True, road_index)
                    road_index += 1
                    self.walk_graph[bi, ai] = sidewalk.length
                    self.sidewalk_matrix[bi][ai] = [sidewalk]
                    if mode != 2:  # mode 2 = walk / bike\
                        road = self.create_road(b, a, mode, False, road_index)
                        # # End Vertex
                        # if a == (25, 29):
                        #     # Possible starting vertices
                        #     if b == (22, 29) or b == (30, 29) or b == (25, 36) or b == (25, 21):
                        #         print(b, a)
                        #         print(road.index)
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

            transit_times = []
            transit_options = []
            transit_speeds = [self.walk_max_velocity, self.bus_max_velocity, ]

            length = self.walk_graph[start_vertex, end_vertex]
            walk_length = length / self.walk_max_velocity
            transit_times.append(length)
            transit_options.append('walk')

            #time estimate to walk to bus stop, catch bus, and walk from bus stop to destination
            bus_length = self.car_graph[start_vertex, end_vertex] / self.bus_max_velocity + self.bus_delay
            transit_times.append(bus_length)
            transit_options.append('bus')

            own_bike = random() * 100 < self.bike_ownership_percentage
            own_car = random() * 100 < self.car_ownership_percentage
            if own_bike:
                bike_length = length / self.bike_max_velocity
                transit_times.append(bike_length)
                transit_options.append('bike')
                transit_speeds.append(self.bike_max_velocity)
            if own_car and (walk_length > bus_length):
                # time estimate to get into car and park car so people don't always take car
                car_length = self.car_graph[start_vertex, end_vertex] / self.car_max_velocity + self.car_delay
                transit_times.append(car_length)
                transit_options.append('car')
                transit_speeds.append(self.car_max_velocity)


            #Finds best transit given options
            i = argmin(transit_times)
            best_transit = transit_options[argmin(transit_times)]
            transit_speed = transit_speeds[i]
            if best_transit == 'bus' or best_transit == 'car':
                path = self.road_matrix[start_vertex][end_vertex]
                path = [road.index for road in path]
            elif best_transit == 'bike' or best_transit == 'walk':
                path = self.sidewalk_matrix[start_vertex][end_vertex]
                path = [sidewalk.index for sidewalk in path]
            vehicles.append({"path": path, 'vehicle_type': best_transit, 'v_max':transit_speed})
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
                else:
                    self.total_trips += 1
                    self.total_trip_time += self.t - vehicle.time_added
                # In all cases, remove it from its road
                road.vehicles.popleft()
                # Increment time
        if self.total_trips != 0:
            print('Avg Trip Time', self.total_trip_time / self.total_trips, end='\r')
        self.t += self.dt
        self.frame_count += 1

    def run(self, steps):
        for _ in range(steps):
            self.update()