from json import load
from time import sleep
from datetime import timedelta

import matplotlib.pyplot as plt

from graph import Graph, Locality, CarsFactory, Car, Edge, Junction, Node
from normal_distribution import get_leaving_citizens_factor, get_leaving_guests_factor
from shortest_path import find_path
from visualization import show


def load_graph() -> Graph:
    with open('./map.json', 'r', encoding='utf-8') as file:
        json = load(file)

    try:
        j_nodes = json["nodes"]
        nodes = [
            j_node if j_node[0] == "locality"
            else j_node[:3] + [{int(k): v for k, v in j_node[3].items()}]
            for j_node in j_nodes
        ]
        roads = json["roads"]
        return Graph(nodes, roads)
    except KeyError as e:
        raise KeyError("Incorrect json format") from e


graph = load_graph()

cars_factory = CarsFactory(graph)

cars_edges: dict[Edge, list[Car]] = {edge: [] for edge in graph.edges}
cars_nodes: dict[int, list[Car]] = {idx: [] for idx in range(len(graph.nodes))}

time = timedelta(hours=7)
delta = timedelta(seconds=30)
mod = timedelta(days=1)
    

def distribute_cars(locality: Locality, cars: list[Car]):
    for car in cars:
        if car.cur_path is None or len(car.cur_path) == 0:
            continue

        nearest_node = car.cur_path[0]

        road = locality.output_roads[nearest_node.idx]

        if road.update_cars((old_amount_cars := road.cars) + 1) == old_amount_cars + 1:
            if car in cars_nodes[locality.idx]:
                cars_nodes[locality.idx].remove(car)

            car.cur_edge = road
            car.cur_node_idx = None

            car.cur_path.pop(0)

            if road not in cars_edges:
                cars_edges[road] = []

            cars_edges[road].append(car)


def generate_cars():
    for node in graph:
        if not isinstance(node, Locality):
            continue

        locality: Locality = node

        all_leaving_native_cars = locality.population * locality.emigration_factor
        cur_leaving_native_cars = round(all_leaving_native_cars * get_leaving_citizens_factor(time))

        guest_cars = cars_nodes[locality.idx]

        all_leaving_guest_cars = len(guest_cars)
        cur_leaving_guest_cars = round(all_leaving_guest_cars * get_leaving_guests_factor(time))

        for car in guest_cars[:cur_leaving_guest_cars]:
            car.cur_path = find_path(graph, car.cur_node_idx, car.from_node_idx)

        distribute_cars(
            node,
            cars_factory.generate_cars(
                locality.idx,
                cur_leaving_native_cars
            )
        )

        distribute_cars(node, guest_cars[:cur_leaving_guest_cars])


def cars_driving():
    for edge, cars_stream in cars_edges.items():
        cars_to_remove = []

        for car in cars_stream:
            if not car.cur_path:
                raise ValueError("Car's path became empty before reaching destination node.")

            next_node: Node = car.cur_path[0]

            if len(car.cur_path) == 1:
                edge.update_cars(edge.cars - 1)
                cars_to_remove.append(car)

                if car.cur_path[0] == car.dest_node_idx:
                    car.cur_path.pop(0)
                    car.cur_edge = None
                    car.cur_node_idx = next_node.idx
                    cars_nodes[next_node.idx].append(car)
                else:
                    del car
                continue

            if isinstance(next_node, Junction):
                next_node: Junction = next_node

                if not next_node.out_stoplight.is_green(time):
                    continue

                stoplight = next_node.stoplights.get(car.cur_path[1].idx)
                if stoplight is not None and not stoplight.is_green(time):
                    continue
            else:
                next_node: Locality = next_node

            next_road = next_node.output_roads.get(car.cur_path[1].idx)

            if next_road.update_cars((next_road_cars := next_road.cars) + 1) > next_road_cars:
                edge.update_cars(edge.cars - 1)
                car.cur_edge = next_road
                car.cur_path.pop(0)

                if next_road not in cars_edges:
                    cars_edges[next_road] = []

                cars_edges[next_road].append(car)
                cars_to_remove.append(car)

        for car in cars_to_remove:
            cars_stream.remove(car)
        cars_to_remove.clear()


def main():
    global time

    plt.ion()

    while True:
        generate_cars()

        show(graph, time)
        sleep(0.05)

        cars_driving()

        show(graph, time)
        sleep(0.05)

        time = (time + delta) % mod

    plt.ioff()
    plt.show()


if __name__ == "__main__":
    main()
