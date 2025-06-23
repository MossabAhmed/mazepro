from node import Node

class StackFrontier():
    """
    Frontier class for DFS (LIFO stack).
    """
    def __init__(self):
        self.frontier = []

    def add(self, node):
        # Add a node to the stack
        self.frontier.append(node)

    def contains_state(self, state):
        # Check if a given state is already in the frontier
        return any(node.state == state for node in self.frontier)

    def empty(self):
        # Return True if the frontier is empty
        return len(self.frontier) == 0

    def remove(self):
        # Remove and return the last node (LIFO)
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):
    """
    Frontier class for BFS (FIFO queue).
    Inherits from StackFrontier but overrides remove method.
    """
    def remove(self):
        # Remove and return the first node (FIFO)
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node


class PriorityQueueFrontierforUniformCost(QueueFrontier):
    """
    Frontier for Uniform Cost Search.
    Nodes are sorted by path cost (score_g).
    """
    def add(self, node):
        self.frontier.append(node)
        self.frontier.sort(key=lambda n: n.score_g)  # Sort by score_g


class PriorityQueueFrontierforGreedy(QueueFrontier):
    """
    Frontier for Greedy Best-First Search.
    Nodes are sorted by heuristic value (score_h).
    """
    def add(self, node):
        self.frontier.append(node)
        self.frontier.sort(key=lambda n: n.score_h)  # Sort by heuristic


class PriorityQueueFrontierforAStar(QueueFrontier):
    """
    Frontier for A* Search.
    Nodes are sorted by f(n) = g(n) + h(n).
    """
    def add(self, node):
        self.frontier.append(node)
        self.frontier.sort(key=lambda n: n.score_f)  # Sort by f(n) = g(n) + h(n)