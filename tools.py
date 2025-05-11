from graph import Node, Edge


A = -1.04772
B = -0.70369
C = 1.09484
D = -0.360749
E = 1.01732

HOUR = 3600


def calc_bandwidth_road_factor(workload: float) -> float:
    return (
        A * workload**4 +
        B * workload**3 +
        C * workload**2 +
        D * workload + E
    )


def calc_avg_speed(edge: Edge) -> float:
    a = calc_bandwidth_road_factor(edge.workload)
    return a * edge.speed_limit


def calc_road_time(a: Node, b: Node) -> float:
    edge = a.output_roads[b.idx]
    avg_speed = calc_avg_speed(edge)
    return HOUR * (edge.length / 1000) / avg_speed
