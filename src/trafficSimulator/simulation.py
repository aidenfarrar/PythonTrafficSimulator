from .road import Road
from copy import deepcopy
from .vehicle_generator import VehicleGenerator
from .traffic_signal import TrafficSignal


class Simulation:
    def __init__(self, num_vertices, vertex_dict, config={}, ):
        self.num_vertices = num_vertices
        self.vertex_dict = vertex_dict
        # Set default configuration
        self.set_default_config()

        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)

    def set_default_config(self):
        self.t = 0.0  # Time keeping
        self.frame_count = 0  # Frame count keeping
        self.dt = 1 / 60  # Simulation time step
        self.roads = []  # Array to store roads
        self.generators = []
        self.traffic_signals = []
        self.road_dicts = [dict() for x in range(self.num_vertices)]

    def create_road(self, start, end, color, car_friendly=False, i=-1):
        road = Road(start, end, color, car_friendly, i)
        self.roads.append(road)
        self.road_dicts[self.vertex_dict[start]][self.vertex_dict[end]] = i
        return road

    # def load_roads_from_file(self, filename):
    #     with open(filename, 'r') as file:
    #         mode = -1
    #         for line in file.readlines():
    #             if line[0] == '#':
    #                 mode += 1
    #                 continue
    #             a, b = line.split(':')
    #             points = a.split(',') + b.split(',')
    #             a1, a2, b1, b2 = [int(x) * scale_factor + offset for x in points]
    #             # a1, a2, b1, b2 = [int(x) for x in points]
    #             a, b = (a1, a2), (b1, b2)
    #
    #             if a not in vertex_dict.keys():
    #                 vertex_dict[a] = vertex_index
    #                 reverse_vertex_dict[vertex_index] = a
    #                 walk_graph[vertex_index, vertex_index] = 0
    #                 if mode != 2:  # mode 2 = walk / bike
    #                     vertices_to_path_to.add(a)
    #                     car_graph[vertex_index, vertex_index] = 0
    #                 vertex_index += 1
    #             if b not in vertex_dict.keys():
    #                 vertex_dict[b] = vertex_index
    #                 reverse_vertex_dict[vertex_index] = b
    #                 walk_graph[vertex_index, vertex_index] = 0
    #                 if mode != 2:  # mode 2 = walk / bike
    #                     vertices_to_path_to.add(b)
    #                     car_graph[vertex_index, vertex_index] = 0
    #                 vertex_index += 1
    #             ai, bi = vertex_dict[a], vertex_dict[b]
    #             dist = distance.euclidean(a, b)
    #             walk_graph[ai, bi] = dist
    #             if mode != 2:  # mode 2 = walk / bike
    #                 car_graph[ai, bi] = dist
    #                 car_path_matrix[ai][bi] = [(ai, bi)]
    #             walk_path_matrix[ai][bi] = [(ai, bi)]
    #             roads.append((a, b, mode, mode == 2))
    #             if mode != 0:
    #                 roads.append((b, a, mode, mode == 2))
    #                 walk_graph[bi, ai] = dist
    #                 walk_path_matrix[bi][ai] = [(bi, ai)]
    #                 if mode != 2:  # mode 2 = walk / bike
    #                     car_graph[bi, ai] = dist
    #                     car_path_matrix[bi][ai] = [(bi, ai)]

    def create_roads(self, road_list):
        for i, road in enumerate(road_list):
            self.create_road(*road, i)

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

    def path_converter(self, coord_list):
        path = []
        for start, end in coord_list:
            path.append(self.road_dicts[start][end])
        return path

    def run(self, steps):
        for _ in range(steps):
            self.update()
