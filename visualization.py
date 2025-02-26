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
    for node in g.nodes:
        for to_node, edge in node:
            G.add_edge(node.idx, to_node)
            edge_labels[(node.idx, to_node)] = f"{round(edge.workload * 100, 1)}%"

    if node_positions is None:
        node_positions = nx.spring_layout(G, k=1, iterations=50) # Fruchterman-Reingold

    plt.clf()
    plt.figure(1, figsize=(20, 10))

    nx.draw_networkx_nodes(G, node_positions, node_color='lightblue', node_size=500)
    nx.draw_networkx_labels(G, node_positions)

    for edge in G.edges():
        if (edge[1], edge[0]) in G.edges():
            if edge[0] < edge[1]:
                nx.draw_networkx_edges(G, node_positions, edgelist=[edge],
                                       connectionstyle=f"arc3,rad=0.3", # изгиб
                                       edge_color='blue',
                                       arrows=True)
            else:
                nx.draw_networkx_edges(G, node_positions, edgelist=[edge],
                                       connectionstyle=f"arc3,rad=0.3",
                                       edge_color='red',
                                       arrows=True)
        else:
            nx.draw_networkx_edges(G, node_positions, edgelist=[edge],
                                   arrows=True)

    curved_edges = [(u, v) for (u, v) in G.edges() if (v, u) in G.edges()]
    straight_edges = [(u, v) for (u, v) in G.edges() if (v, u) not in G.edges()]
    curved_edge_labels = {edge: edge_labels[edge] for edge in curved_edges}
    straight_edge_labels = {edge: edge_labels[edge] for edge in straight_edges}

    nx.draw_networkx_edge_labels(G, node_positions, edge_labels=straight_edge_labels)
    nx.draw_networkx_edge_labels(G, node_positions, edge_labels=curved_edge_labels,
                                 label_pos=0.3)

    plt.title("Traffic Light Intelligence")
    plt.axis('off')
    plt.pause(0.01)
    plt.show(block=False)
