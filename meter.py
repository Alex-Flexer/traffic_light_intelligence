import csv


def avg_work_load(graph) -> float:
    edges = graph.edges
    return sum(map(lambda x: x.workload, graph.edges)) / len(edges)


def calculate_hourly_averages(filepath: str) -> list[float]:
    hourly_sums = [0.0] * 24
    hourly_count = 0

    with open(filepath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) != 24:
                continue
            
            for hour in range(24):
                value = float(row[hour])
                hourly_sums[hour] += value
                hourly_count += 1
    
    return [
        hourly_sums[i] / hourly_count if hourly_count > 0 else 0 
        for i in range(24)
    ]
