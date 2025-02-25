from __future__ import annotations


class Edge:
    _length: float
    _width: float
    _cars: float

    def __init__(self, length: float, width: float, cars: int = 0):
        self._length = length
        self._width = width
        self._cars = cars

    @property
    def workload(self) -> float:
        return self.cars / (self._length * self._width)

    @property
    def cars(self) -> float:
        return self._cars

    def update_cars(self, new_cars: int) -> None:
        self._cars = min(self._length * self._width, new_cars)


class Node:
    idx: int
    is_light: bool
    output_roads: dict[int, Edge] = {}
    adjacent_nodes: list[int] = []
    throughput_capacity: float

    def __init__(self, idx: int, is_light: bool, throughput_capacity: float):
        self.idx = idx
        self.is_light = is_light
        self.throughput_capacity = throughput_capacity

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
        graph[to].adjacent_nodes.append(self.idx)

    def __getitem__(self, idx: int) -> Edge:
        return self.output_roads[idx]


class Graph:
    _graph: list[Node]

    def __init__(self, nodes: list[tuple], edges: list[tuple]) -> None:
        """
        nodes[i] = (is-light: bool, throughput_capacity: float)
        edges[i] = (from: int, to: int, length: float, width: float, cars: int)
        """
        self._graph: list[Node] = [Node(idx, *node)
                                   for idx, node in enumerate(nodes)]
        for edge in edges:
            self._graph[edge[0]].build_road(self._graph, *edge[1:])

    def __getitem__(self, idx: int) -> Node:
        return self._graph[idx]
