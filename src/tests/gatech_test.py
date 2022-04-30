from trafficSimulator import *
from pickle import dump, load
from numpy import ones
from scipy.spatial import distance
from random import sample
from trafficSimulator import utils

# Create simulation

# Add multiple roads


#Parameters
roads = []


sim_config = {
    'scale_factor': 15,
    'offset': 40,
    'vertex_dict': {},
    'reverse_vertex_dict': {},
    'vertices_to_path_to': set(),
    'INF': 9999,
    'car_max_velocity': 25,
    'bike_max_velocity': 15,
    'walk_max_velocity': 3.5,
    'num_random_trips': 100,
    'car_delay': 100
}

sim = Simulation(config=sim_config)
# Set default configuration
sim.load_vertices_from_file('gt-model.txt')
sim.plan_paths()
vehicles, weights = sim.trip_generation()
sim.create_gen({
    'vehicle_rate': 100,
    'vehicles': vehicles,
    'weights': weights
})

# Start simulation
win = Window(sim)
win.offset = (-150, -110)
win.run(steps_per_update=5)
