def avg_work_load(graph) -> float:
    edges = graph.edges
    return sum(map(lambda x: x.workload, graph.edges)) / len(edges)
