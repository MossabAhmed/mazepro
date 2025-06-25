from PIL import Image, ImageDraw, ImageTk
import imageio
from node import Node
import random

class Maze():
    def __init__(self, filename=None, width=None, height=None):
        # Initialize maze state and statistics
        self.solution = None      # To store the solution path
        self.co_path = 0          # To count the solution steps
        self.frames = []          # For GIF frames
        self.num_explored = 0     # To count explored states
        self.explored = set()     # To keep track of explored nodes

        if filename:
            # Load maze from file
            with open(filename) as f:
                contents = f.read()

            contents = contents.splitlines()
            self.height = len(contents)
            self.width = max(len(line) for line in contents)

            self.walls = []
            for i in range(self.height):
                row = []
                for j in range(self.width):
                    try:
                        if contents[i][j] == "A":
                            self.start = (i, j)
                            row.append(False)
                        elif contents[i][j] == "B":
                            self.goal = (i, j)
                            row.append(False)
                        elif contents[i][j] == " ":
                            row.append(False)
                        else:
                            row.append(True)
                    except IndexError:
                        row.append(False)
                self.walls.append(row)

            # Validate start and goal for file-loaded mazes
            if not hasattr(self, 'start') or not hasattr(self, 'goal'):
                raise Exception("maze must have exactly one start and one goal point")

        elif width and height:
            # Generate a new maze with given dimensions
            self.width = width
            self.height = height
            # Initialize all cells as walls
            self.walls = [[True for _ in range(width)] for _ in range(height)]
            self.start = None
            self.goal = None
            self.generate_maze() # Call maze generation algorithm

        else:
            raise Exception("Must provide either a filename or width and height to initialize Maze.")

        # Common validation for both loading and generation
        if not hasattr(self, 'start') or not hasattr(self, 'goal'):
            # This check is mainly for generated mazes if they fail to set start/goal
            raise Exception("Generated maze must have a start and a goal point.")

    def generate_maze(self):
        """
        Generates a maze using a Recursive Backtracking (DFS) algorithm,
        then adds additional paths by randomly removing some walls.
        This sets self.walls, self.start, and self.goal.
        """
        # Initialize all cells as walls (True)
        self.walls = [[True for _ in range(self.width)] for _ in range(self.height)]
        
        # Keep track of visited cells during generation
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        # Stack for DFS
        stack = []

        # Start from a random cell
        start_row = random.randrange(0, self.height, 2)
        start_col = random.randrange(0, self.width, 2)
        
        self.walls[start_row][start_col] = False # Make start cell a path
        visited[start_row][start_col] = True
        stack.append((start_row, start_col))

        # Define directions (dr, dc) and corresponding wall removal actions
        # (dr, dc) for moving to neighbor, (w_dr, w_dc) for removing wall between
        directions = [
            ((0, 2), (0, 1)),   # Right
            ((0, -2), (0, -1)),  # Left
            ((2, 0), (1, 0)),   # Down
            ((-2, 0), (-1, 0))   # Up
        ]

        while stack:
            current_row, current_col = stack[-1]
            
            # Find unvisited neighbors (2 steps away)
            unvisited_neighbors = []
            for (dr, dc), (w_dr, w_dc) in directions:
                new_row, new_col = current_row + dr, current_col + dc
                if 0 <= new_row < self.height and 0 <= new_col < self.width and not visited[new_row][new_col]:
                    unvisited_neighbors.append(((new_row, new_col), (current_row + w_dr, current_col + w_dc)))
            
            if unvisited_neighbors:
                # Pick a random unvisited neighbor
                (next_row, next_col), (wall_row, wall_col) = random.choice(unvisited_neighbors)
                
                # Carve path to neighbor (make current cell, wall cell, and neighbor cell a path)
                self.walls[wall_row][wall_col] = False # Remove wall
                self.walls[next_row][next_col] = False # Make neighbor a path
                visited[next_row][next_col] = True
                stack.append((next_row, next_col))
            else:
                stack.pop() # Backtrack

        # --- Add multiple paths by randomly removing walls ---
        # Iterate through all cells and consider removing walls to create loops
        for r in range(1, self.height - 1):
            for c in range(1, self.width - 1):
                # Only consider internal walls
                if self.walls[r][c]:
                    # Check if removing this wall connects two already open paths
                    # This is a simplified check, more robust would be to check connectivity
                    # For now, if it's a wall and has open neighbors, consider removing it
                    
                    # Check horizontal wall
                    if c + 1 < self.width and not self.walls[r][c-1] and not self.walls[r][c+1]:
                        if random.random() < 0.1: # 10% chance to remove a wall
                            self.walls[r][c] = False
                    # Check vertical wall
                    if r + 1 < self.height and not self.walls[r-1][c] and not self.walls[r+1][c]:
                        if random.random() < 0.1: # 10% chance to remove a wall
                            self.walls[r][c] = False

        # Set start and goal points randomly
        # Ensure start and goal are open cells and distinct
        open_cells = []
        for r in range(self.height):
            for c in range(self.width):
                if not self.walls[r][c]:
                    open_cells.append((r, c))

        if not open_cells:
            raise Exception("Generated maze has no open paths.")

        self.start = random.choice(open_cells)
        
        # Ensure goal is different from start
        if len(open_cells) > 1:
            self.goal = random.choice([cell for cell in open_cells if cell != self.start])
        else: # Handle very small mazes where start might be the only open cell
            self.goal = self.start
            if self.height > 1 or self.width > 1: # Try to find a different goal if possible
                # If only one cell, start and goal are the same
                pass
            else:
                raise Exception("Maze too small to have distinct start and goal.")

    def reset_state(self):
        """
        Resets the maze's solution and exploration state.
        This should be called before solving with a new algorithm.
        """
        self.solution = None
        self.co_path = 0
        self.num_explored = 0
        self.explored = set()
        self.frames = [] # Clear frames for new GIF generation

    def print(self):
        # Print the maze with solution and explored nodes if available
        solution = self.solution[1] if self.solution is not None else None

        print()

        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")                # Wall

                elif (i, j) == self.start:
                    print("A", end="")                # Start

                elif (i, j) == self.goal:
                    print("B", end="")                # Goal

                elif solution is not None and (i, j) in solution:
                    print("*", end="")                # Solution path

                elif solution is not None and (i, j) in self.explored:
                    print(".", end="")                # Explored node

                else:
                    print(" ", end="")                # Empty space

            print()

        print()

    def neighbors(self, state):
        # Return list of valid neighboring cells from the current state
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def heuristic(self, state, method):
        """Computes the heuristic distance from the given state to the goal."""
        row, col = state
        goal_row, goal_col = self.goal
        if method == "manhattan":
            return abs(row - goal_row) + abs(col - goal_col)
        elif method == "euclidean":
            return ((row - goal_row) ** 2 + (col - goal_col) ** 2) ** 0.5
        elif method == "chebyshev":
            return max(abs(row - goal_row), abs(col - goal_col))

    def solve(self, algo, save_gif=False, method = "manhattan"):
        """
        Finds a solution to the maze using the specified algorithm.
        Optionally saves the solution process as a GIF.
        """
        # Reset maze state before starting a new solve operation
        self.reset_state()

        # Initialize frontier with the starting position
        start = Node(state=self.start, parent=None, action=None, score_h=self.heuristic(self.start, method))
        if algo == "bidirectional": # Special case for bidirectional search
            self.solve_bidirectional(save_gif=save_gif)
            return

        if algo == "bfs":
            from frontiers import QueueFrontier 
            frontier = QueueFrontier() 

        elif algo == "dfs":
            from frontiers import StackFrontier 
            frontier = StackFrontier() 

        elif algo == "a*":
            from frontiers import PriorityQueueFrontierforAStar 
            frontier = PriorityQueueFrontierforAStar() 

        elif algo == "greedy":
            from frontiers import PriorityQueueFrontierforGreedy 
            frontier = PriorityQueueFrontierforGreedy() 

        elif algo == "uniform":
            from frontiers import PriorityQueueFrontierforUniformCost 
            frontier = PriorityQueueFrontierforUniformCost() 
        
        # Add the start node to the frontier
        frontier.add(start)
        
        # self.explored = set() # This line is moved to reset_state()

        if save_gif:
            self.frames.append(self._get_current_image(show_explored=True))
        # Main loop to search for the solution

        while True:
            # If nothing left in frontier, then no path exists
            if frontier.empty():
                raise Exception("no solution")

            # Choose a node from the frontier
            node = frontier.remove()
            self.num_explored += 1

            if save_gif:
                self.frames.append(self._get_current_image(show_explored=True))

            # If node is the goal, reconstruct the solution path
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                    self.co_path += 1
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                if save_gif:
                    self.frames.append(self._get_current_image(show_solution=True, show_explored=True))
                return

            # Mark node as explored
            self.explored.add(node.state)

            # Add neighbors to frontier
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    score_g = node.score_g + 1
                    if algo in ["a*", "greedy"]:
                        # For A* and Greedy, we need to calculate the heuristic score
                        score_h = self.heuristic(state, method)
                    else:
                        score_h = 0 # For BFS, DFS, and Uniform Cost, heuristic is not used

                    child = Node(state=state, parent=node, action=action, score_g=score_g, score_h=score_h) 
                    frontier.add(child)

    def solve_bidirectional(self, save_gif=False):
        """Solves the maze using bidirectional BFS."""
        self.reset_state() # Ensure state is reset

        # Initialize frontiers for both directions
        from frontiers import QueueFrontier
        frontier_start = QueueFrontier()
        frontier_goal = QueueFrontier()

        # Nodes for start and goal
        start_node = Node(state=self.start, parent=None, action=None)
        goal_node = Node(state=self.goal, parent=None, action=None)

        frontier_start.add(start_node)
        frontier_goal.add(goal_node)

        # To keep track of explored nodes and their corresponding Node objects from both sides
        explored_start_nodes = {self.start: start_node}
        explored_goal_nodes = {self.goal: goal_node}
        
        # For GIF visualization
        if save_gif:
            self.frames.append(self._get_current_image(show_explored=True))

        while not frontier_start.empty() and not frontier_goal.empty():
            # Alternate expansion between start and goal frontiers

            # Expand from start side
            current_start = frontier_start.remove()
            self.explored.add(current_start.state) 
            self.num_explored += 1 # Increment explored count

            if save_gif:
                self.frames.append(self._get_current_image(show_explored=True))

            # Check for meeting point
            if current_start.state in explored_goal_nodes:
                meet_node_from_goal_side = explored_goal_nodes[current_start.state]
                self._reconstruct_bidirectional_path(current_start, meet_node_from_goal_side)
                if save_gif:
                    self.frames.append(self._get_current_image(show_solution=True, show_explored=True))
                return

            # Add neighbors to start frontier
            for action, state in self.neighbors(current_start.state):
                if state not in explored_start_nodes:
                    new_node = Node(state=state, parent=current_start, action=action)
                    explored_start_nodes[state] = new_node
                    frontier_start.add(new_node)

            # Expand from goal side
            current_goal = frontier_goal.remove()
            self.explored.add(current_goal.state)
            self.num_explored += 1

            if save_gif:
                self.frames.append(self._get_current_image(show_explored=True))

            # Check for meeting point
            if current_goal.state in explored_start_nodes:
                meet_node_from_start_side = explored_start_nodes[current_goal.state]
                self._reconstruct_bidirectional_path(meet_node_from_start_side, current_goal)
                if save_gif:
                    self.frames.append(self._get_current_image(show_solution=True, show_explored=True))
                return

            # Add neighbors to goal frontier
            for action, state in self.neighbors(current_goal.state):
                if state not in explored_goal_nodes:
                    new_node = Node(state=state, parent=current_goal, action=action)
                    explored_goal_nodes[state] = new_node
                    frontier_goal.add(new_node)
        
        # If no solution is found
        raise Exception("No solution found by bidirectional search.")

    def _reconstruct_bidirectional_path(self, node_from_start_side, node_from_goal_side):
        """
        Reconstructs the full path from the start to the goal by merging
        the two paths found by bidirectional search.
        """
        path_start = []
        current = node_from_start_side
        while current.parent is not None:
            path_start.append(current.action)
            current = current.parent
        path_start.reverse() # Reverse to get path from start to meeting point

        path_goal = []
        current = node_from_goal_side
        while current.parent is not None:
            # Reverse actions for the path from the goal side
            if current.action == "up":
                path_goal.append("down")
            elif current.action == "down":
                path_goal.append("up")
            elif current.action == "left":
                path_goal.append("right")
            elif current.action == "right":
                path_goal.append("left")
            current = current.parent

        full_path_actions = path_start + path_goal

        # Reconstruct the full path of cells
        full_path_cells = []
        current_state = self.start
        full_path_cells.append(current_state)
        for action in full_path_actions:
            if action == "up":
                current_state = (current_state[0] - 1, current_state[1])
            elif action == "down":
                current_state = (current_state[0] + 1, current_state[1])
            elif action == "left":
                current_state = (current_state[0], current_state[1] - 1)
            elif action == "right":
                current_state = (current_state[0], current_state[1] + 1)
            full_path_cells.append(current_state)
        
        # Store the solution in the maze properties
        self.solution = (full_path_actions, full_path_cells)
        self.co_path = len(full_path_actions)

    def _get_current_image(self, show_solution=False, show_explored=False):
        """
        Creates and returns a PIL Image of the current maze state.
        This is a helper function for GIF generation.
        """
        cell_size = 50
        cell_border = 2

        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    fill = (40, 40, 40)              # Wall
                elif (i, j) == self.start:
                    fill = (255, 0, 0)               # Start
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)              # Goal
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)           # Solution path
                elif show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)             # Explored node
                else:
                    fill = (237, 240, 252)           # Empty cell

                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )
        return img

    def output_image(self, filename, show_solution=True, show_explored=False):
        # Save an image of the maze with the solution and/or explored nodes
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                # Walls
                if col:
                    fill = (40, 40, 40)
                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)
                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)
                # Solution
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)
                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)
                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)

    def get_state_image(self, cell_size=30):
        """
        Returns a Tkinter PhotoImage of the current maze state
        """
        img = Image.new("RGB", (self.width*cell_size, self.height*cell_size), "white")
        draw = ImageDraw.Draw(img)
    
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                x1, y1 = j*cell_size, i*cell_size
                x2, y2 = x1+cell_size, y1+cell_size
            
                if col:
                    draw.rectangle([x1, y1, x2, y2], fill="black")
                elif (i, j) == self.start:
                    draw.rectangle([x1, y1, x2, y2], fill="red")
                elif (i, j) == self.goal:
                    draw.rectangle([x1, y1, x2, y2], fill="green")
                elif self.solution and (i, j) in self.solution[1]:
                    draw.rectangle([x1, y1, x2, y2], fill="blue")
                elif hasattr(self, 'explored') and (i, j) in self.explored:
                    draw.rectangle([x1, y1, x2, y2], fill="gray")
    
        return ImageTk.PhotoImage(img)

    def save_solution_gif(self, gif_path="maze_solution.gif", frame_delay=250):
        """
        Generate and save an animated GIF of the maze solving process.
        This method uses the frames collected during the last call to solve().
        """
        if not self.frames:
            # If no frames were collected, generate frames now
            raise Exception("No frames available. Please solve the maze with frame collection enabled.")
        imageio.mimsave(gif_path, self.frames, fps=1000/frame_delay)

    def save_to_file(self, filename="generated_maze.txt"):
        """
        Saves the current maze configuration to a text file.
        'A' represents the start, 'B' represents the goal,
        ' ' (space) represents a path, and '#' represents a wall.
        """
        try:
            with open(filename, "w") as f:
                for r in range(self.height):
                    row_str = ""
                    for c in range(self.width):
                        if (r, c) == self.start:
                            row_str += "A"
                        elif (r, c) == self.goal:
                            row_str += "B"
                        elif self.walls[r][c]:
                            row_str += "#"
                        else:
                            row_str += " "
                    f.write(row_str + "\n")
            print(f"Maze saved successfully to {filename}")
        except Exception as e:
            print(f"Error saving maze to file: {e}")


