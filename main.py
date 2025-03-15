from math import sqrt
from matplotlib import pyplot as plt

from graph import Graph, Locality, Junction
from visualization import show
from sigma_math import calc_leaving_people


g: Graph = Graph(
    [(0, 10), (0, 10), (0, 10), (0, 5)],
    [(0, 1, 10, 2, 4),
     (1, 2, 10, 2, 4),
     (2, 0, 10, 2, 4),
     (1, 3, 5, 2, 2),
     (3, 1, 1, 0.1, 0),
     (3, 0, 1, 0.1, 0)]
)

REPETITIONS = 200
time = 0
plt.ion()

for _ in range(REPETITIONS):
    for from_node in g:
        if isinstance(from_node, Locality):
            locality: Locality = from_node

            leaving_cars = calc_leaving_people(time, locality.emigration_factor, locality.population)

            for _, road in locality:
                leaving_cars = road.cars * road.workload
                real_leaving_cars = 0
                
                for _, next_road in locality:
                    incoming_cars = leaving_cars * \
                        (next_road.volume / sum_volume) * sqrt(1 - next_road.workload)

                    real_incoming_cars = -next_road.cars + \
                        next_road.update_cars(next_road.cars + incoming_cars)

                    real_leaving_cars += real_incoming_cars

                road.update_cars(road.cars - real_leaving_cars)
        else:
            junction: Junction = from_node

            for to_node_idx, road in junction:
                to_node = g[to_node_idx]

                if len(to_node.output_roads) == 0:
                    continue

                leaving_cars = min(road.cars * road.workload, to_node.bandwidth)
                real_leaving_cars = 0

                sum_volume = sum([edge.volume for _, edge in to_node])

                for _, next_road in to_node:
                    incoming_cars = leaving_cars * \
                        (next_road.volume / sum_volume) * sqrt(1 - next_road.workload)

                    real_incoming_cars = -next_road.cars + \
                        next_road.update_cars(next_road.cars + incoming_cars)

                    real_leaving_cars += real_incoming_cars

                road.update_cars(road.cars - real_leaving_cars)
    show(g)
    time += 1

plt.ioff()
plt.show()
