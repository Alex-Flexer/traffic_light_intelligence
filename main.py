from matplotlib import pyplot as plt
from scipy.stats import norm

from graph import Graph, Locality, Junction, CarsFactory
from visualization import show
from normal_distribution import get_leaving_citizens_factor, get_leaving_guests_factor

# graph initialization
g: Graph = Graph([...], [...])

cars_factory = CarsFactory(g)

REPETITIONS = 200

time = 0
plt.ion()

cars: dict[Edge, list[Car]] = {}

for _ in range(REPETITIONS):
    for node in g:
        if not isinstance(node, Locality):
            continue

        locality: Locality = node

        all_leaving_cars = locality.population * locality.emigration_factor
        cur_leaving_cars = round(
            all_leaving_cars * get_leaving_citizens_factor(time)
        )

        for car in cars_factory.generate_cars(locality.idx, cur_leaving_cars):
            if car.cur_path is None or len(car.cur_path) == 0:
                continue

            nearest_node = car.cur_path[0]
            road = locality.output_roads[nearest_node.idx]

            if road.update_cars((old_amount_cars := road.cars) + 1) == old_amount_cars + 1:
                car.cur_edge = road
                car.cur_node_idx = None

                if road not in cars:
                    car[road] = []

                cars[road].append(car)

    for edge, cars_stream in cars:
        for car in cars_stream:
            # cars stream distribution
            ... 

    show(g)
    time += 1

plt.ioff()
plt.show()
