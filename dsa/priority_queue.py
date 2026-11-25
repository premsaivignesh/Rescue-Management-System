class PriorityNode:

    def __init__(self, incident):
        self.incident = incident


class PriorityQueue:

    def __init__(self):
        self.heap = []

    def parent(self, index):
        return (index - 1) // 2

    def left(self, index):
        return 2 * index + 1

    def right(self, index):
        return 2 * index + 2

    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

# ========================================
# COMPARE PRIORITY
# ========================================

    def is_higher_priority(self, node1, node2):

        priority1 = node1.incident[16]
        priority2 = node2.incident[16]

        if priority1 > priority2:
            return True

        if priority1 < priority2:
            return False

        # If priority is same, older report comes first
        return node1.incident[18] < node2.incident[18]

# ========================================
# INSERT
# ========================================

    def insert(self, incident):

        node = PriorityNode(incident)
        self.heap.append(node)
        self.heapify_up(len(self.heap) - 1)

# ========================================
# HEAPIFY UP
# ========================================

    def heapify_up(self, index):

        while index > 0:

            parent = self.parent(index)

            if self.is_higher_priority(self.heap[index], self.heap[parent]):
                self.swap(index, parent)
                index = parent
            else:
                break

# ========================================
# PEEK
# ========================================

    def peek(self):

        if self.is_empty():
            return None

        return self.heap[0].incident

# ========================================
# GET MAX
# ========================================

    def get_max(self):
        return self.peek()

# ========================================
# EXTRACT MAX
# ========================================

    def extract_max(self):

        if self.is_empty():
            return None

        maximum = self.heap[0]
        last = self.heap.pop()

        if not self.is_empty():
            self.heap[0] = last
            self.heapify_down(0)

        return maximum.incident

# ========================================
# HEAPIFY DOWN
# ========================================

    def heapify_down(self, index):

        size = len(self.heap)

        while True:

            largest = index
            left = self.left(index)
            right = self.right(index)

            if left < size and self.is_higher_priority(self.heap[left], self.heap[largest]):
                largest = left

            if right < size and self.is_higher_priority(self.heap[right], self.heap[largest]):
                largest = right

            if largest == index:
                break

            self.swap(index, largest)
            index = largest

# ========================================
# SIZE
# ========================================

    def size(self):
        return len(self.heap)

# ========================================
# IS EMPTY
# ========================================

    def is_empty(self):
        return len(self.heap) == 0

# ========================================
# CLEAR
# ========================================

    def clear(self):
        self.heap.clear()