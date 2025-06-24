# gui.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from maze import Maze
from PIL import Image, ImageTk
import time
import threading
import imageio

class MazeSolverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver")
        self.setup_ui()
        self.cell_size = 30  # Size of each cell in pixels
        self.maze = None # Initialize maze to None
        
    def setup_ui(self):
        # Create the control frame for buttons and input fields
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10, fill=tk.X)
        
        # Maze Generation Controls
        tk.Label(control_frame, text="Width:").pack(side=tk.LEFT, padx=2)
        self.width_entry = tk.Entry(control_frame, width=5)
        self.width_entry.insert(0, "21") # Default width
        self.width_entry.pack(side=tk.LEFT, padx=2)

        tk.Label(control_frame, text="Height:").pack(side=tk.LEFT, padx=2)
        self.height_entry = tk.Entry(control_frame, width=5)
        self.height_entry.insert(0, "21") # Default height
        self.height_entry.pack(side=tk.LEFT, padx=2)

        tk.Button(control_frame, text="Generate Maze", command=self.generate_maze).pack(side=tk.LEFT, padx=5)
        
        # Button to load maze from file
        tk.Button(control_frame, text="Load Maze", command=self.load_maze).pack(side=tk.LEFT, padx=5)
        
        # Algorithm selection dropdown
        self.algo_var = tk.StringVar(value="bfs")
        tk.OptionMenu(control_frame, self.algo_var, "a*", "bfs", "dfs", "greedy", "uniform", "bidirectional").pack(side=tk.LEFT, padx=5)

        # Heuristic selection (enabled only for A* and Greedy)
        tk.Label(control_frame, text="Heuristic:").pack(side=tk.LEFT, padx=2)
        self.heuristic_var = tk.StringVar(value="manhattan")
        self.heuristic_combobox = ttk.Combobox(control_frame, textvariable=self.heuristic_var, 
                                            values=["manhattan", "euclidean", "chebyshev"], state="disabled", width=10)
        self.heuristic_combobox.pack(side=tk.LEFT, padx=2)
        self.algo_var.trace("w", self.on_algo_selected)  # Update heuristic options when algorithm changes
        self.on_algo_selected() # Set initial heuristic state
        
        # Buttons for solving and saving
        tk.Button(control_frame, text="Solve", command=self.solve_maze).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Solve with GIF", command=lambda: self.solve_maze(solve_gif=True)).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Save Solution", command=self.save_solution).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Save Solution GIF", command=self.save_solution_gif).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Save maze to file", command=self.save_maze).pack(side=tk.LEFT, padx=5)

        # Canvas with scrollbars for displaying the maze
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(expand=True, fill=tk.BOTH)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.h_scroll = ttk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.v_scroll = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def on_algo_selected(self, *args):
        """Enables/disables heuristic selection based on the chosen algorithm."""
        selected_algo = self.algo_var.get()
        if selected_algo in ["a*", "greedy"]:
            self.heuristic_combobox.config(state="readonly")
        else:
            self.heuristic_combobox.config(state="disabled")
        
    def load_maze(self):
        # Load a maze from a text file
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                self.maze = Maze(filename=file_path)
                self.adjust_canvas_size()
                self.draw_maze()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def generate_maze(self):
        # Generate a new random maze with the specified dimensions
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())

            # Ensure dimensions are odd and >= 3 for proper maze generation
            if width < 3 or height < 3 or width % 2 == 0 or height % 2 == 0:
                messagebox.showerror("Invalid Dimensions", "Width and Height must be odd numbers greater than or equal to 3 for proper maze generation.")
                return

            self.maze = Maze(width=width, height=height)
            self.adjust_canvas_size()
            self.draw_maze()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integer values for Width and Height.")
        except Exception as e:
            messagebox.showerror("Maze Generation Error", str(e))
    
    def adjust_canvas_size(self):
        # Adjust the canvas scroll region based on the maze size
        if hasattr(self, 'maze'):
            canvas_width = self.maze.width * self.cell_size
            canvas_height = self.maze.height * self.cell_size
            self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
    
    def draw_maze(self):
        """Draws the maze on the Canvas."""
        self.canvas.delete("all")
        
        if not hasattr(self, 'maze') or self.maze is None:
            return
            
        for i, row in enumerate(self.maze.walls):
            for j, col in enumerate(row):
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                if col:  # Wall
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#282828", outline="") # Dark gray wall
                elif (i, j) == self.maze.start:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#FF0000", outline="") # Red start
                elif (i, j) == self.maze.goal:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#00AB1C", outline="") # Green goal
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#EDF0FC", outline="") # Off-white empty cell
    
    def solve_maze(self, solve_gif=False):
        # Solve the maze using the selected algorithm and heuristic
        if not hasattr(self, 'maze') or self.maze is None:
            messagebox.showwarning("Warning", "Please load or generate a maze first!")
            return
            
        # Clear the canvas by redrawing the maze in its initial state
        self.draw_maze()

        def solve_thread():
            algo = self.algo_var.get()
            heuristic = self.heuristic_var.get() if algo in ["a*", "greedy"] else None
            start_time = time.time()
            
            try:
                if solve_gif:
                    if heuristic:
                        self.maze.solve(algo, save_gif=True, method=heuristic)
                    else:
                        self.maze.solve(algo, save_gif=True)
                else:
                    if heuristic:
                        self.maze.solve(algo, method=heuristic)
                    else:
                        self.maze.solve(algo)
                end_time = time.time()
                self.draw_solution()
                messagebox.showinfo("Info", f"Solved in {end_time-start_time:.2f} seconds\n"
                                        f"Path length: {self.maze.co_path}\n"
                                        f"Explored nodes: {self.maze.num_explored}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            
        # Run the solving process in a separate thread to keep the GUI responsive
        threading.Thread(target=solve_thread, daemon=True).start()
    
    def draw_solution(self):
        """Draws the solution path and explored nodes on the maze."""
        if hasattr(self, 'maze') and self.maze.solution:
            # First, draw explored nodes (if any)
            if hasattr(self.maze, 'explored'):
                for i, j in self.maze.explored:
                    x1, y1 = j * self.cell_size, i * self.cell_size
                    x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                    # Check if it's not the start or goal before drawing as explored
                    if (i, j) != self.maze.start and (i, j) != self.maze.goal:
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#D46155", outline="") # Reddish/Orange explored

            # Then draw the solution path on top (if it exists)
            for i, j in self.maze.solution[1]:
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                # Ensure start and goal are not overwritten by blue solution path
                if (i, j) != self.maze.start and (i, j) != self.maze.goal:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#DCF071", outline="") # Yellow solution
    
    def save_solution(self):
        # Save the current maze solution as a PNG image
        if hasattr(self, 'maze') and self.maze.solution:
            file_path = filedialog.asksaveasfilename(defaultextension=".png")
            if file_path.endswith(".png"):
                self.maze.output_image(file_path, show_explored=True)
            else:
                messagebox.showerror("Error", "Please save the file with a .png extension.")

    def save_solution_gif(self):
        # Save the solution process as an animated GIF
        if hasattr(self, 'maze') and self.maze.solution:
            file_path = filedialog.asksaveasfilename(defaultextension=".gif")
            if file_path.endswith(".gif"):
                self.maze.save_solution_gif(gif_path=file_path)
            else:
                messagebox.showerror("Error", "Please save the file with a .gif extension.")

    def save_maze(self):
        # Save the current maze to a text file
        if not hasattr(self, 'maze'):
            messagebox.showwarning("Warning", "Please load or generate a maze first!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path.endswith(".txt"):
            self.maze.save_to_file(file_path)
        else:
            messagebox.showerror("Error", "Please save the file with a .txt extension.")

if __name__ == "__main__":
    # Start the Tkinter main loop
    root = tk.Tk()
    root.geometry("800x600")
    app = MazeSolverGUI(root)
    root.mainloop()