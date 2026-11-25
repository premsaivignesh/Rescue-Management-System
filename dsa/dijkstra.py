import heapq


def dijkstra(graph, source):
    """Return shortest distances and predecessor map for a Graph."""
    distances = {node: float('inf') for node in graph.nodes()}
    previous = {node: None for node in graph.nodes()}
    distances[source] = 0.0
    heap = [(0.0, source)]

    while heap:
        distance, node = heapq.heappop(heap)
        if distance != distances[node]:
            continue
        for neighbor, weight in graph.neighbors(node):
            candidate = distance + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = node
                heapq.heappush(heap, (candidate, neighbor))
    return distances, previous


def shortest_path(graph, source, destination):
    distances, previous = dijkstra(graph, source)
    if destination not in distances or distances[destination] == float('inf'):
        return [], float('inf')
    path = []
    node = destination
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()
    return path, distances[destination]
