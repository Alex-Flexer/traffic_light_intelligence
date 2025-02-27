import networkx as nx
import matplotlib.pyplot as plt
from graph import Graph

node_positions = None


def show(g: Graph) -> None:
    global node_positions
    print(g)

    G = nx.DiGraph()

    for node in g.nodes:
        G.add_node(node.idx)

    edge_labels = {}
    edge_colors = {}
    for node in g.nodes:
        for to_node, edge in node:
            G.add_edge(node.idx, to_node)
            workload_percentage = round(edge.workload * 100, 1)
            edge_labels[(node.idx, to_node)] = f"{workload_percentage}%"

            edge_colors[(node.idx, to_node)] = workload_percentage / 100

    if node_positions is None:
        node_positions = nx.spring_layout(G, k=1, iterations=50) # Fruchterman-Reingold

    plt.clf()
    plt.figure(1, figsize=(20, 10))

    nx.draw_networkx_nodes(G, node_positions, node_color='lightblue', node_size=500)
    nx.draw_networkx_labels(G, node_positions)

    for edge in G.edges():
        color = edge_colors[edge]
        if (edge[1], edge[0]) in G.edges():
            if edge[0] < edge[1]:
                nx.draw_networkx_edges(G, node_positions, edgelist=[edge],
                                       connectionstyle=f"arc3,rad=0.3", # изгиб
                                       edge_color=(color, 0.3, 0),
                                       arrows=True)
            else:
                nx.draw_networkx_edges(G, node_positions, edgelist=[edge],
                                       connectionstyle=f"arc3,rad=0.3",
                                       edge_color=(color, 0.3, 0),
                                       arrows=True)
        else:
            nx.draw_networkx_edges(G, node_positions, edgelist=[edge],
                                   edge_color=(color, 0.3, 0),
                                   arrows=True)

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

    plt.title("Traffic Light Intelligence")
    plt.axis('off')
    plt.pause(0.01)
    plt.show(block=False)
