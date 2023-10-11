import networkx as nx
import matplotlib.pyplot as plt


def PlotPaths(pos, arrival_time, pred, solution, ignitions, target, plotsize):
    plt.figure(figsize=(plotsize, plotsize), dpi=400)
    plt.axis("off")

    nodes = pos.keys()
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    for n in pred:
        if pred[n] is not None:
            graph.add_edge(pred[n], n)

    drawedges = nx.draw_networkx_edges(graph, pos)

    drawall = nx.draw_networkx_nodes(graph, pos, node_color="white")
    drawall.set_edgecolor("k")

    nodelabels = nx.draw_networkx_labels(
        graph, pos, {n: arrival_time[n] for n in nodes}, font_size=8
    )
    # nodelabels = nx.draw_networkx_labels(graph, pos, {n: n for n in nodes}, font_size=8)

    burns = [
        n
        for n in nodes
        if arrival_time[n] < target and n not in solution and n not in ignitions
    ]
    burnsres = [n for n in nodes if arrival_time[n] < target and n in solution]
    safe = [n for n in nodes if arrival_time[n] >= target and n not in solution]
    saferes = [n for n in nodes if arrival_time[n] >= target and n in solution]

    drawignitions = nx.draw_networkx_nodes(
        graph, pos, nodelist=ignitions, node_color="thistle"
    )
    drawburns = nx.draw_networkx_nodes(
        graph, pos, nodelist=burns, node_color="orangered"
    )
    drawburnsres = nx.draw_networkx_nodes(
        graph, pos, nodelist=burnsres, node_color="firebrick"
    )
    drawsafe = nx.draw_networkx_nodes(
        graph, pos, nodelist=safe, node_color="forestgreen"
    )
    drawsaferes = nx.draw_networkx_nodes(
        graph, pos, nodelist=saferes, node_color="green"
    )

    drawburns.set_edgecolor("k")
    drawburnsres.set_edgecolor("k")
    drawignitions.set_edgecolor("k")
    drawsafe.set_edgecolor("k")
