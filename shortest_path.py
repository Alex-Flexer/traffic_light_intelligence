from typing import Iterable
import astar
from graph import Graph, Node, Edge


A = -1.04772
B = -0.70369
C = 1.09484
D = 0.360749
E = 1.00674


def find_path(graph: Graph, start_idx: int, goal_idx: int) -> Iterable[Node]:
    def get_neighbors(node: Node) -> Iterable[Node]:
        return [graph[idx] for idx in node.output_roads.keys()]

    def calc_bandwidth_road_factor(workload: float) -> float:
        return (
            A * workload**4 +
            B * workload**3 +
            C * workload**2 +
            D * workload + E
        )

    def calc_avg_speed(edge: Edge) -> float:
        return calc_bandwidth_road_factor(edge.workload) * edge.speed_limit

    def calc_distance(a: Node, b: Node) -> float:
        edge = a.output_roads[b.idx]
        avg_speed = calc_avg_speed(edge)
        return edge.length / avg_speed

    start, goal = graph[start_idx], graph[goal_idx]

    return astar.find_path(start, goal,
                           neighbors_fnct=get_neighbors,
                           distance_between_fnct=calc_distance)
