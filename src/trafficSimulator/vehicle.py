import numpy as np


class Vehicle:
    def __init__(self, config={}):
        self.car_attributes = {
            'l': 4,         # length of the car
            's0': 4,
            'T': 1,
            # 'v_max': 16.6,  # max velocity of the car
            'a_max': 1.44,  # max acceleration of the car
            'b_max': 4.61,
            'color': (0, 0, 255)
        }

        self.bike_attributes = {
            'l': 2,         # length of the bike
            's0': 2,
            'T': 1,
            # 'v_max': 8,     # max velocity of the bike
            'a_max': 0.85,  # max acceleration of the bike
            'b_max': 4.61,  # max break speed
            'color': (255, 255, 0)
        }

        self.walk_attributes = {
            'l': 1,         # length of the person
            's0': 1,
            'T': 1,
            # 'v_max': 4,     # max velocity of the person
            'a_max': 0.32,  # max acceleration of the person
            'b_max': 4.61,
            'color': (255, 0, 0)
        }

        self.bus_attributes = {
            'l': 8,         # length of the bus
            's0': 4,
            'T': 1,
            # 'v_max': 12,     # max velocity of the bus
            'a_max': 1,  # max acceleration of the bus
            'b_max': 4.61,
            'color': (200, 0, 200)
        }


        # Set default configuration
        self.set_default_config()

        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)

        if self.vehicle_type == 'car':
            for attr, val in self.car_attributes.items():
                setattr(self, attr, val)
        elif self.vehicle_type == 'bike':
            for attr, val in self.bike_attributes.items():
                setattr(self, attr, val)
        elif self.vehicle_type == 'walk':
            for attr, val in self.walk_attributes.items():
                setattr(self, attr, val)
        elif self.vehicle_type == "bus":
            for attr, val in self.bus_attributes.items():
                setattr(self, attr, val)

        self.v = self.v_max
        # Calculate properties
        self.init_properties()

    def set_default_config(self):
        self.path = []
        self.current_road_index = 0

        self.x = 0
        self.a = 0
        self.stopped = False

    def init_properties(self):
        self.sqrt_ab = 2 * np.sqrt(self.a_max * self.b_max)
        self._v_max = self.v_max

    def update(self, lead, dt):
        # Update position and velocity
        if self.v + self.a * dt < 0:
            self.x -= 1 / 2 * self.v * self.v / self.a
            self.v = 0
        else:
            self.v += self.a * dt
            self.x += self.v * dt + self.a * dt * dt / 2

        # Update acceleration

        alpha = 0
        if lead:
            delta_x = lead.x - self.x - lead.l
            delta_v = self.v - lead.v

            alpha = (self.s0 + max(0, self.T * self.v + delta_v * self.v / self.sqrt_ab)) / delta_x

        self.a = self.a_max * (1 - (self.v / self.v_max) ** 4 - alpha ** 2)

        if self.stopped:
            self.a = -self.b_max * self.v / self.v_max

    def stop(self):
        self.stopped = True

    def unstop(self):
        self.stopped = False

    def slow(self, v):
        self.v_max = v

    def unslow(self):
        self.v_max = self._v_max
