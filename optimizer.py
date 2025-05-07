from graph import Graph, StopLight
from tools import calc_avg_speed
import math
from collections import deque


def optimize_graph(graph: Graph) -> None:
    '''
    Function optimizes stoplights time-intervals based on road traffic
    '''
    visited = set()
    queue = deque()

    queue.append(graph[0])
    visited.add(0)

    while queue:
        current_node = queue.popleft()

        if not hasattr(current_node, 'stoplights'):
            for adj_idx, _ in current_node:
                if adj_idx not in visited:
                    visited.add(adj_idx)
                    queue.append(graph[adj_idx])
            continue

        stoplights = current_node.stoplights
        if not stoplights:
            continue

        for node_idx, stoplight in stoplights.items():
            weights = []
            total_weight = 0

            for input_idx in current_node.input_nodes:
                if input_idx in graph[input_idx].output_roads:
                    edge = graph[input_idx].output_roads[current_node.idx]
                    weight = edge.workload
                    weights.append(weight)
                    total_weight += weight

            if not weights:
                continue

            current_cycle = stoplight.green_time.seconds + stoplight.red_time.seconds
            if len(weights) == 1:
                g_new = current_cycle
            else:
                g_new = int(current_cycle * weights[0] / total_weight)

            ideal_red = current_cycle - g_new

            possible_red_times = find_non_overlapping_red_time(stoplight, g_new, ideal_red)

            if possible_red_times:
                r_new = possible_red_times[-1]

                current_node.update_stoplight_times(
                    stoplight.time_last_update,
                    g_new,
                    r_new,
                    node_idx
                )

        for adj_idx, _ in current_node:
            if adj_idx not in visited:
                visited.add(adj_idx)
                queue.append(graph[adj_idx])


def find_non_overlapping_red_time(tl1, G2, ideal_red):
    """
    Находит все возможные R₂, при которых зелёные фазы не пересекаются.

    Параметры:
    - tl1: первый светофор (имеет поля green_time и red_time, начинает с зелёного)
    - G2: длительность зелёного сигнала второго светофора

    Возвращает:
    - Список возможных R₂ (красное время второго светофора)
    """
    G1 = tl1.green_time
    R1 = tl1.red_time
    T1 = G1 + R1

    possible_R2 = []

    if T1 == 0:
        return []  # Некорректные данные

    k_min = math.floor(G2 / T1) + 1
    k_max = k_min + T1  # Проверяем T₁ уникальных вариантов

    for k in range(k_min, k_max + 1):
        R2_candidate = k * T1 - G2
        if ideal_red < R2_candidate:
            break
        else:
            if R2_candidate > 0:
                possible_R2.append(R2_candidate)

    return possible_R2
