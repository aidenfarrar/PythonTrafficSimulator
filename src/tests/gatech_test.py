from trafficSimulator import *
sim_parameters = {
    'scale_factor': 15,
    'offset': 40,
    'INF': 99999,
    'bus_max_velocity': 20,
    'car_max_velocity': 25,
    'bike_max_velocity': 15,
    'walk_max_velocity': 3.5,
    'num_random_trips': 400,
    'car_delay': 100,
    'bus_delay': 150,
    'bike_ownership_percentage': 15,
    'car_ownership_percentage': 40
}

sim = Simulation(config=sim_parameters)
# Set default configuration
sim.load_vertices_from_file('gt-model.txt')
sim.plan_paths()
vehicles, weights = sim.trip_generation()
sim.create_gen({
    'vehicle_rate': 100,
    'vehicles': vehicles,
    'weights': weights
})

sim.create_signal([[165, 293], [161, 227]])
sim.create_signal([[281, 287]])
sim.create_signal([[327], [339]])
sim.create_signal([[125, 317], [139]]) #0, 29
sim.create_signal([[133, 189], [173, 179]]) #0, 29

# Start simulation
win = Window(sim)
win.offset = (-150, -110)
win.run(steps_per_update=5)