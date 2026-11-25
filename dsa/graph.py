class Graph:
    """Weighted adjacency-list graph used by the emergency routing module."""

    def __init__(self):
        self.adjacency = {}

    def add_node(self, node):
        self.adjacency.setdefault(node, [])

    def add_edge(self, source, destination, weight, bidirectional=True):
        self.add_node(source)
        self.add_node(destination)
        self.adjacency[source].append((destination, float(weight)))
        if bidirectional:
            self.adjacency[destination].append((source, float(weight)))

    def neighbors(self, node):
        return self.adjacency.get(node, [])

    def nodes(self):
        return list(self.adjacency.keys())
