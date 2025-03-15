from typing import Iterable
import astar
from graph import Graph, Node, Edge


def find_path(graph: Graph, start: Node, goal: Node) -> Iterable[Node]:
    def get_neighbors(node: Node) -> Iterable[Node]:
        return [graph[idx] for idx, _ in node.output_roads]

    def calc_road_weight(edge: Edge) -> float:
        return edge.workload

    def calc_distance(a: Node, b: Node) -> float:
        return calc_road_weight(a.output_roads[b.idx])

    return astar.find_path(start, goal,
                           neighbors_fnct=get_neighbors,
                           distance_between_fnct=calc_distance)
