from math import sqrt
from matplotlib import pyplot as plt

from graph import Graph
from visualization import show


g: Graph = Graph(
    [(0, 10), (0, 10), (0, 10), (0, 5)],
    [(0, 1, 10, 2, 4),
     (1, 2, 10, 2, 4),
     (2, 0, 10, 2, 4),
     (1, 3, 5, 2, 2),
     (3, 1, 1, 0.1, 0)]
)


t = 200
plt.ion()

for _ in range(t):
    for from_node in g:
        for to_node_idx, road in from_node:
            node = g[to_node_idx]

            if len(node.output_roads) == 0:
                continue

            leaving_cars = min(road.cars * road.workload,
                               node.throughput_capacity)
            real_leaving_cars = 0

            spec_leaving_cars = leaving_cars / len(node.output_roads)

            sum_volume = sum([edge.volume for _, edge in node])

            for _, next_road in node:
                incoming_cars = leaving_cars * \
                    (next_road.volume / sum_volume) * (1 - next_road.workload)

                real_incoming_cars = -next_road.cars + \
                    next_road.update_cars(next_road.cars + incoming_cars)

                real_leaving_cars += real_incoming_cars

            road.update_cars(road.cars - real_leaving_cars)
    show(g)

plt.ioff()
plt.show()
