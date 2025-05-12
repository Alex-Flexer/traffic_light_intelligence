from graph import Graph, Locality, Node, Junction, StopLight
import math
from collections import deque
from collections.abc import MutableSequence


def optimize_graph(graph: Graph) -> None:
    '''
    Function optimizes stoplights time-intervals based on road traffic
    '''
    visited = set()
    queue: MutableSequence[Node] = deque()

    localities = [node for node in graph.nodes if isinstance(node, Locality)]
    queue.extend(localities)

    visited.update(localities)

    while queue:
        current_node = queue.popleft()

        for adj_idx, _ in current_node:
            if adj_idx not in visited:
                visited.add(adj_idx)
                queue.append(graph[adj_idx])

        if isinstance(current_node, Locality):
            for adj_idx, _ in current_node:
                if adj_idx not in visited:
                    visited.add(adj_idx)
                    queue.append(graph[adj_idx])
            continue

        current_node: Junction = current_node

        weights = {}
        total_weight = 0

        for node_idx, road in current_node.output_roads.items():
            weight = road.workload
            weights[node_idx] = weight
            total_weight += weight

        if not weights or total_weight == 0:
            continue

        stoplights = current_node.stoplights
        if not stoplights:
            continue

        for node_idx, stoplight in stoplights.items():
            if node_idx not in weights:
                print(node_idx)
                continue

            current_cycle = stoplight.green_time.seconds + stoplight.red_time.seconds
            if len(weights) == 1:
                g_new = current_cycle
            else:
                g_new = current_cycle * weights[node_idx] // total_weight

            ideal_red = current_cycle - g_new

            r_new = find_non_overlapping_red_time(stoplight, g_new, ideal_red)

            if node_idx == 5:
                print(stoplight.green_time, stoplight.red_time)
                print(g_new, ideal_red, r_new)

            if r_new:
                current_node.update_stoplight_times(
                    stoplight.time_last_update,
                    g_new,
                    r_new,
                    node_idx
                )


def find_non_overlapping_red_time(stoplight: StopLight, g_new: int, ideal_red: int) -> int | None:
    min_red = ideal_red * 0.85
    max_red = ideal_red * 1.15

    temp_stoplight = StopLight(g_new, ideal_red)
    temp_stoplight.initial_light = stoplight.initial_light

    if temp_stoplight.is_compatible(stoplight):
        return ideal_red

    best_red = None
    min_diff = float('inf')

    for red in range(int(min_red), int(max_red) + 1):
        temp_stoplight = StopLight(g_new, red)
        temp_stoplight.initial_light = stoplight.initial_light

        if temp_stoplight.is_compatible(stoplight):
            diff = abs(red - ideal_red)

            if diff < min_diff:
                min_diff = diff
                best_red = red

    return best_red
