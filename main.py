from json import load
from time import sleep
from datetime import timedelta
import csv
import argparse

import matplotlib.pyplot as plt

from graph import Graph, Locality, CarsFactory, Car, Edge, Junction, Node
from distributor import get_leaving_citizens_factor, get_leaving_guests_factor
from pathfinder import find_path
from visualization import show
from optimizer import optimize_graph
from tools import calc_road_time
from meter import calc_avg_workload


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

accumulator_leaving_native_cars = 0
accumulator_leaving_guest_cars = 0

DELTA = timedelta(seconds=3)
MOD = timedelta(days=1)
HOUR_BORDER = timedelta(hours=1)

FILEPATH = 'stat\hourly_factors_{mode}.csv'

time = timedelta(days=1) - DELTA
hourly_stats = []

def save_hourly_factors(factors: list[float], mode: str) -> None:
    if len(factors) != 24:
        raise ValueError("Input list must contain exactly 24 elements (one for each hour).")
    
    # Open file in append mode, creating it if it doesn't exist
    with open(FILEPATH.format(mode), 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(factors)


def check_hour_border() -> bool:
    global time
    a = time // HOUR_BORDER
    b = (time + DELTA) // HOUR_BORDER
    return a < b


def distribute_cars(locality: Locality, cars: list[Car]):
    for car in cars:
        if car.cur_path is None or len(car.cur_path) == 0:
            continue

        nearest_node = car.cur_path[0]

        road = locality.output_roads[nearest_node.idx]

        if road.update_cars((old_amount_cars := road.cars) + 1) == old_amount_cars + 1:
            if car in cars_nodes[locality.idx]:
                cars_nodes[locality.idx].remove(car)

            car.previous_node = locality
            car.cur_edge = road
            car.time_reaching_node = time + timedelta(seconds=round(calc_road_time(locality, nearest_node)))
            car.cur_node_idx = None

            cars_edges[road].append(car)


def generate_cars():
    global accumulator_leaving_guest_cars, accumulator_leaving_native_cars, time

    leaving_citizens_factor = get_leaving_citizens_factor(time, DELTA)
    leaving_guests_factor = get_leaving_guests_factor(time, DELTA)

    for node in graph:
        if not isinstance(node, Locality):
            continue

        locality: Locality = node

        all_leaving_native_cars = locality.population * locality.emigration_factor
        accumulator_leaving_native_cars += all_leaving_native_cars * leaving_citizens_factor
        cur_leaving_native_cars = int(accumulator_leaving_native_cars)
        accumulator_leaving_native_cars -= cur_leaving_native_cars

        guest_cars = cars_nodes[locality.idx]

        all_leaving_guest_cars = len(guest_cars)
        accumulator_leaving_guest_cars += all_leaving_guest_cars * leaving_guests_factor
        cur_leaving_guest_cars = int(accumulator_leaving_guest_cars)
        accumulator_leaving_guest_cars -= cur_leaving_guest_cars

        for car in guest_cars[:cur_leaving_guest_cars]:
            car.cur_path = find_path(graph, car.cur_node_idx, car.from_node_idx)

        leaving_citizens_cars = cars_factory.generate_cars(
                locality.idx,
                cur_leaving_native_cars
            )

        distribute_cars(
            locality,
            leaving_citizens_cars
        )

        distribute_cars(locality, guest_cars[:cur_leaving_guest_cars])


def cars_driving():
    for edge, cars_stream in cars_edges.items():
        cars_to_remove = []
        number_passed_cars = 0

        for car in cars_stream:
            cur_node = car.cur_path[0]
            if isinstance(cur_node, Junction) and number_passed_cars >= cur_node.bandwidth:
                break

            if time < car.time_reaching_node:
                continue

            if len(car.cur_path) == 1:
                car.cur_path.pop(0)
                edge.update_cars(edge.cars - 1)
                cars_to_remove.append(car)

                car.previous_node = None
                car.cur_edge = None
                car.cur_node_idx = cur_node.idx

                if cur_node.idx == car.from_node_idx:
                    del car
                else:
                    cars_nodes[cur_node.idx].append(car)

                continue

            next_node: Node = car.cur_path[1]

            if isinstance(cur_node, Junction):
                if not cur_node.out_stoplight.is_green(time):
                    continue

                stoplight = cur_node.stoplights.get(next_node.idx)

                if stoplight is not None and not stoplight.is_green(time):
                    continue
            
            number_passed_cars += 1
            next_road = cur_node.output_roads.get(next_node.idx)

            if next_road.update_cars((next_road_cars := next_road.cars) + 1) > next_road_cars:
                edge.update_cars(edge.cars - 1)
                car.cur_edge = next_road
                car.time_reaching_node = time + timedelta(seconds=round(calc_road_time(cur_node, next_node)))
                car.previous_node = cur_node
                car.cur_path.pop(0)

                cars_edges[next_road].append(car)
                cars_to_remove.append(car)

        for car in cars_to_remove:
            cars_stream.remove(car)


def main():
    global time

    parser = argparse.ArgumentParser(description='Analyze and plot hourly factor data')
    parser.add_argument('--optimized', action='store_true', help='Combine all plots in one graph')
    parser.add_argument('--show-data', action='store_true', help='Combine all plots in one graph')
    parser.add_argument('--show-plot', action='store_true', help='Combine all plots in one graph')
    parser.add_argument('--save', action='store_true', help='Combine all plots in one graph')

    args = parser.parse_args()

    is_optimized = args.optimized
    show_plot = args.show_plot
    show_data = args.show_data
    save_data = args.save

    mode = "optimized" if is_optimized else "default"

    if show_plot:
        plt.ion()

    while True:
        generate_cars()

        if show_plot:
            show(graph, time)

        cars_driving()
        if show_plot:
            show(graph, time)

        if is_optimized:
            optimize_graph(graph)

        if check_hour_border() and (show_data or save_data):
            hour = (time + DELTA) % MOD // HOUR_BORDER
            avg_workload = round(calc_avg_workload(graph) * 1e4, 3)
            hourly_stats.append(avg_workload)

            if show_data:
                print(f"{hour}: {avg_workload}")

            if save_data and len(hourly_stats) == 24:
                save_hourly_factors(hourly_stats, mode)
                print("DATA IS SAVED!")
                hourly_stats.clear()

        time = (time + DELTA) % MOD

    if show_plot:
        plt.ioff()
        plt.show()


if __name__ == "__main__":
    main()
