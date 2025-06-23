class Node():
    """
    Node class represents a state in the search tree.
    Stores the state, parent node, action taken, and cost values.
    """
    def __init__(self, state, parent, action, score_g=0, score_h=0):
        self.state = state          # The current state (position in the maze)
        self.parent = parent        # Reference to the parent Node
        self.action = action        # Action taken to reach this node
        self.score_g = score_g      # Cost from start node to this node
        self.score_h = score_h      # Heuristic cost to the goal
        self.score_f = score_g + score_h  # Total cost (for A* and similar algorithms)

    def __lt__(self, other):
        # Less-than comparison based on total cost (used for sorting in priority queues)
        return self.score_f < other.score_f