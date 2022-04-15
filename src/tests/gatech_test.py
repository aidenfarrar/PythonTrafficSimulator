from trafficSimulator import *

# Create simulation
sim = Simulation()

# Add multiple roads
roads = []
scale_factor = 4
offset = 40
with open("gt-model.txt", 'r') as file:
    file.readline()
    mode = 0
    for line in file.readlines():
        if line[0] == '#':
            print(line)
            mode += 1
            continue
        a, b = line.split(':')
        points = a.split(',') + b.split(',')
        a1, a2, b1, b2 = [int(x) * scale_factor + offset for x in points]
        a, b = (a1, a2), (b1, b2)
        roads.append((a, b, mode, mode == 2))
        if mode != 0:
            roads.append((b, a, mode, mode == 2))

sim.create_roads(roads)

# sim.create_gen({
#     'vehicle_rate': 60,
#     'vehicles': [
#         [1, {"path": [4, 3, 2]}],
#         [1, {"path": [0]}],
#         [1, {"path": [1]}],
#         [1, {"path": [6]}],
#         [1, {"path": [7]}]
#     ]
# })

# Start simulation
win = Window(sim)
win.offset = (-150, -110)
win.run(steps_per_update=5)
