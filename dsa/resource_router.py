"""Emergency resource routing using Graph + Dijkstra.

The router works with real resource coordinates when they are available. It intentionally
returns no route when coordinates are missing rather than inventing a location.
"""
import math
from dsa.graph import Graph
from dsa.dijkstra import shortest_path


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def build_resource_graph(resources):
    graph = Graph()
    valid = []
    for resource in resources:
        # resource tuple: id, name, type, latitude, longitude, availability
        if resource[3] is None or resource[4] is None:
            continue
        if float(resource[3]) == 0 and float(resource[4]) == 0:
            continue
        valid.append(resource)
        graph.add_node(resource[0])

    for i, a in enumerate(valid):
        for b in valid[i + 1:]:
            distance = haversine_km(float(a[3]), float(a[4]), float(b[3]), float(b[4]))
            graph.add_edge(a[0], b[0], distance)
    return graph


def shortest_resource_path(resources, source_id, destination_id):
    graph = build_resource_graph(resources)
    return shortest_path(graph, source_id, destination_id)
