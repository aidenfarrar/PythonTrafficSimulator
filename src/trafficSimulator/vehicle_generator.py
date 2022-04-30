from .vehicle import Vehicle
from numpy.random import randint
from collections import deque
from random import choices

class VehicleGenerator:
    def __init__(self, sim, config={}):
        self.sim = sim
        # Set default configurations
        self.set_default_config()
        # Update configurations
        for attr, val in config.items():
            setattr(self, attr, val)

        # Calculate properties
        self.init_properties()

    def set_default_config(self):
        """Set default configuration"""
        self.poisson = True
        self.vehicle_rate = 20 # rate for poisson dist
        self.vehicles = [
            (1, {})  # (weight for generation, vehicle config)
        ]
        self.last_added_time = 0

        self.burst_queue = deque()  # queue of generated vehicles
        self.burst_freq = 15  # time between bursts
        self.last_burst = 0  # time last burst was completed
        self.min_burst = 75  # min number of vehicles in burst
        self.max_burst = 100  # max number of vehicles in burst


    def init_properties(self):
        self.upcoming_vehicle = self.generate_vehicle()

    def generate_vehicle(self):
        """Returns a random vehicle from self.vehicles with random proportions"""
        [config] = choices(self.vehicles, weights=self.weights)
        return Vehicle(config)


    def update(self):
        """Add vehicles"""
        if self.poisson:
            if self.sim.t - self.last_added_time >= 60 / self.vehicle_rate:
                # If time elasped after last added vehicle is
                # greater than vehicle_period; generate a vehicle
                road = self.sim.roads[self.upcoming_vehicle.path[0]]
                if len(road.vehicles) == 0\
                   or road.vehicles[-1].x > self.upcoming_vehicle.s0 + self.upcoming_vehicle.l:
                    # If there is space for the generated vehicle; add it
                    self.upcoming_vehicle.time_added = self.sim.t
                    road.vehicles.append(self.upcoming_vehicle)
                    # Reset last_added_time and upcoming_vehicle
                    self.last_added_time = self.sim.t
                    self.upcoming_vehicle = self.generate_vehicle()

        else:
            # print(self.sim.t)
            if len(self.burst_queue) > 0:
                if self.sim.t - self.last_burst >= self.burst_freq:
                    self.upcoming_vehicle = self.burst_queue[-1]
                    road = self.sim.roads[self.upcoming_vehicle.path[0]]
                    if len(road.vehicles) == 0\
                       or road.vehicles[-1].x > self.upcoming_vehicle.s0 + self.upcoming_vehicle.l:
                        # If there is space for the generated vehicle; add it
                        self.upcoming_vehicle.time_added = self.sim.t
                        road.vehicles.append(self.upcoming_vehicle)
                        print(f"car sent : {self.sim.t}")
                        self.burst_queue.pop()

            else:
                print(f"last burst time : {self.sim.t}")
                self.last_burst = self.sim.t
                self.bursty_gen(self.burst_queue)





    def bursty_gen(self, burst_queue):
        r = randint(self.min_burst, self.max_burst + 1)
        for i in range(r):
            burst_queue.append(self.generate_vehicle())
