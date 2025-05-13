from datetime import timedelta

import networkx as nx
import matplotlib.pyplot as plt
from meter import calculate_hourly_averages
from graph import Graph

HOUR = 3600
MINUTE = 60

node_positions = None


def show(g: Graph, time: timedelta) -> None:
    global node_positions

    G = nx.DiGraph()

    for node in g.nodes:
        G.add_node(node.idx)

    edge_labels = {}
    edge_colors = {}
    for node in g.nodes:
        for to_node, edge in node:
            G.add_edge(node.idx, to_node)
            workload_percentage = round(edge.workload * 100, 1)
            edge_labels[(node.idx, to_node)] = f"{workload_percentage}"

            edge_colors[(node.idx, to_node)] = workload_percentage / 100

    if node_positions is None:
        node_positions = nx.spring_layout(G, k=1, iterations=50)

    plt.clf()
    plt.figure(1, figsize=(20, 10))

    nx.draw_networkx_nodes(G, node_positions, node_color='lightblue', node_size=500)
    nx.draw_networkx_labels(G, node_positions)

    for edge in G.edges():
        color = edge_colors[edge]
        params = {
            "edgelist": [edge],
            "edge_color": (color, 0.3, 0),
            "arrows": True
        }

        if (edge[1], edge[0]) in G.edges():
            params["connectionstyle"] = "arc3,rad=0.3"

        nx.draw_networkx_edges(G, node_positions, **params)

    for edge, label in edge_labels.items():
        color = edge_colors[edge]
        x1, y1 = node_positions[edge[0]]
        x2, y2 = node_positions[edge[1]]
        if (edge[1], edge[0]) in G.edges():
            x = (x1 + x2) / 2 + (y2 - y1) / 4
            y = (y1 + y2) / 2 - (x2 - x1) / 4
        else:
            x = (x1 + x2) / 2
            y = (y1 + y2) / 2
        plt.text(x, y, label, ha='center', va='center', color=(color, 0.3, 0))

    hours = str(time.seconds // HOUR).rjust(2, '0')
    minutes = str(time.seconds % HOUR // 60).rjust(2, '0')
    seconds = str(time.seconds % HOUR % MINUTE).rjust(2, '0')

    plt.title(f"{hours}:{minutes}:{seconds}")
    plt.axis('off')
    plt.pause(0.01)
    plt.show(block=False)


def plot_hourly_data(data_sets: list[dict]) -> None:
    plt.figure(figsize=(12, 6))
    for dataset in data_sets:
        plt.plot(
            range(24),
            dataset['averages'], 
            marker='o',
            linestyle='-', 
            color=dataset.get('color', None),
            label=dataset.get('label', 'Unknown')
        )

    plt.title('Comparison of Hourly Averages')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Workload (×10⁴)')
    plt.xticks(range(24))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xlim(0, 23)
    plt.legend()
    plt.show()


def get_data_sets(
        filepaths: list[str],
        labels: list[str] | None = None,
        colors: list[str] | None = None
    ) -> list[dict[str, str | int]]:
    if labels is None:
        labels = [f"Dataset {i+1}" for i in range(len(filepaths))]

    if colors is None:
        colors = [None] * len(filepaths)
    
    data_sets = []
    for filepath, label, color in zip(filepaths, labels, colors):
        averages = calculate_hourly_averages(filepath)
        data_sets.append({
            'averages': averages,
            'label': label,
            'color': color
        })

    return data_sets


def analyze_and_plot(
        filepaths: list[str],
        labels: list[str] | None = None,
        colors: list[str] | None = None
    ) -> None:

    data_sets = get_data_sets(filepaths, labels, colors)
    plot_hourly_data(data_sets)


def calc_diff_on_peak_hours(*args, filepaths: str) -> list[float]:
    for a in args:
        if not isinstance(a, int):
            raise TypeError("Arguments values must be integers")
        if a > 23 or a < 0:
            raise ValueError("Arguments values must be between 0 and 23")

    mins = [float("inf")] * 24
    maxes = [-float("inf")] * 24

    for filepath in filepaths:
        averages = calculate_hourly_averages(filepath)
        for idx in args:
            mins[idx] = min(mins[idx], averages[idx])
            maxes[idx] = max(maxes[idx], averages[idx])
    
    return [round((1 - mins[i] / maxes[i]) * 100, 1) for i in args] 


if __name__ == "__main__":
    print(calc_diff_on_peak_hours(
        9, 18,
        filepaths=[
            'stat\hourly_factors_default.csv',
            'stat\hourly_factors_optimized.csv']
        )
    )

    analyze_and_plot(
        filepaths=['stat\hourly_factors_default.csv', 'stat\hourly_factors_optimized.csv'],
        labels=['Default', 'Optimized'],
        colors=['blue', 'orange']
    )
