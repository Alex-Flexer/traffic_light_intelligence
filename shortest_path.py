from typing import Iterable
import astar
from graph import Graph, Node, Edge


BOUND = 0.8


def find_path(graph: Graph, start: Node, goal: Node) -> Iterable[Node]:
    def get_neighbors(node: Node) -> Iterable[Node]:
        return [graph[idx] for idx in node.output_roads.keys()]

    def calc_avg_speed(edge: Edge) -> float:
        return (
            edge.speed_limit
            if edge.workload <= BOUND
            else (edge.workload - 1) * (-edge.speed_limit) / (1 - BOUND)
        )

    def calc_distance(a: Node, b: Node) -> float:
        edge = a.output_roads[b.idx]
        avg_speed = calc_avg_speed(edge)
        return edge.length / avg_speed

    return astar.find_path(start, goal,
                           neighbors_fnct=get_neighbors,
                           distance_between_fnct=calc_distance)
