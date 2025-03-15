from matplotlib import pyplot as plt
from scipy.stats import norm

from graph import Graph, Locality, Junction, CarsFactory
from visualization import show

# graph initialization
g: Graph = Graph([...], [...])

cars_factory = CarsFactory(g)

REPETITIONS = 200
MU = 6
SIGMA = 1

time = 0
plt.ion()

cars: dict[tuple[int, int], list[Car]] = {}

for _ in range(REPETITIONS):
    for from_node in g:
        if isinstance(from_node, Locality):
            locality: Locality = from_node

            all_leaving_cars = locality.population * locality.emigration_factor
            cur_leaving_cars = round(
                all_leaving_cars * norm.pdf(time % 24, loc=MU, scale=SIGMA)
            )
            
            for car in  cars_factory.generate_cars(locality.idx, cur_leaving_cars):
                if len(car.cur_path) == 0:
                    continue

                nearest_node = car.cur_path[0]
                road = locality.output_roads[nearest_node.idx]

                if road.update_cars((old_amount_cars:=road.cars) + 1) == old_amount_cars + 1:
                    car.cur_edge = road
                    car.cur_node_idx = None

                    if (locality.idx, nearest_node.idx) not in cars:
                        car[(locality.idx, nearest_node.idx)] = []

                    cars[(locality.idx, nearest_node.idx)].append(car)
        else:
            junction: Junction = from_node
            ...
            
    show(g)
    time += 1

plt.ioff()
plt.show()
