from __future__ import annotations
from typing import Generator, Iterable
from datetime import timedelta

from numpy.random import choice


class Edge:
    _speed_limit: float
    _length: float
    _width: float
    _cars: int

    def __init__(self, speed_limit: float, length: float, width: float):
        self._speed_limit = speed_limit
        self._length = length
        self._width = width
        self._cars = 0

    @property
    def workload(self) -> float:
        return self.cars / self.volume

    @property
    def volume(self) -> float:
        return self._length * self._width

    @property
    def cars(self) -> int:
        return self._cars

    @property
    def speed_limit(self) -> float:
        return self._speed_limit

    @property
    def length(self) -> float:
        return self._length

    @property
    def width(self) -> float:
        return self._width

    def update_cars(self, new_cars: int) -> int:
        self._cars = min(self.volume, new_cars)
        return self._cars


class Node:
    idx: int
    output_roads: dict[int, Edge]
    input_nodes: list[int]

    def __init__(self, idx: int):
        self.output_roads: dict[int, Edge] = {}
        self.input_nodes: list[int] = []
        self.idx = idx

    def build_road(
        self,
        graph: list[Node],
        to: int,
        speed_limit: int,
        road_length: float,
        road_width: float
    ) -> None:
        if to in self.output_roads:
            raise ValueError(
                f"Road between nodes {self.idx} and {to} already exists.")

        self.output_roads[to] = Edge(speed_limit, road_length, road_width)
        graph[to].input_nodes.append(self.idx)

    def __getitem__(self, idx: int) -> Edge:
        return self.output_roads[idx]

    def __setitem__(self, idx: int, value: int) -> None:
        self.output_roads[idx].update_cars(value)

    def __iter__(self) -> Iterable[tuple[int, Edge]]:
        for idx, edge in self.output_roads.items():
            yield (idx, edge)


class Locality(Node):
    population: float
    emigration_factor: float
    popularity_factor: float

    def __init__(self, idx: int, population: float, emigration_factor, popularity_factor) -> None:
        super().__init__(idx)
        self.population = population
        self.emigration_factor = emigration_factor
        self.popularity_factor = popularity_factor


class StopLight:
    green_time: timedelta
    red_time: timedelta

    _future_red_time: timedelta
    _future_green_time: timedelta

    time_last_update: timedelta

    def __init__(self, green_time: int, red_time: int) -> None:
        self.time_last_update = timedelta(days=100000)

        self.green_time = timedelta(seconds=green_time)
        self.red_time = timedelta(seconds=red_time)

        self._future_green_time = timedelta()
        self._future_red_time = timedelta()

    def update_times(self, time: timedelta, new_green_time: int, new_red_time: int):
        full_cycle = (self.green_time + self.red_time).seconds

        self._future_green_time = timedelta(seconds=new_green_time)
        self._future_red_time = timedelta(seconds=new_red_time)

        self.time_last_update = timedelta(seconds=(time.seconds + full_cycle) // full_cycle * full_cycle)
        # print((time + full_cycle).seconds, type(full_cycle))

    def is_green(self, time: timedelta) -> bool:
        if (time >= self.time_last_update
            and self._future_green_time != self.green_time
            and self._future_red_time != self.red_time):

            self.green_time = self._future_green_time
            self.red_time = self._future_red_time

        return (time - self.time_last_update) % (self.green_time + self.red_time) < self.green_time


class Junction(Node):
    bandwidth: int
    out_stoplight: StopLight | None
    stoplights: dict[int, StopLight]
    dependencies: dict[int, list[int]]

    def __init__(
        self,
        idx: int,
        bandwidth: int,
        out_stoplight: tuple[int],
        stoplights: dict[int, tuple[int]],
        dependencies: dict[int, list[int]] = []
    ) -> None:

        super().__init__(idx)
        self.bandwidth = bandwidth
        self.out_stoplight = StopLight(*out_stoplight)
        self.stoplights: dict[int, StopLight] = {
            node_idx: StopLight(*args)
            for node_idx, args in stoplights.items()
        }
        self.dependencies = dependencies


class Car:
    from_node_idx: int
    dest_node_idx: int
    cur_node_idx: int | None
    cur_edge: Edge | None
    cur_path: list[Node]

    def __init__(self, from_node: int, dest_node: int, path: list[Node] = []):
        self.from_node_idx = from_node
        self.dest_node_idx = dest_node
        self.cur_node_idx = from_node
        self.cur_edge: Edge | None = None
        self.cur_path = path


class Graph:
    _graph: list[Node]

    def __init__(self, nodes: list[tuple], edges: list[tuple]) -> None:
        """
        nodes[i][0] = type: str
        types:
            "junction": (
                [0]bandwidth: int
                [1]out-stoplight: (green-time: int, red-time: int),
                [2]in-stoplights: {node-idx: (green-time: int, red-time: int)}
            )
            "locality": (
                [0]population: int,
                [1]emigration-factor: float,
                [2]popularity-factor: float
            )
        edges[i] = (
            [0]from: int,
            [1]to: int,
            [2]speed-limit: int
            [3]length: float,
            [4]width: float
        )
        """
        self._graph = []
        for idx, node_args in enumerate(nodes):
            class_type: Locality | Junction = 0

            if node_args[0] == "locality":
                class_type = Locality
            elif node_args[0] == "junction":
                class_type = Junction

            if not class_type:
                raise ValueError("Unknown type of node.")

            self._graph.append(class_type(idx, *node_args[1:]))

        for edge in edges:
            self._graph[edge[0]].build_road(self._graph, *edge[1:])

    @property
    def nodes(self) -> list[Node]:
        return self._graph

    @property
    def edges(self) -> list[Edge]:
        return sum([[edge for _, edge in node] for node in self.nodes], start=[])

    def __getitem__(self, idx: int) -> Node:
        return self._graph[idx]

    def __iter__(self) -> Iterable[Node]:
        for node in self.nodes:
            yield node

    def __str__(self) -> str:
        res = ""
        for node in self._graph:
            for adj_idx, edge in node:
                res += f"({id(edge)}) {node.idx} --> {adj_idx}: {edge.cars}\n"
        return res


class CarsFactory:
    _graph: Graph
    _popularity_factors: list[tuple[int, float]]

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

        self._popularity_factors = sorted(
            [
                (node.idx, node.popularity_factor)
                for node in self._graph.nodes
                if isinstance(node, Locality)
            ]
        )

    def generate_cars(self, node_idx: int, amount: int) -> Generator[Car, None, None]:
        from shortest_path import find_path

        idxs, factors = zip(*self._popularity_factors)
        res = []

        for _ in range(amount):
            chosen_idx = choice(idxs, p=factors)
            path = find_path(self._graph, node_idx, chosen_idx)
            res.append(Car(node_idx, chosen_idx, path))

        return res
