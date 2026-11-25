from dsa.graph import Graph
from dsa.dijkstra import shortest_path


def test_dijkstra():
    graph = Graph()
    graph.add_edge('A', 'B', 2)
    graph.add_edge('B', 'C', 3)
    graph.add_edge('A', 'C', 10)
    path, distance = shortest_path(graph, 'A', 'C')
    assert path == ['A', 'B', 'C']
    assert distance == 5
