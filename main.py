import matplotlib.pyplot as plt

from graph import Graph, Locality, CarsFactory, Car, Edge, Junction, Node
from normal_distribution import get_leaving_citizens_factor
from visualization import show

# graph initialization
graph: Graph = Graph(
    ["locality", 100, 0.8, 0.15],
    [...]
)

cars_factory = CarsFactory(graph)

REPETITIONS = 200

plt.ion()

cars: dict[Edge, list[Car]] = {}
time = 0

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
        cars_idx_to_remove = []

        for car_idx, car in enumerate(cars_stream):
            if not car.cur_path:
                raise ValueError("Car's path became empty before reaching destination node.")

            next_node: Node = car.cur_path[0]

            if len(car.cur_path) == 1:
                edge.update_cars(edge.cars - 1)
                car.cur_path.pop(0)
                car.cur_edge = None
                car.cur_node_idx = next_node.idx
                cars_idx_to_remove.append(car_idx)
                continue

            if isinstance(next_node, Junction):
                next_node: Junction = next_node

                if not next_node.out_stoplight.is_green(time):
                    continue

                stoplight = next_node.stoplights.get(car.cur_path[1].idx)
                if stoplight is not None and not stoplight.is_green():
                    continue
            else:
                next_node: Locality = next_node

            next_road = next_node.output_roads.get(car.cur_path[1].idx)

            if next_road.update_cars((next_road_cars := next_road.cars) + 1) > next_road_cars:
                edge.update_cars(edge.cars - 1)
                car.cur_edge = next_road
                car.cur_path.pop(0)

                if next_road not in cars:
                    cars[next_road] = []

                cars[next_road].append(car)
                cars_idx_to_remove.append(car_idx)

        for car_idx in cars_idx_to_remove:
            cars_stream.pop(car_idx)

    show(graph)
    time += 1

plt.ioff()
plt.show()
