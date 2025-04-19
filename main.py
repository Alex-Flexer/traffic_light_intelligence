from json import load
from time import sleep

from collections import defaultdict
import matplotlib.pyplot as plt

from graph import Graph, Locality, CarsFactory, Car, Edge, Junction, Node
from normal_distribution import get_leaving_citizens_factor
# from shortest_path import find_path
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
        graph = Graph(nodes, roads)
    except KeyError:
        raise KeyError("Incorrect json format")
    else:
        return graph


# graph initialization
# graph: Graph=Graph(
#     [
#         ("locality", 1000, 0.7, 0.6),
#         ("locality", 500, 0.5, 0.3),
#         ("locality", 200, 0.3, 0.1),
#         ("junction", 50, (30, 20), {0: (25, 25), 1: (25, 25), 2: (25, 25)}),
#         ("junction", 40, (20, 30), {0: (20, 30), 3: (25, 25)})
#     ],
#     [
#         (0, 4, 60, 150, 2, 0),
#         (0, 3, 60, 100, 3, 0),
#         (1, 3, 60, 80, 2, 0),
#         (2, 3, 60, 60, 1, 0),
#         (3, 0, 60, 100, 3, 0),
#         (3, 1, 60, 80, 2, 0),
#         (3, 2, 60, 60, 1, 0),
#         (3, 4, 60, 50, 2, 0),
#         (4, 0, 60, 150, 2, 0),
#         (4, 3, 60, 50, 2, 0)
#     ]
# )
graph = load_graph()

cars_factory = CarsFactory(graph)

REPETITIONS = 200

cars_edges: dict[Edge, list[Car]] = {edge: [] for edge in graph.edges}
cars_nodes: dict[int, list[Car]] = {idx: [] for idx in range(len(graph.nodes))}
time = 0


def generate_cars():
    for node in graph:
        if not isinstance(node, Locality):
            continue

        locality: Locality = node

        all_leaving_native_cars = locality.population * locality.emigration_factor
        leaving_factor = get_leaving_citizens_factor(time)
        cur_leaving_native_cars = round(all_leaving_native_cars * leaving_factor)
        # print(all_leaving_native_cars, cur_leaving_native_cars, leaving_factor)

        # all_leaving_guest_cars = cars_nodes[locality.idx]
        # cur_leaving_guest_cars = round(all_leaving_guest_cars * get_leaving_guests_factor(time))

        # for car in cars_nodes[locality.idx][:cur_leaving_guest_cars]:
        #     car.cur_path = find_path(graph, car.cur_node_idx, car.from_node_idx)

        for car in cars_factory.generate_cars(locality.idx, cur_leaving_native_cars):
            # print([node.idx for node in car.cur_path], locality.output_roads)
            # print(car.from_node_idx, car.dest_node_idx)
            if car.cur_path is None or len(car.cur_path) == 0:
                continue

            nearest_node = car.cur_path[0]
            road = locality.output_roads[nearest_node.idx]

            if road.update_cars((old_amount_cars := road.cars) + 1) == old_amount_cars + 1:
                # print(f"({id(road)}) {node.idx} --> {nearest_node.idx}: {road.cars}")
                car.cur_edge = road
                car.cur_node_idx = None
                car.cur_path.pop(0)

                if road not in cars_edges:
                    cars_edges[road] = []

                cars_edges[road].append(car)


def cars_driving():
    for edge, cars_stream in cars_edges.items():
        cars_to_remove = []

        for car in cars_stream:
            if not car.cur_path:
                raise ValueError("Car's path became empty before reaching destination node.")

            next_node: Node = car.cur_path[0]

            if len(car.cur_path) == 1:
                edge.update_cars(edge.cars - 1)
                car.cur_path.pop(0)
                car.cur_edge = None
                car.cur_node_idx = next_node.idx
                cars_nodes[next_node.idx] = cars_nodes.get(next_node.idx, []) + [car]
                cars_to_remove.append(car)
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

        # print(cars_stream, cars_to_remove)
        for car in cars_to_remove:
            cars_stream.remove(car)
        cars_to_remove.clear()


def main():
    global time

    plt.ion()

    for _ in range(REPETITIONS):
        # print(f"TIME: {time}")
        generate_cars()

        show(graph)
        sleep(0.3)
        # input()

        cars_driving()

        # print(f"TIME: {time}")
        # show(graph)
        sleep(0.3)
        # input()

        time = (time + 1) % 24

    plt.ioff()
    plt.show()


if __name__ == "__main__":
    main()
