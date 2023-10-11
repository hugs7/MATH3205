import heapq

# Dijkstra's Algorithm
def ShortestPaths(nodes, arcs, inarcs, outarcs, resources, ignitions, delay):
    
    # Weighted graph encoding
    graph = {u: {v: arcs[u, v] + (delay * int(u in resources))
        for (u, v) in outarcs[u]} for u in nodes}
    
    # Distances
    arrival_time = {n: float("inf") for n in nodes}

    # FirePaths
    fire_path = {n: None for n in nodes}

    # Ignitions
    for n in ignitions:
        arrival_time[n] = 0
        fire_path[n] = []

    # Predecessors
    pred = {n: None for n in nodes}

    # Priority queue
    queue = [(0, n) for n in ignitions]

    # Dijkstra
    while len(queue) > 0:
        current_dist, current_nodes = heapq.heappop(queue)
        if current_dist > arrival_time[current_nodes]:
            continue

        for neigh, length in graph[current_nodes].items():
            dist = current_dist + length
            if dist < arrival_time[neigh]:
                arrival_time[neigh] = dist
                fire_path[neigh] = fire_path[current_nodes] + [neigh]
                pred[neigh] = current_nodes
                heapq.heappush(queue, (dist, neigh))

    # Return distances and predecessors
    return arrival_time, fire_path, pred


