import matplotlib.pyplot as plt

from graph import Graph, Locality, CarsFactory, Car, Edge, Junction
from normal_distribution import get_leaving_citizens_factor
from visualization import show

# graph initialization
graph: Graph = Graph([...], [...])

cars_factory = CarsFactory(graph)

REPETITIONS = 200

time = 0
plt.ion()

cars: dict[Edge, list[Car]] = {}

for _ in range(REPETITIONS):
    for node in graph:
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
                car.cur_path.pop(0)

                if road not in cars:
                    car[road] = []

                cars[road].append(car)

    for edge, cars_stream in cars.items():
        cars_to_remove = []

        for car in cars_stream:
            if not car.cur_path:  
                cars_to_remove.append(car)
                edge.update_cars(edge.cars - 1)
                continue

            next_node = car.cur_path[0]
            if isinstance(next_node, Junction):
                stoplight = next_node.stoplights.get(car.cur_edge.idx)
                if stoplight and stoplight.tp == "out":
                    if (time % (stoplight.green_time + stoplight.red_time)) >= stoplight.green_time:
                        continue

            next_road = next_node.output_roads.get(car.cur_path[1].idx if len(car.cur_path) > 1 else car.dest_node_idx)

            if next_road:
                old_cars = next_road.cars
                if next_road.update_cars(old_cars + 1) > old_cars:  
                    edge.update_cars(edge.cars - 1)
                    cars_to_remove.append(car)
                    car.cur_edge = next_road
                    car.cur_path.pop(0)

                    if next_road not in cars:
                        cars[next_road] = []
                    cars[next_road].append(car)

        for car in cars_to_remove:
            cars_stream.remove(car)

    show(graph)
    time += 1

plt.ioff()
plt.show()
