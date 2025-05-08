from graph import Graph, Locality, Node, Junction
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
                continue

            current_cycle = stoplight.green_time.seconds + stoplight.red_time.seconds
            if len(weights) == 1:
                g_new = current_cycle
            else:
                g_new = current_cycle * weights[node_idx] // total_weight

            ideal_red = current_cycle - g_new

            r_new = find_non_overlapping_red_time(stoplight, g_new, ideal_red)

            if r_new:
                current_node.update_stoplight_times(
                    stoplight.time_last_update,
                    g_new,
                    r_new,
                    node_idx
                )


def find_non_overlapping_red_time(tl1, G2, ideal_red) -> int | None:
    G1 = tl1.green_time.seconds
    R1 = tl1.red_time.seconds
    T1 = G1 + R1

    prev_r2 = None

    if T1 == 0:
        return None

    k_min = math.floor(G2 / T1) + 1
    k_max = k_min + T1

    for k in range(k_min, k_max + 1):
        candidate_r2 = k * T1 - G2
        if ideal_red <= candidate_r2:
            if prev_r2 is None:
                return candidate_r2
            else:
                return prev_r2 if abs(ideal_red - prev_r2) < abs(ideal_red - candidate_r2) else candidate_r2
        else:
            prev_r2 = candidate_r2

    return prev_r2 if prev_r2 > 0 else None
