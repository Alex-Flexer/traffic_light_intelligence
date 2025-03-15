from __future__ import annotations
from typing import Generator, Iterable

from numpy.random import choice


class Edge:
    _speed_limit: float
    _length: float
    _width: float
    _cars: float

    def __init__(self, speed_limit: float, length: float, width: float, cars: int = 0):
        self._speed_limit = speed_limit
        self._length = length
        self._width = width
        self._cars = cars

    @property
    def workload(self) -> float:
        return self.cars / self.volume

    @property
    def volume(self) -> float:
        return self._length * self._width

    @property
    def cars(self) -> float:
        return self._cars

    @property
    def speed_limit(self) -> float:
        return self._speed_limit

    @property
    def length(self) -> float:
        return self._length

    @property
    def width(self) -> float:
        return self.width

    def update_cars(self, new_cars: int) -> int:
        self._cars = min(self._length * self._width, new_cars)
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
        road_length: float,
        road_width: float,
        road_cars: float = 0.0
    ) -> None:
        if to in self.output_roads:
            raise ValueError(
                f"Road between nodes {self.idx} and {to} already exists.")

        self.output_roads[to] = Edge(road_length, road_width, road_cars)
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
    # tp = in | out
    tp: str
    green_time: int
    red_time: int

    def __init__(self, tp: str, green_time: int, red_time: int) -> None:
        self.tp = tp
        self.green_time = green_time
        self.red_time = red_time


class Junction(Node):
    bandwidth: float
    stoplights: dict[int, StopLight]

    def __init__(self, idx: int, bandwidth: float, stoplights: dict[int, tuple[int]]):
        super().__init__(idx)
        self.bandwidth = bandwidth
        self.stoplights = {
            road_idx: StopLight(*args)
            for road_idx, args in stoplights
        }


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
        self.cur_edge = None
        self.cur_node_idx = path


class Graph:
    _graph: list[Node]

    def __init__(self, nodes: list[tuple], edges: list[tuple]) -> None:
        """
        nodes[i][0] = type: str\n
        types:
            "junction": {node-idx: (green-time: int, red-time: int, type: str = "in" | "out")}
            "locality": (population: float, emigration-factor: float, popularity-factor: float)
        edges[i] = (from: int, to: int, length: float, width: float, cars: int)
        """
        for idx, node_args in enumerate(nodes):
            class_type =\
                Junction if node_args[0] == "junction"\
                else (Locality if node_args[0] == "locality" else 0)

            if not class_type:
                raise ValueError("Unknown type of node.")

            self._graph.append(class_type(idx, *node_args))

        for edge in edges:
            self._graph[edge[0]].build_road(self._graph, *edge[1:])

    @property
    def nodes(self) -> list[Node]:
        return self._graph

    @property
    def edges(self) -> list[Edge]:
        return sum([edge for _, edge in node] for node in self.nodes)

    def __getitem__(self, idx: int) -> Node:
        return self._graph[idx]

    def __iter__(self) -> Iterable[Node]:
        for node in self.nodes:
            yield node

    def __str__(self) -> str:
        res = ""
        for node in self._graph:
            for adj_idx, edge in node:
                res += f"{node.idx} --> {adj_idx}: {round(edge.workload * 100, 3)}%\n"
        return res


class CarsFactory:
    _graph: Graph
    _popularity_factors: list[tuple[int, float]]

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

        self._popularity_factors = sorted([
            (node.idx, node.popularity_factor)
            for node in self._graph.nodes
            if isinstance(node, Locality)
        ], key=lambda item: item[0])

    def generate_cars(self, node_idx: int, amount: int) -> Generator[Car, None, None]:
        from shortest_path import find_path

        idxs, factors = zip(*self._popularity_factors)

        for _ in range(amount):
            chosen_idx = choice(idxs, factors)
            path = find_path(self._graph, node_idx, chosen_idx)
            yield Car(node_idx, chosen_idx, path)
