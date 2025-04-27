from typing import Iterable
import astar
from tools import calc_road_time
from graph import Graph, Node




def find_path(graph: Graph, start_idx: int, goal_idx: int) -> Iterable[Node]:
    def get_neighbors(node: Node) -> Iterable[Node]:
        return [graph[idx] for idx in node.output_roads.keys()]

    start, goal = graph[start_idx], graph[goal_idx]

    return list(astar.find_path(
        start, goal,
        neighbors_fnct=get_neighbors,
        distance_between_fnct=calc_road_time)
    )[1:]
